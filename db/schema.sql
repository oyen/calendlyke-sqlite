DROP TABLE IF EXISTS Users;

DROP TABLE IF EXISTS Schedules;

CREATE TABLE Users (
    [UserId] INTEGER ,
    [Created] TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    [Name] TEXT NOT NULL,
    [Email] TEXT NOT NULL,
    CONSTRAINT [pk_Users_UserId] PRIMARY KEY ([UserId])
);

CREATE TABLE Schedules (
    [UserId] INTEGER NOT NULL,
    [Date] TEXT NOT NULL,
    [Time] TEXT NOT NULL,
    [Name] TEXT NOT NULL,
    [Email] TEXT NOT NULL,
    [Phone] TEXT NOT NULL,
    [Notes] TEXT NOT NULL,
    [isFree] INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT [pk_Schedules_UserId_Date_Time] PRIMARY KEY ([UserId], [Date], [Time]),
    CONSTRAINT [fk_Schedules_UserId_Users_UserId] FOREIGN KEY ([UserId]) REFERENCES [Users]([UserId])
);
