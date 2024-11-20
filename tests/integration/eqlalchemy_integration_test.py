import unittest
from sqlalchemy.orm import mapped_column, Mapped, sessionmaker
from sqlalchemy import create_engine, func
from datetime import date
from eqlpy.eql_types import EqlInt, EqlBool, EqlDate, EqlFloat, EqlText, EqlJsonb

from eqlpy.eqlalchemy import *


class TestExampleModel(unittest.TestCase):
    pg_password = os.getenv("PGPASSWORD", "postgres")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = os.getenv("PGPORT", "6432")
    pg_db = os.getenv("PGDATABASE", "cipherstash_getting_started")

    @classmethod
    def create_example_record(cls, id, utf8_str, jsonb, float_val, date_val, bool_val):
        ex = Example(
            e_int=id,
            e_utf8_str=utf8_str,
            e_jsonb=jsonb,
            e_float=float_val,
            e_date=date_val,
            e_bool=bool_val,
        )
        cls.session.add(ex)
        cls.session.commit()
        return ex

    @classmethod
    def setUpClass(self):
        print("in set up class")
        self.engine = create_engine(
            f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        BaseModel.metadata.create_all(self.engine)

        self.session.query(Example).delete()

        self.example1 = self.create_example_record(
            1,
            "string123",
            {"key": ["value"], "num": 1, "cat": "a"},
            1.1,
            date(2024, 1, 1),
            True,
        )
        self.create_example_record(
            -1, "another_example", {"num": 2, "cat": "b"}, 2.1, date(2024, 1, 2), False
        )
        self.create_example_record(
            0, "yet_another", {"num": 3, "cat": "b"}, 5.0, date(2024, 1, 3), False
        )

        self.session.commit()

    def tearDown(self):
        self.session.rollback()

    def test_encrypted_int(self):
        found = self.session.query(Example).filter(Example.id == self.example1.id).one()
        self.assertEqual(found.encrypted_int, 1)

    def test_encrypted_boolean(self):
        found = self.session.query(Example).filter(Example.id == self.example1.id).one()
        self.assertEqual(found.encrypted_boolean, True)

    def test_encrypted_date(self):
        found = self.session.query(Example).filter(Example.id == self.example1.id).one()
        self.assertEqual(found.encrypted_date, date(2024, 1, 1))

    def test_encrypted_float(self):
        found = self.session.query(Example).filter(Example.id == self.example1.id).one()
        self.assertEqual(found.encrypted_float, 1.1)

    def test_encrypted_utf8_str(self):
        found = self.session.query(Example).filter(Example.id == self.example1.id).one()
        self.assertEqual(found.encrypted_utf8_str, "string123")

    def test_encrypted_jsonb(self):
        found = self.session.query(Example).filter(Example.id == self.example1.id).one()
        self.assertEqual(
            found.encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_example_prints_value(self):
        self.example1.id = 1
        self.assertEqual(
            str(self.example1),
            "<Example(id=1, encrypted_utf8_str=string123, encrypted_jsonb={'cat': 'a', 'key': ['value'], 'num': 1}, encrypted_int=1, encrypted_float=1.1, encrypted_date=2024-01-01, encrypted_boolean=True)>",
        )

    def test_string_partial_match(self):
        found = (
            self.session.query(Example)
            .filter(
                cs_match_v1(Example.encrypted_utf8_str).op("@>")(
                    cs_match_v1(
                        EqlText(
                            "string", "examples", "encrypted_utf8_str"
                        ).to_db_format()
                    )
                )
            )
            .one()
        )
        self.assertEqual(found.encrypted_utf8_str, "string123")

    def test_string_exact_match(self):
        found = (
            self.session.query(Example)
            .filter(
                cs_unique_v1(Example.encrypted_utf8_str)
                == cs_unique_v1(
                    EqlText(
                        "string123", "examples", "encrypted_utf8_str"
                    ).to_db_format()
                )
            )
            .one()
        )
        self.assertEqual(found.encrypted_utf8_str, "string123")

    def test_float_ore(self):
        found = (
            self.session.query(Example)
            .filter(
                cs_ore_64_8_v1(Example.encrypted_float)
                < cs_ore_64_8_v1(
                    EqlFloat(1.5, "examples", "encrypted_float").to_db_format()
                )
            )
            .one()
        )
        self.assertEqual(found.encrypted_float, 1.1)

    def test_jsonb_containment_1(self):
        found = (
            self.session.query(Example)
            .filter(
                cs_ste_vec_v1(Example.encrypted_jsonb).op("@>")(
                    cs_ste_vec_v1(
                        EqlJsonb(
                            {"key": []}, "examples", "encrypted_jsonb"
                        ).to_db_format("ste_vec")
                    )
                )
            )
            .one()
        )
        self.assertEqual(
            found.encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_containment_2(self):
        found = (
            self.session.query(Example)
            .filter(
                cs_ste_vec_v1(Example.encrypted_jsonb).op("<@")(
                    cs_ste_vec_v1(
                        EqlJsonb(
                            {
                                "key": ["value", "another value"],
                                "num": 1,
                                "cat": "a",
                                "non-existent": "val",
                            },
                            "examples",
                            "encrypted_jsonb",
                        ).to_db_format("ste_vec")
                    )
                )
            )
            .one()
        )
        self.assertEqual(
            found.encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_extraction(self):
        found = self.session.query(
            cs_ste_vec_value_v1(
                Example.encrypted_jsonb,
                EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format(
                    "ejson_path"
                ),
            ).label("extracted_value")
        ).all()  # ._asdict()['extracted_value']
        extracted = list(
            map(
                lambda x: EqlJsonb.from_parsed_json(x._asdict()["extracted_value"]),
                found,
            )
        )
        self.assertEqual(sorted(extracted), [1, 2, 3])

    def test_jsonb_field_in_where(self):
        found = (
            self.session.query(Example)
            .filter(
                cs_ste_vec_term_v1(
                    Example.encrypted_jsonb,
                    EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format(
                        "ejson_path"
                    ),
                )
                < (
                    cs_ste_vec_term_v1(
                        EqlJsonb(2, "examples", "encrypted_jsonb").to_db_format(
                            "ste_vec"
                        )
                    )
                )
            )
            .one()
        )
        self.assertEqual(
            found.encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )

    def test_jsonb_field_in_order_by(self):
        found = (
            self.session.query(Example)
            .order_by(
                cs_ste_vec_term_v1(
                    Example.encrypted_jsonb,
                    EqlJsonb("$.num", "examples", "encrypted_jsonb").to_db_format(
                        "ejson_path"
                    ),
                )
            )
            .all()
        )
        self.assertEqual(
            found[0].encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )
        self.assertEqual(found[1].encrypted_jsonb, {"num": 2, "cat": "b"})
        self.assertEqual(found[2].encrypted_jsonb, {"num": 3, "cat": "b"})

    def test_jsonb_field_in_group_by(self):
        found = (
            self.session.query(
                cs_grouped_value_v1(
                    cs_ste_vec_value_v1(
                        Example.encrypted_jsonb,
                        EqlJsonb("$.cat", "examples", "encrypted_jsonb").to_db_format(
                            "ejson_path"
                        ),
                    )
                ),
                func.count().label("count"),
            )
            .group_by(
                cs_ste_vec_term_v1(
                    Example.encrypted_jsonb,
                    EqlJsonb("$.cat", "examples", "encrypted_jsonb").to_db_format(
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


class Example(BaseModel):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(primary_key=True)
    encrypted_int = mapped_column(EncryptedInt(__tablename__, "encrypted_int"))
    encrypted_boolean = mapped_column(
        EncryptedBoolean(__tablename__, "encrypted_boolean")
    )
    encrypted_date = mapped_column(EncryptedDate(__tablename__, "encrypted_date"))
    encrypted_float = mapped_column(EncryptedFloat(__tablename__, "encrypted_float"))
    encrypted_utf8_str = mapped_column(
        EncryptedUtf8Str(__tablename__, "encrypted_utf8_str")
    )
    encrypted_jsonb = mapped_column(EncryptedJsonb(__tablename__, "encrypted_jsonb"))

    def __init__(
        self,
        e_utf8_str=None,
        e_jsonb=None,
        e_int=None,
        e_float=None,
        e_date=None,
        e_bool=None,
    ):
        self.encrypted_utf8_str = e_utf8_str
        self.encrypted_jsonb = e_jsonb
        self.encrypted_int = e_int
        self.encrypted_float = e_float
        self.encrypted_date = e_date
        self.encrypted_boolean = e_bool

    def __repr__(self):
        return (
            "<Example("
            f"id={self.id}, "
            f"encrypted_utf8_str={self.encrypted_utf8_str}, "
            f"encrypted_jsonb={self.encrypted_jsonb}, "
            f"encrypted_int={self.encrypted_int}, "
            f"encrypted_float={self.encrypted_float}, "
            f"encrypted_date={self.encrypted_date}, "
            f"encrypted_boolean={self.encrypted_boolean}"
            ")>"
        )


if __name__ == "__main__":
    unittest.main()
