import unittest
import os
from eqlpy.eqldjango import *
from datetime import date


class EqlDjangoTest(unittest.TestCase):
    def assert_common_parts(self, parsed):
        self.assertIsNone(parsed["q"])
        self.assertEqual(parsed["i"]["t"], "table")
        self.assertEqual(parsed["i"]["c"], "column")
        self.assertEqual(parsed["v"], 1)

    def test_age(self):
        col_type = EncryptedInt(table="table", column="column")
        prep_value = col_type.get_prep_value(-2)
        self.assert_common_parts(prep_value)
        self.assertEqual("-2", prep_value["p"])
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(-2, db_value)

    def test_is_citizen_false(self):
        col_type = EncryptedBoolean(table="table", column="column")
        prep_value = col_type.get_prep_value(False)
        self.assert_common_parts(prep_value)
        self.assertEqual("false", prep_value["p"])
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(False, db_value)

    def test_is_citizen_true(self):
        col_type = EncryptedBoolean(table="table", column="column")
        prep_value = col_type.get_prep_value(True)
        self.assert_common_parts(prep_value)
        self.assertEqual("true", prep_value["p"])
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(True, db_value)

    def test_start_date(self):
        col_type = EncryptedDate(table="table", column="column")
        prep_value = col_type.get_prep_value(date(2024, 11, 17))
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(date(2024, 11, 17), db_value)

    def test_weight(self):
        col_type = EncryptedFloat(table="table", column="column")
        prep_value = col_type.get_prep_value(-0.01)
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual(-0.01, db_value)

    def test_encrypted_text(self):
        col_type = EncryptedText(table="table", column="column")
        prep_value = col_type.get_prep_value("test string")
        self.assert_common_parts(prep_value)
        db_value = col_type.from_db_value(prep_value, None, None)
        self.assertEqual("test string", db_value)

    def test_extra_info(self):
        col_type = EncryptedJsonb(table="table", column="column")
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
            prep_value = col_type(table="table", column="column").get_prep_value(None)
            self.assertIsNone(prep_value)
