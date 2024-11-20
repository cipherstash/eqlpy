from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator, String
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement
from functools import wraps
from datetime import date
import json

import sys
import os


class EqlTypeDecorator(TypeDecorator):
    def __init__(self, table, column):
        super().__init__()
        self.table = table
        self.column = column

    def process_bind_param(self, value, dialect):
        if value is not None:
            value_dict = {
                "k": "pt",
                "p": str(value),
                "i": {"t": self.table, "c": self.column},
                "v": 1,
                "q": None,
            }
            value = json.dumps(value_dict)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value["p"]


class EncryptedInt(EqlTypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return int(value["p"])


class EncryptedBoolean(EqlTypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = str(value).lower()
        return super().process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value["p"] == "true"


class EncryptedDate(EqlTypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return date.fromisoformat(value["p"])


class EncryptedFloat(EqlTypeDecorator):
    impl = String
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return float(value["p"])


class EncryptedUtf8Str(EqlTypeDecorator):
    impl = String
    cache_ok = True


class EncryptedJsonb(EqlTypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return super().process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value["p"])


class BaseModel(DeclarativeBase):
    pass


# metaprogramming to add custom function calls
def create_cs_function(function_name, param_count=1):
    def decorator(func):
        class CsFunction(FunctionElement):
            inherit_cache = True
            name = function_name

        @compiles(CsFunction, "postgresql")
        @wraps(func)
        def compile_cs_function(element, compiler, **kw):
            if param_count == 1:
                return f"{function_name}(%s)" % compiler.process(element.clauses)
            elif param_count == 2:
                args = list(element.clauses)
                return f"{function_name}(%s, %s)" % (
                    compiler.process(args[0]),
                    compiler.process(args[1]),
                )
            else:
                raise ValueError(f"Invalid number of parameters for {function_name}")

        return CsFunction

    return decorator


@create_cs_function("cs_unique_v1")
def cs_unique_v1():
    pass


@create_cs_function("cs_match_v1")
def cs_match_v1():
    pass


@create_cs_function("cs_ore_64_8_v1")
def cs_ore_64_8_v1():
    pass


@create_cs_function("cs_ste_vec_v1")
def cs_ste_vec_v1():
    pass


@create_cs_function("cs_ste_vec_value_v1", 2)
def cs_ste_vec_value_v1():
    pass


@create_cs_function("cs_ste_vec_term_v1", 1)
def cs_ste_vec_term_v1(*args):
    pass


@create_cs_function("cs_grouped_value_v1")
def cs_grouped_value_v1():
    pass
