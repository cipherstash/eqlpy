import unittest
import os
import django
from django.conf import settings
from django.db import models, connection
from django.db.models import Q, F, Value, Count
from django.db.models.expressions import RawSQL
from eqlpy.eql_types import EqlFloat, EqlText, EqlJsonb
from eqlpy.eqldjango import *
from datetime import date


class TestSettings:
    pg_password = os.getenv("PGPASSWORD", "postgres")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = os.getenv("PGPORT", "6432")
    pg_db = os.getenv("PGDATABASE", "eqlpy_test")
    secret_key = os.getenv("SECRET_KEY", "test_secret_key")


if not settings.configured:
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=[
            "eqldjango_integration_test",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": f"{TestSettings.pg_db}",
                "USER": f"{TestSettings.pg_user}",
                "PASSWORD": f"{TestSettings.pg_password}",
                "HOST": f"{TestSettings.pg_host}",
                "PORT": f"{TestSettings.pg_port}",
            }
        },
        SECRET_KEY=f"{TestSettings.secret_key}",
        AUTOCOMMIT=False,
    )

django.setup()


class TestExampleDjangoModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        Example.objects.all().delete()
        self.example1 = Example(
            encrypted_int=1,
            encrypted_boolean=True,
            encrypted_utf8_str='string123',
            encrypted_date=date(2024, 1, 1),
            encrypted_float=1.1,
            encrypted_jsonb={"key": ["value"], "num": 1, "cat": "a"},
        )
        self.example1.save()

        self.example2 = Example(
            encrypted_int=-1,
            encrypted_boolean=False,
            encrypted_utf8_str='another_example',
            encrypted_date=date(2024, 1, 2),
            encrypted_float=2.1,
            encrypted_jsonb={"num": 2, "cat": "b"},
        )
        self.example2.save()

        self.example3 = Example(
            encrypted_int=0,
            encrypted_boolean=False,
            encrypted_utf8_str='yet_another',
            encrypted_date=date(2024, 1, 3),
            encrypted_float=5.0,
            encrypted_jsonb={"num": 3, "cat": "b"},
        )
        self.example3.save()

    def test_save_null_example(self):
        count = Example.objects.count()
        self.null_eaxmple = Example()
        self.null_eaxmple.save()
        self.assertEqual(count + 1, Example.objects.count())

    # Simple tests for storing and loading encrypted columns
    def test_encrypted_int(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_int, 1)

    def test_encrypted_boolean(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_boolean, True)

    def test_encrypted_date(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_date, date(2024, 1, 1))

    def test_encrypted_float(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_float, 1.1)

    def test_encrypted_utf8_str(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_utf8_str, 'string123')

    def test_encrypted_jsonb(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(
            found.encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_update_encrypted_columns(self):
        example = Example.objects.get(id=self.example1.id)
        example.encrypted_float = 99.9
        example.encrypted_utf8_str = "UPDATED_STRING"
        example.encrypted_jsonb = { "UPDATED_KEY": "UPDATED VALUE" }
        example.save()
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_float, 99.9)
        self.assertEqual(found.encrypted_utf8_str, "UPDATED_STRING")
        self.assertEqual(found.encrypted_jsonb, { "UPDATED_KEY": "UPDATED VALUE" })

    def test_string_partial_match_with_sql_clause(self):
        term = EqlText("string", "examples", "encrypted_utf8_str").to_db_format("match")
        result = Example.objects.raw(
            "SELECT * FROM examples WHERE cs_match_v1(encrypted_utf8_str) @> cs_match_v1(%s)",
            [term],
        )[0]
        self.assertEqual("string123", result.encrypted_utf8_str)

    def test_string_partial_match(self):
        term = EqlText("string", "examples", "encrypted_utf8_str").to_db_format("match")
        query = Q(CsContains(
            CsMatchV1(F('encrypted_utf8_str')),
            CsMatchV1(Value(term))
        ))
        result = Example.objects.filter(query)
        self.assertEqual(1, result.count())
        self.assertEqual("string123", result[0].encrypted_utf8_str)

    def test_string_exact_match_with_sql_clause(self):
        term = EqlText("string123", "examples", "encrypted_utf8_str").to_db_format("unique")
        result = Example.objects.raw(
            "SELECT * FROM examples WHERE cs_unique_v1(encrypted_utf8_str) = cs_unique_v1(%s)",
            [term],
        )[0]
        self.assertEqual("string123", result.encrypted_utf8_str)

    def test_string_exact_match(self):
        term = EqlText("string123", "examples", "encrypted_utf8_str").to_db_format("unique")
        query = Q(
            CsEquals(
                CsUniqueV1(F('encrypted_utf8_str')), CsUniqueV1(Value(term))
            )
        )
        found = Example.objects.get(query)
        self.assertEqual(found.encrypted_utf8_str, "string123")

    def test_float_ore_with_sql_clause(self):
        term = EqlFloat(2.0, "examples", "encrypted_float").to_db_format("ore")
        result = Example.objects.raw(
            "SELECT * FROM examples WHERE cs_ore_64_8_v1(encrypted_float) > cs_ore_64_8_v1(%s)",
            [term],
        )
        self.assertEqual(2.1, result[0].encrypted_float)
        self.assertEqual(5.0, result[1].encrypted_float)

    def test_float_ore(self):
        term = EqlFloat(2.0, "examples", "encrypted_float").to_db_format("ore")
        query = Q(
            CsGt(
                CsOre648V1(F('encrypted_float')), CsOre648V1(Value(term))
            )
        )
        result = Example.objects.filter(query).all()
        self.assertEqual(2.1, result[0].encrypted_float)
        self.assertEqual(5.0, result[1].encrypted_float)

    def test_jsonb_contains_with_sql_clause(self):
        term = EqlJsonb({"key": []}, "examples", "encrypted_jsonb").to_db_format("ste_vec")
        result = Example.objects.raw(
            "SELECT * FROM examples WHERE cs_ste_vec_v1(encrypted_jsonb) @> cs_ste_vec_v1(%s)",
            [term],
        )[0]
        self.assertEqual(
            {"key": ["value"], "num": 1, "cat": "a"}, result.encrypted_jsonb
        )

    def test_jsonb_contains(self):
        term = EqlJsonb({"key": []}, "examples", "encrypted_jsonb").to_db_format("ste_vec")
        query = Q(
            CsContains(
                CsSteVecV1(F('encrypted_jsonb')), CsSteVecV1(Value(term))
            )
        )
        found = Example.objects.get(query)
        self.assertEqual(
            {"key": ["value"], "num": 1, "cat": "a"}, found.encrypted_jsonb
        )

    def test_jsonb_contained_by_with_sql_clause(self):
        term = EqlJsonb({"key": ["value", "another value"], "num": 1, "cat": "a", "non-existent": "val"}, "examples", "encrypted_jsonb").to_db_format("ste_vec")
        result = Example.objects.raw(
            "SELECT * FROM examples WHERE cs_ste_vec_v1(encrypted_jsonb) <@ cs_ste_vec_v1(%s)",
            [term],
        )[0]
        self.assertEqual(
            {"key": ["value"], "num": 1, "cat": "a"}, result.encrypted_jsonb
        )

    def test_jsonb_contained_by(self):
        term = EqlJsonb({"key": ["value", "another value"], "num": 1, "cat": "a", "non-existent": "val"}, "examples", "encrypted_jsonb").to_db_format("ste_vec")
        query = Q(
            CsContainedBy(
                CsSteVecV1(F('encrypted_jsonb')), CsSteVecV1(Value(term))
            )
        )
        found = Example.objects.get(query)
        self.assertEqual(
            {"key": ["value"], "num": 1, "cat": "a"}, found.encrypted_jsonb
        )

    def test_jsonb_field_extraction_with_sql_clause(self):
        term = EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format("ejson_path")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cs_ste_vec_value_v1(encrypted_jsonb, %s) AS extracted_value FROM examples",
                [term],
            )
            results = cursor.fetchall()

        extracted = [EqlJsonb.from_parsed_json(json.loads(row[0])) for row in results]
        self.assertEqual(sorted(extracted), [1, 2, 3])

    def test_jsonb_field_extraction(self):
        term = EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format("ejson_path")
        results = Example.objects.annotate(
            extracted_value = CsSteVecValueV1(F("encrypted_jsonb"), Value(term))
        ).values_list('extracted_value', flat=True)

        extracted = [EqlJsonb.from_parsed_json(json.loads(result)) for result in list(results)]

    def test_jsonb_in_where_with_sql_clause(self):
        term1=EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format(
            "ejson_path"
        ),
        term2=EqlJsonb(2, "examples", "encrypted_jsonb").to_db_format(
            "ste_vec"
        ),
        result = Example.objects.raw(
            "SELECT * FROM examples WHERE cs_ste_vec_term_v1(encrypted_jsonb, %s) < cs_ste_vec_term_v1(%s)",
            [term1, term2],
        )[0]

        self.assertEqual(
            {"key": ["value"], "num": 1, "cat": "a"}, result.encrypted_jsonb
        )

    def test_jsonb_in_where(self):
        term1=EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format(
            "ejson_path"
        )
        term2=EqlJsonb(2, "examples", "encrypted_jsonb").to_db_format(
            "ste_vec"
        )
        query = Q(
            CsLt(
                CsSteVecTermV1(F('encrypted_jsonb'), Value(term1)),
                CsSteVecTermV1(Value(term2))
            )
        )
        found = Example.objects.get(query)
        self.assertEqual(
            {"key": ["value"], "num": 1, "cat": "a"}, found.encrypted_jsonb
        )


    def test_jsonb_field_in_order_by_with_sql_clause(self):
        term = EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format("ejson_path")
        results = Example.objects.raw(
            "SELECT * FROM examples ORDER BY cs_ste_vec_term_v1(encrypted_jsonb, %s) DESC",
            [term],
        )
        self.assertEqual(results[0].encrypted_jsonb, {"num": 3, "cat": "b"})
        self.assertEqual(results[1].encrypted_jsonb, {"num": 2, "cat": "b"})
        self.assertEqual(results[2].encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"})

    def test_jsonb_field_in_order_by(self):
        term = EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format("ejson_path")
        results = Example.objects.order_by(
            CsSteVecTermV1(F("encrypted_jsonb"), Value(term)).desc()
        )
        self.assertEqual(results[0].encrypted_jsonb, {"num": 3, "cat": "b"})
        self.assertEqual(results[1].encrypted_jsonb, {"num": 2, "cat": "b"})
        self.assertEqual(results[2].encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"})

    def test_jsonb_in_group_by_with_sql_clause(self):
        term = EqlJsonb("$.cat", "examples", "encrypted_jsonb").to_db_format("ejson_path")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cs_grouped_value_v1(cs_ste_vec_value_v1(encrypted_jsonb, %s)) AS category, COUNT(*) FROM examples GROUP BY cs_ste_vec_term_v1(encrypted_jsonb, %s)",
                [term, term],
            )
            results = cursor.fetchall()

        counts = [(EqlJsonb.from_parsed_json(json.loads(row[0])), row[1]) for row in results]
        self.assertEqual(sorted(counts)[0], ("a", 1))
        self.assertEqual(sorted(counts)[1], ("b", 2))

    def test_jsonb_in_group_by(self):
        term = EqlJsonb("$.cat", "examples", "encrypted_jsonb").to_db_format("ejson_path")
        results = Example.objects.values(cat=CsSteVecTermV1(F("encrypted_jsonb"), Value(term))).annotate(
            category=CsGroupedValueV1(CsSteVecValueV1(F("encrypted_jsonb"), Value(term))),
            count=Count('*')
        )

        result_list = list(results)
        self.assertEqual(EqlJsonb.from_parsed_json(json.loads(result_list[0]['category'])), "a")
        self.assertEqual(result_list[0]['count'], 1)
        self.assertEqual(EqlJsonb.from_parsed_json(json.loads(result_list[1]['category'])), "b")
        self.assertEqual(result_list[1]['count'], 2)


class Example(models.Model):
    encrypted_int = EncryptedInt(table="examples", column="encrypted_int", null=True)
    encrypted_boolean = EncryptedBoolean(
        table="examples", column="encrypted_boolean", null=True
    )
    encrypted_date = EncryptedDate(table="examples", column="encrypted_date", null=True)
    encrypted_float = EncryptedFloat(table="examples", column="encrypted_float", null=True)
    encrypted_utf8_str = EncryptedText(
        table="examples", column="encrypted_utf8_str", null=True
    )
    encrypted_jsonb = EncryptedJsonb(table="examples", column="encrypted_jsonb", null=True)

    class Meta:
        db_table = "examples"
