import unittest
import json
from datetime import date
from eqlpy.eql_types import *


class EqlTest(unittest.TestCase):
    def setUp(self):
        self.template_dict = json.loads(
            '{"k": "pt", "p": "1", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}'
        )

    def test(self):
        self.assertTrue(True)

    def test_to_db_format(self):
        self.assertEqual(
            EqlInt(1, "table", "column").to_db_format(),
            '{"k": "pt", "p": "1", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
        )

    def test_from_parsed_json_uses_p_value(self):
        self.template_dict["p"] = "1"
        self.assertEqual(EqlInt.from_parsed_json(self.template_dict), 1)

    def test_eql_int_to_db_format(self):
        eql_int = EqlInt(123, "table", "column")
        self.assertEqual(
            '{"k": "pt", "p": "123", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
            eql_int.to_db_format(),
        )

    def test_eql_int_from_parsed_json(self):
        self.template_dict["p"] = "123"
        self.assertEqual(EqlInt.from_parsed_json(self.template_dict), 123)

    def test_eql_bool_to_db_format_true(self):
        eql_bool = EqlBool(True, "table", "column")
        self.assertEqual(
            '{"k": "pt", "p": "true", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
            eql_bool.to_db_format(),
        )

    def test_eql_bool_to_db_format_false(self):
        eql_bool = EqlBool(False, "table", "column")
        self.assertEqual(
            '{"k": "pt", "p": "false", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
            eql_bool.to_db_format(),
        )

    def test_eql_bool_from_parsed_json_true(self):
        self.template_dict["p"] = "true"
        self.assertEqual(EqlBool.from_parsed_json(self.template_dict), True)

    def test_eql_bool_from_parsed_json_false(self):
        self.template_dict["p"] = "false"
        self.assertEqual(EqlBool.from_parsed_json(self.template_dict), False)

    def test_eql_date_to_db_format(self):
        eql_date = EqlDate(date(2024, 11, 1), "table", "column")
        self.assertEqual(
            '{"k": "pt", "p": "2024-11-01", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
            eql_date.to_db_format(),
        )

    def test_eql_date_from_parsed_json(self):
        self.template_dict["p"] = "2024-11-01"
        self.assertEqual(
            EqlDate.from_parsed_json(self.template_dict), date(2024, 11, 1)
        )

    def test_eql_float_to_db_format(self):
        eql_float = EqlFloat(1.1, "table", "column")
        self.assertEqual(
            '{"k": "pt", "p": "1.1", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
            eql_float.to_db_format(),
        )

    def test_eql_float_from_parsed_json(self):
        self.template_dict["p"] = "1.1"
        self.assertEqual(EqlFloat.from_parsed_json(self.template_dict), 1.1)

    def test_eql_text_to_db_format(self):
        eql_text = EqlText("text", "table", "column")
        self.assertEqual(
            '{"k": "pt", "p": "text", "i": {"t": "table", "c": "column"}, "v": 1, "q": null}',
            eql_text.to_db_format(),
        )

    def test_eql_text_from_parsed_json(self):
        self.template_dict["p"] = "text"
        self.assertEqual(EqlText.from_parsed_json(self.template_dict), "text")

    def test_eql_jsonb_prints_json_string(self):
        eql_jsonb = EqlJsonb({"a": 1}, "table", "column")
        self.assertEqual(eql_jsonb._value_in_db_format("ste_vec"), '{"a": 1}')

    def test_eql_jsonb_prints_value_for_ejson_path(self):
        eql_jsonb = EqlJsonb("$.a.b", "table", "column")
        self.assertEqual(eql_jsonb._value_in_db_format("ejson_path"), "$.a.b")

    def test_eql_jsonb_returns_value(self):
        self.assertEqual(EqlJsonb._value_from_db_format('{"a": 1}'), {"a": 1})

    def test_eql_row_makes_row(self):
        column_function_mapping = {
            "encrypted_int": EqlInt.from_parsed_json,
            "encrypted_boolean": EqlBool.from_parsed_json,
            "encrypted_date": EqlDate.from_parsed_json,
            "encrypted_float": EqlFloat.from_parsed_json,
            "encrypted_utf8_str": EqlText.from_parsed_json,
            "encrypted_jsonb": EqlText.from_parsed_json,
        }

        eql_row = EqlRow(
            column_function_mapping,
            {
                "encrypted_int": json.loads(
                    EqlInt(1, "table", "column").to_db_format()
                ),
                "encrypted_boolean": json.loads(
                    EqlBool(True, "table", "column").to_db_format()
                ),
                "encrypted_date": json.loads(
                    EqlDate(date(2024, 11, 1), "table", "column").to_db_format()
                ),
                "encrypted_float": json.loads(
                    EqlFloat(1.1, "table", "column").to_db_format()
                ),
                "encrypted_utf8_str": json.loads(
                    EqlText("text", "table", "column").to_db_format()
                ),
                "encrypted_jsonb": json.loads(
                    EqlJsonb('{"a": 1}', "table", "column").to_db_format()
                ),
            },
        )

        self.assertEqual(
            eql_row.row,
            {
                "encrypted_int": 1,
                "encrypted_boolean": True,
                "encrypted_date": date(2024, 11, 1),
                "encrypted_float": 1.1,
                "encrypted_utf8_str": "text",
                "encrypted_jsonb": '"{\\"a\\": 1}"',
            },
        )


if __name__ == "__main__":
    unittest.main()
