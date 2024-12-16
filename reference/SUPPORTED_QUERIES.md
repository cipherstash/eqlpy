# EQL Supported Queries

`eqlpy` supports querying on encrypted data through EQL's [specialized functions](https://github.com/cipherstash/encrypt-query-language#searching-data-with-eql).

## Table of contents

- [Query types](#query-types)
- [Required index types](#required-index-types)
- [Supported query interfaces](#supported-query-interfaces)
  - [Django ORM](#django-orm)
  - [SQLAlchemy](#sqlalchemy)
  - [psycopg](#psycopg)

## Query types

The `eqlpy` library enables the following types of queries on encrypted data:

- Equality where values are exactly matched, like `X = Y`
- Partial matching where a string is a substring of another, similar to `X like Y`
- Comparison where a value is greater than, less than, or equal to another, like `X > Y`
  - Ordering is supported where comparison is supported, like `ORDER BY C`
- JSONB containment where a document is contained in another, like `X @> Y`
- JSONB value extraction where a value is extracted from a document with a path, like `$.X.Y`

## Required index types

- Equality queries require either the `unique` or `ore` index type
- Partial matching of strings requires the `match` index type
- Comparison requires the `ore` index type
- JSONB containment requires the `ste_vec` index type

TODO: add details for ejson_path

## Supported query interfaces

### Django ORM

For Django ORM, `eqlpy.eqldjango` provides custom field types that allow querying similar to how Django queries are typically run:

```python
Customer.objects.get(name__match="carol")
```

The following table shows custom field types provided by `eqldjango`.

| EncryptedValue subclass | Supported lookups                | Supported index type |
|-------------------------|----------------------------------|----------------------|
| EncryptedText           | eq (EncryptedUniqueEquals)       | "unique"             |
|                         | match (EncryptedTextMatch)       | "match"              |
| EncryptedBoolean        | eq (EncryptedOreEquals)          | "ore"                |
| EncryptedDate           | eq (EncryptedOreEquals)          | "ore"                |
|                         | lt (EncryptedOreLt)              | "ore"                |
|                         | gt (EncryptedOreGt)              | "ore"                |
| EncryptedInt            | eq (EncryptedOreEquals)          | "ore"                |
|                         | lt (EncryptedOreLt)              | "ore"                |
|                         | gt (EncryptedOreGt)              | "ore"                |
| EncryptedFloat          | eq (EncryptedOreEquals)          | "ore"                |
|                         | lt (EncryptedOreLt)              | "ore"                |
|                         | gt (EncryptedOreGt)              | "ore"                |
| EncryptedJsonb          | contains (EncryptedJsonContains) | "ste_vec"            |

`eqldjango` also provides query expression classes:

```python
Customer.objects.filter(
    Q(
        CsMatch(
            CsMatchV1(F("name")),
            CsMatchV1(
                Value(EqlText("ali", "customers", "name").to_db_format("match"))
            )
        )
    )
)
```

This is the more expressive but verbose method of expressing EQL queries with Django ORM.

The following table shows the relevant classes in `eqldjango`.

| Function or operator class | PostgreSQL function or operator |
|----------------------------|---------------------------------|
| CsMatchV1                  | cs_match_v1                     |
| CsUniqueV1                 | cs_unique_v1                    |
| CsOre648V1                 | cs_ore_64_8_v1                  |
| CsSteVecV1                 | cs_ste_vec_v1                   |
| CsSteVecValueV1            | cs_ste_vec_value_v1             |
| CsSteVecTermV1             | cs_ste_vec_term_v1              |
| CsGroupedValueV1           | cs_grouped_value_v1             |
| CsContains                 | @>                              |
| CsMatch                    | @>                              |
| CsContainedBy              | <@                              |
| CsEquals                   | =                               |
| CsGt                       | >                               |
| CsLt                       | <                               |

### SQLAlchemy

For SQLAlchemy, `eqlpy.eqlalchemy` provides python functions that correspond to the EQL functions.
`eqlpy` also provides EQL-specific type decorators which helps with converting between the database types and Python types.

```python
session.query(Example)
    .filter(
        cs_match_v1(Example.encrypted_utf8_str).op("@>")(
            cs_match_v1(
                EqlText("hello", "examples", "encrypted_utf8_str").to_db_format(
                    "match"
                )
            )
        )
    )
    .one()
```

With those functions, instead of calls to `cs_*` functions directly in SQL, they can be expressed in Python.

The following EQL functions are available in Python for SQLAlchemy.

- cs_unique_v1
- cs_match_v1
- cs_ore_64_8_v1
- cs_ste_vec_v1
- cs_ste_vec_value_v1
- cs_ste_vec_term_v1
- cs_grouped_value_v1

The EQL-specific type decorators are:

- EncryptedInt
- EncryptedBoolean
- EncryptedDate
- EncryptedFloat
- EncryptedUtf8Str
- EncryptedJsonb

### psycopg

For psycopg, the query interface involves SQL, with `cs_*` functions, with EQL value types:

```python
cur.execute(
    "SELECT * FROM examples WHERE cs_match_v1(encrypted_utf8_str) @> cs_match_v1(%s)",
    (EqlText("hello", "examples", "encrypted_utf8_str").to_db_format("match"),),
)
```

This is the more verbose but expressive way of writing EQL queries.

`eqlpy` provides the following classes to represent EQL values:

- EqlInt
- EqlBool
- EqlDate
- EqlFloat
- EqlText
- EqlJsonb


