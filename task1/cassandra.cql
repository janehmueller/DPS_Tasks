-- Data Preparation for Science
CREATE KEYSPACE dps WITH REPLICATION = {
    'class' : 'SimpleStrategy',
    'replication_factor' : 3
};



CREATE TYPE dps.property (
    propertytype text,
    claimtype text,
    snaktype text,
    value text
);

CREATE TYPE dps.sitelink (
    site text,
    title text,
    badges list<text>
);

CREATE TABLE dps.wikidata (
    id text PRIMARY KEY,
    entitytype text,
    labels map<text, text>,
    descriptions map<text, text>,
    aliases map<text, frozen<list<text>>>,
    sitelinks map<text, frozen<sitelink>>,
    claims map<text, frozen<list<frozen<property>>>>
);
