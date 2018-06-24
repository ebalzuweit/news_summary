BEGIN TRANSACTION;
DROP TABLE IF EXISTS `Sources`;
CREATE TABLE IF NOT EXISTS `Sources` (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Name`	TEXT,
	`Link`	TEXT,
	`RSS`	TEXT,
	`Text_Element`	TEXT,
	`Text_Class`	TEXT,
	`Text_Class_Fallback`	TEXT,
	`Date_Format`	TEXT
);
INSERT INTO `Sources` (ID,Name,Link,RSS,Text_Element,Text_Class,Text_Class_Fallback,Date_Format) VALUES (1,'The New York Times','https://nytimes.com','http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml','p','story-body-text story-content','css-1i0edl6 e2kc3sl0','%a, %d %b %Y %H:%M:%S %Z');
DROP TABLE IF EXISTS `Articles`;
CREATE TABLE IF NOT EXISTS `Articles` (
	`Source`	INTEGER NOT NULL,
	`Title`	TEXT,
	`Published`	TEXT,
	`Link`	TEXT,
	`Summary`	TEXT,
	`Summary_Score`	REAL
);
COMMIT;
