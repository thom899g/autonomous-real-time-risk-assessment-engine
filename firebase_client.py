"""
Firebase integration for state persistence, real-time updates, and logging.
CRITICAL: All database and state management uses Firebase as required.
"""
import firebase_admin
from firebase_admin import credentials, firestore, db
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime
import logging

from config import config, logger

class FirebaseClient:
    """Manages Firebase connections and operations with robust error handling"""
    
    def __init__(self, credential_path: Optional[str] = None):
        """
        Initialize Firebase client.
        
        Args:
            credential_path: Path to Firebase service account JSON file.
                           If None, uses GOOGLE_APPLICATION_CREDENTIALS env var.
        
        Raises:
            ValueError: If Firebase initialization fails
        """
        self._initialized = False
        self.firestore_client = None
        self.realtime_db = None
        self.credential_path = credential_path
        
        try:
            self._initialize_firebase()
            self._initialized = True
            logger.info("Firebase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise ValueError(f"Firebase initialization failed: {e}")
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase app with error handling and retries"""
        attempts = 0
        max_attempts = config.MAX_RETRIES
        
        while attempts < max_attempts:
            try:
                if not firebase_admin._apps:
                    if self.credential_path:
                        cred = credentials.Certificate(self.credential_path)
                    else:
                        cred = credentials.ApplicationDefault()
                    
                    firebase_admin.initialize_app(cred, {
                        'projectId': config.FIREBASE_PROJECT_ID,
                        'databaseURL': config.REALTIME_DB_URL
                    })
                
                self.firestore_client = firestore.client()
                
                if config.REALTIME_DB_URL:
                    self.realtime_db = db.reference()
                
                break
            except Exception as e:
                attempts += 1
                logger.warning(f"Firebase initialization attempt {attempts} failed: {e}")
                if attempts == max_attempts:
                    raise
                time.sleep(config.RETRY_DELAY)
    
    def save_risk_assessment(self, 
                            assessment: Dict[str, Any],
                            asset_class: str,
                            timestamp: datetime = None) -> str:
        """
        Save risk assessment to Firestore with error handling.
        
        Args:
            assessment: Risk assessment data
            asset_class: Asset class identifier
            timestamp: Assessment timestamp (defaults to now)
        
        Returns:
            Document ID if successful, empty string