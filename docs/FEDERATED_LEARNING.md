# Federated Learning Setup

This document explains how to set up and use the federated learning functionality in the Astronaut AI Ecosystem.

## Overview

Federated learning allows multiple devices to collaboratively train AI models while keeping data private and decentralized. The system uses a coordinator-based approach where devices register as participants, submit model updates, and receive aggregated global models.

## Quick Start

1. **Start the services:**
   ```batch
   start_federated_learning.bat --skip-install
   ```

2. **Check health endpoints:**
   - Auth Server: http://localhost:7000/health
   - AI Server: http://localhost:8000/health
   - Web Assistant: http://localhost:5000/health

3. **Access federated learning endpoints:**
   - Register device: `POST http://localhost:8000/federated/register`
   - Start round: `POST http://localhost:8000/federated/round/start`
   - Submit update: `POST http://localhost:8000/federated/update/submit`

## Architecture

### Core Components

- **FederatedCoordinator**: Manages participants, rounds, and model aggregation
- **FederatedParticipant**: Represents a device participating in federated learning
- **PrivacyEngine**: Handles differential privacy and secure aggregation
- **ModelAggregator**: Combines model updates using FedAvg algorithm

### Services

- **AI Server (port 8000)**: Central server with federated learning API endpoints
- **Auth Server (port 7000)**: User authentication and device registration
- **Web Assistant (port 5000)**: Main web interface for interaction
- **Automated Training Service**: Background service for triggering model training

## API Endpoints

### Register Device
```http
POST /federated/register
Content-Type: application/json

{
  "device_id": "device_123",
  "device_info": {
    "os": "Windows",
    "cpu": "Intel i7",
    "memory_gb": 16
  }
}
```

### Start Federated Round
```http
POST /federated/round/start
Content-Type: application/json

{
  "min_participants": 3,
  "max_rounds": 10
}
```

### Submit Model Update
```http
POST /federated/update/submit
Content-Type: application/json

{
  "device_id": "device_123",
  "model_update": {
    "weights": [...],
    "gradients": [...],
    "n_samples": 1000
  }
}
```

## Configuration

Federated learning settings can be configured in the `.env` file:

```env
# Federated Learning Settings
FEDERATED_MIN_PARTICIPANTS=3
FEDERATED_MAX_ROUNDS=10
FEDERATED_AGGREGATION_STRATEGY=fedavg
FEDERATED_PRIVACY_BUDGET=1.0
```

## Privacy Features

- **Differential Privacy**: Adds noise to model updates to protect individual data
- **Secure Aggregation**: Uses cryptographic techniques to aggregate updates without revealing individual contributions
- **Data Isolation**: Personal data never leaves the device
- **Opt-out Controls**: Users can disable federated learning participation

## Monitoring

Monitor federated learning activity through:

- Service logs in `logs/bat/`
- Database tables: `federated_participants`, `federated_rounds`, `model_updates`
- Health endpoints for service status
- Web interface at `http://localhost:5000`

## Troubleshooting

### Common Issues

1. **Federated learning not available**: Check that all services are running and AI server has federated endpoints registered
2. **Registration fails**: Ensure device_id is unique and auth server is accessible
3. **Round won't start**: Check minimum participant requirements are met
4. **Model updates rejected**: Verify model format and participant registration

### Logs

Check logs in:
- `logs/bat/start_federated_learning_*.log` - Service startup logs
- Individual service logs in their respective directories

## Development

To extend federated learning functionality:

1. Modify `services/federated_learning/federated_core.py` for core logic
2. Add new endpoints in `services/federated_learning/federated_api.py`
3. Update aggregation strategies in `services/federated_learning/federated_update.py`
4. Test with the automated training service in `services/training_triggers/`

## Security Considerations

- All communication uses HTTPS in production
- Model updates are validated before aggregation
- Participants are authenticated through the auth server
- Privacy budgets are enforced to prevent data leakage
- Failed aggregations don't compromise the global model