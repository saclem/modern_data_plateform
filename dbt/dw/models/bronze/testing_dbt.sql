CREATE TABLE iceberg.warehouse.name_basics (
    id INTEGER,
    primaryName VARCHAR,
    birthYear VARCHAR,
    deathYear VARCHAR,
    primaryProfession VARCHAR,
    knownForTitles VARCHAR
)
WITH (
    external_location = 's3://warehouse/name_basics.tsv',
    format = 'TEXTFILE',
    field_delimiter = '\t'
);
