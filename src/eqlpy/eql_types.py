from datetime import datetime
import json


class EqlValue:
    def __init__(self, v, t: str, c: str):
        self.value = v
        self.table = t
        self.column = c

    def to_db_format(self, query_type=None):
        data = {
            "k": "pt",
            "p": self._value_in_db_format(query_type),
            "i": {"t": str(self.table), "c": str(self.column)},
            "v": 1,
            "q": query_type,
        }
        return json.dumps(data)

    @classmethod
    def from_parsed_json(cls, parsed):
        return cls._value_from_db_format(parsed["p"])


class EqlInt(EqlValue):
    def _value_in_db_format(self, query_type):
        return str(self.value)

    @classmethod
    def _value_from_db_format(cls, s: str):
        return int(s)


class EqlBool(EqlValue):
    def _value_in_db_format(self, query_type):
        return str(self.value).lower()

    @classmethod
    def _value_from_db_format(cls, s: str):
        return s.lower() == "true"


class EqlDate(EqlValue):
    def _value_in_db_format(self, query_type):
        return self.value.isoformat()

    @classmethod
    def _value_from_db_format(cls, s: str):
        return datetime.fromisoformat(s).date()


class EqlFloat(EqlValue):
    def _value_in_db_format(self, query_type):
        return str(self.value)

    @classmethod
    def _value_from_db_format(cls, s: str):
        return float(s)


class EqlText(EqlValue):
    def _value_in_db_format(self, query_type):
        return self.value

    @classmethod
    def _value_from_db_format(cls, s: str):
        return s


class EqlJsonb(EqlValue):
    def _value_in_db_format(self, query_type):
        if query_type == "ejson_path":
            return self.value
        else:
            return json.dumps(self.value)

    @classmethod
    def _value_from_db_format(cls, s: str):
        return json.loads(s)


class EqlRow:
    @staticmethod
    def id_map(x):
        return x

    def __init__(self, column_function_map, row):
        self.row = {}
        for k, v in row.items():
            if v == None:
                self.row[k] = None
            else:
                mapping = column_function_map.get(k, self.id_map)
                self.row[k] = mapping(v)
