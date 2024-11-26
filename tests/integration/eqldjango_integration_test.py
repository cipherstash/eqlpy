import unittest
import os
import django
from django.conf import settings
from django.db import models
from eqlpy.eqldjango import *
from datetime import date


class TestSettings:
    pg_password = os.getenv("PGPASSWORD", "postgres")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = os.getenv("PGPORT", "6432")
    pg_db = os.getenv("PGDATABASE", "eqlpy_test")
    secret_key = os.getenv("SECRET_KEY", "test_secret_key")


if not settings.configured:
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=[
            "eql_django_integration_test",
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


class TestExampleDjangoModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        Example.objects.all().delete()
        self.example1 = Example(
            encrypted_int=65535,
            encrypted_boolean=True,
            encrypted_utf8_str='test_string with \\ " "',
            encrypted_date=date(2024, 1, 1),
            encrypted_float=1.1,
            encrypted_jsonb={"key": ["value"], "num": 1, "cat": "a"},
        )
        self.example1.save()

    def test_save_null_example(self):
        count = Example.objects.count()
        self.null_eaxmple = Example()
        self.null_eaxmple.save()
        self.assertEqual(count + 1, Example.objects.count())

    # Simple tests for storing and loading encrypted columns
    def test_encrypted_int(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_int, 65535)

    def test_encrypted_boolean(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_boolean, True)

    def test_encrypted_date(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_date, date(2024, 1, 1))

    def test_encrypted_float(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_float, 1.1)

    def test_encrypted_utf8_str(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(found.encrypted_utf8_str, 'test_string with \\ " "')

    def test_encrypted_jsonb(self):
        found = Example.objects.get(id=self.example1.id)
        self.assertEqual(
            found.encrypted_jsonb, {"key": ["value"], "num": 1, "cat": "a"}
        )


class Example(models.Model):
    encrypted_int = EqlInt(table="examples", column="encrypted_int", null=True)
    encrypted_boolean = EqlBoolean(
        table="examples", column="encrypted_boolean", null=True
    )
    encrypted_date = EqlDate(table="examples", column="encrypted_date", null=True)
    encrypted_float = EqlFloat(table="examples", column="encrypted_float", null=True)
    encrypted_utf8_str = EqlUtf8Str(
        table="examples", column="encrypted_utf8_str", null=True
    )
    encrypted_jsonb = EqlJsonb(table="examples", column="encrypted_jsonb", null=True)

    class Meta:
        db_table = "examples"
