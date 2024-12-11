import django
from django.conf import settings
from django.db import models, connection
from django.db.models import Q, F, Value, Count
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

def greet():
    print("Welcome to CipherStash eqlpy examples!")
    print()
    print("These examples demonstrate basic usage of CipherStash's encryption with eqlpy and Django.")
    print()

def print_prerequisites():
    print("Make sure you have the following prerequisites:")
    print("  * PostgreSQL container and Proxy container running")
    print("  * Django and psycopg2 installed")
    print()


def insert_example_records():
    print("\n\nInserting example records...", end="")
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
    print()
    print("Encrypted records created!")
    print()
    print("3 Example models stored:\n")
    print(f"  {example1}")
    print(f"  {example2}")
    print(f"  {example3}")


    return [example1, example2, example3]


def print_psql_instructions():
    print("Now you can see the encrypted data in CipherStash Proxy and PostgreSQL.")
    print()
    print("For CipherStash: In another terminal window, run:\n")
    print('    $ psql -h localhost -p 6432 -U postgres -x -c "select * from examples limit 1;" eqlpy_example')
    print()
    print(
        f"      (if you get prompted for password, use '{TestSettings.pg_password}' without the surrounding quotes)\n"
    )
    prompt_enter()
    print("To check what is actually stored on PostgreSQL, run:\n")
    print('   $ psql -h localhost -p 5432 -U postgres -x -c "select * from examples limit 1;" eqlpy_example')


def query_example_match():
    print(
        "\nQuery example Example.objects.get(encrypted_utf8_str__match=\"str\"), which should find example1 with \"string123\":"
    )
    record = Example.objects.get(encrypted_utf8_str__match="str")

    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()


def query_example_ore():
    print("\nQuery example Example.objects.get(encrypted_float__gt=3.0), which should find example3 with 5.0:")
    record = Example.objects.get(encrypted_float__gt=3.0)

    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()


def query_example_json_contains():
    print('\nQuery example Example.objects.get(encrypted_jsonb__contains={"key": []}), which should find example1 with {"key": ["value"], "num": 1, "cat": "a"}:')
    record = Example.objects.get(encrypted_jsonb__contains={"key": []})

    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()

def print_end_message():
    print("That's it! Thank you for running this example! Please look at the example code itself to see how records are created and queries are run.")

step = 0

def prompt_enter():
    global step
    print()
    input("Press Enter to continue.")
    print("\n\n\n\n")
    print(f"== step {step} ==")
    step += 1


def main():
    # refresh config just in case
    with connection.cursor() as cursor:
        cursor.execute("SELECT cs_refresh_encrypt_config()")

    greet()
    prompt_enter()

    print_prerequisites()
    prompt_enter()

    [e1, e2, e3] = insert_example_records()
    prompt_enter()

    print_psql_instructions()
    prompt_enter()

    query_example_match()
    prompt_enter()

    query_example_ore()
    prompt_enter()

    query_example_json_contains()
    prompt_enter()

    print_end_message()
    print("\n=== End of examples ===\n")


if __name__ == "__main__":
    main()
