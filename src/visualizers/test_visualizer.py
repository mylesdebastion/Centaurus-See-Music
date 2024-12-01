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
WLED_IP = "192.168.8.106"
WLED_PORT = 21324
NUM_LEDS = 144

# Piano settings
START_NOTE = 36  # Start from C2
NUM_OCTAVES = 4
NOTES_PER_OCTAVE = 12
TOTAL_NOTES = NUM_OCTAVES * NOTES_PER_OCTAVE

# Color mappings
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

class TestVisualizer(BaseVisualizer):
    def __init__(self):
        print("Initializing Test Visualizer...")
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
        pygame.display.set_caption("Test Visualizer")

        # Add input mode toggle
        self.local_input_enabled = True  # Toggle for local MIDI input
        
        # Initialize status messages
        self.mqtt_status = "MQTT: Not connected"
        self.last_midi_message = "No MIDI connected"

        # Generate unique client ID and set instrument type
        self.client_id = f"test_{uuid.uuid4().hex[:8]}"
        self.instrument_type = "piano"
        
        # MQTT setup
        print("\nSetting up MQTT...")
        try:
            self.mqtt = MusicMQTTClient(self.client_id, self.instrument_type)
            print(f"Created MQTT client with ID: {self.client_id}")
            
            if self.mqtt.connect():
                self.mqtt_status = f"MQTT: Connected ({self.client_id})"
                print("Successfully connected to MQTT broker")
                # Subscribe to other instruments
                for instrument in ['guitar', 'drums', 'bass', 'piano']:
                    print(f"Subscribing to {instrument} messages...")
                    self.mqtt.register_callback(instrument, self._handle_remote_notes)
            else:
                self.mqtt_status = "MQTT: Connection failed"
                print("Failed to connect to MQTT broker")
        except Exception as e:
            self.mqtt_status = f"MQTT: Error - {str(e)}"
            print(f"MQTT setup error: {e}")

        # Initialize remote notes storage
        self.remote_notes = {}  # Store notes from other clients

        # MIDI setup
        print("Setting up MIDI...")
        self.midi_input = None
        self.last_midi_message = "No MIDI connected"
        self.setup_midi()

        # WLED setup
        print(f"Setting up WLED connection to {WLED_IP}:{WLED_PORT}")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Initialization complete.")

    def setup_midi(self):
        """Set up MIDI input"""
        try:
            midi_devices = mido.get_input_names()
            print(f"Available MIDI devices: {midi_devices}")
            
            if midi_devices:
                self.midi_input = mido.open_input(midi_devices[0])
                self.last_midi_message = f"Connected to: {midi_devices[0]}"
                print(f"Connected to MIDI device: {midi_devices[0]}")
                
                # Start MIDI listener thread
                midi_thread = threading.Thread(target=self.midi_listener, daemon=True)
                midi_thread.start()
            else:
                print("No MIDI devices found")
        except Exception as e:
            print(f"MIDI setup error: {e}")

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

    def draw(self):
        """Implementation of abstract method from BaseVisualizer"""
        try:
            self.screen.fill((0, 0, 0))
            self.draw_piano()
            
            # Update status text to show input mode
            mode_text = "LOCAL" if self.local_input_enabled else "REMOTE"
            info_text = (f"Mode: {mode_text} | "
                        f"{self.mqtt_status} | "
                        f"MIDI: {self.last_midi_message} | "
                        f"Local Notes: {len(self.local_notes)} | "
                        f"Remote Sources: {len(self.remote_notes)} "
                        f"(Notes: {sum(len(notes) for notes in self.remote_notes.values())}) | "
                        f"Press 't' to toggle mode | 'm' to rescan MIDI | 'q' to quit")
            self.draw_info(info_text)
            
            led_data = self.create_wled_data()
            self.send_wled_data(led_data)
            
        except Exception as e:
            print(f"Error in draw method: {e}")

    def draw_piano(self):
        """Draw piano visualization"""
        white_key_width = self.width // (NUM_OCTAVES * 7)  # 7 white keys per octave
        white_key_height = self.height * 0.8
        black_key_width = white_key_width * 0.6
        black_key_height = white_key_height * 0.6

        # Draw white keys
        x = 0
        white_notes = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
        white_key_positions = []  # Track positions for black keys
        for octave in range(NUM_OCTAVES):
            for i, white_note in enumerate(white_notes):
                note = START_NOTE + octave * 12 + white_note
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

                pygame.draw.rect(self.screen, color,
                               (x, self.height - white_key_height,
                                white_key_width - 1, white_key_height))
                
                # Draw note number with source indicator
                note_text = str(note)
                if note in self.local_notes:
                    note_text += "(L)"
                elif any(note in notes for notes in self.remote_notes.values()):
                    note_text += "(R)"
                text = self.font.render(note_text, True, (0, 0, 0))
                text_rect = text.get_rect(center=(x + white_key_width//2, 
                                                self.height - white_key_height + 20))
                self.screen.blit(text, text_rect)
                
                white_key_positions.append(x)  # Store position for black keys
                x += white_key_width

        # Draw black keys
        black_notes = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#
        black_key_offsets = [0, 1, 3, 4, 5]  # Position offsets for black keys in an octave
        for octave in range(NUM_OCTAVES):
            for offset in black_key_offsets:
                x = white_key_positions[octave * 7 + offset] + white_key_width * 0.75
                note = START_NOTE + octave * 12 + black_notes[black_key_offsets.index(offset)]
                note_class = note % 12
                color = CHROMATIC_COLORS[note_class]
                
                # Brighten if note is active (either local or remote)
                if note in self.local_notes or any(note in notes for notes in self.remote_notes.values()):
                    color = tuple(min(int(c * 1.5), 255) for c in color)
                else:
                    color = tuple(int(c * 0.3) for c in color)

                pygame.draw.rect(self.screen, color,
                               (x - black_key_width / 2, self.height - white_key_height,
                                black_key_width, black_key_height))
                
                # Draw note number with source indicator
                note_text = str(note)
                if note in self.local_notes:
                    note_text += "(L)"
                elif any(note in notes for notes in self.remote_notes.values()):
                    note_text += "(R)"
                text = self.font.render(note_text, True, (255, 255, 255))
                text_rect = text.get_rect(center=(x,
                                                self.height - white_key_height + black_key_height//2))
                self.screen.blit(text, text_rect)

    def create_wled_data(self) -> bytes:
        """Create WLED data packet"""
        data = []
        for i in range(NUM_LEDS):
            # Map LED position to MIDI note
            note = START_NOTE + (i * TOTAL_NOTES) // NUM_LEDS
            note_class = note % 12
            color = CHROMATIC_COLORS[note_class]
            
            # Brighten if note is active (either local or remote)
            if note in self.local_notes or any(note in notes for notes in self.remote_notes.values()):
                color = tuple(min(int(c * 1.5), 255) for c in color)
            else:
                color = tuple(int(c * 0.1) for c in color)
            
            data.extend(color)

        return bytes(data)

    def send_wled_data(self, data: bytes):
        """Send data to WLED"""
        try:
            packet = bytearray([2, 255])  # WARLS protocol
            packet.extend(data)
            self.udp_socket.sendto(packet, (WLED_IP, WLED_PORT))
        except Exception as e:
            print(f"WLED communication error: {e}")

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
                    # Toggle between local and remote mode
                    self.local_input_enabled = not self.local_input_enabled
                    mode = "LOCAL" if self.local_input_enabled else "REMOTE"
                    print(f"\nSwitched to {mode} input mode")
                    # Clear local notes when switching modes
                    if not self.local_input_enabled:
                        self.local_notes.clear()
                        self.mqtt.publish_notes(self.local_notes)  # Publish empty notes
        return True

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

    def handle_local_note(self, note: int, is_on: bool):
        """Handle local MIDI note and publish to MQTT"""
        if is_on:
            self.local_notes.add(note)
        else:
            self.local_notes.discard(note)
        
        # Publish updated notes via MQTT
        self.mqtt.publish_notes(self.local_notes)

    def cleanup(self):
        """Override cleanup to handle MIDI, MQTT and WLED"""
        print("Cleaning up...")
        if self.midi_input:
            self.midi_input.close()
        self.mqtt.disconnect()  # Add MQTT disconnect
        self.udp_socket.close()
        super().cleanup()
        print("Cleanup complete.")

if __name__ == "__main__":
    print("Starting Test Visualizer...")
    visualizer = TestVisualizer()
    visualizer.run()