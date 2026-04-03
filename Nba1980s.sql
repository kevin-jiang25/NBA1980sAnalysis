/*USE nba_1980s;
CREATE TABLE PerGame (
    Season VARCHAR(9),
    Player VARCHAR(255),
    Pos VARCHAR(10),
    Age INT,
    Tm VARCHAR(10),
    G INT,
    GS INT,
    MP FLOAT,
    FG FLOAT,
    FGA FLOAT,
    FG% DECIMAL (5, 2),
    3P FLOAT,
    3PA FLOAT,
    3P% DECIMAL (5, 2),
    TwoP FLOAT,
    TwoPA FLOAT,
    2P% DECIMAL (5, 2),
    eFG% DECIMAL (5, 2),
    FT FLOAT,
    FTA FLOAT,
    FT% DECIMAL (5, 2),
    ORB FLOAT,
    DRB FLOAT,
    TRB FLOAT,
    AST FLOAT,
    STL FLOAT,
    BLK FLOAT,
    TOV FLOAT,
    PF FLOAT,
    PTS FLOAT,
    PRIMARY KEY (Player, Tm, Season)
);
CREATE TABLE Totals (
    Season VARCHAR(9),
    Player VARCHAR(255),
    Pos VARCHAR(10),
    Age INT,
    Tm VARCHAR(10),
    G INT,
    GS INT,
    MP FLOAT,
    FG FLOAT,
    FGA FLOAT,
    FG% DECIMAL(5, 2),
    3P FLOAT,
    3PA FLOAT,
    3P% DECIMAL(5, 2),
    2P FLOAT,
    2PA FLOAT,
    2P% DECIMAL(5, 2),
    eFG% DECIMAL(5, 2),
    FT FLOAT,
    FTA FLOAT,
    FT% DECIMAL(5, 2),
    ORB FLOAT,
    DRB FLOAT,
    TRB FLOAT,
    AST FLOAT,
    STL FLOAT,
    BLK FLOAT,
    TOV FLOAT,
    PF FLOAT,
    PTS FLOAT,
    PRIMARY KEY (Player, Tm, Season)
);

CREATE TABLE AdvancedStats (
    Season VARCHAR(9),
    Player VARCHAR(255),
    Pos VARCHAR(10),
    Age INT,
    Tm VARCHAR(10),
    G INT,
    MP INT,
    PER DECIMAL(5, 2),
    TS% DECIMAL(5, 3),
    ThreePAr DECIMAL(5, 3),
    FTr DECIMAL(5, 3),
    ORB% DECIMAL(5, 2),
    DRB% DECIMAL(5, 2),
    TRB% DECIMAL(5, 2),
    AST% DECIMAL(5, 2),
    STL% DECIMAL(5, 2),
    BLK% DECIMAL(5, 2),
    TOV% DECIMAL(5, 2),
    USG% DECIMAL(5, 2),
    OWS DECIMAL(5, 2),
    DWS DECIMAL(5, 2),
    WS DECIMAL(5, 2),
    WSPer48 DECIMAL(5, 3),
    OBPM DECIMAL(5, 2),
    DBPM DECIMAL(5, 2),
    BPM DECIMAL(5, 2),
    VORP DECIMAL(5, 2),
    PRIMARY KEY (Player, Tm, Season)
);

There was an error with importing FG%, FT% and 3P% for the PerGame table, I'll manually calculate their FT% and 3P%  below.  
 SET SQL_SAFE_UPDATES = 0;
 UPDATE PerGame
SET `FT%` = CASE
              WHEN `FTA` = 0 THEN 0
              ELSE `FT`/`FTA`
            END;
UPDATE PerGame
SET `3P%` = CASE
              WHEN `3PA` = 0 THEN 0
              ELSE `3P`/`3PA`
            END;
Same FT% issue with Totals table
UPDATE Totals
SET `FT%` = CASE
              WHEN `FTA` = 0 THEN 0
              ELSE `FT`/`FTA`
            END;
SET SQL_SAFE_UPDATES = 1;
*/ 
SELECT(*) FROM PerGame WHERE Season = '1989-1990';
































