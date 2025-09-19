import json
import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp

class StorageManager:
    """Hybrid storage system - JSON files locally, database in cloud"""
    
    def __init__(self, data_dir: str = "data", use_database: bool = False, db_url: str = None):
        self.data_dir = data_dir
        self.use_database = use_database
        self.db_url = db_url
        
        if not use_database:
            # Use JSON files (local development)
            os.makedirs(data_dir, exist_ok=True)
            self.prefixes_file = os.path.join(data_dir, "prefixes.json")
            self.blacklist_file = os.path.join(data_dir, "blacklist.json")
            self._init_json_files()
        else:
            # Use database (cloud deployment)
            self._init_database()
    
    def _init_json_files(self):
        """Initialize JSON files if they don't exist"""
        if not os.path.exists(self.prefixes_file):
            self._write_json(self.prefixes_file, {})
        if not os.path.exists(self.blacklist_file):
            self._write_json(self.blacklist_file, [])
    
    def _init_database(self):
        """Initialize database tables"""
        # This would create tables in your database
        # For now, we'll use a simple in-memory storage for demo
        self._prefixes = {}
        self._blacklist = []
    
    # JSON file methods
    def _read_json(self, file_path: str) -> Any:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'prefixes' in file_path else []
    
    def _write_json(self, file_path: str, data: Any):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Public API methods
    def get_prefix(self, guild_id: int) -> str:
        if self.use_database:
            return self._prefixes.get(str(guild_id), '-')
        else:
            prefixes = self._read_json(self.prefixes_file)
            return prefixes.get(str(guild_id), '-')
    
    def set_prefix(self, guild_id: int, prefix: str):
        if self.use_database:
            self._prefixes[str(guild_id)] = prefix
            # In real implementation, you'd save to database here
        else:
            prefixes = self._read_json(self.prefixes_file)
            prefixes[str(guild_id)] = prefix
            self._write_json(self.prefixes_file, prefixes)
    
    def remove_prefix(self, guild_id: int):
        if self.use_database:
            self._prefixes.pop(str(guild_id), None)
        else:
            prefixes = self._read_json(self.prefixes_file)
            prefixes.pop(str(guild_id), None)
            self._write_json(self.prefixes_file, prefixes)
    
    def is_blacklisted(self, user_id: int) -> bool:
        if self.use_database:
            return user_id in self._blacklist
        else:
            blacklist = self._read_json(self.blacklist_file)
            return user_id in blacklist
    
    def add_to_blacklist(self, user_id: int):
        if self.use_database:
            if user_id not in self._blacklist:
                self._blacklist.append(user_id)
        else:
            blacklist = self._read_json(self.blacklist_file)
            if user_id not in blacklist:
                blacklist.append(user_id)
                self._write_json(self.blacklist_file, blacklist)
    
    def remove_from_blacklist(self, user_id: int):
        if self.use_database:
            if user_id in self._blacklist:
                self._blacklist.remove(user_id)
        else:
            blacklist = self._read_json(self.blacklist_file)
            if user_id in blacklist:
                blacklist.remove(user_id)
                self._write_json(self.blacklist_file, blacklist)
    
    def get_blacklist(self) -> List[int]:
        if self.use_database:
            return self._blacklist.copy()
        else:
            return self._read_json(self.blacklist_file)
