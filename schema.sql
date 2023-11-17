CREATE TABLE character_votes (
	charID	INTEGER NOT NULL,
	for_votes	TEXT,
	against_votes	TEXT,
	PRIMARY KEY(charID)
);

CREATE TABLE charlist (
	charID	INTEGER NOT NULL UNIQUE,
	owner	TEXT,
	status	NUMERIC,
	name	TEXT,
	age	TEXT,
	gender	TEXT,
	abilities	TEXT,
	appearance	TEXT,
	species	TEXT,
	backstory	TEXT,
	personality	TEXT,
	prefilled	TEXT,
	misc	TEXT,
	PRIMARY KEY(charID)
);

CREATE TABLE deleted_chars (
	charID	INTEGER,
	owner	TEXT,
	status	TEXT,
	name	TEXT,
	age	TEXT,
	gender	TEXT,
	abilities	TEXT,
	appearance	TEXT,
	species	TEXT,
	backstory	TEXT,
	personality	TEXT,
	prefilled	TEXT,
	misc	TEXT
);

CREATE TABLE registering_chars (
	charID	INTEGER NOT NULL UNIQUE,
	owner	TEXT,
	status	NUMERIC,
	name	TEXT,
	age	TEXT,
	gender	TEXT,
	abilities	TEXT,
	appearance	TEXT,
	species	TEXT,
	backstory	TEXT,
	personality	TEXT,
	prefilled	TEXT,
	misc	TEXT,
	thread	INTEGER,
	PRIMARY KEY(charID)
);