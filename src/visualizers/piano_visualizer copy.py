from ..visualizers.base_visualizer import BaseVisualizer
from ..communication.wled_client import WLEDClient, WLEDManager
from ..communication.mqtt_client import MusicMQTTClient
from ..midi.midi_handler import MIDIHandler
from ..config.device_config import DeviceManager
import uuid

class PianoVisualizer(BaseVisualizer):
    def __init__(self):
        # Load device configuration
        self.device_manager = DeviceManager()
        self.config = self.device_manager.config
        
        super().__init__(1200, 400)
        pygame.display.set_caption(f"Piano Visualizer - {self.config.name}")
        
        # Initialize components
        self.wled = WLEDManager(self.config.wled_devices)
        self.midi = MIDIHandler(self._handle_midi_note)
        
        # Initialize MQTT with configured broker
        self.mqtt = MusicMQTTClient(
            self.config.user_id,
            self.config.instrument,
            self.config.mqtt_broker,
            self.config.mqtt_port
        )
        
        if self.mqtt.connect():
            # Subscribe to all other instruments
            for instrument in ['guitar', 'drums', 'bass']:
                if instrument != self.config.instrument:
                    self.mqtt.register_callback(instrument, self._handle_remote_notes)
        
        # Piano specific settings
        self.color_mapping = "chromatic"
        self.last_message = "No message"
        
    def _handle_midi_note(self, note: int, is_on: bool):
        """Handle local MIDI note"""
        if is_on:
            self.local_notes.add(note)
            self.mqtt.publish_notes(self.local_notes)
        else:
            self.local_notes.discard(note)
            self.mqtt.publish_notes(self.local_notes)
    
    def _handle_remote_notes(self, data: dict):
        """Handle remote notes from MQTT"""
        source_id = data["client_id"]
        self.remote_notes[source_id] = set(data["notes"])
    
    def draw(self):
        """Draw piano visualization"""
        # ... (existing piano drawing code, but using both local_notes and remote_notes) ...
        
        # Create info text
        device_name = self.midi.last_device or "None"
        info_text = (f"Mapping (c): {self.color_mapping.capitalize()} | "
                    f"MIDI Device [M]: {device_name} | "
                    f"Remote Sources: {len(self.remote_notes)} | "
                    f"Last: {self.last_message}")
        self.draw_info(info_text)
        
        # Update WLED
        led_colors = self._create_led_colors()
        self.wled.broadcast_data(led_colors)
    
    def handle_events(self) -> bool:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.color_mapping = "harmonic" if self.color_mapping == "chromatic" else "chromatic"
                elif event.key == pygame.K_m:
                    self.midi.connect()
                elif event.key == pygame.K_q:
                    return False
            # ... (handle mouse events) ...
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        self.wled.close()
        self.midi.close()
        self.mqtt.disconnect()
        super().cleanup() 