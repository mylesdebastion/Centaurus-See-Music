import pygame
import socket
import time
import mido
from typing import Set
import threading

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400
FPS = 30

# WLED settings - Update this IP to match your WLED device
WLED_IP = "192.168.8.106"
WLED_PORT = 21324
NUM_LEDS = 144

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

class TestVisualizer:
    def __init__(self):
        print("Initializing Test Visualizer...")
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Test Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # MIDI setup
        print("Setting up MIDI...")
        self.midi_input = None
        self.midi_notes: Set[int] = set()
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
                        self.midi_notes.add(message.note)
                        print(f"Note ON: {message.note}")
                    elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                        self.midi_notes.discard(message.note)
                        print(f"Note OFF: {message.note}")
                time.sleep(0.001)
        except Exception as e:
            print(f"MIDI listener error: {e}")
        finally:
            print("MIDI listener ended")

    def draw_piano(self):
        """Draw piano visualization"""
        white_key_width = SCREEN_WIDTH // 28  # 4 octaves * 7 white keys
        white_key_height = SCREEN_HEIGHT * 0.8
        black_key_width = white_key_width * 0.6
        black_key_height = white_key_height * 0.6

        # Draw white keys
        x = 0
        for octave in range(4):  # 4 octaves
            for key in [0, 2, 4, 5, 7, 9, 11]:  # White key positions
                note = octave * 12 + key
                color = CHROMATIC_COLORS[key]
                
                # Brighten if note is active
                if note in self.midi_notes:
                    color = tuple(min(int(c * 1.5), 255) for c in color)
                else:
                    color = tuple(int(c * 0.5) for c in color)

                pygame.draw.rect(self.screen, color,
                               (x, SCREEN_HEIGHT - white_key_height,
                                white_key_width - 1, white_key_height))
                x += white_key_width

        # Draw black keys
        x = 0
        for octave in range(4):
            for i, key in enumerate([0, 2, 4, 5, 7, 9, 11]):
                if i < 6:  # Don't draw after last white key
                    if key in [0, 5]:  # After C and F
                        if i < 5:  # Don't draw after last white key
                            note = octave * 12 + key + 1
                            color = CHROMATIC_COLORS[(key + 1) % 12]
                            
                            # Brighten if note is active
                            if note in self.midi_notes:
                                color = tuple(min(int(c * 1.5), 255) for c in color)
                            else:
                                color = tuple(int(c * 0.3) for c in color)

                            pygame.draw.rect(self.screen, color,
                                           (x + white_key_width - black_key_width/2,
                                            SCREEN_HEIGHT - white_key_height,
                                            black_key_width, black_key_height))
                x += white_key_width

    def create_wled_data(self) -> bytes:
        """Create WLED data packet"""
        data = []
        for i in range(NUM_LEDS):
            note_index = (i * 12) // NUM_LEDS
            color = CHROMATIC_COLORS[note_index]
            
            # Brighten if any note in this section is active
            if any(note % 12 == note_index for note in self.midi_notes):
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

    def draw_info(self):
        """Draw information overlay"""
        info_text = f"MIDI Status: {self.last_midi_message} | Active Notes: {len(self.midi_notes)}"
        text = self.font.render(info_text, True, (200, 200, 200))
        self.screen.blit(text, (10, 10))

    def run(self):
        """Main loop"""
        print("Starting main loop...")
        running = True
        try:
            while running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            running = False
                        elif event.key == pygame.K_m:
                            print("Rescanning MIDI devices...")
                            self.setup_midi()

                # Clear screen
                self.screen.fill((0, 0, 0))

                # Draw visualizations
                self.draw_piano()
                self.draw_info()

                # Update WLED
                led_data = self.create_wled_data()
                self.send_wled_data(led_data)

                # Update display
                pygame.display.flip()
                self.clock.tick(FPS)

        finally:
            print("Cleaning up...")
            if self.midi_input:
                self.midi_input.close()
            self.udp_socket.close()
            pygame.quit()
            print("Cleanup complete.")

if __name__ == "__main__":
    print("Starting Test Visualizer...")
    visualizer = TestVisualizer()
    visualizer.run()