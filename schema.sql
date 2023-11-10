CREATE TABLE "charlist" (
	"charID"	INTEGER NOT NULL UNIQUE,
	"owner"	TEXT NOT NULL,
	"status"	NUMERIC NOT NULL,
	"name"	TEXT NOT NULL,
	"age"	TEXT,
	"gender"	TEXT,
	"abilities"	TEXT,
	"appearance"	TEXT,
	"species"	TEXT,
	"backstory"	TEXT,
	"personality"	TEXT,
	"prefilled"	TEXT,
	"misc"	TEXT,
	PRIMARY KEY("charID")
)

CREATE TABLE "deleted_chars" (
	"charID"	INTEGER,
	"owner"	TEXT,
	"status"	TEXT,
	"name"	TEXT,
	"age"	TEXT,
	"gender"	TEXT,
	"abilities"	TEXT,
	"appearance"	TEXT,
	"species"	TEXT,
	"backstory"	TEXT,
	"personality"	TEXT,
	"prefilled"	TEXT,
	"misc"	TEXT
)