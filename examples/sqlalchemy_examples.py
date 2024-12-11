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


class Customer(BaseModel):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    age = mapped_column(EncryptedInt(__tablename__, "age"))
    is_citizen = mapped_column(EncryptedBoolean(__tablename__, "is_citizen"))
    start_date = mapped_column(EncryptedDate(__tablename__, "start_date"))
    weight = mapped_column(EncryptedFloat(__tablename__, "weight"))
    name = mapped_column(EncryptedUtf8Str(__tablename__, "name"))
    extra_info = mapped_column(EncryptedJsonb(__tablename__, "extra_info"))

    def __init__(
        self,
        e_utf8_str=None,
        e_jsonb=None,
        e_int=None,
        e_float=None,
        e_date=None,
        e_bool=None,
    ):
        self.name = e_utf8_str
        self.extra_info = e_jsonb
        self.age = e_int
        self.weight = e_float
        self.start_date = e_date
        self.is_citizen = e_bool

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


def connect_to_db():
    engine = create_engine(
        "postgresql://postgres:postgres@localhost:6432/eqlpy_example"
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    BaseModel.metadata.create_all(engine)
    return session


def insert_customer_record(session):
    print("\n\nInserting an customer record...", end="")
    session.execute(text("DELETE FROM customers"))
    session.execute(text("SELECT cs_refresh_encrypt_config()"))

    customer_data = Customer(
        "User Name",
        {"num": 1, "category": "a", "top": {"nested": ["a", "b", "c"]}},
        51,
        58.5,
        date(2024, 11, 19),
        False,
    )
    session.add(customer_data)

    print("done\n")
    return customer_data


def print_instructions():
    print(
        """
In another terminal window, you can check the data on CipherStash Proxy with (assuming you are using default setting):

  $ psql -h localhost -p 6432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example

Also you can check what is really stored on PostgreSQL with:

  $ psql -h localhost -p 5432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example

"""
    )


def query_customer(session):
    print("\nQuery customer for partial Match of 'hello' in customers.name:")
    record = (
        session.query(Customer)
        .filter(
            cs_match_v1(Customer.name).op("@>")(
                cs_match_v1(EqlText("user", "customers", "name").to_db_format("match"))
            )
        )
        .one()
    )
    print()
    print(f"  Text inside the found record: {record.name}")
    print()
    print(f"  Jsonb inside the found record: {record.extra_info}")


def main():
    session = connect_to_db()

    ex = insert_customer_record(session)
    session.commit()

    print_instructions()
    input("Press Enter to continue.")
    print()

    print("The record looks like this as an Customer model instance:\n")
    print(f"  {ex}")
    print()
    input("Press Enter to continue.")
    print()

    query_customer(session)

    print("\n=== End of customers ===\n")

    session.close()


if __name__ == "__main__":
    main()
