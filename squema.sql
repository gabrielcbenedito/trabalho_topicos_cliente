CREATE TABLE owners (
    owner_id    serial PRIMARY KEY,
    name        varchar(30) NOT NULL,
    last_name   varchar(50) NOT NULL
);

CREATE TABLE servers (
    server_id       serial PRIMARY KEY,
    owner_id        integer REFERENCES owners (owner_id) NOT NULL,
    ipv4            inet NOT NULL,
    port            integer DEFAULT 502,
    server_address  integer DEFAULT 1,
    device_name     varchar(30)
);

CREATE TABLE resources (
    res_id          serial PRIMARY KEY,
    server_id       integer REFERENCES servers (server_id) NOT NULL,
    address         integer,
    is_coil         boolean NOT NULL,
    read_only       boolean NOT NULL
);

CREATE TABLE coil_rw (
    op_id           serial PRIMARY KEY,
    res_id          integer REFERENCES resources (res_id) NOT NULL,
    function_code   integer NOT NULL,
    value           boolean NOT NULL,
    timestamp       timestamp NOT NULL
);

CREATE TABLE register_rw (
    op_id           serial PRIMARY KEY,
    res_id          integer REFERENCES resources (res_id) NOT NULL,
    function_code   integer NOT NULL,
    value           integer NOT NULL,
    timestamp       timestamp NOT NULL
);