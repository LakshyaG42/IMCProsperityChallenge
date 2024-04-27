
-- @block
DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS PlaylistSong;
DROP TABLE IF EXISTS SongGenre;
DROP TABLE IF EXISTS Song;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Artist;

DROP TABLE IF EXISTS Playlist;

DROP TABLE IF EXISTS User;

DROP TABLE IF EXISTS Genre;

-- @block
CREATE TABLE Artist (
    ArtistID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Album (
    AlbumID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    ArtistID INT NOT NULL,
    ReleaseDate DATE NOT NULL,
    FOREIGN KEY (ArtistID) REFERENCES Artist(ArtistID),
    UNIQUE (Name, ArtistID)
);
CREATE TABLE Song (
    SongID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    ArtistID INT NOT NULL,
    AlbumID INT,
    ReleaseDate DATE,
    FOREIGN KEY (ArtistID) REFERENCES Artist(ArtistID),
    FOREIGN KEY (AlbumID) REFERENCES Album(AlbumID),
    UNIQUE (Title, ArtistID)
);

CREATE TABLE Genre (
    GenreID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE SongGenre (
    SongID INT NOT NULL,
    GenreID INT NOT NULL,
    PRIMARY KEY (SongID, GenreID),
    FOREIGN KEY (SongID) REFERENCES Song(SongID),
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
);

CREATE TABLE User (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Playlist (
    PlaylistID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    Title VARCHAR(255) NOT NULL,
    CreationDateTime DATETIME NOT NULL,
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    UNIQUE (UserID, Title)
);
CREATE TABLE PlaylistSong (
    PlaylistID INT NOT NULL,
    SongID INT NOT NULL,
    FOREIGN KEY (PlaylistID) REFERENCES Playlist(PlaylistID),
    FOREIGN KEY (SongID) REFERENCES Song(SongID)
);

CREATE TABLE Rating (
    RatingID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    RatedID INT NOT NULL,
    RatedType ENUM('song', 'album', 'playlist') NOT NULL,
    Score TINYINT CHECK (Score BETWEEN 1 AND 5) NOT NULL,
    RatingDate DATE NOT NULL,
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    UNIQUE (UserID, RatedID, RatedType)
);



--@block 
-- Populate Artist table
INSERT INTO Artist (Name) VALUES
('The Beatles'),
('Michael Jackson'),
('Taylor Swift'),
('Queen'),
('Eminem'),
('Adele'),
('Ed Sheeran'),
('Beyonce'),
('Coldplay'),
('Drake');

-- Populate Genre table
INSERT INTO Genre (Name) VALUES
('Rock'),
('Pop'),
('Hip Hop'),
('Country'),
('R&B'),
('Electronic'),
('Indie'),
('Jazz'),
('Classical'),
('Reggae');

-- Populate User table
INSERT INTO User (Username) VALUES
('musiclover1'),
('songbird22'),
('beatsmaster'),
('rhythmlover'),
('harmonizer'),
('melodymaker'),
('grooveseeker'),
('lyricist'),
('beatkeeper'),
('tunesmith');

-- Populate Album table
INSERT INTO Album (Name, ArtistID, ReleaseDate) VALUES
('Abbey Road', 1, '1969-09-26'),
('Thriller', 2, '1982-11-30'),
('1989', 3, '2014-10-27'),
('A Night at the Opera', 4, '1975-11-21'),
('The Marshall Mathers LP', 5, '2000-05-23'),
('21', 6, '2011-01-24'),
('Divide', 7, '2017-03-03'),
('Lemonade', 8, '2016-04-23'),
('X&Y', 9, '2005-06-06'),
('Take Care', 10, '2011-11-15');

-- Populate Song table
INSERT INTO Song (Title, ArtistID, AlbumID, ReleaseDate) VALUES
('Hey Jude', 1, 1, '1968-08-26'),
('Billie Jean', 2, 2, '1982-01-02'),
('Shake It Off', 3, 3, '2014-08-18'),
('Bohemian Rhapsody', 4, 4, '1975-10-31'),
('Lose Yourself', 5, NULL, '2002-10-28'),
('MockingBird', 5, 5, '2004-04-25'),
('Rolling in the Deep', 6, 6, '2010-11-29'),
('Shape of You', 7, 7, '2017-01-06'),
('Formation', 8, 8, '2016-04-23'),
('Fix You', 9, 9, '2005-06-06'),
('Hotline Bling', 10, 10, '2015-07-31');

-- Populate SongGenre table
INSERT INTO SongGenre (SongID, GenreID) VALUES
(1, 1), (1, 7), -- Hey Jude (Rock, Indie)
(2, 2), (2, 5), -- Billie Jean (Pop, R&B)
(3, 3), (3, 2), -- Shake It Off (Pop, Pop)
(4, 4), (4, 1), -- Bohemian Rhapsody (Rock, Rock)
(5, 5), (5, 3), -- Lose Yourself (Hip Hop, Hip Hop)
(6, 6), (6, 5), -- Rolling in the Deep (Pop, Electronic)
(7, 7), (7, 3), -- Shape of You (Pop, Hip Hop)
(8, 8), (8, 4), -- Formation (R&B, Country)
(9, 9), (9, 1), -- Fix You (Rock, Rock)
(10, 10), (10, 3); -- Hotline Bling (Hip Hop, Hip Hop)

-- Populate Playlist table
INSERT INTO Playlist (UserID, Title, CreationDateTime) VALUES
(1, 'Favorite Hits', '2022-04-10 09:00:00'),
(2, 'Chill Vibes', '2022-04-11 17:30:00'),
(3, 'Road Trip Mix', '2022-04-12 12:15:00'),
(4, 'Morning Melodies', '2022-04-13 08:45:00'),
(5, 'Party Playlist', '2022-04-14 21:00:00'),
(6, 'Study Tunes', '2022-04-15 14:00:00'),
(7, 'Workout Jams', '2022-04-16 07:30:00'),
(8, 'Relaxation Station', '2022-04-17 20:15:00'),
(9, 'Driving Beats', '2022-04-18 10:30:00'),
(10, 'Sleep Sounds', '2022-04-19 23:00:00');

-- Populate PlaylistSong table
INSERT INTO PlaylistSong (PlaylistID, SongID) VALUES
(1, 1), (1, 3), (1, 5), (1, 7), (1, 9), -- Favorite Hits
(2, 2), (2, 4), (2, 6), (2, 8), (2, 10), -- Chill Vibes
(3, 3), (3, 5), (3, 7), (3, 9), (3, 2), -- Road Trip Mix
(4, 4), (4, 4), (4, 4), (4, 4), (4, 4), -- Morning Melodies (Repeats for testing)
(5, 5), (5, 5), (5, 5), (5, 5), (5, 5), -- Party Playlist (Repeats for testing)
(6, 6), (6, 6), (6, 6), (6, 6), (6, 6), -- Study Tunes (Repeats for testing)
(7, 7), (7, 7), (7, 7), (7, 7), (7, 7), -- Workout Jams (Repeats for testing)
(8, 8), (8, 8), (8, 8), (8, 8), (8, 8), -- Relaxation Station (Repeats for testing)
(9, 9), (9, 9), (9, 9), (9, 9), (9, 9), -- Driving Beats (Repeats for testing)
(10, 10), (10, 10), (10, 10), (10, 10), (10, 10); -- Sleep Sounds (Repeats for testing)

-- Populate Rating table



-- @block
-- Query 1: 
SELECT g.Name AS genre, COUNT(sg.SongID) AS number_of_songs
FROM Genre g
JOIN SongGenre sg ON g.GenreID = sg.GenreID
GROUP BY g.GenreID
ORDER BY number_of_songs DESC
LIMIT 3;

-- @block
-- Query 2: 
SELECT DISTINCT a.Name AS artist_name
FROM Artist a
JOIN Song s ON a.ArtistID = s.ArtistID
WHERE EXISTS (
    SELECT 1 FROM Song WHERE ArtistID = s.ArtistID AND AlbumID IS NOT NULL
) AND EXISTS (
    SELECT 1 FROM Song WHERE ArtistID = s.ArtistID AND AlbumID IS NULL
);

-- @block
-- Query 3: 
SELECT al.Name AS album_name, AVG(r.Score) AS average_user_rating
FROM Album al
JOIN Rating r ON al.AlbumID = r.RatedID
WHERE r.RatingDate BETWEEN '1990-01-01' AND '1999-12-31' AND r.RatedType = 'album'
GROUP BY al.AlbumID
ORDER BY average_user_rating DESC, al.Name ASC
LIMIT 10;

-- @block
-- Query 4:
SELECT g.Name AS genre_name, COUNT(r.RatingID) AS number_of_song_ratings
FROM Genre g
JOIN SongGenre sg ON g.GenreID = sg.GenreID
JOIN Song s ON sg.SongID = s.SongID
JOIN Rating r ON s.SongID = r.RatedID
WHERE r.RatingDate BETWEEN '1991-01-01' AND '1995-12-31'
GROUP BY g.GenreID
ORDER BY number_of_song_ratings DESC
LIMIT 3;


-- @block
-- Query 5:
-- SELECT u.Username, p.Title AS playlist_title, AVG(r.Score) AS average_song_rating
-- FROM User u
-- JOIN Playlist p ON u.UserID = p.UserID
-- JOIN PlaylistSong ps ON p.PlaylistID = ps.PlaylistID
-- JOIN Rating r ON ps.SongID = r.RatedID
-- WHERE r.RatedType = 'song'
-- GROUP BY p.PlaylistID
-- HAVING average_song_rating >= 4.0;

SELECT u.Username, p.Title AS playlist_title, AVG(song_avg_rating.rating) AS average_song_rating
FROM User u
JOIN Playlist p ON u.UserID = p.UserID
JOIN PlaylistSong ps ON p.PlaylistID = ps.PlaylistID
JOIN (
    SELECT ps.SongID, AVG(r.Score) AS rating
    FROM PlaylistSong ps
    JOIN Rating r ON ps.SongID = r.RatedID
    WHERE r.RatedType = 'song'
    GROUP BY ps.SongID
) AS song_avg_rating ON ps.SongID = song_avg_rating.SongID
GROUP BY u.UserID, p.PlaylistID
HAVING average_song_rating >= 4.0;


-- @block
-- Query 6:
SELECT u.Username, COUNT(r.RatingID) AS number_of_ratings
FROM User u
JOIN Rating r ON u.UserID = r.UserID
WHERE r.RatedType IN ('song', 'album')
GROUP BY u.UserID
ORDER BY number_of_ratings DESC
LIMIT 5;


-- @block
-- Query 7:


SELECT a.Name AS artist_name, COUNT(s.SongID) AS number_of_songs
FROM Artist a
JOIN Song s ON a.ArtistID = s.ArtistID
WHERE (s.ReleaseDate BETWEEN '1990-01-01' AND '2010-12-31' OR s.AlbumID IN (SELECT AlbumID FROM Album WHERE ReleaseDate BETWEEN '1990-01-01' AND '2010-12-31'))
GROUP BY a.ArtistID
ORDER BY number_of_songs DESC
LIMIT 10;

-- @block
-- Query 8: 

SELECT s.Title AS song_title, COUNT(DISTINCT ps.PlaylistID) AS number_of_playlists
FROM Song s
JOIN PlaylistSong ps ON s.SongID = ps.SongID
GROUP BY s.SongID
ORDER BY number_of_playlists DESC, s.Title ASC
LIMIT 10;



-- @block
-- Query 9:
SELECT s.Title AS song_title, a.Name AS artist_name, COUNT(r.RatingID) AS number_of_ratings
FROM Song s
JOIN Artist a ON s.ArtistID = a.ArtistID
JOIN Rating r ON s.SongID = r.RatedID
WHERE s.AlbumID IS NULL
GROUP BY s.SongID
ORDER BY number_of_ratings DESC
LIMIT 20;


-- @block
-- Query 10: 

SELECT a.Name AS artist_title
FROM Artist a
WHERE NOT EXISTS (
    SELECT 1 FROM Song s WHERE s.ArtistID = a.ArtistID AND s.ReleaseDate > '1993-12-31'
);

-- @block

-- ADDITIONAL DATA:
-- Populate Artist table with additional artists
INSERT INTO Artist (Name) VALUES
('Ariana Grande'),
('Kanye West'),
('Lady Gaga'),
('Justin Bieber'),
('Bruno Mars');

-- Populate Genre table with additional genres
INSERT INTO Genre (Name) VALUES
('Alternative'),
('Funk'),
('Soul'),
('Metal'),
('Blues');

-- Populate Album table with more albums for existing artists
INSERT INTO Album (Name, ArtistID, ReleaseDate) VALUES
('Sweetener', 11, '2018-08-17'),
('Yeezus', 12, '2013-06-18'),
('Born This Way', 13, '2011-05-23'),
('Purpose', 14, '2015-11-13'),
('24K Magic', 15, '2016-11-18');

-- Populate Song table with more songs from existing and new artists
INSERT INTO Song (Title, ArtistID, AlbumID, ReleaseDate) VALUES
('God is a Woman', 11, 11, '2018-07-13'),
('Stronger', 12, 12, '2013-05-15'),
('Bad Romance', 13, 13, '2010-10-28'),
('Sorry', 14, 14, '2015-10-23'),
('24K Magic', 15, 15, '2016-10-07'),
('No Tears Left to Cry', 11, 11, '2018-04-20'),
('Power', 12, 12, '2013-06-04'),
('Poker Face', 13, 13, '2008-09-26'),
('Love Yourself', 14, 14, '2015-11-09'),
('Thats What I Like', 15, 15, '2016-11-18');

-- Populate more songs (singles) for existing and new artists
INSERT INTO Song (Title, ArtistID, AlbumID, ReleaseDate) VALUES
('Love Me Harder', 11, NULL, '2014-09-30'), -- Ariana Grande
('Heartless', 12, NULL, '2008-11-04'), -- Kanye West
('Born This Way', 13, NULL, '2011-02-11'), -- Lady Gaga
('Locked Out of Heaven', 15, NULL, '2012-10-01'), -- Bruno Mars
('Into You', 11, NULL, '2016-05-06'), -- Ariana Grande
('Gold Digger', 12, NULL, '2005-07-05'), -- Kanye West
('What Do You Mean?', 14, NULL, '2015-08-28'), -- Justin Bieber
('Uptown Funk', 15, NULL, '2014-11-10'); -- Bruno Mars

-- Populate more randomized playlists for existing users with new songs
INSERT INTO Playlist (UserID, Title, CreationDateTime) VALUES
(1, 'Throwback Jams', '2022-04-20 12:00:00'),
(2, 'Feel Good Mix', '2022-04-21 18:30:00'),
(3, 'Summer Vibes', '2022-04-22 10:45:00'),
(4, 'Night Owl Playlist', '2022-04-23 23:15:00'),
(5, 'Relax and Chill', '2022-04-24 15:30:00');


-- Populate PlaylistSong table with new songs for existing playlists without duplicates
-- Playlist: Throwback Jams
INSERT INTO PlaylistSong (PlaylistID, SongID) VALUES
(11, 1), (11, 3), (11, 5), (11, 7), (11, 9), (11, 11), -- Favorite Hits + Ariana Grande songs
(12, 2), (12, 4), (12, 6), (12, 8), (12, 10), (12, 12), -- Chill Vibes + Kanye West songs
(13, 3), (13, 5), (13, 7), (13, 9), (13, 2), (13, 14), -- Road Trip Mix + Lady Gaga and Justin Bieber songs
(14, 4), (14, 6), (14, 8), (14, 10), (14, 12), (14, 15), -- Morning Melodies + Bruno Mars songs
(15, 5), (15, 7), (15, 9), (15, 2), (15, 14), (15, 1); -- Party Playlist + Justin Bieber and The Beatles songs

-- Populate Rating table with more ratings for existing and new songs/albums
INSERT INTO Rating (UserID, RatedID, RatedType, Score, RatingDate) VALUES
(1, 1, 'song', 5, '1992-04-10'), -- Hey Jude
(3, 3, 'playlist', 3, '1992-04-12'), -- Road Trip Mix
(4, 4, 'song', 2, '1992-04-13'), -- Bohemian Rhapsody
(6, 6, 'playlist', 5, '1992-04-15'), -- Study Tunes
(7, 7, 'song', 4, '1992-04-16'), -- Shape of You
(9, 9, 'playlist', 2, '1992-04-18'), -- Driving Beats
(10, 10, 'song', 1, '1992-04-19'), -- Hotline Bling
(1, 11, 'song', 4, '1992-04-20'), -- God is a Woman
(2, 12, 'song', 5, '1992-04-21'), -- Stronger
(3, 13, 'song', 3, '1992-04-22'), -- Bad Romance
(4, 14, 'song', 2, '1992-04-23'), -- Sorry
(5, 15, 'song', 4, '1992-04-24'), -- 24K Magic
(6, 16, 'song', 5, '1992-04-25'), -- Love Me Harder
(7, 17, 'song', 4, '1992-04-26'), -- Heartless
(8, 18, 'song', 3, '1992-04-27'), -- Born This Way
(9, 19, 'song', 5, '1992-04-28'), -- Sorry
(10, 20, 'song', 4, '1992-04-29'), -- 24K Magic
(1, 1, 'album', 4, '1992-04-30'), -- Abbey Road
(2, 2, 'album', 5, '1992-05-01'), -- Thriller
(3, 3, 'album', 3, '1992-05-02'), -- 1989
(4, 4, 'album', 2, '1992-05-03'), -- A Night at the Opera
(5, 5, 'album', 5, '1992-05-04'), -- The Marshall Mathers LP
(6, 6, 'album', 4, '1992-05-05'), -- 21
(7, 7, 'album', 5, '1992-05-06'), -- Divide
(8, 8, 'album', 3, '1992-05-07'), -- Lemonade
(9, 9, 'album', 2, '1992-05-08'), -- X&Y
(10, 10, 'album', 5, '1992-05-09'); -- Take Care

-- @block
INSERT INTO Playlist (UserID, Title, CreationDateTime) VALUES
(5, 'Throwback Jams', '2022-04-20 12:00:00');


-- @block
INSERT INTO Rating (UserID, RatedID, RatedType, Score, RatingDate) VALUES
(1, 22, 'song', 5, '1992-04-10'), 
(3, 22, 'playlist', 3, '1992-04-12'), 
(4, 22, 'song', 2, '1992-04-13'),
(6, 22, 'playlist', 5, '1992-04-15'),
(7, 22, 'song', 4, '1992-04-16'), 
(1, 23, 'song', 5, '1992-04-10'), 
(3, 23, 'playlist', 3, '1992-04-12'), 
(4, 24, 'song', 2, '1992-04-13'),
(6, 24, 'playlist', 5, '1992-04-15'),
(7, 24, 'song', 4, '1992-04-16'), 
(1, 25, 'song', 5, '1992-04-10'), 
(3, 25, 'playlist', 3, '1992-04-12'), 
(4, 26, 'song', 2, '1992-04-13'),
(6, 27, 'playlist', 5, '1992-04-15'),
(7, 29, 'song', 4, '1992-04-16');


-- @block

INSERT INTO Rating (UserID, RatedID, RatedType, Score, RatingDate) VALUES
(1, 8, 'song', 5, '1992-04-10'), 
(4, 8, 'song', 5, '1992-04-13'),
(7, 8, 'song', 5, '1992-04-16'), 
(3, 8, 'song', 5, '1992-04-12'), 
(6, 8, 'song', 5, '1992-04-15');


-- @block
INSERT INTO Rating (UserID, RatedID, RatedType, Score, RatingDate) VALUES
-- User 8 ratings
(8, 1, 'song', 5, '2022-04-10'), -- Hey Jude
(8, 3, 'song', 5, '2022-04-10'), -- Shake It Off
(8, 5, 'song', 5, '2022-04-10'), -- Lose Yourself
(8, 7, 'song', 5, '2022-04-10'), -- Shape of You
(8, 9, 'song', 5, '2022-04-10'), -- Fix You
(8, 11, 'song', 5, '2022-04-10'), -- Ariana Grande song
-- User 9 ratings
(9, 2, 'song', 5, '2022-04-11'), -- Billie Jean
(9, 4, 'song', 5, '2022-04-11'), -- Bohemian Rhapsody
(9, 6, 'song', 5, '2022-04-11'), -- Rolling in the Deep
(9, 8, 'song', 5, '2022-04-11'), -- Formation
(9, 10, 'song', 5, '2022-04-11'), -- Hotline Bling
(9, 12, 'song', 5, '2022-04-11'), -- Kanye West song
-- User 10 ratings
(10, 3, 'song', 5, '2022-04-12'), -- Shake It Off
(10, 5, 'song', 5, '2022-04-12'), -- Lose Yourself
(10, 7, 'song', 5, '2022-04-12'), -- Shape of You
(10, 9, 'song', 5, '2022-04-12'), -- Fix You
(10, 2, 'song', 5, '2022-04-12'), -- Billie Jean
(10, 14, 'song', 5, '2022-04-12'); -- Lady Gaga song