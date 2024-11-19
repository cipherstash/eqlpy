import unittest
from datetime import date

from eqlpy.eqlalchemy import *

from pprint import pprint


class EqlAlchemyTest(unittest.TestCase):
    def assert_common_parts(self, parsed):
        self.assertIsNone(parsed['q'])
        self.assertEqual(parsed['i']['t'], "table")
        self.assertEqual(parsed['i']['c'], "column")
        self.assertEqual(parsed['v'], 1)

    def test_encrypted_int(self):
        col_type = EncryptedInt("table", "column")
        bound = col_type.process_bind_param(-2, None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], "-2")

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, -2)

    def test_encrypted_boolean_false(self):
        col_type = EncryptedBoolean("table", "column")
        bound = col_type.process_bind_param(False, None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], "false")

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, False)

    def test_encrypted_boolean_true(self):
        col_type = EncryptedBoolean("table", "column")
        bound = col_type.process_bind_param(True, None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], "true")

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, True)

    def test_encrypted_date(self):
        col_type = EncryptedDate("table", "column")
        bound = col_type.process_bind_param(date(2024, 11, 17), None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], date(2024, 11, 17).isoformat())

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, date(2024, 11, 17))

    def test_encrypted_float(self):
        col_type = EncryptedFloat("table", "column")
        bound = col_type.process_bind_param(-0.01, None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], "-0.01")

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, -0.01)

    def test_encrypted_utf8_str(self):
        col_type = EncryptedUtf8Str("table", "column")
        bound = col_type.process_bind_param("test string", None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], "test string")

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, "test string")

    def test_encrypted_jsonb(self):
        col_type = EncryptedJsonb("table", "column")
        bound = col_type.process_bind_param({"key": "value"}, None)
        parsed = json.loads(bound)
        self.assert_common_parts(parsed)
        self.assertEqual(parsed['p'], '{"key": "value"}')

        result = col_type.process_result_value(parsed, None)
        self.assertEqual(result, {"key": "value"})

    def test_nones(self):
        col_types = [ EncryptedInt, EncryptedBoolean, EncryptedDate, EncryptedFloat, EncryptedUtf8Str, EncryptedJsonb ]

        for col_type in col_types:
            bound = col_type("table", "column").process_bind_param(None, None)
            self.assertIsNone(bound)


