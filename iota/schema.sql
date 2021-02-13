/*
 * (C) Copyright 2020 Tillmann Heidsieck
 *
 * SPDX-License-Identifier: MIT
 *
 */

DROP TABLE IF EXISTS versions;
DROP TABLE IF EXISTS tokens;

CREATE TABLE versions (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	version VARCHAR(128) NOT NULL
);
CREATE UNIQUE INDEX unique_version ON versions (version);

CREATE TABLE tokens (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	name VARCHAR(512) NOT NULL,
	token VARCHAR(512) NOT NULL,
	permissions VARCHAR(16)
);
CREATE UNIQUE INDEX unique_token_name ON tokens (name);
CREATE INDEX token ON tokens (token);

INSERT INTO tokens (name, token, permissions) VALUES ("admin", "$argon2id$v=19$m=65536,t=2,p=1$bUIXjfewRvbW7B1aEd+Mxw$Q3aeaari5GqwojBAlqVf0X0IyFcGzwrBPFqds5lmnWk", "arw");
