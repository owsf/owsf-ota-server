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
	permissions VARCHAR(16) NOT NULL
);
CREATE UNIQUE INDEX unique_token_name ON tokens (name);
CREATE INDEX token ON tokens (token);
