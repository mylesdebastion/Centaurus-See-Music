from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml
import os
import socket
import uuid

@dataclass
class WLEDDevice:
    name: str
    ip: str
    port: int = 21324
    num_leds: int = 144
    instrument: str = ""  # Which instrument this WLED strip is for
    location: str = ""    # Physical location description

@dataclass
class UserConfig:
    user_id: str
    name: str
    instrument: str
    wled_devices: List[WLEDDevice]
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    
class DeviceManager:
    def __init__(self, config_path: str = "config/devices.yaml"):
        self.config_path = config_path
        self.user_id = self._get_or_create_user_id()
        self.config = self._load_config()
    
    def _get_or_create_user_id(self) -> str:
        """Get existing user ID or create new one"""
        id_file = "config/user_id"
        if os.path.exists(id_file):
            with open(id_file, 'r') as f:
                return f.read().strip()
        
        # Create new ID using hostname and uuid
        user_id = f"{socket.gethostname()}_{uuid.uuid4().hex[:8]}"
        os.makedirs("config", exist_ok=True)
        with open(id_file, 'w') as f:
            f.write(user_id)
        return user_id
    
    def _load_config(self) -> UserConfig:
        """Load or create configuration"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Find config for this user
            for user_config in data['users']:
                if user_config['user_id'] == self.user_id:
                    return UserConfig(
                        user_id=user_config['user_id'],
                        name=user_config['name'],
                        instrument=user_config['instrument'],
                        wled_devices=[
                            WLEDDevice(**device) 
                            for device in user_config['wled_devices']
                        ],
                        mqtt_broker=user_config.get('mqtt_broker', 'localhost'),
                        mqtt_port=user_config.get('mqtt_port', 1883)
                    )
            
            # User not found in config
            print(f"User {self.user_id} not found in config. Using defaults.")
        
        # Return default config
        return self._create_default_config()
    
    def _create_default_config(self) -> UserConfig:
        """Create default configuration"""
        return UserConfig(
            user_id=self.user_id,
            name=socket.gethostname(),
            instrument="unknown",
            wled_devices=[
                WLEDDevice(
                    name="Default WLED",
                    ip="192.168.1.255",  # Broadcast address as default
                    port=21324,
                    num_leds=144
                )
            ]
        )
    
    def save_config(self):
        """Save current configuration"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Load existing config if it exists
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = yaml.safe_load(f) or {'users': []}
        else:
            data = {'users': []}
        
        # Update or add this user's config
        user_data = {
            'user_id': self.config.user_id,
            'name': self.config.name,
            'instrument': self.config.instrument,
            'mqtt_broker': self.config.mqtt_broker,
            'mqtt_port': self.config.mqtt_port,
            'wled_devices': [
                {
                    'name': device.name,
                    'ip': device.ip,
                    'port': device.port,
                    'num_leds': device.num_leds,
                    'instrument': device.instrument,
                    'location': device.location
                }
                for device in self.config.wled_devices
            ]
        }
        
        # Update existing user or add new one
        for i, user in enumerate(data['users']):
            if user['user_id'] == self.user_id:
                data['users'][i] = user_data
                break
        else:
            data['users'].append(user_data)
        
        # Save config
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(data, f) 