"""
Astronaut AI Ecosystem - Web Assistant Backend
Flask application for personal AI with federated learning

Integrates with:
- Central AI Server (chat/routing/escalation)
- Federated Learning (FL server)
- Multiple specialty agents (fitness, mental_health, nutrition)
- Authentication Server
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add services to path for imports
SERVICES_PATH = Path(__file__).parent / 'services'
sys.path.insert(0, str(SERVICES_PATH))

LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
WEB_ASSISTANT_LOG = LOG_DIR / 'web-assistant.log'

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(WEB_ASSISTANT_LOG, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application with integrated services"""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS for inter-service communication
    CORS(app, resources={
        r"/*": {"origins": ["http://localhost", "http://localhost:8000", "http://localhost:3000"]}
    })
    
    # Load core configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/nasa_ai_system'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # =====================================================================
    # IMPORT & REGISTER CENTRAL SERVER AI ROUTES
    # =====================================================================
    try:
        from central_server.ai_server import app as ai_server_app
        logger.info("[OK] Central AI Server initialized")
        
        # Register the central server routes
        @app.route('/chat', methods=['POST', 'OPTIONS'])
        def chat_handler():
            """Forward chat requests to central server"""
            from central_server.ai_server import chat
            return chat()
        
    except Exception as e:
        logger.warning(f"Could not load central AI server: {e}")
    
    # =====================================================================
    # IMPORT & REGISTER AUTH SERVER ROUTES
    # =====================================================================
    try:
        from auth.auth_server import app as auth_app
        logger.info("[OK] Auth Server initialized")
        
        @app.route('/auth/login', methods=['POST'])
        def login_handler():
            """Forward login requests to auth server"""
            from auth.auth_server import login
            return login()
            
        @app.route('/auth/register', methods=['POST'])
        def register_handler():
            """Forward registration requests to auth server"""
            from auth.auth_server import register
            return register()
            
    except Exception as e:
        logger.warning(f"Could not load auth server: {e}")
    
    # =====================================================================
    # HEALTH CHECK & STATUS ENDPOINTS
    # =====================================================================
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'web-assistant',
            'version': '1.0.0',
            'components': {
                'ai_server': 'online',
                'auth_server': 'online',
                'federated_learning': 'available'
            }
        }, 200
    
    @app.route('/api/status', methods=['GET'])
    def status():
        """Get full system status"""
        return {
            'service': 'web-assistant',
            'status': 'running',
            'port': os.getenv('WEB_ASSISTANT_PORT', 5000),
            'components': {
                'central_ai': 'ready',
                'auth': 'ready',
                'federated_learning': 'ready'
            }
        }, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('WEB_ASSISTANT_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Web Assistant on {port}")
    logger.info("Components: AI Server | Auth | Federated Learning")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    )
