import psycopg
import pprint
from datetime import datetime
from eqlpy.eql_types import (
    EqlInt,
    EqlBool,
    EqlDate,
    EqlFloat,
    EqlText,
    EqlJsonb,
    EqlRow,
)


def connect_to_db():
    db_string = (
        "host=localhost dbname=eqlpy_example user=postgres password=postgres port=6432"
    )
    conn = psycopg.connect(db_string)
    return conn, conn.cursor(row_factory=psycopg.rows.dict_row)


def insert_customer_record(cur):
    print("\n\nInserting an customer record...", end="")
    cur.execute("DELETE FROM customers")
    cur.execute("SELECT cs_refresh_encrypt_config()")

    customer_data = {
        "age": EqlInt(51, "customers", "age"),
        "is_citizen": EqlBool(False, "customers", "is_citizen"),
        "start_date": EqlDate(datetime.now().date(), "customers", "start_date"),
        "weight": EqlFloat(58.5, "customers", "weight"),
        "name": EqlText(":Some User", "customers", "name"),
        "extra_info": EqlJsonb(
            {"num": 1, "category": "a", "top": {"nested": ["a", "b", "c"]}},
            "customers",
            "extra_info",
        ),
    }

    insert_query = """
    INSERT INTO customers (age, is_citizen, start_date, weight, name, extra_info)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(
        insert_query, tuple(field.to_db_format() for field in customer_data.values())
    )
    print("done\n")


def print_instructions():
    print(
        """
In another terminal window, you can check the data on CipherStash Proxy with (assuming you are using default setting):

  $ psql -h localhost -p 6432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example

Also you can check what is really stored on PostgreSQL with:

  $ psql -h localhost -p 5432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example

"""
    )


def display_eql_row(cur):
    column_function_map = {
        "age": EqlInt.from_parsed_json,
        "is_citizen": EqlBool.from_parsed_json,
        "start_date": EqlDate.from_parsed_json,
        "weight": EqlFloat.from_parsed_json,
        "name": EqlText.from_parsed_json,
        "extra_info": EqlJsonb.from_parsed_json,
    }

    cur.execute("SELECT * FROM customers")
    found = cur.fetchall()

    pp = pprint.PrettyPrinter(indent=4)
    print("The record looks like this when converted to an EqlRow:\n")
    for f in found:
        pp.pprint(EqlRow(column_function_map, f).row)


def query_customer(cur):
    print("\nQuery customer for partial Match of 'hello' in customers.name:")
    cur.execute(
        "SELECT * FROM customers WHERE cs_match_v1(name) @> cs_match_v1(%s)",
        (EqlText("some", "customers", "name").to_db_format("match"),),
    )
    found = cur.fetchall()
    for f in found:
        print()
        print(f"  Text inside the found record: {EqlText.from_parsed_json(f['name'])}")
        print()
        print(
            f"  Jsonb inside the found record: {EqlJsonb.from_parsed_json(f['extra_info'])}"
        )


def main():
    conn, cur = connect_to_db()

    insert_customer_record(cur)
    conn.commit()

    print_instructions()
    input("Press Enter to continue.")
    print()

    display_eql_row(cur)
    print()
    input("Press Enter to continue.")
    print()

    query_customer(cur)

    print("\n=== End of customers ===\n")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
