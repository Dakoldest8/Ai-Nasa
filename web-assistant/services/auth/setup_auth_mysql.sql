CREATE DATABASE IF NOT EXISTS cards;
USE cards;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS tournament_players;
DROP TABLE IF EXISTS deck_cards;
DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS players;

SET FOREIGN_KEY_CHECKS = 1;

-- ========================
-- PLAYERS
-- ========================
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    age TINYINT UNSIGNED NOT NULL,
    region VARCHAR(100) NOT NULL,
    `rank` VARCHAR(50) NOT NULL,
    join_date DATE NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    CONSTRAINT chk_age CHECK (age BETWEEN 5 AND 120)
);

-- ========================
-- CARDS
-- ========================
CREATE TABLE cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    card_name VARCHAR(100) NOT NULL,
    card_type VARCHAR(50) NOT NULL,
    attribute VARCHAR(50) NOT NULL,
    stars TINYINT UNSIGNED,
    atk INT UNSIGNED,
    def INT UNSIGNED,
    description TEXT,
    rarity VARCHAR(50) NOT NULL,
    release_date DATE NOT NULL,
    CONSTRAINT chk_stars CHECK (stars IS NULL OR stars BETWEEN 0 AND 18)
);

-- ========================
-- TOURNAMENTS
-- ========================
CREATE TABLE tournaments (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    format VARCHAR(50) NOT NULL,
    prize_pool DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_players INT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT chk_dates CHECK (end_date >= start_date)
);

-- ========================
-- DECKS
-- ========================
CREATE TABLE decks (
    deck_id INT AUTO_INCREMENT PRIMARY KEY,
    deck_name VARCHAR(100) NOT NULL,
    player_id INT NOT NULL,
    theme VARCHAR(100) NOT NULL,
    creation_date DATE NOT NULL,
    format VARCHAR(50) NOT NULL,
    CONSTRAINT fk_decks_player
        FOREIGN KEY (player_id)
        REFERENCES players(player_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ========================
-- DECK_CARDS
-- ========================
CREATE TABLE deck_cards (
    deck_id INT NOT NULL,
    card_id INT NOT NULL,
    quantity TINYINT UNSIGNED NOT NULL DEFAULT 1,
    card_role VARCHAR(50),
    note TEXT,
    PRIMARY KEY (deck_id, card_id),
    CONSTRAINT chk_quantity CHECK (quantity BETWEEN 1 AND 60),
    CONSTRAINT fk_deck_cards_deck
        FOREIGN KEY (deck_id)
        REFERENCES decks(deck_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_deck_cards_card
        FOREIGN KEY (card_id)
        REFERENCES cards(card_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ========================
-- TOURNAMENT_PLAYERS
-- ========================
CREATE TABLE tournament_players (
    tournament_id INT NOT NULL,
    player_id INT NOT NULL,
    deck_id INT DEFAULT NULL,
    placement INT UNSIGNED,
    match_wins INT UNSIGNED NOT NULL DEFAULT 0,
    match_losses INT UNSIGNED NOT NULL DEFAULT 0,
    points INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (tournament_id, player_id),
    CONSTRAINT fk_tp_tournament
        FOREIGN KEY (tournament_id)
        REFERENCES tournaments(tournament_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_tp_player
        FOREIGN KEY (player_id)
        REFERENCES players(player_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_tp_deck
        FOREIGN KEY (deck_id)
        REFERENCES decks(deck_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);
