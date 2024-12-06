import django
from django.conf import settings
from django.db import models, connection
from django.db.models import Q, F, Value, Count
from eqlpy.eql_types import EqlFloat, EqlText, EqlJsonb
from eqlpy.eqldjango import *
from datetime import date
import os


class TestSettings:
    pg_password = os.getenv("PGPASSWORD", "postgres")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = os.getenv("PGPORT", "6432")
    pg_db = os.getenv("PGDATABASE", "eqlpy_example")
    secret_key = os.getenv("SECRET_KEY", "test_secret_key")


if not settings.configured:
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=[
            "eqlpy.eqldjango",
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


class Example(models.Model):
    encrypted_int = EncryptedInt(table="examples", column="encrypted_int", null=True)
    encrypted_boolean = EncryptedBoolean(
        table="examples", column="encrypted_boolean", null=True
    )
    encrypted_date = EncryptedDate(table="examples", column="encrypted_date", null=True)
    encrypted_float = EncryptedFloat(
        table="examples", column="encrypted_float", null=True
    )
    encrypted_utf8_str = EncryptedText(
        table="examples", column="encrypted_utf8_str", null=True
    )
    encrypted_jsonb = EncryptedJsonb(
        table="examples", column="encrypted_jsonb", null=True
    )

    class Meta:
        app_label = "eqlpy.eqldjango"
        db_table = "examples"

    def __str__(self):
        return (
            f"Example(id={self.id}, int={self.encrypted_int}, bool={self.encrypted_boolean}, "
            f"date={self.encrypted_date}, float={self.encrypted_float}, "
            f"str='{self.encrypted_utf8_str}', jsonb={self.encrypted_jsonb})"
        )


def insert_example_records():
    print("\n\nInserting an example records...", end="")
    Example.objects.all().delete()

    example1 = Example(
        encrypted_int=1,
        encrypted_boolean=True,
        encrypted_utf8_str="string123",
        encrypted_date=date(2024, 1, 1),
        encrypted_float=1.1,
        encrypted_jsonb={"key": ["value"], "num": 1, "cat": "a"},
    )
    example1.save()

    example2 = Example(
        encrypted_int=-1,
        encrypted_boolean=False,
        encrypted_utf8_str="another_example",
        encrypted_date=date(2024, 1, 2),
        encrypted_float=2.1,
        encrypted_jsonb={"num": 2, "cat": "b"},
    )
    example2.save()

    example3 = Example(
        encrypted_int=0,
        encrypted_boolean=False,
        encrypted_utf8_str="yet_another",
        encrypted_date=date(2024, 1, 3),
        encrypted_float=5.0,
        encrypted_jsonb={"num": 3, "cat": "b"},
    )
    example3.save()

    print("done\n")

    return [example1, example2, example3]


def print_instructions():
    print(
        """
In another terminal window, you can check the data on CipherStash Proxy with (assuming you are using default setting):

  $ psql -h localhost -p 6432 -U postgres -x -c "select * from examples limit 1;" eqlpy_example

Also you can check what is really stored on PostgreSQL with:

  $ psql -h localhost -p 5432 -U postgres -x -c "select * from examples limit 1;" eqlpy_example

"""
    )
    print(
        f"If you get prompted for password, use '{TestSettings.pg_password}' (without quotes).\n"
    )


def query_example_match():
    print(
        "\nQuery example for partial Match of 'string1' in examples.encrypted_utf8_str:"
    )
    term = EqlText("string", "examples", "encrypted_utf8_str").to_db_format("match")
    record = Example.objects.filter(
        Q(CsContains(CsMatchV1(F("encrypted_utf8_str")), CsMatchV1(Value(term))))
    )[0]

    print()
    print(f"  Record found: {record}")
    print()


def query_example_ore():
    print("\nQuery example for 3.0 < examples.encrypted_float:")
    term = EqlFloat(3.0, "examples", "encrypted_float").to_db_format("ore")
    record = Example.objects.filter(
        Q(CsGt(CsOre648V1(F("encrypted_float")), CsOre648V1(Value(term))))
    )[0]

    print()
    print(f"  Record found: {record}")
    print()


def query_example_json_contains():
    print('\nQuery example for examples.encrypted_json @> {"key:": []} :')
    term = EqlJsonb({"key": []}, "examples", "encrypted_jsonb").to_db_format("ste_vec")
    record = Example.objects.get(
        Q(CsContains(CsSteVecV1(F("encrypted_jsonb")), CsSteVecV1(Value(term))))
    )

    print()
    print(f"  Record found: {record}")
    print()


def main():
    # refresh config just in case
    with connection.cursor() as cursor:
        cursor.execute("SELECT cs_refresh_encrypt_config()")

    [e1, e2, e3] = insert_example_records()

    print_instructions()
    input("Press Enter to continue.")
    print()

    print("A record looks like this as an Example model instance:\n")
    print(f"  {e1}")
    print()
    input("Press Enter to continue.")
    print()

    query_example_match()
    input("Press Enter to continue.")

    query_example_ore()
    input("Press Enter to continue.")

    query_example_json_contains()
    input("Press Enter to continue.")

    print("\n=== End of examples ===\n")


if __name__ == "__main__":
    main()
