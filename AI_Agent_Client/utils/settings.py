import os
from dotenv import load_dotenv

load_dotenv()


class ApplicationSettings:
    def __init__(self):
        self.name = os.getenv("APP_NAME", "AI_Agent_client")
        self.environment = os.getenv("APP_ENVIRONMENT", "local")
        self.app_host = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port = int(os.getenv("APP_PORT", "9100"))
        self.logging_level = os.getenv("APP_LOGGING_LEVEL", "INFO")
        self.app_reload = bool(os.getenv("APP_RELOAD", True))
        self.timeout = int(os.getenv("APP_TIMEOUT", 600))
        self.workers = int(os.getenv("APP_WORKERS", 1))


def initialize_settings():
    settings = ApplicationSettings()
    return settings
