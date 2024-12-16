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
    age = EncryptedInt(null=True)
    is_citizen = EncryptedBoolean(null=True)
    start_date = EncryptedDate(null=True)
    weight = EncryptedFloat(null=True)
    name = EncryptedText(null=True)
    extra_info = EncryptedJsonb(null=True)

    # non-sensitive fields (not encrypted)
    visit_count = IntegerField()

    class Meta:
        app_label = "eqlpy.eqldjango"
        db_table = "customers"

    def __str__(self):
        return (
            f"Customer(id={self.id}, age={self.age}, is_citizen={self.is_citizen}, "
            f"start_date={self.start_date}, weight={self.weight}, "
            f"name='{self.name}', extra_info={self.extra_info}, "
            f"visit_count={self.visit_count})"
        )


def greet():
    print("\n\nWelcome to CipherStash eqldjango example!")
    print()
    print(
        "This example script demonstrates basic usage of CipherStash's encryption with eqlpy and Django."
    )


def print_prerequisites():
    print("Make sure you have the following prerequisites:")
    print("  * PostgreSQL container and Proxy container running")
    print("  * CihperStash EQL installed on PostgreSQL")
    print(
        "  * Example table(s) created with create_tables.sql script in this directory"
    )
    print("  * Django and psycopg2 installed")
    print()
    print("If you do not, please refer to README.md in this directory.")


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
    print("For CipherStash Proxy: In another terminal window, run:\n")
    print(
        '    $ psql -h localhost -p 6432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example'
    )
    print()
    print(
        f"      (if you get prompted for password, use '{TestSettings.pg_password}' without the surrounding quotes)\n"
    )
    prompt_enter()
    print("To see what is actually stored on PostgreSQL, run:\n")
    print(
        '    $ psql -h localhost -p 5432 -U postgres -x -c "select * from customers limit 1;" eqlpy_example'
    )


def wait_and_show_record(record):
    print()
    input("Press Enter to continue.")
    print()
    print(f"  Record found: {record}")
    print()


def query_exact_string():
    query_code = 'Customer.objects.get(name__eq="Carol Customer")'
    print(
        f'\nQuery example {query_code}, which should find customer with the exact name "Carol Customer":'
    )
    record = eval(query_code)

    wait_and_show_record(record)


def query_example_match_string():
    query_code = 'Customer.objects.get(name__match="ali")'
    print(
        f'\nQuery example {query_code}, which should find customer with the matching name "Alice Developer":'
    )
    record = eval(query_code)

    wait_and_show_record(record)


def query_example_ore():
    query_code = 'Customer.objects.get(weight__gt=73.0)'
    print(
        f"\nQuery example {query_code}, which should find the customer with the weight 82.1:"
    )
    record = eval(query_code)

    wait_and_show_record(record)


def query_example_json_contains():
    query_code = 'Customer.objects.get(extra_info__contains={"key": []})'
    print(
        f'\nQuery example {query_code}, which should find the customer with the extra_info '
         '{"key": ["value"], "num": 1, "cat": "a"}:'
    )
    record = eval(query_code)

    wait_and_show_record(record)


def query_example_exact_date():
    query_code = 'Customer.objects.get(start_date__eq=date(2024, 1, 2))'
    print(
        f"\nQuery example {query_code}, which should find the customer with the start date 2024-01-02:"
    )
    record = eval(query_code)

    wait_and_show_record(record)


def query_example_date_ore():
    query_code = 'Customer.objects.get(start_date__gt=date(2024, 1, 2))'
    print(
        f"\nQuery example {query_code}, which should find the customer with the start date 2024-01-03:"
    )
    record = Customer.objects.get(start_date__gt=date(2024, 1, 2))

    wait_and_show_record(record)


def query_example_date_ore_with_name_match():
    query_code = 'Customer.objects.get(start_date__lt=date(2024, 1, 3), name__match="Customer")'
    print(
        f'\nQuery example {query_code}, which should find the customer with the matching name and start date:'
    )
    record = eval(query_code)
    wait_and_show_record(record)


def query_example_visit_count_exact():
    query_code = "Customer.objects.get(visit_count=2)"
    print(
        f"\nQuery example {query_code}, which uses a plain text column only:"
    )
    record = eval(query_code)

    wait_and_show_record(record)


def query_example_visit_count_with_date_ore():
    query_code = "Customer.objects.get(visit_count__gt=0, start_date__lt=date(2024, 1, 3))"
    print(
        f"\nQuery example {query_code}, which uses both a plain text column and an encrypted column:"
    )
    record = eval(query_code)

    wait_and_show_record(record)


def print_end_message():
    print("That's it! Thank you for following along!")
    print(
        f"Please look at the example code ({os.path.basename(__file__)}) itself to see how records are created and queries are run."
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

    query_exact_string()
    prompt_enter()

    query_example_match_string()
    prompt_enter()

    query_example_ore()
    prompt_enter()

    query_example_exact_date()
    prompt_enter()

    query_example_date_ore()
    prompt_enter()

    query_example_json_contains()
    prompt_enter()

    query_example_date_ore_with_name_match()
    prompt_enter()

    query_example_visit_count_exact()
    prompt_enter()

    query_example_visit_count_with_date_ore()
    prompt_enter()

    print_end_message()
    print("\n=== End of example script ===\n")


if __name__ == "__main__":
    main()
