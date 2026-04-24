# Phase 2: MySQL Brain Integration

This phase introduces MySQL as the "brain" of the system, tracking all interactions and model versions for intelligent decision making.

## Overview

The database integration consists of three main components:

1. **Database Connection** (`connection.py`) - MySQL connection management
2. **Interaction Logger** (`interaction_logger.py`) - Logs all AI conversations
3. **Model Tracker** (`model_tracker.py`) - Tracks model versions and training history

## Database Schema

Phase 2 adds three core tables to your existing schema:

```sql
-- Models: Track all trained model versions
CREATE TABLE models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version INT NOT NULL UNIQUE,
    file_name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    training_interactions INT DEFAULT 0,
    base_model VARCHAR(100),
    status ENUM('training', 'completed', 'exported', 'failed') DEFAULT 'training'
);

-- Interactions: Store all AI interactions for training data
CREATE TABLE interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source ENUM('web_assistant', 'pi_robot') DEFAULT 'web_assistant',
    user_id INT,
    input TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment_score FLOAT,
    agent_type VARCHAR(50),
    used_for_training BOOLEAN DEFAULT FALSE
);

-- System State: Track current system status and triggers
CREATE TABLE system_state (
    id INT PRIMARY KEY DEFAULT 1,
    last_model_version INT DEFAULT 0,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_interactions INT DEFAULT 0,
    pending_training BOOLEAN DEFAULT FALSE,
    last_training_trigger DATETIME,
    system_status ENUM('active', 'training', 'updating', 'error') DEFAULT 'active'
);
```

## Setup

### 1. Database Configuration

Set environment variables for database connection:

```bash
# Windows
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=your_password
set DB_NAME=nasa_ai_system
set DB_PORT=3306

# Or create .env file in web-assistant/ directory
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=nasa_ai_system
DB_PORT=3306
```

### 2. Install MySQL Connector

```bash
pip install mysql-connector-python
```

### 3. Initialize Database

Run the updated schema:

```sql
-- Run the contents of database_schema.sql
source web-assistant/database_schema.sql;
```

### 4. Test Connection

```python
from services.database.connection import init_database_connection
success = init_database_connection()
print("Connected!" if success else "Connection failed")
```

## Usage

### Logging Interactions

```python
from services.database.interaction_logger import log_web_interaction, log_pi_interaction

# Log web assistant interaction
log_web_interaction(
    user_id=1,
    input_text="Hello!",
    response="Hi there!",
    agent_type="general",
    sentiment_score=0.1
)

# Log Pi robot interaction
log_pi_interaction(
    input_text="Tell me a joke",
    response="Why did the robot...",
    agent_type="robot_general"
)
```

### Tracking Models

```python
from services.database.model_tracker import record_new_model, get_training_summary

# Record a new trained model
record_new_model(
    version=1,
    file_name="model_v1",
    training_data={
        "notes": "Trained on 100 interactions",
        "training_interactions": 100,
        "base_model": "microsoft/DialoGPT-small"
    }
)

# Get training data summary
summary = get_training_summary()
print(f"Available: {summary['unused_interactions']} interactions")
```

### System State

```python
from services.database.model_tracker import get_model_tracker

tracker = get_model_tracker()
state = tracker.get_system_state()
print(f"Current model version: {state['last_model_version']}")
```

## Integration Points

### AI Server Integration

The `ai_server.py` now automatically logs all web interactions:

```python
# In ai_server.py chat() function
if DB_ENABLED:
    sentiment = mental_health_score(message)
    log_web_interaction(
        user_id=int(user_id),
        input_text=message,
        response=response,
        agent_type=topic,
        sentiment_score=sentiment
    )
```

### Model Training Integration

The `trainer.py` now:
- Loads interactions from database (preferred)
- Records trained models in database
- Marks used interactions as "used_for_training"

```python
# In trainer.py train() method
if DB_ENABLED:
    record_new_model(version, f"model_v{version}", training_data)
    interaction_logger.mark_as_used_for_training(interaction_ids)
```

## Training Triggers

The system now supports intelligent training triggers:

```python
from services.database.model_tracker import should_trigger_training

if should_trigger_training():
    # Train a new model
    trainer = ModelTrainer()
    model_path = trainer.train()
```

**Trigger Logic**: Training is triggered when there are 50+ unused interactions.

## Data Flow

```
User Input → AI Server → Database (interactions table)
                                      ↓
Model Training → New Model → Database (models table)
                                      ↓
System State → Updated → Training Triggers
```

## Monitoring

### Check System Status

```python
from services.database.model_tracker import get_training_summary

summary = get_training_summary()
print(f"""
Total Interactions: {summary['total_interactions']}
Unused for Training: {summary['unused_interactions']}
Latest Model: v{summary['latest_model_version']}
Ready to Train: {summary['training_ready']}
""")
```

### View Recent Interactions

```python
from services.database.interaction_logger import get_interaction_logger

logger = get_interaction_logger()
recent = logger.get_recent_interactions(limit=10)
for interaction in recent:
    print(f"{interaction['timestamp']}: {interaction['input'][:50]}...")
```

## Testing

Run the complete Phase 2 test:

```bash
cd web-assistant/services/database
python test_phase2.py
```

This will:
- Test database connection
- Log sample interactions
- Record a test model
- Verify system state tracking
- Test training trigger logic

## Next Steps

After Phase 2 is working:
- **Phase 3**: Implement smart training triggers based on database state
- **Phase 4**: Enhanced export system with database integration
- **Phase 5**: Pi-side database sync for robot interactions

## Troubleshooting

### Connection Issues
- Verify MySQL is running: `sudo systemctl status mysql`
- Check credentials in environment variables
- Ensure database `nasa_ai_system` exists

### Import Errors
- Install required packages: `pip install mysql-connector-python`
- Check Python path includes `web-assistant/services`

### Logging Failures
- Database falls back gracefully if connection fails
- Check MySQL error logs for constraint violations
- Verify table schemas match the SQL file