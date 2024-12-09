import unittest
from sqlalchemy.orm import mapped_column, Mapped, sessionmaker
from sqlalchemy import create_engine, func, select, text
from datetime import date
import os
from eqlpy.eql_types import EqlFloat, EqlText, EqlJsonb
from eqlpy.eqlalchemy import *


class TestCustomerModel(unittest.TestCase):
    pg_password = os.getenv("PGPASSWORD", "postgres")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = os.getenv("PGPORT", "6432")
    pg_db = os.getenv("PGDATABASE", "eqlpy_test")

    @classmethod
    def create_customer_record(cls, id, utf8_str, jsonb, float_val, date_val, bool_val):
        ex = Customer(
            e_age=id,
            e_name=utf8_str,
            e_extra_info=jsonb,
            e_weight=float_val,
            e_start_date=date_val,
            e_is_citizen=bool_val,
        )
        cls.session.add(ex)
        cls.session.commit()
        return ex

    @classmethod
    def setUpClass(self):
        self.engine = create_engine(
            f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        BaseModel.metadata.create_all(self.engine)

        self.session.query(Customer).delete()
        self.session.execute(text("SELECT cs_refresh_encrypt_config()"))

        self.customer1 = self.create_customer_record(
            31,
            "Alice Developer",
            {"key": ["value"], "num": 1, "cat": "a"},
            51.1,
            date(2024, 1, 1),
            True,
        )
        self.create_customer_record(
            29,
            '"Bob Customer"',
            {"num": 2, "cat": "b"},
            82.1,
            date(2024, 1, 2),
            False,
        )
        self.create_customer_record(
            30, "Carol Customer", {"num": 3, "cat": "b"}, 55.0, date(2024, 1, 3), False
        )

        self.session.commit()

    def tearDown(self):
        self.session.rollback()

    # Simple tests for storing and loading encrypted columns
    def test_age(self):
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(found.age, 31)

    def test_is_citizen(self):
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(found.is_citizen, True)

    def test_start_date(self):
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(found.start_date, date(2024, 1, 1))

    def test_weight(self):
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(found.weight, 51.1)

    def test_name(self):
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(found.name, "Alice Developer")

    def test_extra_info(self):
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    # Simple update test for encrypted columns
    def test_update_encrypted_columns(self):
        customer = (
            self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        )
        customer.weight = 99.9
        customer.name = "UPDATED_STRING"
        customer.extra_info = {"key1": "value1", "key2": "value2"}
        found = self.session.query(Customer).filter(Customer.id == self.customer1.id).one()
        self.assertEqual(found.weight, 99.9)
        self.assertEqual(found.name, "UPDATED_STRING")
        self.assertEqual(found.extra_info, {"key1": "value1", "key2": "value2"})

    # Queries by encrypted columns
    def test_string_partial_match_with_sql_clause(self):
        query = (
            select(Customer)
            .where(text("cs_match_v1(name) @> cs_match_v1(:term)"))
            .params(
                term=EqlText("ali", "customers", "name").to_db_format(
                    "match"
                )
            )
        )
        found = self.session.execute(query).scalar()
        self.assertEqual("Alice Developer", found.name)

    def test_string_partial_match(self):
        found = (
            self.session.query(Customer)
            .filter(
                cs_match_v1(Customer.name).op("@>")(
                    cs_match_v1(
                        EqlText(
                            "ali", "customers", "name"
                        ).to_db_format()
                    )
                )
            )
            .one()
        )
        self.assertEqual("Alice Developer", found.name)

    def test_string_exact_match_with_sql_clause(self):
        query = (
            select(Customer)
            .where(text("cs_unique_v1(name) == cs_unique_v1(:term)"))
            .params(
                term=EqlText(
                    "Alice Developer", "customers", "name"
                ).to_db_format("unique")
            )
        )
        found = self.session.execute(query).scalar()
        self.assertEqual("Alice Developer", found.name)

    def test_string_exact_match(self):
        found = (
            self.session.query(Customer)
            .filter(
                cs_unique_v1(Customer.name)
                == cs_unique_v1(
                    EqlText(
                        "Alice Developer", "customers", "name"
                    ).to_db_format()
                )
            )
            .one()
        )
        self.assertEqual(found.name, "Alice Developer")

    def test_float_ore_with_sql_clause(self):
        query = (
            select(Customer)
            .where(text("cs_ore_64_8_v1(weight) > cs_ore_64_8_v1(:term)"))
            .params(
                term=EqlFloat(80.0, "customers", "weight").to_db_format("ore")
            )
        )
        found = self.session.execute(query).scalar()
        self.assertEqual(82.1, found.weight)
        self.assertEqual('"Bob Customer"', found.name)

    def test_float_ore(self):
        found = (
            self.session.query(Customer)
            .filter(
                cs_ore_64_8_v1(Customer.weight)
                < cs_ore_64_8_v1(
                    EqlFloat(51.5, "customers", "weight").to_db_format()
                )
            )
            .one()
        )
        self.assertEqual(found.weight, 51.1)

    # JSONB Qqueries
    def test_jsonb_containment_1_with_sql_clause(self):
        query = (
            select(Customer)
            .where(text("cs_ste_vec_v1(extra_info) @> cs_ste_vec_v1(:term)"))
            .params(
                term=EqlJsonb({"key": []}, "customers", "extra_info").to_db_format(
                    "ste_vec"
                )
            )
        )
        found = self.session.execute(query).scalar()
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_containment_1(self):
        found = (
            self.session.query(Customer)
            .filter(
                cs_ste_vec_v1(Customer.extra_info).op("@>")(
                    cs_ste_vec_v1(
                        EqlJsonb(
                            {"key": []}, "customers", "extra_info"
                        ).to_db_format("ste_vec")
                    )
                )
            )
            .one()
        )
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_containment_2_with_sql_clause(self):
        query = (
            select(Customer)
            .where(text("cs_ste_vec_v1(extra_info) <@ cs_ste_vec_v1(:term)"))
            .params(
                term=EqlJsonb(
                    {
                        "key": ["value", "another value"],
                        "num": 1,
                        "cat": "a",
                        "non-existent": "val",
                    },
                    "customers",
                    "extra_info",
                ).to_db_format("ste_vec")
            )
        )
        found = self.session.execute(query).scalar()
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_containment_2(self):
        found = (
            self.session.query(Customer)
            .filter(
                cs_ste_vec_v1(Customer.extra_info).op("<@")(
                    cs_ste_vec_v1(
                        EqlJsonb(
                            {
                                "key": ["value", "another value"],
                                "num": 1,
                                "cat": "a",
                                "non-existent": "val",
                            },
                            "customers",
                            "extra_info",
                        ).to_db_format("ste_vec")
                    )
                )
            )
            .one()
        )
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_extraction_with_sql_clause(self):
        query = (
            select(
                text("cs_ste_vec_value_v1(extra_info, :term) AS extracted_value")
            )
            .select_from(Customer)
            .params(
                term=EqlJsonb("$.num", "customers", "extra_info").to_db_format(
                    "ejson_path"
                ),
            )
        )
        found = self.session.execute(query).all()
        extracted = [EqlJsonb.from_parsed_json(row[0]) for row in found]
        self.assertEqual(sorted(extracted), [1, 2, 3])

    def test_jsonb_field_extraction(self):
        found = self.session.query(
            cs_ste_vec_value_v1(
                Customer.extra_info,
                EqlJsonb("$.num", "customers", "extra_info").to_db_format(
                    "ejson_path"
                ),
            ).label("extracted_value")
        ).all()
        extracted = list(
            map(
                lambda x: EqlJsonb.from_parsed_json(x._asdict()["extracted_value"]),
                found,
            )
        )
        self.assertEqual(sorted(extracted), [1, 2, 3])

    def test_jsonb_field_in_where_with_sql_clause(self):
        query = (
            select(Customer)
            .where(
                text(
                    "cs_ste_vec_term_v1(extra_info, :term1) < cs_ste_vec_term_v1(:term2)"
                )
            )
            .params(
                term1=EqlJsonb("$.num", "customers", "extra_info").to_db_format(
                    "ejson_path"
                ),
                term2=EqlJsonb(2, "customers", "extra_info").to_db_format(
                    "ste_vec"
                ),
            )
        )
        found = self.session.execute(query).scalar()
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_in_where(self):
        found = (
            self.session.query(Customer)
            .filter(
                cs_ste_vec_term_v1(
                    Customer.extra_info,
                    EqlJsonb("$.num", "customers", "extra_info").to_db_format(
                        "ejson_path"
                    ),
                )
                < (
                    cs_ste_vec_term_v1(
                        EqlJsonb(2, "customers", "extra_info").to_db_format(
                            "ste_vec"
                        )
                    )
                )
            )
            .one()
        )
        self.assertEqual(
            found.extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_in_order_by_with_sql_clause(self):
        query = (
            select(Customer)
            .order_by(text("cs_ste_vec_term_v1(extra_info, :term) DESC"))
            .params(
                term=EqlJsonb("$.num", "customers", "extra_info").to_db_format(
                    "ejson_path"
                )
            )
        )
        found = self.session.execute(query).all()
        self.assertEqual(found[0][0].extra_info, {"num": 3, "cat": "b"})
        self.assertEqual(found[1][0].extra_info, {"num": 2, "cat": "b"})
        self.assertEqual(
            found[2][0].extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_in_order_by(self):
        found = (
            self.session.query(Customer)
            .order_by(
                cs_ste_vec_term_v1(
                    Customer.extra_info,
                    EqlJsonb("$.num", "customers", "extra_info").to_db_format(
                        "ejson_path"
                    ),
                ).desc()
            )
            .all()
        )
        self.assertEqual(found[0].extra_info, {"num": 3, "cat": "b"})
        self.assertEqual(found[1].extra_info, {"num": 2, "cat": "b"})
        self.assertEqual(
            found[2].extra_info, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_in_group_by_with_sql_clause(self):
        query = (
            select(
                text(
                    "cs_grouped_value_v1(cs_ste_vec_value_v1(extra_info, :term)) AS category"
                ),
                text("COUNT(*)"),
            )
            .select_from(Customer)
            .group_by(text("cs_ste_vec_term_v1(extra_info, :term)"))
            .params(
                term=EqlJsonb("$.cat", "customers", "extra_info").to_db_format(
                    "ejson_path"
                )
            )
        )
        found = self.session.execute(query).all()
        self.assertEqual(
            ("a", 1), (EqlJsonb.from_parsed_json(found[0][0]), found[0][1])
        )
        self.assertEqual(
            ("b", 2), (EqlJsonb.from_parsed_json(found[1][0]), found[1][1])
        )

    def test_jsonb_field_in_group_by(self):
        found = (
            self.session.query(
                cs_grouped_value_v1(
                    cs_ste_vec_value_v1(
                        Customer.extra_info,
                        EqlJsonb("$.cat", "customers", "extra_info").to_db_format(
                            "ejson_path"
                        ),
                    )
                ),
                func.count().label("count"),
            )
            .group_by(
                cs_ste_vec_term_v1(
                    Customer.extra_info,
                    EqlJsonb("$.cat", "customers", "extra_info").to_db_format(
                        "ejson_path"
                    ),
                )
            )
            .all()
        )
        # return value is a list of tuples of encrypted jsonb for category, and count
        self.assertEqual(
            ("a", 1), (EqlJsonb.from_parsed_json(found[0][0]), found[0][1])
        )
        self.assertEqual(
            ("b", 2), (EqlJsonb.from_parsed_json(found[1][0]), found[1][1])
        )


class Customer(BaseModel):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    age = mapped_column(EncryptedInt(__tablename__, "age"))
    is_citizen = mapped_column(
        EncryptedBoolean(__tablename__, "is_citizen")
    )
    start_date = mapped_column(EncryptedDate(__tablename__, "start_date"))
    weight = mapped_column(EncryptedFloat(__tablename__, "weight"))
    name = mapped_column(
        EncryptedUtf8Str(__tablename__, "name")
    )
    extra_info = mapped_column(EncryptedJsonb(__tablename__, "extra_info"))

    def __init__(
        self,
        e_name=None,
        e_extra_info=None,
        e_age=None,
        e_weight=None,
        e_start_date=None,
        e_is_citizen=None,
    ):
        self.name = e_name
        self.extra_info = e_extra_info
        self.age = e_age
        self.weight = e_weight
        self.start_date = e_start_date
        self.is_citizen = e_is_citizen

    def __repr__(self):
        return (
            "<Customer("
            f"id={self.id}, "
            f"name={self.name}, "
            f"extra_info={self.extra_info}, "
            f"age={self.age}, "
            f"weight={self.weight}, "
            f"start_date={self.start_date}, "
            f"is_citizen={self.is_citizen}"
            ")>"
        )
