-- Astronaut AI Ecosystem - MySQL Database Setup Script
-- Import this file into MySQL Workbench or run: mysql -u root -p < setup_auth_mysql.sql

CREATE DATABASE IF NOT EXISTS nasa_ai_system;
USE nasa_ai_system;

-- 1. Users: Centralized authentication for Robot and Web App
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('astronaut', 'general_user', 'admin') DEFAULT 'astronaut',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Notes: Session-specific memory for cognitive stimulation
CREATE TABLE IF NOT EXISTS notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100),
    content TEXT,
    is_private BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Reminders: Daily task management
CREATE TABLE IF NOT EXISTS reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    task_description TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    reminder_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Agent Interactions: Logs for Nutrition, Fitness, and Mental Health
CREATE TABLE IF NOT EXISTS agent_interactions (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    agent_type ENUM('mental_health', 'nutrition', 'fitness', 'robot_general') NOT NULL,
    user_input TEXT,
    ai_response TEXT,
    sentiment_score FLOAT,
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Federated Learning: Tracking model update metadata
CREATE TABLE IF NOT EXISTS federated_updates (
    update_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50),
    model_version VARCHAR(20),
    update_path VARCHAR(255),
    status ENUM('pending', 'aggregated', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert test user (password: test123)
-- SHA256 hash of "test123": ecd71870d1963316a97e3ac3408169f6f2c007ad0f81bed599b62fef7ad67b6
INSERT IGNORE INTO users (username, password_hash, role)
VALUES ('testuser', 'ecd71870d1963316a97e3ac3408169f6f2c007ad0f81bed599b62fef7ad67b6', 'astronaut');

-- Verify setup
SELECT 'Database setup complete!' AS Status;
SELECT COUNT(*) AS total_users FROM users;
SELECT user_id, username, role FROM users;

-- Create application user for security (optional)
-- Uncomment below to create a limited user instead of using root
-- CREATE USER IF NOT EXISTS 'astronaut'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE ON nasa_ai_system.* TO 'astronaut'@'localhost';
-- FLUSH PRIVILEGES;
