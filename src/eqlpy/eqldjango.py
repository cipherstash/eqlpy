import json
from django.db import models
from datetime import datetime
from django.db.models import Func, JSONField, Aggregate
from django.db.models.fields import BooleanField
from django.db.models import Q, F, Value
from django.db.models.lookups import Lookup
from eqlpy.eql_types import EqlFloat, EqlText, EqlJsonb
from functools import reduce


class EncryptedValue(models.JSONField):
    def __init__(self, *args, **kwargs):
        self.eql_table = kwargs.pop("eql_table", None)
        self.eql_column = kwargs.pop("eql_column", None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["eql_table"] = self.eql_table
        kwargs["eql_column"] = self.eql_column
        return name, path, args, kwargs

    def get_prep_value(self, value):
        if value is not None:
            dict = {
                "k": "pt",
                "p": self._to_db_format(value),
                "i": {"t": self.eql_table, "c": self.eql_column},
                "v": 1,
                "q": None,
            }
            return dict
        else:
            return None

    def _to_db_format(self, value):
        if value is None:
            return None
        return str(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, str):
            # TODO: seems like we get a string from the database, but we should be getting a dict
            value = json.loads(value)
        return self._from_db_format(value["p"])

    def db_type(self, connection):
        return "cs_encrypted_v1"

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        # if table or column are not set, use cls and name
        if (not hasattr(self, "eql_table")) or (getattr(self, "eql_table") is None):
            self.eql_table = cls._meta.db_table
        if (not hasattr(self, "eql_column")) or (getattr(self, "eql_column") is None):
            self.eql_column = name


class EncryptedInt(EncryptedValue):
    def _from_db_format(self, value):
        return int(value)


class EncryptedBoolean(EncryptedValue):
    def _to_db_format(self, value):
        if value is None:
            return None
        elif value == True:
            return "true"
        else:
            return "false"

    def _from_db_format(self, value):
        return value == "true"


class EncryptedDate(EncryptedValue):
    def _to_db_format(self, value):
        if value is None:
            return None

        return value.isoformat()

    def _from_db_format(self, value):
        return datetime.fromisoformat(value).date()


class EncryptedFloat(EncryptedValue):
    def _from_db_format(self, value):
        return float(value)


class EncryptedText(EncryptedValue):
    def _from_db_format(self, value):
        return value


class EncryptedJsonb(EncryptedValue):
    def _to_db_format(self, value):
        return json.dumps(value)

    def _from_db_format(self, value):
        return json.loads(value)


class EncryptedUniqueEquals(Lookup):
    lookup_name = "eq"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # TODO: could this be done in get_prep_value?
        rhs_params = [dict(e, q="unique") for e in rhs_params]
        params = map(json.dumps, (lhs_params + rhs_params))
        return "cs_unique_v1(%s) = cs_unique_v1(%s)" % (lhs, rhs), params


EncryptedText.register_lookup(EncryptedUniqueEquals)


class EncryptedOreEquals(Lookup):
    lookup_name = "eq"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # TODO: could this be done in get_prep_value?
        rhs_params = [dict(e, q="ore") for e in rhs_params]
        params = map(json.dumps, (lhs_params + rhs_params))
        return "cs_ore_64_8_v1(%s) = cs_ore_64_8_v1(%s)" % (lhs, rhs), params


EncryptedBoolean.register_lookup(EncryptedOreEquals)
EncryptedDate.register_lookup(EncryptedOreEquals)
EncryptedInt.register_lookup(EncryptedOreEquals)
EncryptedFloat.register_lookup(EncryptedOreEquals)


class EncryptedTextMatch(Lookup):
    lookup_name = "match"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # TODO: could this be done in get_prep_value?
        rhs_params = [dict(e, q="match") for e in rhs_params]
        params = map(json.dumps, (lhs_params + rhs_params))
        return "cs_match_v1(%s) @> cs_match_v1(%s)" % (lhs, rhs), params


EncryptedText.register_lookup(EncryptedTextMatch)


class EncryptedOreLt(Lookup):
    lookup_name = "lt"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # TODO: could this be done in get_prep_value?
        rhs_params = [dict(e, q="ore") for e in rhs_params]
        params = map(json.dumps, (lhs_params + rhs_params))
        return "cs_ore_64_8_v1(%s) < cs_ore_64_8_v1(%s)" % (lhs, rhs), params


EncryptedFloat.register_lookup(EncryptedOreLt)
EncryptedInt.register_lookup(EncryptedOreLt)
EncryptedDate.register_lookup(EncryptedOreLt)


class EncryptedOreGt(Lookup):
    lookup_name = "gt"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # TODO: could this be done in get_prep_value?
        rhs_params = [dict(e, q="ore") for e in rhs_params]
        params = map(json.dumps, (lhs_params + rhs_params))
        return "cs_ore_64_8_v1(%s) > cs_ore_64_8_v1(%s)" % (lhs, rhs), params


EncryptedFloat.register_lookup(EncryptedOreGt)
EncryptedInt.register_lookup(EncryptedOreGt)
EncryptedDate.register_lookup(EncryptedOreGt)


class EncryptedJsonContains(Lookup):
    lookup_name = "contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # TODO: could this be done in get_prep_value?
        rhs_params = [dict(e, q="ste_vec") for e in rhs_params]
        params = map(json.dumps, (lhs_params + rhs_params))
        return "cs_ste_vec_v1(%s) @> cs_ste_vec_v1(%s)" % (lhs, rhs), params


EncryptedJsonb.register_lookup(EncryptedJsonContains)

# EQL functions
# These classes are data structures that represent EQL functions
# Needed for complex EQL queries


class CsMatchV1(Func):
    function = "cs_match_v1"
    output_field = JSONField()


class CsUniqueV1(Func):
    function = "cs_unique_v1"
    output_field = JSONField()


class CsOre648V1(Func):
    function = "cs_ore_64_8_v1"
    output_field = JSONField()


class CsSteVecV1(Func):
    function = "cs_ste_vec_v1"
    output_field = JSONField()


class CsSteVecValueV1(Func):
    function = "cs_ste_vec_value_v1"
    output_field = JSONField()


class CsSteVecTermV1(Func):
    function = "cs_ste_vec_term_v1"
    output_field = JSONField()


class CsGroupedValueV1(Aggregate):
    function = "cs_grouped_value_v1"
    output_field = JSONField()


# meta-programming to create custom EQL operators for Django
# This create_operator and the calls below define Classes
# CsContains, CsContainedBy, CsEquals, CsGt, CsLt
# which represent Postgres operators @>, <@, =, >, < respectively.
def create_operator(operator_name, template):
    class CsOperator(models.Func):
        function = ""
        output_field = BooleanField()

        def __init__(self, left, right, **extra):
            self.template = template
            super().__init__(left, right, **extra)

        def as_sql(self, compiler, connection):
            left, right = self.source_expressions
            left_sql, left_params = compiler.compile(left)
            right_sql, right_params = compiler.compile(right)

            template = self.template % {"left": left_sql, "right": right_sql}
            params = left_params + right_params

            return template, params

    CsOperator.__name__ = f"Cs{operator_name.capitalize()}Operator"

    return CsOperator


CsContains = create_operator("CsContains", "%(left)s @> %(right)s")
CsMatch = create_operator("CsMatch", "%(left)s @> %(right)s")
CsContainedBy = create_operator("CsContainedBy", "%(left)s <@ %(right)s")
CsEquals = create_operator("CsEquals", "%(left)s = %(right)s")
CsGt = create_operator("CsGt", "%(left)s > %(right)s")
CsLt = create_operator("CsLt", "%(left)s < %(right)s")
