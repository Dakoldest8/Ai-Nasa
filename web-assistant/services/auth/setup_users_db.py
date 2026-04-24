import mysql.connector
from mysql.connector import Error
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root and web-assistant folder (web-assistant overrides root)
THIS_FILE = Path(__file__).resolve()
ROOT_ENV = THIS_FILE.parents[3] / ".env"
WEB_ENV = THIS_FILE.parents[2] / ".env"
load_dotenv(ROOT_ENV)
load_dotenv(WEB_ENV, override=True)

# MySQL Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "nasa_ai_system")
DB_PORT = int(os.getenv("DB_PORT", 3306))

try:
    # Connect to MySQL server (without database first)
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cur = conn.cursor()
    
    # Create database if it doesn't exist
    print(f"[SETUP] Creating database '{DB_NAME}' if not exists...")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    print(f"[SETUP] Database '{DB_NAME}' ready.")
    
    # Create users table
    print("[SETUP] Creating users table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('astronaut', 'general_user', 'admin') DEFAULT 'astronaut',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_username (username)
    )
    """)
    print("[SETUP] Users table created.")

    print("[SETUP] Creating notes table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        note_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(100),
        content TEXT,
        is_private BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)

    print("[SETUP] Creating reminders table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        reminder_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        task_description TEXT NOT NULL,
        is_completed BOOLEAN DEFAULT FALSE,
        reminder_time DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)

    print("[SETUP] Creating agent_interactions table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_interactions (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        agent_type ENUM('mental_health', 'nutrition', 'fitness', 'robot_general') NOT NULL,
        user_input TEXT,
        ai_response TEXT,
        sentiment_score FLOAT,
        interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """)

    print("[SETUP] Creating federated_updates table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS federated_updates (
        update_id INT AUTO_INCREMENT PRIMARY KEY,
        device_id VARCHAR(50),
        model_version VARCHAR(20),
        update_path VARCHAR(255),
        status ENUM('pending', 'aggregated', 'failed') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    print("[SETUP] Creating reading_activities table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reading_activities (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        book_title VARCHAR(255) NOT NULL,
        duration_minutes INT DEFAULT 0,
        start_time DATETIME,
        end_time DATETIME,
        progress_percent FLOAT,
        mood_tag VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        INDEX idx_user_time (user_id, start_time)
    )
    """)
    
    # Create default users
    print("[SETUP] Creating default users...")
    default_users = [
        ("testuser", "test123", "astronaut"),
        ("admin", "admin123", "admin")
    ]

    for username, plain_password, role in default_users:
        pw_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, pw_hash, role)
            )
            print(f"[SETUP] User created: {username} / {plain_password} ({role})")
        except mysql.connector.Error as e:
            if "Duplicate entry" in str(e):
                print(f"[SETUP] User already exists, skipping: {username}")
            else:
                raise
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✓ MySQL Database Setup Complete!")
    print("="*50)
    print(f"Database: {DB_NAME}")
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print("Default Users:")
    print(" - testuser / test123 (astronaut)")
    print(" - admin / admin123 (admin)")
    print("="*50)

except Error as e:
    print(f"[ERROR] Database setup failed: {e}")
    print("\nPlease ensure:")
    print("1. MySQL Server is running")
    print("2. Credentials are correct in .env file")
    print("3. You have permission to create databases")
    exit(1)
