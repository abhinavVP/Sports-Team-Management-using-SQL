CREATE DATABASE IF NOT EXISTS sports_team_db;
USE sports_team_db;

CREATE TABLE IF NOT EXISTS coaches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    position ENUM('Forward', 'Midfielder', 'Defender', 'Goalkeeper') NOT NULL
);

CREATE TABLE IF NOT EXISTS injuries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    player_username VARCHAR(50) NOT NULL,
    injury_name VARCHAR(100),
    recovery_time INT,
    FOREIGN KEY (player_id) REFERENCES players(id)
);

drop table schedules;

INSERT INTO coaches (username, password)
VALUES 
('carlo', 'password123'), 
('zidane', 'password456');

CREATE TABLE IF NOT EXISTS matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type ENUM('Match', 'Training') NOT NULL,
    opponents VARCHAR(255) DEFAULT NULL,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL
);

DELIMITER //

CREATE TRIGGER before_injury_update
BEFORE UPDATE ON injuries
FOR EACH ROW
BEGIN
    DECLARE player_exists INT;

    
    SELECT COUNT(*) INTO player_exists
    FROM players
    WHERE username = NEW.player_username;  

    
    IF player_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Player username does not exist.';
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE FUNCTION get_player_status(player_id INT)
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
    DECLARE status VARCHAR(10);
    IF EXISTS (SELECT 1 FROM injuries WHERE player_id = player_id) THEN
        SET status = 'Injured';
    ELSE
        SET status = 'Healthy';
    END IF;
    RETURN status;
END;
//

DELIMITER ;

DELIMITER //

CREATE FUNCTION count_events(event_type VARCHAR(10))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM matches WHERE event_type = event_type;
    RETURN total;
END;
//

DELIMITER ;
DELIMITER //

CREATE FUNCTION get_recovery_time(player_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE recovery INT;
    SELECT recovery_time INTO recovery FROM injuries WHERE player_id = player_id LIMIT 1;
    RETURN IFNULL(recovery, 0); -- Returns 0 if no injury is found
END;
//

DELIMITER ;








