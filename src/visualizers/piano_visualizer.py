from ..visualizers.base_visualizer import BaseVisualizer
from ..communication.wled_client import WLEDManager
from ..midi.midi_handler import MIDIHandler
import pygame

class PianoVisualizer(BaseVisualizer):
    def __init__(self, test_mode=False):
        super().__init__(1200, 400)
        pygame.display.set_caption("Piano Visualizer - Test Mode" if test_mode else "Piano Visualizer")
        
        # Initialize basic components
        if not test_mode:
            self.device_manager = DeviceManager()
            self.config = self.device_manager.config
        else:
            # Use basic test configuration
            from ..config.device_config import create_test_config
            self.config = create_test_config()
        
        # Initialize WLED
        self.wled = WLEDManager(self.config.wled_devices)
        
        # Initialize MIDI
        self.midi = MIDIHandler(self._handle_midi_note)
        
        # Basic state
        self.color_mapping = "chromatic"
        self.last_message = "Test Mode Active" if test_mode else "Ready"
    
    def _handle_midi_note(self, note: int, is_on: bool):
        """Handle local MIDI note"""
        if is_on:
            self.local_notes.add(note)
        else:
            self.local_notes.discard(note)
        print(f"MIDI Note {'ON' if is_on else 'OFF'}: {note}") 