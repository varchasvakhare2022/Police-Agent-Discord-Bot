import json
import os
import asyncio
from typing import Dict, Any, Optional

class JSONStorage:
    """Simple JSON file storage system for bot data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.prefixes_file = os.path.join(data_dir, "prefixes.json")
        self.blacklist_file = os.path.join(data_dir, "blacklist.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files with empty data if they don't exist"""
        if not os.path.exists(self.prefixes_file):
            self._write_json(self.prefixes_file, {})
        
        if not os.path.exists(self.blacklist_file):
            self._write_json(self.blacklist_file, [])
    
    def _read_json(self, file_path: str) -> Any:
        """Read JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'prefixes' in file_path else []
    
    def _write_json(self, file_path: str, data: Any):
        """Write JSON data to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Prefix management methods
    def get_prefix(self, guild_id: int) -> str:
        """Get custom prefix for a guild, returns default '-' if not found"""
        prefixes = self._read_json(self.prefixes_file)
        return prefixes.get(str(guild_id), '-')
    
    def set_prefix(self, guild_id: int, prefix: str):
        """Set custom prefix for a guild"""
        prefixes = self._read_json(self.prefixes_file)
        prefixes[str(guild_id)] = prefix
        self._write_json(self.prefixes_file, prefixes)
    
    def remove_prefix(self, guild_id: int):
        """Remove custom prefix for a guild (revert to default)"""
        prefixes = self._read_json(self.prefixes_file)
        prefixes.pop(str(guild_id), None)
        self._write_json(self.prefixes_file, prefixes)
    
    # Blacklist management methods
    def is_blacklisted(self, user_id: int) -> bool:
        """Check if user is blacklisted"""
        blacklist = self._read_json(self.blacklist_file)
        return user_id in blacklist
    
    def add_to_blacklist(self, user_id: int):
        """Add user to blacklist"""
        blacklist = self._read_json(self.blacklist_file)
        if user_id not in blacklist:
            blacklist.append(user_id)
            self._write_json(self.blacklist_file, blacklist)
    
    def remove_from_blacklist(self, user_id: int):
        """Remove user from blacklist"""
        blacklist = self._read_json(self.blacklist_file)
        if user_id in blacklist:
            blacklist.remove(user_id)
            self._write_json(self.blacklist_file, blacklist)
    
    def get_blacklist(self) -> list:
        """Get all blacklisted user IDs"""
        return self._read_json(self.blacklist_file)
