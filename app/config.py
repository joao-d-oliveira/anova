import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Centralized configuration class for the application.
    Loads environment variables from config/.env file or environment.
    Works in both local development and ECS environments.
    """
    _instance = None
    _initialized = False
    _values: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_config()
            self._initialized = True
    
    def _find_project_root(self) -> Path:
        """
        Find the project root directory using multiple strategies.
        This ensures the config works in different environments.
        """
        # Strategy 1: Use CONFIG_PATH environment variable if set
        if os.environ.get("CONFIG_PATH"):
            config_path = Path(os.environ.get("CONFIG_PATH"))
            if config_path.exists():
                logger.info(f"Using CONFIG_PATH environment variable: {config_path}")
                return config_path.parent.parent
        
        # Strategy 2: Use the current file's location
        current_file = Path(__file__)
        app_dir = current_file.parent
        
        # If we're in the app directory, the parent is the project root
        if app_dir.name == "app":
            logger.info(f"Using app directory location: {app_dir}")
            return app_dir.parent
        
        # Strategy 3: Use the current working directory
        cwd = Path.cwd()
        logger.info(f"Current working directory: {cwd}")
        
        # Check if we're in the project root (has app directory)
        if (cwd / "app").exists():
            logger.info("Using current working directory as project root")
            return cwd
        
        # Strategy 4: Look for app directory in parent directories
        parent = cwd
        for _ in range(3):  # Don't go too far up
            if (parent / "app").exists():
                logger.info(f"Found project root at: {parent}")
                return parent
            parent = parent.parent
        
        # Strategy 5: Fall back to current working directory
        logger.warning("Could not determine project root, using current directory")
        return cwd
    
    def _load_config(self):
        """Load configuration from .env file or environment variables"""
        # Find project root
        project_root = self._find_project_root()
        logger.info(f"Project root: {project_root}")
        
        # Check for config in multiple locations
        config_paths = [
            os.environ.get("CONFIG_PATH"),  # Explicit config path
            project_root / "config" / ".env",  # New location
            project_root / ".env",  # Legacy location
        ]
        
        # Try each path
        env_loaded = False
        for path in config_paths:
            if not path:
                continue
                
            path = Path(path)
            if path.exists():
                logger.info(f"Loading configuration from {path}")
                load_dotenv(dotenv_path=str(path))
                env_loaded = True
                break
        
        if not env_loaded:
            logger.warning("No .env file found, using environment variables only")
        
        # Load all environment variables
        self._load_database_config()
        self._load_aws_config()
        self._load_api_keys()
        self._load_session_config()
        self._load_email_config()
        
        # Validate required configuration
        self._validate_config()
        
        # Log configuration summary (without sensitive values)
        self._log_config_summary()
    
    def _load_database_config(self):
        """Load database configuration"""
        self._values["db_host"] = os.getenv("DB_HOST", "localhost")
        self._values["db_port"] = os.getenv("DB_PORT", "5432")
        self._values["db_name"] = os.getenv("DB_NAME", "anova")
        self._values["db_user"] = os.getenv("DB_USER", "anova_user")
        self._values["db_password"] = os.getenv("DB_PASSWORD", "")
    
    def _load_aws_config(self):
        """Load AWS configuration"""
        self._values["aws_region"] = os.getenv("AWS_REGION", "us-east-1")
        self._values["aws_profile"] = os.getenv("AWS_PROFILE")
        self._values["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
        self._values["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        self._values["noreply_access_key_id"] = os.getenv("NO_REPLY_ACCESS_KEY_ID")
        self._values["noreply_secret_access_key"] = os.getenv("NO_REPLY_SECRET_ACCESS_KEY")
    
    
    def _load_api_keys(self):
        """Load API keys"""
        self._values["anthropics_api_key"] = os.getenv("ANTHROPICS_API_KEY")
    
    def _load_session_config(self):
        """Load session configuration"""
        self._values["base_dir"] = os.getenv("BASE_DIR", "")
        self._values["session_secret_key"] = os.getenv("SESSION_SECRET_KEY")
        self._values["environment"] = os.getenv("ENVIRONMENT", "development")
    
    def _load_email_config(self):
        """Load email configuration"""
        self._values["email_noreply_address"] = os.getenv("EMAIL_NOREPLY_ADDRESS", "")
        self._values["email_noreply_password"] = os.getenv("EMAIL_NOREPLY_PASSWORD", "")
        self._values["email_smtp_server"] = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self._values["email_smtp_port"] = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    
    def _validate_config(self):
        """Validate required configuration values"""
        required_vars = [
            ("db_host", self.db_host),
            ("db_name", self.db_name),
            ("db_user", self.db_user),
            ("db_password", self.db_password),
            ("session_secret_key", self.session_secret_key)
        ]
        
        
        missing = [name for name, value in required_vars if not value]
        if missing:
            logger.warning(f"Missing required configuration: {', '.join(missing)}")
    
    def _log_config_summary(self):
        """Log a summary of the configuration (without sensitive values)"""
        logger.info(f"Configuration loaded for environment: {self.environment}")
        logger.info(f"Database: {self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}")
        logger.info(f"AWS Region: {self.aws_region}")
    
    def get_database_url(self) -> str:
        """Get the database URL for SQLAlchemy"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def is_production(self) -> bool:
        """Check if the environment is production"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if the environment is development"""
        return self.environment.lower() == "development"
    
    # Property getters for all configuration values
    @property
    def db_host(self) -> str:
        return self._values.get("db_host", "")
    
    @property
    def db_port(self) -> int:
        return self._values.get("db_port", "5432")
    
    @property
    def db_name(self) -> str:
        return self._values.get("db_name", "")
    
    @property
    def db_user(self) -> str:
        return self._values.get("db_user", "")
    
    @property
    def db_password(self) -> str:
        return self._values.get("db_password", "")
    
    @property
    def aws_region(self) -> str:
        return self._values.get("aws_region", "")
    
    @property
    def aws_profile(self) -> Optional[str]:
        return self._values.get("aws_profile")
    
    @property
    def aws_access_key_id(self) -> Optional[str]:
        return self._values.get("aws_access_key_id")
    
    @property
    def noreply_access_key_id(self) -> Optional[str]:
        return self._values.get("noreply_access_key_id")
    
    @property
    def noreply_secret_access_key(self) -> Optional[str]:
        return self._values.get("noreply_secret_access_key")
    
    @property
    def aws_secret_access_key(self) -> Optional[str]:
        return self._values.get("aws_secret_access_key")
    
    @property
    def anthropics_api_key(self) -> Optional[str]:
        return self._values.get("anthropics_api_key")
    
    @property
    def session_secret_key(self) -> Optional[str]:
        return self._values.get("session_secret_key")
    
    @property
    def environment(self) -> str:
        return self._values.get("environment", "development")
    
    @property
    def base_dir(self) -> str:
        return self._values.get("base_dir", "")

    @property
    def email_noreply_address(self) -> str:
        return self._values.get("email_noreply_address", "")
    
    @property
    def email_noreply_password(self) -> str:
        return self._values.get("email_noreply_password", "")
    
    @property
    def email_smtp_server(self) -> str:
        return self._values.get("email_smtp_server", "")
    
    @property
    def email_smtp_port(self) -> int:
        return self._values.get("email_smtp_port", 0)
