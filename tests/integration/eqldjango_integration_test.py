import unittest
import os
import django
from django.conf import settings
from django.db import models, connection
from django.db.models import Q, F, Value, Count, IntegerField
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


def create_customer_records():
    customer1 = Customer(
        age=31,
        is_citizen=True,
        name="Alice Developer",
        start_date=date(2024, 1, 1),
        weight=51.1,
        extra_info={"key": ["value"], "num": 1, "cat": "a"},
        visit_count=0,
    )
    customer1.save()

    customer2 = Customer(
        age=29,
        is_citizen=False,
        name="Bob Customer",
        start_date=date(2024, 1, 2),
        weight=82.1,
        extra_info={"num": 2, "cat": "b"},
        visit_count=1,
    )
    customer2.save()

    customer3 = Customer(
        age=30,
        is_citizen=False,
        name="Carol Customer",
        start_date=date(2024, 1, 3),
        weight=55.0,
        extra_info={"num": 3, "cat": "b"},
        visit_count=2,
    )
    customer3.save()

    return [customer1, customer2, customer3]


class TestCustomerDjangoModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        Customer.objects.all().delete()
        self.customer1, self.customer2, self.customer3 = create_customer_records()

    def test_save_null_customer(self):
        count = Customer.objects.count()
        self.null_eaxmple = Customer()
        self.null_eaxmple.save()
        self.assertEqual(count + 1, Customer.objects.count())

    # Simple tests for storing and loading encrypted columns
    def test_age(self):
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.age, 31)

    def test_is_citizen(self):
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.is_citizen, True)

    def test_start_date(self):
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.start_date, date(2024, 1, 1))

    def test_weight(self):
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.weight, 51.1)

    def test_name(self):
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.name, "Alice Developer")

    def test_extra_info(self):
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.extra_info, {"key": ["value"], "num": 1, "cat": "a"})

    def test_update_encrypted_columns(self):
        customer = Customer.objects.get(id=self.customer1.id)
        customer.weight = 99.9
        customer.name = "UPDATED_STRING"
        customer.extra_info = {"UPDATED_KEY": "UPDATED VALUE"}
        customer.save()
        found = Customer.objects.get(id=self.customer1.id)
        self.assertEqual(found.weight, 99.9)
        self.assertEqual(found.name, "UPDATED_STRING")
        self.assertEqual(found.extra_info, {"UPDATED_KEY": "UPDATED VALUE"})

    def test_string_partial_match_with_sql_clause(self):
        term = EqlText("ali", "customers", "name").to_db_format("match")
        result = Customer.objects.raw(
            "SELECT * FROM customers WHERE cs_match_v1(name) @> cs_match_v1(%s)",
            [term],
        )[0]
        self.assertEqual("Alice Developer", result.name)

    def test_string_partial_match(self):
        term = EqlText("ali", "customers", "name").to_db_format("match")
        query = Q(CsContains(CsMatchV1(F("name")), CsMatchV1(Value(term))))
        result = Customer.objects.filter(query)
        self.assertEqual(1, result.count())
        self.assertEqual("Alice Developer", result[0].name)

    def test_string_exact_match_with_sql_clause(self):
        term = EqlText("Alice Developer", "customers", "name").to_db_format("unique")
        result = Customer.objects.raw(
            "SELECT * FROM customers WHERE cs_unique_v1(name) = cs_unique_v1(%s)",
            [term],
        )[0]
        self.assertEqual("Alice Developer", result.name)

    def test_string_exact_match(self):
        term = EqlText("Alice Developer", "customers", "name").to_db_format("unique")
        query = Q(CsEquals(CsUniqueV1(F("name")), CsUniqueV1(Value(term))))
        found = Customer.objects.get(query)
        self.assertEqual(found.name, "Alice Developer")

    def test_float_ore_with_sql_clause(self):
        term = EqlFloat(80.0, "customers", "weight").to_db_format("ore")
        result = Customer.objects.raw(
            "SELECT * FROM customers WHERE cs_ore_64_8_v1(weight) < cs_ore_64_8_v1(%s)",
            [term],
        )
        self.assertEqual(51.1, result[0].weight)
        self.assertEqual(55.0, result[1].weight)

    def test_float_ore(self):
        term = EqlFloat(80.0, "customers", "weight").to_db_format("ore")
        query = Q(CsLt(CsOre648V1(F("weight")), CsOre648V1(Value(term))))
        result = Customer.objects.filter(query).all()
        self.assertEqual(51.1, result[0].weight)
        self.assertEqual(55.0, result[1].weight)

    def test_jsonb_contains_with_sql_clause(self):
        term = EqlJsonb({"key": []}, "customers", "extra_info").to_db_format("ste_vec")
        result = Customer.objects.raw(
            "SELECT * FROM customers WHERE cs_ste_vec_v1(extra_info) @> cs_ste_vec_v1(%s)",
            [term],
        )[0]
        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, result.extra_info)

    def test_jsonb_contains(self):
        term = EqlJsonb({"key": []}, "customers", "extra_info").to_db_format("ste_vec")
        query = Q(CsContains(CsSteVecV1(F("extra_info")), CsSteVecV1(Value(term))))
        found = Customer.objects.get(query)
        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, found.extra_info)

    def test_jsonb_contained_by_with_sql_clause(self):
        term = EqlJsonb(
            {
                "key": ["value", "another value"],
                "num": 1,
                "cat": "a",
                "non-existent": "val",
            },
            "customers",
            "extra_info",
        ).to_db_format("ste_vec")
        result = Customer.objects.raw(
            "SELECT * FROM customers WHERE cs_ste_vec_v1(extra_info) <@ cs_ste_vec_v1(%s)",
            [term],
        )[0]
        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, result.extra_info)

    def test_jsonb_contained_by(self):
        term = EqlJsonb(
            {
                "key": ["value", "another value"],
                "num": 1,
                "cat": "a",
                "non-existent": "val",
            },
            "customers",
            "extra_info",
        ).to_db_format("ste_vec")
        query = Q(CsContainedBy(CsSteVecV1(F("extra_info")), CsSteVecV1(Value(term))))
        found = Customer.objects.get(query)
        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, found.extra_info)

    def test_jsonb_field_extraction_with_sql_clause(self):
        term = EqlJsonb("$.num", "customers", "extra_info").to_db_format("ejson_path")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cs_ste_vec_value_v1(extra_info, %s) AS extracted_value FROM customers",
                [term],
            )
            results = cursor.fetchall()

        extracted = [EqlJsonb.from_parsed_json(json.loads(row[0])) for row in results]
        self.assertEqual(sorted(extracted), [1, 2, 3])

    def test_jsonb_field_extraction(self):
        term = EqlJsonb("$.num", "customers", "extra_info").to_db_format("ejson_path")
        results = Customer.objects.annotate(
            extracted_value=CsSteVecValueV1(F("extra_info"), Value(term))
        ).values_list("extracted_value", flat=True)

        extracted = [EqlJsonb.from_parsed_json(result) for result in list(results)]

    def test_jsonb_in_where_with_sql_clause(self):
        term1 = (
            EqlJsonb("$.num", "customers", "extra_info").to_db_format("ejson_path"),
        )
        term2 = (EqlJsonb(2, "customers", "extra_info").to_db_format("ste_vec"),)
        result = Customer.objects.raw(
            "SELECT * FROM customers WHERE cs_ste_vec_term_v1(extra_info, %s) < cs_ste_vec_term_v1(%s)",
            [term1, term2],
        )[0]

        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, result.extra_info)

    def test_jsonb_in_where(self):
        term1 = EqlJsonb("$.num", "customers", "extra_info").to_db_format("ejson_path")
        term2 = EqlJsonb(2, "customers", "extra_info").to_db_format("ste_vec")
        query = Q(
            CsLt(
                CsSteVecTermV1(F("extra_info"), Value(term1)),
                CsSteVecTermV1(Value(term2)),
            )
        )
        found = Customer.objects.get(query)
        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, found.extra_info)

    def test_jsonb_field_in_order_by_with_sql_clause(self):
        term = EqlJsonb("$.num", "customers", "extra_info").to_db_format("ejson_path")
        results = Customer.objects.raw(
            "SELECT * FROM customers ORDER BY cs_ste_vec_term_v1(extra_info, %s) DESC",
            [term],
        )
        self.assertEqual(results[0].extra_info, {"num": 3, "cat": "b"})
        self.assertEqual(results[1].extra_info, {"num": 2, "cat": "b"})
        self.assertEqual(
            results[2].extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_in_order_by(self):
        term = EqlJsonb("$.num", "customers", "extra_info").to_db_format("ejson_path")
        results = Customer.objects.order_by(
            CsSteVecTermV1(F("extra_info"), Value(term)).desc()
        )
        self.assertEqual(results[0].extra_info, {"num": 3, "cat": "b"})
        self.assertEqual(results[1].extra_info, {"num": 2, "cat": "b"})
        self.assertEqual(
            results[2].extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_in_group_by_with_sql_clause(self):
        term = EqlJsonb("$.cat", "customers", "extra_info").to_db_format("ejson_path")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cs_grouped_value_v1(cs_ste_vec_value_v1(extra_info, %s)) AS category, COUNT(*) FROM customers GROUP BY cs_ste_vec_term_v1(extra_info, %s)",
                [term, term],
            )
            results = cursor.fetchall()

        counts = [
            (EqlJsonb.from_parsed_json(json.loads(row[0])), row[1]) for row in results
        ]
        self.assertEqual(sorted(counts)[0], ("a", 1))
        self.assertEqual(sorted(counts)[1], ("b", 2))

    def test_jsonb_in_group_by(self):
        term = EqlJsonb("$.cat", "customers", "extra_info").to_db_format("ejson_path")
        results = Customer.objects.values(
            cat=CsSteVecTermV1(F("extra_info"), Value(term))
        ).annotate(
            category=CsGroupedValueV1(CsSteVecValueV1(F("extra_info"), Value(term))),
            count=Count("*"),
        )

        result_list = list(results)
        self.assertEqual(EqlJsonb.from_parsed_json(result_list[0]["category"]), "a")
        self.assertEqual(result_list[0]["count"], 1)
        self.assertEqual(EqlJsonb.from_parsed_json(result_list[1]["category"]), "b")
        self.assertEqual(result_list[1]["count"], 2)


class Customer(models.Model):
    age = EncryptedInt(table="customers", column="age", null=True)
    is_citizen = EncryptedBoolean(table="customers", column="is_citizen", null=True)
    start_date = EncryptedDate(table="customers", column="start_date", null=True)
    weight = EncryptedFloat(table="customers", column="weight", null=True)
    name = EncryptedText(table="customers", column="name", null=True)
    extra_info = EncryptedJsonb(table="customers", column="extra_info", null=True)
    visit_count = IntegerField()

    class Meta:
        db_table = "customers"


class TestModelWithCustomLookup(unittest.TestCase):
    def setUp(self):
        Customer.objects.all().delete()
        self.customer1, self.customer2, self.customer3 = create_customer_records()
        self.eqb = EncryptedQueryBuilder("customers")

    def test_string_equals(self):
        found = Customer.objects.get(self.eqb(name="Alice Developer"))
        self.assertEqual(found.name, "Alice Developer")

    def test_string_contains(self):
        found = Customer.objects.get(self.eqb(name__s_contains="caro"))
        self.assertEqual(found.name, "Carol Customer")

    def test_json_contains(self):
        found = Customer.objects.get(self.eqb(extra_info__j_contains={"key": []}))
        self.assertEqual({"key": ["value"], "num": 1, "cat": "a"}, found.extra_info)

    def test_greater_than(self):
        found = Customer.objects.get(self.eqb(weight__gt=73.0))
        self.assertEqual(found.weight, 82.1)

    def test_less_than_and_json_contains(self):
        found = Customer.objects.get(
            self.eqb(weight__lt=73.0, extra_info__j_contains={"cat": "b"})
        )
        self.assertEqual(found.weight, 55.0)

    def test_text_contains_with_float_lt(self):
        found = Customer.objects.get(name__contains="Customer", weight__lt=80.0)
        self.assertEqual(found.weight, 55.0)

    def test_plaintext_lt_with_float_lt(self):
        found = Customer.objects.get(visit_count__lte=1, weight__lt=60.0)
        self.assertEqual(found.weight, 51.1)

    def test_text_exact_match(self):
        found = Customer.objects.get(name__eq="Alice Developer")
        self.assertEqual(found.name, "Alice Developer")

    def test_text_partial_match(self):
        found = Customer.objects.get(name__contains="caro")
        self.assertEqual(found.name, "Carol Customer")

    def test_float_ore_lt(self):
        found = Customer.objects.get(weight__lt=53.0)
        self.assertEqual(found.weight, 51.1)

    def test_float_ore_gt(self):
        found = Customer.objects.get(weight__gt=80.0)
        self.assertEqual(found.weight, 82.1)

    def test_int_ore_lt(self):
        found = Customer.objects.get(age__lt=30)
        self.assertEqual(found.age, 29)

    def test_int_ore_gt(self):
        found = Customer.objects.get(age__gt=30)
        self.assertEqual(found.age, 31)
