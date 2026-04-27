CREATE DATABASE IF NOT EXISTS nasa_ai_system;
USE nasa_ai_system;

-- 1. Users: Centralized authentication for Robot & Web App
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('astronaut', 'general_user', 'admin') DEFAULT 'astronaut',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Notes: Session-specific memory for cognitive stimulation
CREATE TABLE IF NOT EXISTS notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100),
    content TEXT,
    is_private BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Reminders: Daily task management
CREATE TABLE IF NOT EXISTS reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    task_description TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    reminder_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Agent Interactions: Logs for Nutrition, Fitness, and Mental Health
CREATE TABLE IF NOT EXISTS agent_interactions (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    agent_type ENUM('mental_health', 'nutrition', 'fitness', 'robot_general') NOT NULL,
    user_input TEXT,
    ai_response TEXT,
    sentiment_score FLOAT, -- Critical for tracking mental health trends
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Federated Learning: Tracking model update metadata
CREATE TABLE IF NOT EXISTS federated_updates (
    update_id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50), -- e.g., 'Raspberry_Pi_Robot' or 'Astronaut_Web_App'
    model_version VARCHAR(20),
    update_path VARCHAR(255), -- Path to local encrypted weights file
    status ENUM('pending', 'aggregated', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ===========================================
-- PHASE 2: MySQL Brain Integration Tables
-- ===========================================

-- 6. Models: Track all trained model versions
CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version INT NOT NULL UNIQUE,
    file_name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    training_interactions INT DEFAULT 0,
    base_model VARCHAR(100),
    status ENUM('training', 'completed', 'exported', 'failed') DEFAULT 'training'
) ENGINE=InnoDB;

-- 7. Interactions: Store all AI interactions for training data
CREATE TABLE IF NOT EXISTS interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source ENUM('web_assistant', 'pi_robot') DEFAULT 'web_assistant',
    user_id INT,
    input TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment_score FLOAT,
    agent_type VARCHAR(50),
    used_for_training BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. System State: Track current system status and triggers
CREATE TABLE IF NOT EXISTS system_state (
    id INT PRIMARY KEY DEFAULT 1,
    last_model_version INT DEFAULT 0,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_interactions INT DEFAULT 0,
    pending_training BOOLEAN DEFAULT FALSE,
    last_training_trigger DATETIME,
    system_status ENUM('active', 'training', 'updating', 'error') DEFAULT 'active'
) ENGINE=InnoDB;

-- Initialize system state
INSERT IGNORE INTO system_state (id) VALUES (1);

-- ===========================================
-- PHASE 2: MySQL Brain Integration Tables
-- ===========================================

-- 6. Models: Track all trained model versions
CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version INT NOT NULL UNIQUE,
    file_name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    training_interactions INT DEFAULT 0,
    base_model VARCHAR(100),
    status ENUM('training', 'completed', 'exported', 'failed') DEFAULT 'training'
) ENGINE=InnoDB;

-- 7. Interactions: Store all AI interactions for training data
CREATE TABLE IF NOT EXISTS interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source ENUM('web_assistant', 'pi_robot') DEFAULT 'web_assistant',
    user_id INT,
    input TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment_score FLOAT,
    agent_type VARCHAR(50),
    used_for_training BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 8. System State: Track current system status and triggers
CREATE TABLE IF NOT EXISTS system_state (
    id INT PRIMARY KEY DEFAULT 1,
    last_model_version INT DEFAULT 0,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_interactions INT DEFAULT 0,
    pending_training BOOLEAN DEFAULT FALSE,
    last_training_trigger DATETIME,
    system_status ENUM('active', 'training', 'updating', 'error') DEFAULT 'active'
) ENGINE=InnoDB;

-- Initialize system state
INSERT IGNORE INTO system_state (id) VALUES (1);
