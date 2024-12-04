import pygame
import socket
import time
import mido
from typing import Set
import threading
from .base_visualizer import BaseVisualizer
from src.communication.mqtt_client import MusicMQTTClient
import uuid

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

# WLED settings
WLED_IP = "192.168.8.148"  # Update with your WLED IP
WLED_PORT = 21324
NUM_SEGMENTS = 6
LEDS_PER_SEGMENT = 5
TOTAL_LEDS = NUM_SEGMENTS * LEDS_PER_SEGMENT

# Color settings
SEGMENT_COLORS = [
    (255, 0, 0),     # Red
    (255, 127, 0),   # Orange
    (255, 255, 0),   # Yellow
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (148, 0, 211)    # Purple
]

class MaskVisualizer(BaseVisualizer):
    def __init__(self):
        print("Initializing Mask Visualizer...")
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
        pygame.display.set_caption("Mask Visualizer")

        # Initialize local input mode
        self.local_input_enabled = True
        
        # Initialize status messages
        self.mqtt_status = "MQTT: Not connected"
        self.last_midi_message = "No MIDI connected"

        # MIDI device management
        self.midi_devices = mido.get_input_names()
        self.current_midi_device_index = -1
        self.midi_input = None

        # Generate unique client ID and set instrument type
        self.client_id = f"mask_{uuid.uuid4().hex[:8]}"
        self.instrument_type = "mask"
        
        # MQTT setup
        print("\nSetting up MQTT...")
        try:
            self.mqtt = MusicMQTTClient(self.client_id, self.instrument_type)
            print(f"Created MQTT client with ID: {self.client_id}")
        except Exception as e:
            print(f"MQTT setup error: {e}")
            self.mqtt_status = f"MQTT Error: {str(e)}"

        # Set up MIDI
        print("Setting up MIDI...")
        self.setup_midi()

        # WLED setup
        print(f"Setting up WLED connection to {WLED_IP}:{WLED_PORT}")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Initialization complete.")

    def setup_midi(self):
        """Set up MIDI input with device switching"""
        try:
            self.midi_devices = mido.get_input_names()
            print(f"\nAvailable MIDI devices: {self.midi_devices}")
            
            if self.midi_devices:
                if self.midi_input:
                    self.midi_input.close()
                    self.midi_input = None
                    time.sleep(0.1)

                self.current_midi_device_index = (self.current_midi_device_index + 1) % len(self.midi_devices)
                device_name = self.midi_devices[self.current_midi_device_index]
                
                self.midi_input = mido.open_input(device_name)
                self.last_midi_message = f"Connected to: {device_name}"
                
                midi_thread = threading.Thread(target=self.midi_listener, daemon=True)
                midi_thread.start()
            else:
                self.last_midi_message = "No devices found"
                self.current_midi_device_index = -1
        except Exception as e:
            print(f"MIDI setup error: {e}")
            self.last_midi_message = f"Error: {str(e)}"

    def midi_listener(self):
        """Listen for MIDI messages"""
        try:
            while self.midi_input:
                for message in self.midi_input.iter_pending():
                    if self.local_input_enabled:
                        if message.type == 'note_on' and message.velocity > 0:
                            self.handle_local_note(message.note, True)
                        elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                            self.handle_local_note(message.note, False)
                time.sleep(0.001)
        except Exception as e:
            print(f"MIDI listener error: {e}")

    def draw_hex_segment(self, center_x, center_y, segment_index, intensity):
        """Draw a hexagonal LED segment"""
        radius = 30
        angle = segment_index * (360 / NUM_SEGMENTS)
        color = SEGMENT_COLORS[segment_index]
        
        # Calculate position based on hex layout
        x = center_x + radius * 2 * pygame.math.Vector2().from_polar((1, angle))[0]
        y = center_y + radius * 2 * pygame.math.Vector2().from_polar((1, angle))[1]
        
        # Draw segment with intensity
        adjusted_color = tuple(int(c * intensity) for c in color)
        pygame.draw.circle(self.screen, adjusted_color, (int(x), int(y)), radius)

    def create_wled_data(self):
        """Create LED data for WLED"""
        led_data = []
        
        # Calculate average intensity for each segment based on active notes
        for segment in range(NUM_SEGMENTS):
            note_range = range(segment * 12, (segment + 1) * 12)  # Map each segment to an octave
            segment_notes = sum(1 for note in note_range if note in self.local_notes)
            intensity = min(1.0, segment_notes / 6)  # Max intensity at 6 notes
            
            # Add LED colors for this segment
            base_color = SEGMENT_COLORS[segment]
            segment_color = tuple(int(c * intensity) for c in base_color)
            led_data.extend(segment_color * LEDS_PER_SEGMENT)
            
        return led_data

    def draw(self):
        """Main draw method"""
        try:
            self.screen.fill((0, 0, 0))
            
            # Draw hex segments
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            for segment in range(NUM_SEGMENTS):
                note_range = range(segment * 12, (segment + 1) * 12)
                segment_notes = sum(1 for note in note_range if note in self.local_notes)
                intensity = min(1.0, segment_notes / 6)
                self.draw_hex_segment(center_x, center_y, segment, intensity)
            
            # Update status text
            mode_text = "LOCAL" if self.local_input_enabled else "REMOTE"
            info_text = (f"Mode: {mode_text} | "
                        f"{self.mqtt_status} | "
                        f"MIDI: {self.last_midi_message} | "
                        f"Press 't' to toggle mode | 'm' to rescan MIDI | 'q' to quit")
            self.draw_info(info_text)
            
            # Update WLED
            led_data = self.create_wled_data()
            self.send_wled_data(led_data)
            
        except Exception as e:
            print(f"Error in draw method: {e}")

    def send_wled_data(self, data):
        """Send data to WLED device"""
        try:
            packet = bytearray([2, 255])  # WARLS protocol header
            packet.extend(data)
            self.udp_socket.sendto(packet, (WLED_IP, WLED_PORT))
        except Exception as e:
            print(f"Error sending WLED data: {e}")

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.local_input_enabled = not self.local_input_enabled
                elif event.key == pygame.K_m:
                    self.setup_midi()
                elif event.key == pygame.K_q:
                    return False
        return True

if __name__ == "__main__":
    visualizer = MaskVisualizer()
    visualizer.run() 