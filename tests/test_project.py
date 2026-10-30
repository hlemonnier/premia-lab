"""Black-box contracts written before the new public-demo/archive tooling."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PublicProjectTests(unittest.TestCase):
    def test_frozen_n0_runtime(self):
        manifest = json.loads((ROOT/'docs/runtime_manifest.json').read_text())
        for name, expected in manifest.items():
            with self.subTest(path=name):
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected)

    def test_demo_runs_and_preserves_past(self):
        from examples.synthetic_demo import generate_market, replay
        import numpy as np
        r,x,c=generate_market(days=660, stocks=48, seed=20261030)
        original=replay(r,x,c)
        rr=r.copy();xx=x.copy()
        rng=np.random.default_rng(91)
        rr[630:]=rng.normal(0,.012,rr[630:].shape)
        xx[630:]=rng.normal(size=xx[630:].shape)
        changed=replay(rr,xx,c)
        prefix=replay(r[:631],x[:631],c)
        for other, rows in [(changed,631),(prefix,631)]:
            np.testing.assert_allclose(original['forecasts'][:rows],other['forecasts'][:rows],atol=1e-10,rtol=0)
        np.testing.assert_allclose(original['positions'][:378],changed['positions'][:378],atol=1e-10,rtol=0)
        np.testing.assert_allclose(original['positions'][:len(prefix['positions'])],prefix['positions'],atol=1e-10,rtol=0)
        self.assertGreater(np.max(np.abs(original['forecasts'][631:]-changed['forecasts'][631:])),1e-12)
        self.assertTrue(np.isfinite(original['net_returns']).all())
        self.assertLessEqual(float(np.abs(original['positions']).sum(1).max()),5.0000000001)
        np.testing.assert_array_equal(original['net_returns'],original['gross_returns']-original['costs'])
        self.assertEqual(original['provenance'],'independent_demo_generator_not_private_benchmark')

    def test_archive_preserves_versions_and_excludes_private_material(self):
        from tools.archive_research import build_archive, restore_snapshot, audit_snapshot
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'repo';root.mkdir()
            def git(*args):
                return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
            git('init','-b','main');git('config','user.name','Fixture');git('config','user.email','fixture@users.noreply.github.com')
            (root/'research').mkdir();(root/'source').mkdir()
            (root/'research/RESULTS.md').write_text('No new alpha is established.\n')
            (root/'source/costs.csv').write_text('stock,cost\n0,0.01\n')
            (root/'README.md').write_text('Research fixture\n')
            git('add','.');git('commit','-m','base')
            first=git('rev-parse','HEAD')
            git('checkout','-b','research/second')
            (root/'research/RESULTS.md').write_text('Negative result retained.\n')
            (root/'research/runner.py').write_text('print("experiment")\n')
            git('add','.');git('commit','-m','second');second=git('rev-parse','HEAD')
            destination=Path(temporary)/'out'
            manifest=build_archive(root,{'main':first,'research/second':second},destination)
            self.assertEqual(len(manifest['snapshots']),2)
            self.assertTrue(audit_snapshot(destination)['passed'])
            for label,expected in [('main','No new alpha is established.\n'),('research/second','Negative result retained.\n')]:
                target=Path(temporary)/label.replace('/','_')
                restore_snapshot(destination,label,target)
                self.assertEqual((target/'research/RESULTS.md').read_text(),expected)
                self.assertFalse((target/'source/costs.csv').exists())
            self.assertTrue(any(row['reason']=='third_party_source' for s in manifest['snapshots'] for row in s['excluded']))

if __name__=='__main__':
    unittest.main()
