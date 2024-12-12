create table customers (
  id serial primary key,
  is_citizen cs_encrypted_v1,
  start_date cs_encrypted_v1,
  weight cs_encrypted_v1,
  age cs_encrypted_v1,
  name cs_encrypted_v1,
  extra_info cs_encrypted_v1,
  visit_count integer
);

-- Add CipherStash indexes to Encrypt config
SELECT cs_add_index_v1('customers', 'is_citizen', 'ore', 'boolean');
SELECT cs_add_index_v1('customers', 'start_date', 'ore', 'date');
SELECT cs_add_index_v1('customers', 'weight', 'ore', 'double');
SELECT cs_add_index_v1('customers', 'age', 'ore', 'int');
SELECT cs_add_index_v1('customers', 'name', 'unique', 'text', '{"token_filters": [{"kind": "downcase"}]}');
SELECT cs_add_index_v1('customers', 'name', 'match', 'text');
SELECT cs_add_index_v1('customers', 'name', 'ore', 'text');
SELECT cs_add_index_v1('customers', 'extra_info', 'ste_vec', 'jsonb', '{"prefix": "customers/extra_info"}');

-- Add corresponding PG indexes for each CipherStash index
CREATE INDEX ON customers (cs_ore_64_8_v1(is_citizen));
CREATE INDEX ON customers (cs_ore_64_8_v1(start_date));
CREATE INDEX ON customers (cs_ore_64_8_v1(weight));
CREATE INDEX ON customers (cs_ore_64_8_v1(age));
CREATE UNIQUE INDEX ON customers(cs_unique_v1(name));
CREATE INDEX ON customers USING GIN (cs_match_v1(name));
CREATE INDEX ON customers (cs_ore_64_8_v1(name));
-- CREATE INDEX ON customers USING GIN (cs_ste_vec_v1(extra_info));

-- Transition the Encrypt config state from "pending", to "encrypting", and then "active".
-- The Encrypt config must be "active" for Proxy to use it.
SELECT cs_encrypt_v1(true);
SELECT cs_activate_v1();
