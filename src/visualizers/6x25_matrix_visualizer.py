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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400
FPS = 30

# WLED settings
WLED_IP = "192.168.8.145"
WLED_PORT = 21324

# Guitar settings
STRINGS = 6
FRETS = 25
START_NOTE = 40  # E2 for standard tuning
TUNING = [40, 45, 50, 55, 59, 64]  # Standard tuning: E2, A2, D3, G3, B3, E4

# Color mappings (same as test visualizer)
CHROMATIC_COLORS = [
    (255, 0, 0),    # C
    (255, 69, 0),   # C#
    (255, 165, 0),  # D
    (255, 215, 0),  # D#
    (255, 255, 0),  # E
    (173, 255, 47), # F
    (0, 255, 0),    # F#
    (0, 206, 209),  # G
    (0, 0, 255),    # G#
    (138, 43, 226), # A
    (148, 0, 211),  # A#
    (199, 21, 133)  # B
]

class GuitarVisualizer(BaseVisualizer):
    def __init__(self):
        print("Initializing Guitar Visualizer...")
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
        pygame.display.set_caption("Guitar Visualizer")

        # Add input mode toggle
        self.local_input_enabled = True
        
        # Initialize status messages
        self.mqtt_status = "MQTT: Not connected"
        self.last_midi_message = "No MIDI connected"

        # Generate unique client ID
        self.client_id = f"guitar_{uuid.uuid4().hex[:8]}"
        self.instrument_type = "guitar"
        
        # MQTT setup
        print("\nSetting up MQTT...")
        try:
            self.mqtt = MusicMQTTClient(self.client_id, self.instrument_type)
            if self.mqtt.connect():
                self.mqtt_status = f"MQTT: Connected ({self.client_id})"
                for instrument in ['piano', 'drums', 'bass', 'guitar']:
                    self.mqtt.register_callback(instrument, self._handle_remote_notes)
        except Exception as e:
            self.mqtt_status = f"MQTT: Error - {str(e)}"

        # Initialize note storage
        self.local_notes = set()
        self.remote_notes = {}
        
        # Create fretboard matrix
        self.matrix = self.create_fretboard_matrix()

        # MIDI setup
        self.midi_input = None
        self.setup_midi()

        # WLED setup
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def create_fretboard_matrix(self):
        """Create matrix of notes for each fret position"""
        matrix = []
        for string in range(STRINGS):
            string_notes = []
            for fret in range(FRETS):
                note = TUNING[string] + fret
                string_notes.append(note)
            matrix.append(string_notes)
        return matrix

    def draw_fretboard(self):
        """Draw guitar fretboard visualization"""
        fret_width = self.width // FRETS
        string_height = self.height // (STRINGS + 1)

        # Draw frets
        for fret in range(FRETS):
            x = fret * fret_width
            pygame.draw.line(self.screen, (100, 100, 100), 
                           (x, string_height), 
                           (x, self.height - string_height))

        # Draw strings and notes
        for string in range(STRINGS):
            y = (string + 1) * string_height
            pygame.draw.line(self.screen, (150, 150, 150), 
                           (0, y), 
                           (self.width, y))
            
            for fret in range(FRETS):
                x = fret * fret_width + fret_width // 2
                note = self.matrix[string][fret]
                note_class = note % 12
                base_color = CHROMATIC_COLORS[note_class]
                
                is_local = note in self.local_notes
                is_remote = any(note in notes for notes in self.remote_notes.values())
                
                if is_local:
                    # Local note: White
                    color = (255, 255, 255)
                elif is_remote:
                    # Remote note: Colorful
                    color = base_color
                else:
                    # Inactive note
                    color = tuple(int(c * 0.3) for c in base_color)

                pygame.draw.circle(self.screen, color, (x, y), 10)

    def create_wled_data(self) -> bytes:
        """Create WLED data packet"""
        data = []
        for string in range(STRINGS):
            for fret in range(FRETS):
                note = self.matrix[string][fret]
                note_class = note % 12
                color = CHROMATIC_COLORS[note_class]
                
                if note in self.local_notes or any(note in notes for notes in self.remote_notes.values()):
                    color = tuple(min(int(c * 1.5), 255) for c in color)
                else:
                    color = tuple(int(c * 0.1) for c in color)
                
                data.extend(color)
        return bytes(data)

    def draw(self):
        """Implementation of abstract method from BaseVisualizer"""
        try:
            self.screen.fill((0, 0, 0))
            self.draw_fretboard()
            
            # Status display
            info_text = (
                f"Mode: {'LOCAL' if self.local_input_enabled else 'REMOTE'} | "
                f"{self.mqtt_status} | "
                f"MIDI: {self.last_midi_message} | "
                f"Press 't' to toggle mode | 'm' to rescan MIDI | 'q' to quit"
            )
            self.draw_info(info_text)
            
            # Update WLED
            led_data = self.create_wled_data()
            self.send_wled_data(led_data)
            
        except Exception as e:
            print(f"Error in draw method: {e}")

    def handle_events(self) -> bool:
        """Implementation of abstract method from BaseVisualizer"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_m:
                    print("Rescanning MIDI devices...")
                    self.setup_midi()
                elif event.key == pygame.K_t:
                    self.local_input_enabled = not self.local_input_enabled
                    mode = "LOCAL" if self.local_input_enabled else "REMOTE"
                    print(f"\nSwitched to {mode} input mode")
                    if not self.local_input_enabled:
                        self.local_notes.clear()
                        self.mqtt.publish_notes(self.local_notes)
        return True

    def setup_midi(self):
        """Set up MIDI input with device switching"""
        try:
            # Get fresh list of devices
            self.midi_devices = mido.get_input_names()
            print(f"\nAvailable MIDI devices: {self.midi_devices}")
            
            if self.midi_devices:
                # Close existing connection if any
                if self.midi_input:
                    try:
                        self.midi_input.close()
                        self.midi_input = None
                        time.sleep(0.1)  # Give it time to close
                    except:
                        print("Error closing previous MIDI device")

                # Update device index
                self.current_midi_device_index = (self.current_midi_device_index + 1) % len(self.midi_devices)
                device_name = self.midi_devices[self.current_midi_device_index]
                
                print(f"Attempting to connect to: {device_name} (Device {self.current_midi_device_index + 1} of {len(self.midi_devices)})")
                
                self.midi_input = mido.open_input(device_name)
                self.last_midi_message = f"Connected to: {device_name}"
                print(f"Successfully connected to MIDI device: {device_name}")
                
                # Start MIDI listener thread
                midi_thread = threading.Thread(target=self.midi_listener, daemon=True)
                midi_thread.start()
            else:
                print("No MIDI devices found")
                self.last_midi_message = "No devices found"
                self.current_midi_device_index = -1
        except Exception as e:
            print(f"MIDI setup error: {e}")
            self.last_midi_message = f"Error: {str(e)}"
            self.current_midi_device_index = -1

    def midi_listener(self):
        """Listen for MIDI messages"""
        print("Starting MIDI listener...")
        try:
            while self.midi_input:
                for message in self.midi_input.iter_pending():
                    # Only process MIDI input if local input is enabled
                    if self.local_input_enabled:
                        if message.type == 'note_on' and message.velocity > 0:
                            self.handle_local_note(message.note, True)
                            print(f"LOCAL MIDI Note ON: {message.note}")
                        elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                            self.handle_local_note(message.note, False)
                            print(f"LOCAL MIDI Note OFF: {message.note}")
                time.sleep(0.001)
        except Exception as e:
            print(f"MIDI listener error: {e}")
        finally:
            print("MIDI listener ended")

    def handle_local_note(self, note: int, is_on: bool):
        """Handle local MIDI note and publish to MQTT"""
        if is_on:
            self.local_notes.add(note)
        else:
            self.local_notes.discard(note)
        
        # Publish updated notes via MQTT
        self.mqtt.publish_notes(self.local_notes)

    def _handle_remote_notes(self, data: dict):
        """Handle remote notes from other instruments"""
        source_id = data["client_id"]
        instrument = data["instrument"]
        notes = set(data["notes"])
        old_notes = self.remote_notes.get(source_id, set())
        
        # Find new and removed notes
        new_notes = notes - old_notes
        removed_notes = old_notes - notes
        
        if new_notes:
            print(f"REMOTE MQTT Note ON from {instrument} ({source_id}): {new_notes}")
        if removed_notes:
            print(f"REMOTE MQTT Note OFF from {instrument} ({source_id}): {removed_notes}")
            
        self.remote_notes[source_id] = notes
        self.mqtt_status = f"MQTT: Last msg from {instrument} ({source_id})"

    def send_wled_data(self, data: bytes):
        """Send data to WLED"""
        try:
            packet = bytearray([2, 255])  # WARLS protocol
            packet.extend(data)
            self.udp_socket.sendto(packet, (WLED_IP, WLED_PORT))
        except Exception as e:
            print(f"WLED communication error: {e}")

if __name__ == "__main__":
    print("Starting Guitar Visualizer...")
    visualizer = GuitarVisualizer()
    visualizer.run() 