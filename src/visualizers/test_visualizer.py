import pygame
import socket
import time
import mido
from typing import Set
import threading
from .base_visualizer import BaseVisualizer

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
                    if message.type == 'note_on' and message.velocity > 0:
                        self.handle_local_note(message.note, True)
                        print(f"Note ON: {message.note}")
                    elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                        self.handle_local_note(message.note, False)
                        print(f"Note OFF: {message.note}")
                time.sleep(0.001)
        except Exception as e:
            print(f"MIDI listener error: {e}")
        finally:
            print("MIDI listener ended")

    def draw(self):
        """Implementation of abstract method from BaseVisualizer"""
        try:
            # Clear screen first
            self.screen.fill((0, 0, 0))
            
            # Draw piano keys
            self.draw_piano()
            
            # Draw info text
            info_text = f"MIDI: {self.last_midi_message} | Press 'm' to rescan MIDI devices | 'q' to quit"
            self.draw_info(info_text)
            
            # Update WLED
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
                color = CHROMATIC_COLORS[note_class]
                
                # Brighten if note is active
                if note in self.local_notes:
                    color = tuple(min(int(c * 1.5), 255) for c in color)
                else:
                    color = tuple(int(c * 0.5) for c in color)

                pygame.draw.rect(self.screen, color,
                               (x, self.height - white_key_height,
                                white_key_width - 1, white_key_height))
                
                # Draw note number
                text = self.font.render(str(note), True, (0, 0, 0))
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
                
                # Brighten if note is active
                if note in self.local_notes:
                    color = tuple(min(int(c * 1.5), 255) for c in color)
                else:
                    color = tuple(int(c * 0.3) for c in color)

                pygame.draw.rect(self.screen, color,
                               (x - black_key_width / 2, self.height - white_key_height,
                                black_key_width, black_key_height))
                
                # Draw note number on black key
                text = self.font.render(str(note), True, (255, 255, 255))
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
            
            # Brighten if note is active
            if note in self.local_notes:
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
        return True

    def cleanup(self):
        """Override cleanup to handle MIDI and WLED"""
        print("Cleaning up...")
        if self.midi_input:
            self.midi_input.close()
        self.udp_socket.close()
        super().cleanup()  # Call parent cleanup
        print("Cleanup complete.")

if __name__ == "__main__":
    print("Starting Test Visualizer...")
    visualizer = TestVisualizer()
    visualizer.run()