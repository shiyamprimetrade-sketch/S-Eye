import unittest,tempfile
from pathlib import Path
from copy import deepcopy
from seye.video.continuity import ContinuityTracker
from seye.video.checkpoint import snapshot,restore,save,load
from seye.core.storage import checksum

class PersistenceTests(unittest.TestCase):
    def test_resumed_sequence_exactly_matches_uninterrupted(self):
        t=ContinuityTracker(session_id='resume')
        row=lambda x:{'class':'region','box':[x,10,x+20,30]}
        t.update([row(10)],0,[100,80]);t.update([], .5,[100,80])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'state.json';save(path,t,'a'*64,d)
            other=load(path,'a'*64,d)
            self.assertEqual(t.update([row(12)],1,[100,80]),other.update([row(12)],1,[100,80]))
            with self.assertRaises(FileExistsError):save(path,t,'a'*64,d)
            with self.assertRaises(PermissionError):save(Path(d).parent/'bad.json',t,'a'*64,d)

    def test_corruption_wrong_source_and_rehashed_invalid_state_rejected(self):
        t=ContinuityTracker(session_id='strict');t.update([],0,[100,80]);value=snapshot(t,'a'*64)
        with self.assertRaises(ValueError):restore(value,'b'*64)
        for key,bad in (('frame_count',True),('next_id',9999),('size',[True,80]),('last_timestamp',-1)):
            mutated=deepcopy(value);mutated['payload']['state'][key]=bad
            with self.assertRaises(ValueError):restore(mutated,'a'*64)
            mutated['sha256']=checksum(mutated['payload'])
            with self.assertRaises(ValueError):restore(mutated,'a'*64)
