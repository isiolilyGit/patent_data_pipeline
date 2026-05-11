-- PATENT DATA PIPELINE FULL SQL SCRIPT

-- 1. CREATE DATABASE

DROP TABLE IF EXISTS patent_relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

-- PATENTS
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    filing_date DATE,
    year INTEGER
);

-- INVENTORS
CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT
);

-- COMPANIES
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT
);

-- RELATIONSHIPS
CREATE TABLE patent_relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT,

    FOREIGN KEY (patent_id)
        REFERENCES patents(patent_id),

    FOREIGN KEY (inventor_id)
        REFERENCES inventors(inventor_id),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
);