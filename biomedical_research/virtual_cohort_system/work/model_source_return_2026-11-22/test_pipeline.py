import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pipeline import consulted


class Tables:
    def index(self):
        return [{"id":x,"status":"available"} for x in ("paper:A","paper:B")]

    def get(self,key):
        return {"id":key}


class ReturnTest(unittest.TestCase):
    def test_return_can_stop_without_a_lookup(self):
        with TemporaryDirectory() as name:
            def no_reader(*args):
                self.fail("Unexpected table lookup")
            for operation in ("keep","abstain"):
                hist, end = consulted(Path(name)/operation,"research","source",{},Tables(),
                    decide=lambda *_:{"action":operation,"reason":"No usable question"},reader=no_reader)
                self.assertEqual(hist,[])
                self.assertEqual(end["action"],operation)

    def test_second_choice_has_only_requested_readings(self):
        with TemporaryDirectory() as name:
            def decide(root,number,prompt):
                state = json.loads(prompt)
                history = state["previous_table_requests_and_results"]
                self.assertEqual(state["remaining_table_reads"],3-number)
                self.assertEqual(len(history),number-1)
                if number==1:
                    self.assertNotIn("answer for",prompt)
                else:
                    self.assertEqual(history[-1]["reading"]["cells"],["answer for "+str(number-1)])
                if number==3:
                    self.assertNotIn("read_table",state["actions"])
                    return {"action":"remodel","reason":"Based on the two returned cells"}
                return {"action":"read_table","id":"paper:"+("B" if number==1 else "A"),
                        "question":"Please check the definition","reason":"Needed for interpretation"}
            reads = []
            def reader(root,index,item,question):
                reads.append(item["id"])
                return {"id":item["id"],"cells":["answer for "+str(index)]}
            history,end = consulted(Path(name),"research","source",{},Tables(),decide=decide,reader=reader)
            self.assertEqual(reads,["paper:B","paper:A"])
            self.assertEqual(len(history),2)
            self.assertEqual(end["action"],"remodel")

    def test_reading_unlisted_or_repeat_table_is_refused(self):
        for key in ("unknown","paper:A"):
            with self.subTest(key=key), TemporaryDirectory() as name:
                actual=[]
                def reader(root,index,item,question):
                    actual.append(item["id"])
                    return {"id":item["id"]}
                with self.assertRaisesRegex(ValueError,"Invalid"):
                    consulted(Path(name),"study","source",{},Tables(),
                        decide=lambda *_:{"action":"read_table","id":key,"question":"cell?","reason":"gap"},
                        reader=reader)
                self.assertEqual(actual,[] if key=="unknown" else ["paper:A"])
