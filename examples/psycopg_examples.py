import psycopg
import pprint
from datetime import datetime
from eqlpy.eql_types import EqlInt, EqlBool, EqlDate, EqlFloat, EqlText, EqlJsonb, EqlRow

def connect_to_db():
    db_string = "host=localhost dbname=cipherstash_getting_started user=postgres password=postgres port=6432"
    conn = psycopg.connect(db_string)
    return conn, conn.cursor(row_factory=psycopg.rows.dict_row)

def insert_example_record(cur):
    print("\n\nInserting an example record...", end="")
    cur.execute("DELETE FROM examples")
    cur.execute("SELECT cs_refresh_encrypt_config()")

    example_data = {
        "encrypted_int": EqlInt(-51, "examples", "encrypted_int"),
        "encrypted_boolean": EqlBool(False, "examples", "encrypted_boolean"),
        "encrypted_date": EqlDate(datetime.now().date(), "examples", "encrypted_date"),
        "encrypted_float": EqlFloat(-0.5, "examples", "encrypted_float"),
        "encrypted_utf8_str": EqlText("hello, world", "examples", "encrypted_utf8_str"),
        "encrypted_jsonb": EqlJsonb(
            {"num": 1, "category": "a", "top": {"nested": ["a", "b", "c"]}},
            "examples",
            "encrypted_jsonb"
        )
    }

    insert_query = """
    INSERT INTO examples (encrypted_int, encrypted_boolean, encrypted_date, encrypted_float, encrypted_utf8_str, encrypted_jsonb)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(insert_query, tuple(field.to_db_format() for field in example_data.values()))
    print("done\n")

def print_instructions():
    print("""
In another terminal window, you can check the data on CipherStash Proxy with (assuming you are using default setting):
$ psql -h localhost -p 6432 -U postgres -x -c "select * from examples limit 1;" cipherstash_getting_started

Also you can check what is really stored on PostgreSQL with:
$ psql -h localhost -p 5432 -U postgres -x -c "select * from examples limit 1;" cipherstash_getting_started
""")

def display_eql_row(cur):
    column_function_map = {
        "encrypted_int": EqlInt.from_parsed_json,
        "encrypted_boolean": EqlBool.from_parsed_json,
        "encrypted_date": EqlDate.from_parsed_json,
        "encrypted_float": EqlFloat.from_parsed_json,
        "encrypted_utf8_str": EqlText.from_parsed_json,
        "encrypted_jsonb": EqlText.from_parsed_json,
    }

    cur.execute("SELECT * FROM examples")
    found = cur.fetchall()

    pp = pprint.PrettyPrinter(indent=4)
    print("The record looks like this when converted to an EqlRow:")
    for f in found:
        pp.pprint(EqlRow(column_function_map, f).row)

def query_example(cur):
    print("\nQuery example for partial Match of 'hello' in examples.encrypted_utf8_str:")
    cur.execute(
        "SELECT * FROM examples WHERE cs_match_v1(encrypted_utf8_str) @> cs_match_v1(%s)",
        (EqlText("hello", "examples", "encrypted_utf8_str").to_db_format(),),
    )
    found = cur.fetchall()
    for f in found:
        print(f"Text inside the found record: {EqlText.from_parsed_json(f['encrypted_utf8_str'])}")

def main():
    conn, cur = connect_to_db()

    insert_example_record(cur)
    conn.commit()

    print_instructions()
    input("Press Enter to continue.")
    print()

    display_eql_row(cur)
    print()
    input("Press Enter to continue.")
    print()

    query_example(cur)

    print("\n=== End of examples ===\n")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
