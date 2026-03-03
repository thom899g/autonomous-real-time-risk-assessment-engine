"""
Configuration management for the Risk Assessment Engine.
Centralizes all configurable parameters and environment variables.
"""
import os
from typing import Dict, Any
from dataclasses import dataclass
from datetime import timedelta
import logging

# Environment-based configuration
@dataclass
class RiskConfig:
    """Risk engine configuration parameters"""
    # Data collection
    POLLING_INTERVAL_SECONDS: int = 30
    WEBSOCKET_TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    
    # Risk parameters
    VAR_CONFIDENCE_LEVEL: float = 0.95
    CVAR_QUANTILE: float = 0.05
    VOLATILITY_WINDOW_DAYS: int = 30
    CORRELATION_THRESHOLD: float = 0.7
    MAX_PORTFOLIO_RISK: float = 0.15
    LIQUIDITY_THRESHOLD: float = 1000000  # USD equivalent
    
    # Strategy adaptation
    RISK_LEVELS: Dict[str, float] = None
    REBALANCE_THRESHOLD: float = 0.05
    HEDGE_RATIO: float = 0.3
    
    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "risk-engine-prod")
    FIRESTORE_COLLECTION: str = "risk_assessments"
    REALTIME_DB_URL: str = os.getenv("FIREBASE_DB_URL", "")
    
    # Exchanges
    EXCHANGES: Dict[str, Dict] = None
    
    def __post_init__(self):
        """Initialize with default values"""
        if self.RISK_LEVELS is None:
            self.RISK_LEVELS = {
                "LOW": 0.02,
                "MEDIUM": 0.05,
                "HIGH": 0.10,
                "EXTREME": 0.20
            }
        
        if self.EXCHANGES is None:
            self.EXCHANGES = {
                "binance": {
                    "class": "ccxt.binance",
                    "timeout": 30000,
                    "enableRateLimit": True
                },
                "coinbase": {
                    "class": "ccxt.coinbase",
                    "timeout": 30000
                }
            }

class LoggerConfig:
    """Configure application logging"""
    @staticmethod
    def setup_logger(name: str = "risk_engine") -> logging.Logger:
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            
        return logger

# Global configuration instance
config = RiskConfig()
logger = LoggerConfig.setup_logger()