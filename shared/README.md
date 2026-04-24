# Shared Utilities

Common modules, utilities, and protocols used by both Web Assistant and Pi Robot components.

## Modules

### api_client.py
HTTP client wrapper for inter-component communication
- Handles retries and timeouts
- Response serialization/deserialization
- Error handling

### protocols.py
Communication protocol definitions
- Request/response message formats
- Signature verification
- Protocol versioning

### schemas.py
Data validation schemas using Pydantic
- User models
- Task models
- Query models
- Response models

### auth.py
Authentication utilities
- JWT token generation/validation
- Role-based access control (RBAC)
- Permission checking

### logging.py
Centralized logging configuration
- Structured logging format
- File and console handlers
- Log level management

### constants.py
Shared constants
- API endpoints
- Error codes
- Status codes
- Timeout values

### utils.py
General utility functions
- String sanitization
- Data transformation
- Helper functions

## Usage

```python
from shared.api_client import APIClient
from shared.schemas import TaskSchema
from shared.auth import verify_token

# Use in web-assistant or be-more-agent-main
client = APIClient(base_url='http://localhost:5001')
response = client.post('/api/query', data={'query': 'Hello'})
```

## Development

All shared modules must be:
- Well-documented with docstrings
- Tested with unit tests
- Compatible with both Python 3.9+
- Type-hinted for IDE support

## Adding New Shared Modules

1. Create module in `shared/`
2. Add unit tests to `shared/tests/`
3. Update this README
4. Update imports in components using the module
