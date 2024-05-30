-- Script for creating database:
CREATE TABLE tblBotChat (
    IDNUM bigint NOT NULL IDENTITY(1,1),
    ChatId nvarchar(255) NOT NULL,
    ChatHistory text NULL,
    updated_date datetime NULL,
    PRIMARY KEY (IDNUM)
);

-- Script for additional column creation

ALTER TABLE [dbo].[tblBotChat]
ADD intent varchar(255),
dialogId varchar(255),
rating INTEGER,
query_summary TEXT,
query_category varchar(255);
query_type_is_defined BIT;

-- Script for additional of country, language and domain

ALTER TABLE [dbo].[tblBotChat]
ADD language varchar(255),
country varchar(255),
domain varchar(255);