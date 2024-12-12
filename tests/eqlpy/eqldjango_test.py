import unittest
import os
from eqlpy.eqldjango import *
from datetime import date


class EqlDjangoTest(unittest.TestCase):
    def assert_common_parts(self, parsed):
        self.assertIsNone(parsed["q"])
        self.assertEqual(parsed["v"], 1)

    def test_encrypted_int(self):
        col_type = EncryptedInt()
        prep_value = col_type.get_prep_value(-2)
        self.assert_common_parts(prep_value)
        self.assertEqual("-2", prep_value["p"])
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(-2, db_value)

    def test_encrypted_boolean_false(self):
        col_type = EncryptedBoolean()
        prep_value = col_type.get_prep_value(False)
        self.assert_common_parts(prep_value)
        self.assertEqual("false", prep_value["p"])
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(False, db_value)

    def test_encrypted_boolean_true(self):
        col_type = EncryptedBoolean()
        prep_value = col_type.get_prep_value(True)
        self.assert_common_parts(prep_value)
        self.assertEqual("true", prep_value["p"])
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(True, db_value)

    def test_encrypted_date(self):
        col_type = EncryptedDate()
        prep_value = col_type.get_prep_value(date(2024, 11, 17))
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(date(2024, 11, 17), db_value)

    def test_encrypted_float(self):
        col_type = EncryptedFloat()
        prep_value = col_type.get_prep_value(-0.01)
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(-0.01, db_value)

    def test_encrypted_text(self):
        col_type = EncryptedText()
        prep_value = col_type.get_prep_value("test string")
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual("test string", db_value)

    def test_encrypted_jsonb(self):
        col_type = EncryptedJsonb()
        prep_value = col_type.get_prep_value({"key": "value"})
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual({"key": "value"}, db_value)

    def test_nones(self):
        col_types = [
            EncryptedInt,
            EncryptedBoolean,
            EncryptedDate,
            EncryptedFloat,
            EncryptedText,
            EncryptedJsonb,
        ]

        for col_type in col_types:
            prep_value = col_type().get_prep_value(None)
            self.assertIsNone(prep_value)

    def test_table_and_column_name(self):
        col_type = EncryptedInt(eql_table="some_table", eql_column="some_column")
        prep_value = col_type.get_prep_value(0)
        self.assertEqual("some_table", prep_value["i"]["t"])
        self.assertEqual("some_column", prep_value["i"]["c"])
