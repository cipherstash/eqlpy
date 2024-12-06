from sqlalchemy.orm import mapped_column, Mapped, sessionmaker
from sqlalchemy import create_engine, func, select, text
from eqlpy.eqlalchemy import *
from eqlpy.eql_types import (
    EqlInt,
    EqlBool,
    EqlDate,
    EqlFloat,
    EqlText,
    EqlJsonb,
    EqlRow,
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


def connect_to_db():
    engine = create_engine(
        "postgresql://postgres:postgres@localhost:6432/eqlpy_example"
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    BaseModel.metadata.create_all(engine)
    return session


def insert_example_record(session):
    print("\n\nInserting an example record...", end="")
    session.execute(text("DELETE FROM examples"))
    session.execute(text("SELECT cs_refresh_encrypt_config()"))

    example_data = Example(
        "hello, world",
        {"num": 1, "category": "a", "top": {"nested": ["a", "b", "c"]}},
        -51,
        -0.5,
        date(2024, 11, 19),
        False,
    )
    session.add(example_data)

    print("done\n")
    return example_data


def print_instructions():
    print(
        """
In another terminal window, you can check the data on CipherStash Proxy with (assuming you are using default setting):

  $ psql -h localhost -p 6432 -U postgres -x -c "select * from examples limit 1;" eqlpy_example

Also you can check what is really stored on PostgreSQL with:

  $ psql -h localhost -p 5432 -U postgres -x -c "select * from examples limit 1;" eqlpy_example

"""
    )


def query_example(session):
    print(
        "\nQuery example for partial Match of 'hello' in examples.encrypted_utf8_str:"
    )
    record = (
        session.query(Example)
        .filter(
            cs_match_v1(Example.encrypted_utf8_str).op("@>")(
                cs_match_v1(
                    EqlText("hello", "examples", "encrypted_utf8_str").to_db_format(
                        "match"
                    )
                )
            )
        )
        .one()
    )
    print()
    print(f"  Text inside the found record: {record.encrypted_utf8_str}")
    print()
    print(f"  Jsonb inside the found record: {record.encrypted_jsonb}")


def main():
    session = connect_to_db()

    ex = insert_example_record(session)
    session.commit()

    print_instructions()
    input("Press Enter to continue.")
    print()

    print("The record looks like this as an Example model instance:\n")
    print(f"  {ex}")
    print()
    input("Press Enter to continue.")
    print()

    query_example(session)

    print("\n=== End of examples ===\n")

    session.close()


if __name__ == "__main__":
    main()
