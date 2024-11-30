from typing import List, Dict, Tuple
from ..config.device_config import WLEDDevice
import socket

class WLEDManager:
    def __init__(self, devices: List[WLEDDevice]):
        self.devices = {device.name: device for device in devices}
        self.sockets: Dict[str, socket.socket] = {}
        
        # Create socket for each device
        for name, device in self.devices.items():
            self.sockets[name] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send_data(self, device_name: str, colors: List[Tuple[int, int, int]]):
        """Send color data to specific WLED device"""
        if device_name not in self.devices:
            print(f"Unknown WLED device: {device_name}")
            return
            
        device = self.devices[device_name]
        sock = self.sockets[device_name]
        
        data = []
        for color in colors:
            data.extend(color)
        
        # Fill remaining LEDs with black
        remaining = device.num_leds - len(colors)
        data.extend([0, 0, 0] * remaining)
        
        # Create WARLS packet
        packet = bytearray([2, 255])
        packet.extend(bytes(data))
        
        sock.sendto(packet, (device.ip, device.port))
    
    def broadcast_data(self, colors: List[Tuple[int, int, int]]):
        """Send same data to all WLED devices"""
        for device_name in self.devices:
            self.send_data(device_name, colors)
    
    def close(self):
        """Close all sockets"""
        for sock in self.sockets.values():
            sock.close() 