import unittest
from seye.integration.contracts import describe,validate_request,validate_response,decode_request

class ContractTests(unittest.TestCase):
    def test_required_strict_fields_duplicates_depth_and_nonfinite_rejected(self):
        valid={'schema_version':1,'request_id':'contract','action':'analyze','image':'a.png'}
        self.assertEqual(validate_request(valid,True),valid)
        with self.assertRaises(ValueError):validate_request(dict(valid,unexpected=1),True)
        with self.assertRaises(ValueError):validate_request({k:v for k,v in valid.items() if k!='image'})
        for raw in (b'{"schema_version":1,"schema_version":2}',b'{"n":NaN}'):
            with self.assertRaises(ValueError):decode_request(raw)
        deep=[];cursor=deep
        for _ in range(40):cursor.append([]);cursor=cursor[0]
        with self.assertRaises(ValueError):validate_request(dict(valid,data=deep))

    def test_response_identity_and_result_error_exclusion(self):
        result={'schema_version':1,'request_id':'r','success':True,'result':{}}
        self.assertEqual(validate_response(result,'r'),result)
        for bad in (dict(result,error={'type':'x','message':'x'}),dict(result,request_id='other'),dict(result,success=1)):
            with self.assertRaises(ValueError):validate_response(bad,'r')
        self.assertIn('analyze',describe()['actions'])
