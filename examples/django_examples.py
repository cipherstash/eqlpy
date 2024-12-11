import django
from django.conf import settings
from django.db import models, connection
from django.db.models import Q, F, Value, Count, IntegerField
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


class Customer(models.Model):
    age = EncryptedInt(table="customers", column="age", null=True)
    is_citizen = EncryptedBoolean(table="customers", column="is_citizen", null=True)
    start_date = EncryptedDate(table="customers", column="start_date", null=True)
    weight = EncryptedFloat(table="customers", column="weight", null=True)
    name = EncryptedText(table="customers", column="name", null=True)
    extra_info = EncryptedJsonb(table="customers", column="extra_info", null=True)
    visit_count = IntegerField()

    class Meta:
        app_label = "eqlpy.eqldjango"
        db_table = "customers"

    def __str__(self):
        return (
            f"Customer(id={self.id}, int={self.age}, bool={self.is_citizen}, "
            f"date={self.start_date}, float={self.weight}, "
            f"str='{self.name}', jsonb={self.extra_info})"
        )


def greet():
    print("Welcome to CipherStash eqlpy examples!")
    print()
    print(
        "These examples demonstrate basic usage of CipherStash's encryption with eqlpy and Django."
    )
    print()


def print_prerequisites():
    print("Make sure you have the following prerequisites:")
    print("  * PostgreSQL container and Proxy container running")
    print("  * Django and psycopg2 installed")
    print()


def insert_example_records():
    print("\n\nInserting example records...", end="")
    Customer.objects.all().delete()

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

    print("done\n")
    print()
    print("Encrypted records created!")
    print()
    print("3 Customer models stored:\n")
    print(f"  {customer1}")
    print(f"  {customer2}")
    print(f"  {customer3}")

    return [customer1, customer2, customer3]


def print_psql_instructions():
    print("Now you can see the encrypted data in CipherStash Proxy and PostgreSQL.")
    print()
    print("For CipherStash: In another terminal window, run:\n")
    print(
        '    $ psql -h localhost -p 6432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example'
    )
    print()
    print(
        f"      (if you get prompted for password, use '{TestSettings.pg_password}' without the surrounding quotes)\n"
    )
    prompt_enter()
    print("To check what is actually stored on PostgreSQL, run:\n")
    print(
        '   $ psql -h localhost -p 5432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example'
    )


def query_example_match():
    print(
        '\nQuery example Customer.objects.get(name__match="ali"), which should find customer1 with "Alice Developer":'
    )
    record = Customer.objects.get(name__match="ali")

    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()


def query_example_ore():
    print(
        "\nQuery example Customer.objects.get(weight__gt=73.0), which should find customer2 with 82.1:"
    )
    record = Customer.objects.get(weight__gt=73.0)

    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()


def query_example_json_contains():
    print(
        '\nQuery example Customer.objects.get(extra_info__contains={"key": []}), which should find customer1 with {"key": ["value"], "num": 1, "cat": "a"}:'
    )
    record = Customer.objects.get(extra_info__contains={"key": []})

    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()


def print_end_message():
    print(
        "That's it! Thank you for running this! Please look at the example code itself to see how records are created and queries are run."
    )


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
