import json
from django.db import models
from datetime import datetime


class EqlValue(models.TextField):
    def __init__(self, *args, **kwargs):
        self.table = kwargs.pop("table")
        self.column = kwargs.pop("column")
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value is not None:
            dict = {
                "k": "pt",
                "p": self._to_db_format(value),
                "i": {"t": self.table, "c": self.column},
                "v": 1,
                "q": None,
            }
            return json.dumps(dict)
        else:
            return None

    def _to_db_format(self, value):
        if value is None:
            return None
        return str(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return self._from_db_format(json.loads(value)["p"])

    def db_type(self, connection):
      return "cs_encrypted_v1"


class EqlInt(EqlValue):
    def _from_db_format(self, value):
        return int(value)


class EqlBoolean(EqlValue):

    def _to_db_format(self, value):
        if value is None:
            return None
        elif value == True:
            return "true"
        else:
            return "false"

    def _from_db_format(self, value):
        return value == "true"


class EqlDate(EqlValue):

    def _to_db_format(self, value):
        if value is None:
            return None

        return value.isoformat()

    def _from_db_format(self, value):
        return datetime.fromisoformat(value).date()


class EqlFloat(EqlValue):
    def _from_db_format(self, value):
        return float(value)


class EqlUtf8Str(EqlValue):

    def _from_db_format(self, value):
        return value


class EqlJsonb(EqlValue):
    def _to_db_format(self, value):
        if "foo" == "ejson_path":
            return value
        else:
            return json.dumps(value)

    def _from_db_format(self, value):
        return json.loads(value)
