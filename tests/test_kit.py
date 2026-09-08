import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hermes_knowledge_kit import cli


class KitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'profile com espaço'
        self.area = self.home / 'knowledge-kit'
        self.binary = self.root / 'hermes'
        self.version('0.21.0')
        self.env = {'PATH': str(self.root), 'HOME': str(self.root), 'HERMES_HOME': str(self.home), 'PYTHONPATH': str(ROOT / 'src')}

    def version(self, version):
        self.binary.write_text('#!/bin/sh\nprintf "Hermes Agent v' + version + '\\n"\n')
        self.binary.chmod(0o700)

    def runcli(self, *args):
        return subprocess.run([sys.executable, '-m', 'hermes_knowledge_kit', *args], cwd=self.root, env=self.env, capture_output=True, text=True, timeout=20)

    def install(self, *args):
        result = self.runcli('install', *args)
        self.assertEqual(0, result.returncode, result.stderr)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def interrupt(self, phase, index=None):
        def fault(current, n=None):
            if current == phase and (index is None or index == n):
                raise cli.SimulatedInterruption()
        with patch.dict(os.environ, self.env, clear=True):
            with self.assertRaises(cli.SimulatedInterruption):
                cli.install(self.home, False, False, _fault_hook=fault)
        lock = self.area / cli.LOCK_PATH
        value = json.loads(lock.read_text())
        value['boot_id'] = 'previous-boot-test'
        lock.write_text(json.dumps(value))

    def test_dry_run(self):
        before = self.snapshot()
        self.assertEqual(0, self.runcli('install', '--dry-run').returncode)
        self.assertEqual(before, self.snapshot())
        self.assertNotIn('projeto-aurora', self.runcli('plan').stdout)

    def test_idempotence(self):
        self.install()
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())
        self.assertEqual(0, self.runcli('verify').returncode)

    def test_fixture(self):
        self.install('--fixture')
        self.assertIn('AZ-17', (self.area / 'projects/projeto-aurora.md').read_text())

    def test_identity_preserved(self):
        self.home.mkdir()
        source = self.home / 'AGENTS.md'
        source.write_text('identity')
        self.install()
        self.assertEqual(0, self.runcli('uninstall').returncode)
        self.assertFalse(self.area.exists())
        self.assertEqual('identity', source.read_text())

    def test_edits_preserved(self):
        self.install()
        source = self.area / 'MAPA.md'
        source.write_text('edited')
        self.assertEqual(3, self.runcli('verify').returncode)
        self.assertEqual(3, self.runcli('uninstall').returncode)
        self.assertEqual('edited', source.read_text())

    def test_extras_preserved(self):
        self.install()
        source = self.area / 'mine.md'
        source.write_text('mine')
        self.assertEqual(3, self.runcli('uninstall').returncode)
        self.assertEqual('mine', source.read_text())

    def test_occupied(self):
        self.area.mkdir(parents=True)
        (self.area / 'mine').write_text('mine')
        before = self.snapshot()
        self.assertEqual(2, self.runcli('install').returncode)
        self.assertEqual(before, self.snapshot())

    def test_relative_home(self):
        self.assertEqual(2, self.runcli('--home', 'relative', 'install').returncode)

    def test_symlink(self):
        outside = self.root / 'outside'
        outside.mkdir()
        self.home.symlink_to(outside)
        self.assertEqual(2, self.runcli('install').returncode)
        self.assertEqual([], list(outside.iterdir()))

    def test_hardlink(self):
        self.install()
        os.link(self.area / 'MAPA.md', self.area / 'alias')
        self.assertEqual(2, self.runcli('uninstall').returncode)

    def test_special(self):
        self.install()
        os.mkfifo(self.area / 'fifo')
        self.assertEqual(2, self.runcli('verify').returncode)

    def test_manifest_tampering(self):
        self.install()
        path = self.area / cli.MANIFEST_PATH
        value = json.loads(path.read_text())
        value['files'][0]['path'] = '../../outside'
        path.write_text(json.dumps(value))
        before = self.snapshot()
        self.assertEqual(2, self.runcli('uninstall').returncode)
        self.assertEqual(before, self.snapshot())

    def test_versions(self):
        self.binary.unlink()
        self.assertEqual(2, self.runcli('doctor').returncode)
        self.version('0.20.0')
        self.assertEqual(2, self.runcli('install').returncode)
        self.version('0.22.0')
        self.assertEqual(2, self.runcli('install').returncode)
        self.assertEqual(0, self.runcli('--allow-untested-hermes', 'install').returncode)

    def test_write_ahead(self):
        self.interrupt('before_file', 1)
        value = json.loads((self.area / cli.JOURNAL_PATH).read_text())
        self.assertEqual('AGENTS.md', value['created'][0]['path'])
        self.assertFalse((self.area / 'AGENTS.md').exists())
        self.assertEqual(0, self.runcli('rollback').returncode)
        self.assertFalse(self.area.exists())

    def test_partial_rollback(self):
        self.interrupt('after_file', 2)
        self.assertEqual(3, self.runcli('status').returncode)
        self.assertEqual(0, self.runcli('rollback').returncode)
        self.assertFalse(self.area.exists())

    def test_conflict_retry(self):
        self.interrupt('after_file', 1)
        source = self.area / 'AGENTS.md'
        source.write_text('edited')
        self.assertEqual(3, self.runcli('rollback').returncode)
        self.assertTrue((self.area / cli.LOCK_PATH).exists())
        source.rename(self.root / 'saved')
        self.assertEqual(0, self.runcli('rollback').returncode)
        self.assertFalse(self.area.exists())

    def test_commit_recovery(self):
        self.interrupt('after_manifest')
        result = self.runcli('rollback')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('commit concluído', result.stdout)
        self.assertEqual(0, self.runcli('verify').returncode)

    def test_live_lock(self):
        self.interrupt('after_file', 1)
        (self.area / cli.LOCK_PATH).write_text(json.dumps({'schema': 1, 'pid': os.getpid(), 'boot_id': cli._boot_id()}))
        self.assertEqual(2, self.runcli('rollback').returncode)

    def test_fsync(self):
        with patch.object(cli.os, 'fsync', wraps=os.fsync) as sync:
            cli.atomic_write(self.root / 'file', b'data')
        self.assertGreaterEqual(sync.call_count, 2)

    def test_zipapp_is_byte_deterministic(self):
        first = self.root / 'first.pyz'
        second = self.root / 'second.pyz'
        subprocess.run([sys.executable, str(ROOT / 'scripts/build_zipapp.py'), str(first)], check=True, capture_output=True)
        time.sleep(2.1)
        subprocess.run([sys.executable, str(ROOT / 'scripts/build_zipapp.py'), str(second)], check=True, capture_output=True)
        self.assertEqual(hashlib.sha256(first.read_bytes()).digest(), hashlib.sha256(second.read_bytes()).digest())

    def test_zipapp(self):
        artifact = self.root / 'kit.pyz'
        subprocess.run([sys.executable, str(ROOT / 'scripts/build_zipapp.py'), str(artifact)], check=True, capture_output=True)
        for args in [('doctor',), ('install', '--dry-run'), ('install',), ('verify',), ('install',), ('uninstall',)]:
            result = subprocess.run([sys.executable, str(artifact), *args], cwd=self.root, env=self.env, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.area.exists())
        invalid = subprocess.run([sys.executable, str(artifact), '--home', 'relative', 'install'], env=self.env, capture_output=True)
        self.assertEqual(2, invalid.returncode)

    def test_release_scan(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/check_release_tree.py')], cwd=ROOT, capture_output=True)
        self.assertEqual(0, result.returncode, result.stdout)

    def test_secret_scan(self):
        (self.root / 'bad.txt').write_text('-----BEGIN ' + 'PRIVATE KEY-----\nprivate-test-value')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/check_release_tree.py'), str(self.root)], capture_output=True, text=True)
        self.assertNotEqual(0, result.returncode)
        self.assertNotIn('private-test-value', result.stdout + result.stderr)
