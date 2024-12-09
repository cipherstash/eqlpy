--
-- Application-specific types
--

CREATE DOMAIN customers__encrypted_big_int AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'encrypted_big_int'
);

CREATE DOMAIN customers__is_citizen AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'is_citizen'
);

CREATE DOMAIN customers__start_date AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'start_date'
);

CREATE DOMAIN customers__weight AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'weight'
);

CREATE DOMAIN customers__age AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'age'
);

CREATE DOMAIN customers__encrypted_small_int AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'encrypted_small_int'
);

CREATE DOMAIN customers__name AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'name'
);

CREATE DOMAIN customers__extra_info AS cs_encrypted_v1
CHECK(
    VALUE#>>'{i,t}' = 'customers' AND
    VALUE#>>'{i,c}' = 'extra_info'
);
