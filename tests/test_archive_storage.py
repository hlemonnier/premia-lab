"""E2E contracts for restoring archived bytes omitted/normalized by Git."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.archive_research import build_archive, audit_snapshot

class ArchiveStorageTests(unittest.TestCase):
    def test_repair_then_staged_objects_are_byte_exact(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)/'repo'; repo.mkdir()
            def git(*args):
                return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
            git('init','-b','main');git('config','user.name','Fixture');git('config','user.email','fixture@users.noreply.github.com')
            (repo/'research').mkdir()
            (repo/'research/result.csv').write_bytes(b'metric,value\r\nscore,1.5\r\n')
            (repo/'research/run.log').write_bytes(b'Negative result retained.\n')
            git('add','.');git('commit','-m','record fixture')
            archive=repo/'archive';build_archive(repo,{'main':git('rev-parse','HEAD')},archive)
            objects=list((archive/'archive/objects').rglob('*.*'))
            for obj in objects:
                if obj.suffix=='.log':obj.unlink()
                elif obj.suffix=='.csv':obj.write_bytes(obj.read_bytes().replace(b'\r\n',b'\n'))
            result=subprocess.run([sys.executable,str(ROOT/'tools/repair_archive.py'),'--repo',str(repo),'--archive',str(archive),'--repair'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout)
            self.assertEqual(report['restored_objects'],2)
            self.assertTrue(audit_snapshot(archive)['passed'])
            (repo/'.gitattributes').write_text('* text=auto eol=lf\narchive/archive/objects/** -text\n')
            git('add','.')
            verified=subprocess.run([sys.executable,str(ROOT/'tools/repair_archive.py'),'--repo',str(repo),'--archive',str(archive),'--staged'],capture_output=True,text=True)
            self.assertEqual(verified.returncode,0,verified.stdout+verified.stderr)
            self.assertEqual(json.loads(verified.stdout)['staged_objects_verified'],len(objects))

if __name__=='__main__':unittest.main()
