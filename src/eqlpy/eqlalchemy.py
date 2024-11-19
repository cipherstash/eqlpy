from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator, String
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
                "i": {
                    "t": self.table,
                    "c": self.column
                },
                "v": 1,
                "q": None
            }
            value = json.dumps(value_dict)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value['p']

class EncryptedInt(EqlTypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return int(value['p'])


class EncryptedBoolean(EqlTypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = str(value).lower()
        return super().process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value['p'] == 'true'

class EncryptedDate(EqlTypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return date.fromisoformat(value['p'])

class EncryptedFloat(EqlTypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return float(value['p'])

class EncryptedUtf8Str(EqlTypeDecorator):
    impl = String

class EncryptedJsonb(EqlTypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return super().process_bind_param(value, dialect)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value['p'])

class BaseModel(DeclarativeBase):
    pass
