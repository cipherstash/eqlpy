# EQLPY

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/cipherstash/eqlpy/python-app.yml?style=for-the-badge)](https://github.com/cipherstash/eqlpy/actions/workflows/python-app.yml)
[![Built by CipherStash](https://raw.githubusercontent.com/cipherstash/meta/refs/heads/main/csbadge.svg)](https://cipherstash.com)

 [Website](https://cipherstash.com) | [GitHub](https://github.com/cipherstash/eqlpy) | [Reference](/reference/) | [Discussions](https://github.com/orgs/cipherstash/discussions)

## Searchable encryption for Django and SQLAlchemy.

Based on the CipherStash [Encrypt Query Language (EQL)](https://github.com/cipherstash/encrypt-query-language),`eqlpy` provides a simple, type-driven approach to enabling encryption in your application.
By using EQL's built-in searchable encryption schemes, your model queries retain **full** search capabilities, including exact lookups, range queries, ordering and free text search.

## Table of contents

- [Features](#features)
- [Supported database packages](#supported-database-packages)
- [Installation and Setup](#installation-and-setup)
- [Usage with Django](#usage-with-django)
  - [Defining an encrypted field](#defining-an-encrypted-field)
  - [Inserting data](#inserting-data)
  - [Queries](#queries)
- [Migrating to EQLPY](#migrating-to-eqlpy)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Data type handling**: Supports various data types including integers, booleans, dates, floats, text, and JSONB.
- **Encrypted Search operations**: Search over encrypted data with no noticeable overhead.
- **Standard API**: Includes adapters for Django and SQLAlchemy.
- **Fast!**: Typical queries only incur a few milliseconds of overhead.

## Supported database packages

Currently, eqlpy supports either of the following database packages:

* psycopg 3 or psycopg 2
* sqlalchemy + psycopg 2
* Django + psycopg 2

For code examples of storing and querying encrypted data with [CipherStash Proxy](https://cipherstash.com/docs/getting-started/cipherstash-proxy) using those packages, refer to [examples directory](examples/) and [integration tests](tests/integration/).


## Installation and Setup

### Pre-requistites

To use `eqlpy` in your application, you will first need the following:

* CipherStash Proxy connected to the target database
* A ZeroKMS instance - which you can get via CipherStash Cloud
* EQL installed in your database

### Installation

To install `eqlpy`, use the following command:

```bash
pip install eqlpy
```

You can find the latest version on the [Python Package Index (PyPI)](https://pypi.org/project/eqlpy).

### EQL Configuration




## Usage with Django

### Defining an encrypted field

Let's say you have a customer model with an encrypted `name` field.
You can use the `EncryptedText` type when defining the field in the model:

```python
from django.db import models
from eqlpy.eqldjango import *

class Customer(models.Model):
    name = EncryptedText(table="customers", column="name")
```

The above customer model would create a database table like this:

```sql
CREATE TABLE myapp_customer (
    "id" bigint NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "name" cs_encrypted_v1 NOT NULL,
);
```

[!NOTE]
The column type in the database is `cs_encrypted_v1` which is encrypted type defined in [EQL](https://github.com/cipherstash/encrypt-query-language/blob/main/docs/reference/PAYLOAD.md). Internally EQL uses JSON.

`eqlpy` supports many different data types, including numbers, dates and JSON.
See the [Reference](#) docs for more information.

TODO: Link to the reference docs.


### Inserting data

`eqlpy` automatically encrypts values when saving to the database.
You can interact with the Django model in the same way as you normally would.

```py
>>> customer = Customer(name="Fred Flintstone")
>>> customer.save()
```

When retrieving a record, `eqlpy` automatically decrypts the value using the credentials defined in the setup step.

```py
>>> customer = Customer.objects.get(customer.id)
>>> customer.name
'Fred Flintstone'
```

#### View data in SQL

Viewing data in the database is possible via the proxy.
Query results will be automatically decrypted and returned in EQL form (JSON).

```sql
select id, name from customers;
```

```
  id  |                                        name                                      |
 -----+----------------------------------------------------------------------------------+
  446 | {"k":"pt","p":"Fred Flintstone","i":{"t":"customers","c":"name"},"v":1,"q":null} |
```

However, directly querying data via PostgreSQL will return the fully encrypted values.

```
 id   | name |
 +---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
 446 | {"c": "mBbL^r9sYr{**CKA_6C{IDN*%A*Hh3Y^S6yIkF*Ez{m&ib*gwg#*A)&{F6mjUwBj_aVx|i6EsZUQXbrN)(~iOu-@!cWr+e^P~2NpGTB?trC@Gwq;6qtWxx", "i": {"c": "name", "t": "customers"}, "k": "ct", "m": [77, 1666, 179, 786, 1429, 976, 2005, 1696, 182, 1317, 405, 1850, 1337, 768, 238, 253, 460, 443, 270, 779, 291, 1008, 1051, 1835, 1860, 1665, 538, 1067, 1914, 793, 272, 591, 684, 1861, 2037, 318, 525, 155, 672, 328, 1035, 853, 388, 1721, 1547, 1705, 613, 852, 1947, 1276, 481, 273, 1494, 1378, 1599, 1434, 319, 1794, 816, 1960, 379, 149, 1131, 1309, 204, 438, 1989, 1718, 29, 1413, 1965, 738, 1324, 2006, 802, 201, 251], "o": "(\"{\"\"(\\\\\"\"\\\\\\\\\\\\\\\\xe3596bf64b97d034fe0d967c6b224819467f41057f2fd61e8f2abb873e2c26b5e937781acd24165f09d73e810d516979bc295f66fa1aae86a457ce97d04e42680bb7160ae1f742ec865c06c1cafe6ad87c41bfdb6cda491e83061ca86f7a523c4edc033132370e51e5971bf3000c2a29a526f49d1323a224dfc782667d741a53c9b88936bef7e0fafb5b7d55cf9fdeb7e567a31ed53bde5b628b7f906421126f29bb5195e88fe8df669d5002bd2ed31db5cd8afe560d7dcbf5400c6e4b9eeba94a00078ee2ca5e138c37735648d2248c483156899c560a52fe7f1e41b6146d5382630bf2895dd0438d4de7f75c0c5ecb5f78f04736fff266a21713f701758c32b3dc8e17e01ea1406ad95c6c5cc950140f22e679b12d799b7a56890ded70188ab5c3a965d88bb9f9bb76d0d5f73746a5a048cbb78a8c18bdc5ebadf689ce881c566811fbf86243dd26ab6764656b86ad14358cf973ae99746ad24d7539362e69289a7de27920366bc619663cf5f7e401a6423eaff8699b95eccaf53989d7dd91af08f574932c1b79d89c95973d4dc45e0cfc3fdd0c7bf7dd\\\\\"\")\"\", \"\"(\\\\\"\"\\\\\\\\\\\\\\\\xe969121212121212714451b0a9ac6cd7de810a31ee27792a608ff20fb9d707c0d8de75fa2dd800f7b719322d123b4b314e9e08405426fcbb9ae8fb7e5a7ba009f4fa6f8f31d5e6b61fce62db66d1719390d6eae6aa60d89509de194056631376bad1c56db834982cd02cf69aaf7a8dfddeaab23f3ccf7fb0875d4ac3199188ea30b4d508f1e95810ac1274747298cb8afe20c6c8029811106392ce71683068c1b13c69474c9c81ec4a52b0631722d727bc02a801130369b73b38b4a1acf53cbc16c5773995a788fbc8d17f02945a3a95970aeaf4c08675adf13d29e5bca8e5ea09329e9fd41694a0af963c9a4158cac86257d9adbb66c4fa41b1878bec83394369545270e816a5212d6d5b7f18965c181040a3fcddf1b11d0ff90a5812840eaa8c9768705abae4de1749d9c7a2c608e4e7c9191b2501397e8b8566ae9f0b6ca82496ead7418fdc9d4ec243c8b941a67fae006c64022ada7e6679bffa4d557897ebfb488f795fd78032ff91de8cd186f1721ebf911beeac1810effabd0129a70199a609d79c5fbd8f6d24b3e7304c97358e7454d386f7c0f7\\\\\"\")\"\"}\")", "u": "bc9295f8303391f437f07b9298335347cc17a53a52025457456606e98955f7b8", "v": 1} |
```

### Queries

Queries work much the same way in `eqlpy` as for Django - even though the data is fully encrypted!

For example, to find a record with a given name:

```py
Customer.objects.get(name__eq="Alice Developer")
```

Text search works slightly differently.
EQL doesn't define the `LIKE` operator, but instead uses an operator called `match` which works in a similar way but over encrypted values.

```py
found = Customer.objects.get(name__match="caro")
```

See [Supported Queries](reference/SUPPORTED_QUERIES.md) for a full list of supported queries.

## Migrating to EQLPY

TODO


## Release

This project has been set up to use [Trusted Publisher](https://docs.pypi.org/trusted-publishers/) in PyPI from GitHub Actions.

To make a GitHub release and publish to PyPI do the following steps:

* Update the version in pyproject.toml in `main` branch (eg. "1.2.3")
* Make a tag of the same version prefixed with "v" (eg. "v1.2.3"), and push
  * `git tag v1.2.3`
  * `git push v1.2.3`
* `release-and-publish.yml` workflow will create a GitHub release, and publish the package to PyPI

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/cipherstash/eqlpy).

## License

This project is licensed under the MIT License.
