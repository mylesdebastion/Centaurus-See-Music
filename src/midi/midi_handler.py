import mido
import threading
import time
from typing import Callable, Set, Optional

class MIDIHandler:
    def __init__(self, note_callback: Callable[[int, bool], None]):
        self.note_callback = note_callback
        self.input = None
        self.devices = []
        self.current_device_index = -1
        self.thread = None
        self.running = False
        
        # Try to load last used device
        self.last_device = None
        try:
            with open('last_midi_device.txt', 'r') as f:
                self.last_device = f.read().strip()
        except:
            pass
    
    def get_next_device(self) -> Optional[str]:
        """Get next available MIDI device"""
        self.devices = mido.get_input_names()
        
        if not self.devices:
            return None
            
        # Try last device first
        if self.last_device in self.devices:
            return self.last_device
            
        # Otherwise get next device
        self.current_device_index = (self.current_device_index + 1) % len(self.devices)
        return self.devices[self.current_device_index]
    
    def connect(self, device_name: Optional[str] = None) -> bool:
        """Connect to MIDI device"""
        try:
            if self.input:
                self.close()
            
            if not device_name:
                device_name = self.get_next_device()
                
            if not device_name:
                return False
                
            self.input = mido.open_input(device_name)
            self.last_device = device_name
            
            # Save successful device
            with open('last_midi_device.txt', 'w') as f:
                f.write(device_name)
            
            self.running = True
            self.thread = threading.Thread(target=self._midi_listener, daemon=True)
            self.thread.start()
            return True
            
        except Exception as e:
            print(f"MIDI connection error: {e}")
            return False
    
    def _midi_listener(self):
        """MIDI message listener thread"""
        while self.running and self.input:
            try:
                for message in self.input.iter_pending():
                    if message.type == 'note_on':
                        self.note_callback(message.note, message.velocity > 0)
                    elif message.type == 'note_off':
                        self.note_callback(message.note, False)
                time.sleep(0.001)
            except Exception as e:
                print(f"MIDI listener error: {e}")
                break
    
    def close(self):
        """Close MIDI connection"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.input:
            self.input.close()
            self.input = None 