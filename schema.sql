-- Create database

CREATE DATABASE EnergyGrantsDB;
GO

USE EnergyGrantsDB;
GO

-- Homeowner table

CREATE TABLE Homeowner (
    homeowner_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    email NVARCHAR(50) NOT NULL,
    phone_number NVARCHAR(10) NULL,
    applicant_type NVARCHAR(50) NOT NULL
);

-- Poperty table

CREATE TABLE Property (
    property_id INT IDENTITY(1,1) PRIMARY KEY,
    homeowner_id INT NOT NULL,
    address_line1 NVARCHAR(50) NOT NULL,
    address_line2 NVARCHAR(50) NULL,
    town NVARCHAR(50) NOT NULL,
    county NVARCHAR(50) NOT NULL,
    eircode NVARCHAR(8) NOT NULL,
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    year_built INT NULL,
    ber_rating NVARCHAR(2) NULL,

    CONSTRAINT FK_Property_Homeowner
        FOREIGN KEY (homeowner_id)
        REFERENCES Homeowner(homeowner_id),

    CONSTRAINT UQ_Property_Eircode
        UNIQUE (eircode),

    CONSTRAINT CHK_Eircode_Format
        CHECK (
            eircode = UPPER(eircode)
            AND
            eircode LIKE '[A-Z][0-9][0-9] [A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]'
        ),

    CONSTRAINT CHK_BER_Rating
        CHECK (
            ber_rating IN (
                'A1','A2','A3',
                'B1','B2','B3',
                'C1','C2','C3',
                'D1','D2',
                'E1','E2',
                'F','G'
            )
        )
);

-- Grant type table

CREATE TABLE GrantType (
    grant_id INT IDENTITY(1,1) PRIMARY KEY,
    grant_name NVARCHAR(50) NOT NULL,
    category NVARCHAR(50) NOT NULL,
    max_amount DECIMAL(10,2) NOT NULL
);

-- Application table

CREATE TABLE Application (
    application_id INT IDENTITY(1,1) PRIMARY KEY,
    property_id INT NOT NULL,
    application_date DATE NOT NULL,
    status NVARCHAR(50) NOT NULL,

    CONSTRAINT FK_Application_Property
        FOREIGN KEY (property_id)
        REFERENCES Property(property_id)
);

-- Application Grant table (Junction table)
-- JUNCTION TABLE FOR MANY-TO-MANY RELATIONSHIP

CREATE TABLE Application_Grant (
    application_id INT NOT NULL,
    grant_id INT NOT NULL,
    requested_amount DECIMAL(10,2) NOT NULL,
    approved_amount DECIMAL(10,2) NULL,

    PRIMARY KEY (application_id, grant_id),

    CONSTRAINT FK_ApplicationGrant_Application
        FOREIGN KEY (application_id)
        REFERENCES Application(application_id),

    CONSTRAINT FK_ApplicationGrant_Grant
        FOREIGN KEY (grant_id)
        REFERENCES GrantType(grant_id)
);

-- Contractor table

CREATE TABLE Contractor (
    contractor_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    email NVARCHAR(50) NOT NULL,
    phone_number NVARCHAR(20) NULL,
    registration_status NVARCHAR(50) NOT NULL
);

-- Work table

CREATE TABLE Work (
    work_id INT IDENTITY(1,1) PRIMARY KEY,
    application_id INT NOT NULL,
    contractor_id INT NOT NULL,
    work_status NVARCHAR(50) NOT NULL,
    start_date DATE NULL,
    completion_date DATE NULL,

    CONSTRAINT FK_Work_Application
        FOREIGN KEY (application_id)
        REFERENCES Application(application_id),

    CONSTRAINT FK_Work_Contractor
        FOREIGN KEY (contractor_id)
        REFERENCES Contractor(contractor_id)
);
