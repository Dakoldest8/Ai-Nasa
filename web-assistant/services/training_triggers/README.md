# Phase 3: Smart Training Triggers

This phase implements intelligent decision-making for when to train new AI models, replacing random training with data-driven triggers.

## Overview

The smart training system consists of:

1. **Trigger Logic** (`trigger_logic.py`) - Decides when training should occur
2. **Automated Service** (`automated_service.py`) - Background service that monitors and trains
3. **Training API** (`training_api.py`) - REST endpoints for monitoring and control

## Training Trigger Conditions

Training is automatically triggered when **ALL** conditions are met:

### 1. Minimum Interaction Threshold
- **Condition**: 50+ unused interactions available
- **Purpose**: Ensure sufficient new data for meaningful training

### 2. Time-Based Spacing
- **Condition**: At least 24 hours since last training
- **Purpose**: Prevent over-training and resource waste

### 3. Sentiment-Based Priority (OR condition)
- **Condition**: Average sentiment score > 0.3
- **Purpose**: Prioritize training when users show strong emotions

### 4. Data Diversity
- **Condition**: At least 2 different agent types in recent interactions
- **Purpose**: Ensure training data covers multiple conversation types

## Usage

### Automatic Background Training

```python
from services.training_triggers.automated_service import start_automated_training

# Start background service (checks every 15 minutes)
service = start_automated_training()
```

### Manual Trigger Check

```python
from services.training_triggers.trigger_logic import should_trigger_training

should_train, reason = should_trigger_training()
if should_train:
    print(f"Ready to train: {reason}")
else:
    print(f"Not ready: {reason}")
```

### Get Detailed Status

```python
from services.training_triggers.trigger_logic import get_trigger_status

status = get_trigger_status()
print(f"""
Should Train: {status['should_train']}
Reason: {status['reason']}
Unused Interactions: {status['current_stats']['unused_interactions']}
Hours Since Training: {status['trigger_conditions']['hours_since_last_training']:.1f}
Average Sentiment: {status['trigger_conditions']['average_sentiment']:.2f}
""")
```

## API Endpoints

When integrated with the AI server (port 8000), these endpoints are available:

### Check Training Status
```bash
GET /training/status
```

### Manually Trigger Training
```bash
POST /training/trigger
Content-Type: application/json
{"reason": "Manual trigger for testing"}
```

### Start Training Immediately
```bash
POST /training/train-now
```

### Control Automated Service
```bash
POST /training/service/start
POST /training/service/stop
GET /training/service/status
```

## Configuration

### Customize Trigger Conditions

```python
from services.training_triggers.trigger_logic import TrainingTrigger

# Custom trigger with different thresholds
trigger = TrainingTrigger(
    min_interactions=100,        # Need 100 interactions
    max_training_gap_hours=48,   # Train at most every 2 days
    sentiment_threshold=0.5      # Higher sentiment threshold
)
```

### Automated Service Settings

```python
from services.training_triggers.automated_service import AutomatedTrainingService

# Custom service settings
service = AutomatedTrainingService(
    check_interval_minutes=30,   # Check every 30 minutes
    auto_start=True             # Start immediately
)
```

## Integration with Existing Systems

### AI Server Integration

The training API is automatically registered with the AI server:

```python
# In ai_server.py
if TRAINING_ENABLED:
    register_training_endpoints(app)
```

### Database Integration

Training triggers use the Phase 2 database:

- Reads interaction counts from `interactions` table
- Checks system state from `system_state` table
- Records training events in `models` table

## Monitoring

### Real-time Status

```python
from services.training_triggers.trigger_logic import get_trigger_status

status = get_trigger_status()
print(json.dumps(status, indent=2))
```

Output:
```json
{
  "should_train": true,
  "reason": "Ready to train: 67 unused interactions, diverse data, timing OK",
  "current_stats": {
    "unused_interactions": 67,
    "total_interactions": 156,
    "latest_model_version": 2,
    "training_ready": true
  },
  "trigger_conditions": {
    "min_interactions_threshold": 50,
    "max_training_gap_hours": 24,
    "sentiment_threshold": 0.3,
    "hours_since_last_training": 18.5,
    "average_sentiment": 0.15,
    "agent_diversity_ok": true
  }
}
```

### Service Health

```python
from services.training_triggers.automated_service import get_training_service_status

status = get_training_service_status()
print(f"Service running: {status['service_running']}")
print(f"Last check: {status['last_check_time']}")
```

## Testing

Run the complete Phase 3 test:

```bash
cd web-assistant/services/training_triggers
python test_phase3.py
```

This will:
- Test database connectivity
- Verify trigger logic
- Test automated service
- Check API endpoints (if server running)
- Demonstrate trigger conditions

## Workflow

```
User Interactions → Database (interactions table)
                                      ↓
Background Service → Check Triggers → Should Train?
                                      ↓
YES → Train Model → Update Database → Export Ready
                                      ↓
NO → Wait → Check Again Later
```

## Next Steps

After Phase 3 is working:
- **Phase 4**: Enhanced export system with automatic syncing
- **Phase 5**: Pi robot update logic with model validation
- **Phase 6**: Robot logging system for feedback loop

## Troubleshooting

### Triggers Not Activating
- Check database has sufficient interactions: `SELECT COUNT(*) FROM interactions WHERE used_for_training = FALSE`
- Verify system state: `SELECT * FROM system_state`
- Check trigger conditions manually

### Service Not Starting
- Ensure database connection works
- Check for import errors in logs
- Verify model training dependencies installed

### API Endpoints Not Available
- Confirm AI server is running on port 8000
- Check server logs for registration errors
- Verify training_triggers module is importable