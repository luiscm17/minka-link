# src/civic_chat/agents/memory/thread_manager.py
"""
Thread Manager - Manages conversation thread persistence for multi-turn conversations.

Saves and loads AgentThread objects to enable conversation continuity across sessions.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manages persistent storage of conversation threads."""
    
    def __init__(self, user_id: str, storage_dir: str = "user_data"):
        """Initialize thread manager for a specific user.
        
        Args:
            user_id: Unique identifier for the user
            storage_dir: Directory where thread files are stored
        """
        self.user_id = user_id
        self.storage_dir = storage_dir
        self.thread_file = os.path.join(storage_dir, f"{user_id}_thread.json")
        self._ensure_storage_dir()
        
    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
    async def save_thread(self, thread) -> bool:
        """Save a thread to persistent storage.
        
        Args:
            thread: AgentThread object to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Serialize the thread
            serialized_thread = await thread.serialize()
            
            # Prepare data structure
            thread_data = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'thread': serialized_thread
            }
            
            # Save to file
            with open(self.thread_file, 'w', encoding='utf-8') as f:
                json.dump(thread_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Thread saved for user: {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving thread for {self.user_id}: {e}")
            return False
    
    async def load_thread(self, workflow) -> Optional[Any]:
        """Load a thread from persistent storage.
        
        Args:
            workflow: Workflow instance to deserialize the thread with
            
        Returns:
            Deserialized AgentThread or None if not found/error
        """
        try:
            if not os.path.exists(self.thread_file):
                logger.info(f"No saved thread found for user: {self.user_id}")
                return None
            
            # Load from file
            with open(self.thread_file, 'r', encoding='utf-8') as f:
                thread_data = json.load(f)
            
            # Deserialize the thread
            serialized_thread = thread_data.get('thread')
            if not serialized_thread:
                logger.warning(f"Invalid thread data for user: {self.user_id}")
                return None
            
            thread = await workflow.deserialize_thread(serialized_thread)
            logger.info(f"Thread loaded for user: {self.user_id}")
            return thread
            
        except Exception as e:
            logger.error(f"Error loading thread for {self.user_id}: {e}")
            return None
    
    def delete_thread(self) -> bool:
        """Delete the saved thread file.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(self.thread_file):
                os.remove(self.thread_file)
                logger.info(f"Thread deleted for user: {self.user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting thread for {self.user_id}: {e}")
            return False
    
    def thread_exists(self) -> bool:
        """Check if a saved thread exists for this user.
        
        Returns:
            True if thread file exists, False otherwise
        """
        return os.path.exists(self.thread_file)
    
    def get_thread_info(self) -> Optional[Dict[str, Any]]:
        """Get metadata about the saved thread without loading it.
        
        Returns:
            Dictionary with thread metadata or None if not found
        """
        try:
            if not os.path.exists(self.thread_file):
                return None
            
            with open(self.thread_file, 'r', encoding='utf-8') as f:
                thread_data = json.load(f)
            
            return {
                'user_id': thread_data.get('user_id'),
                'last_updated': thread_data.get('last_updated'),
                'exists': True
            }
        except Exception as e:
            logger.error(f"Error reading thread info for {self.user_id}: {e}")
            return None
