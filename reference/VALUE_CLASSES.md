# EQL Value Classes

`eqlpy` includes a low-level interface to manage [EQL](https://github.com/cipherstash/encrypt-query-language) types directly.
If you're using Django or SQLAlchemy you probably won't need to use these types. 
If you want to implement `eqlpy` for another ORM, you will need to use these types. 

## Table of contents

- [Importing the types](#importing-the-types)
- [EQL value classes](#eql-value-classes)
  - [EqlInt](#eqlint)
  - [EqlBool](#eqlbool)
  - [EqlDate](#eqldate)
  - [EqlFloat](#eqlfloat)
  - [EqlText](#eqltext)
  - [EqlJsonb](#eqljsonb)
- [Parsing values from database format](#parsing-values-from-database-format)
- [EqlRow class](#eqlrow-class)

## Importing the types

```python
from eqlpy import (
    EqlInt,
    EqlBool,
    EqlDate,
    EqlFloat,
    EqlText,
    EqlJsonb,
    EqlRow
)
```

## EQL value classes

Each EQL value class inherits from the base `EqlValue` class and handles specific data types.

### EqlInt

Handles integer values.

```python
eql_int = EqlInt(42, 'users', 'age')
db_format = eql_int.to_db_format()
print(db_format)
```

### EqlBool

Handles boolean values.

```python
eql_bool = EqlBool(True, 'users', 'is_active')
db_format = eql_bool.to_db_format()
print(db_format)
```

### EqlDate

Handles date values.

```python
from datetime import date

eql_date = EqlDate(date.today(), 'users', 'created_at')
db_format = eql_date.to_db_format()
print(db_format)
```

### EqlFloat

Handles floating-point values.

```python
eql_float = EqlFloat(3.14, 'measurements', 'value')
db_format = eql_float.to_db_format()
print(db_format)
```

### EqlText

Handles text values.

```python
eql_text = EqlText('Hello, World!', 'messages', 'content')
db_format = eql_text.to_db_format()
print(db_format)
```

### EqlJsonb

Handles JSONB values.

```python
eql_jsonb = EqlJsonb({'key': 'value'}, 'configs', 'data')
db_format = eql_jsonb.to_db_format()
print(db_format)
```

## Parsing values from database format

Use the `from_parsed_json` method to convert database-formatted JSON back to Python types.

```python
import json

db_data = '{"k": "pt", "p": "42", "i": {"t": "users", "c": "age"}, "v": 1, "q": null}'
parsed = json.loads(db_data)
value = EqlInt.from_parsed_json(parsed)
print(value)  # Output: 42
```

## EqlRow class

`EqlRow` maps database rows to Python objects using a `column_function_map` to process each column.

```python
from datetime import datetime

row = {
    'id': '1',
    'age': '42',
    'is_active': 'true',
    'created_at': '2021-01-01',
    'value': '3.14',
    'content': 'Hello, World!',
    'data': '{"key": "value"}'
}

column_function_map = {
    'id': int,
    'age': int,
    'is_active': lambda x: x.lower() == 'true',
    'created_at': lambda x: datetime.fromisoformat(x).date(),
    'value': float,
    'data': json.loads
}

eql_row = EqlRow(column_function_map, row)
print(eql_row.row)
```

**Output:**

```python
{
    'id': 1,
    'age': 42,
    'is_active': True,
    'created_at': datetime.date(2021, 1, 1),
    'value': 3.14,
    'content': 'Hello, World!',
    'data': {'key': 'value'}
}
```
