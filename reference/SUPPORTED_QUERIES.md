# EQL Supported Queries

`eqlpy` supports querying on encrypted data through EQL's [specialized functions](https://github.com/cipherstash/encrypt-query-language#searching-data-with-eql).

## Table of contents

- [Query types]
- [Required index types]
- [Supported interfaces]

## Query types

`eqlpy` supports X types of queries. They are:

- Equality where values are exactly matched, like `X = Y`
- Partial matching where a string is a substring of another, similar to `X like Y`
- Comparison where a value is greater than, less than, or equal to another, like `X > Y`
- JSONB containment where a document is contained in another, like `X @> Y`
- JSONB value extraction where a value is extracted from a document with a path, like `$.X.Y`

## Required index types

- Equality queries require either the `unique` or `ore` index type
- Partial matching of strings requires the `match` index type
- Comparison requires the `ore` index type
- JSONB containment requires the `ste_vec` index type

TODO: add details for ejson_path

## Supported query interfaces

### psycopg

For psycopg, the query interface involves SQL, with `cs_*` functions, weth EQL value types:
```python
cur.execute(
    "SELECT * FROM examples WHERE cs_match_v1(encrypted_utf8_str) @> cs_match_v1(%s)",
    (EqlText("hello", "examples", "encrypted_utf8_str").to_db_format("match"),),
)
```
This is the more verbose but expressive way of writing EQL queries.

TODO: List of EQL value classes

### SQLAlchemy

For SQLAlchemy, `eqlpy` provides python functions that correspond to the SQL functions.
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

TODO: List of EQL type decorators

### Django

For Django, `eqlpy` provides custom fields that allow querying similar to how Django queries are typically run:

```python
Customer.objects.get(name__match="carol")
```

TODO: list of custom field classes

`eqlpy` also provides query expression classes:

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

TODO: List of query expression classes


