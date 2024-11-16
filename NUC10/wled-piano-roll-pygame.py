import pygame
import socket
import time
from typing import List, Tuple
import pygame.gfxdraw
import mido

# WLED Controller settings
WLED_IP = "192.168.8.145"
WLED_PORT = 21324  # Default WLED UDP port

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400
FPS = 30

# Note and color mappings
NOTE_NAMES = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']
CHROMATIC_COLORS = [
    (255, 0, 0), (255, 69, 0), (255, 165, 0), (255, 215, 0), (255, 255, 0), (173, 255, 47),
    (0, 255, 0), (0, 206, 209), (0, 0, 255), (138, 43, 226), (148, 0, 211), (199, 21, 133)
]
HARMONIC_COLORS = [
    (255, 0, 0),    # C
    (0, 206, 209),  # C#
    (255, 165, 0),  # D
    (138, 43, 226), # D#
    (255, 255, 0),  # E
    (199, 21, 133), # F
    (0, 255, 0),    # F#
    (255, 69, 0),   # G
    (0, 0, 255),    # G#
    (255, 215, 0),  # A
    (148, 0, 211),  # A#
    (173, 255, 47)  # B
]

# Add piano constants
OCTAVES = 4  # Number of octaves to display
KEYS_PER_OCTAVE = 12
TOTAL_KEYS = OCTAVES * KEYS_PER_OCTAVE
WHITE_KEYS = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
BLACK_KEYS = [1, 3, 6, 8, 10]        # C#, D#, F#, G#, A#

class PianoVisualizer:
    def __init__(self):
        print("Initializing PianoVisualizer...")
        pygame.init()
        print("Pygame initialized.")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Piano Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        
        self.color_mapping = "chromatic"
        self.initial_brightness = 0.50
        self.midi_input = None
        self.midi_notes = set()
        self.midi_devices = mido.get_input_names()
        self.current_midi_device_index = -1
        self.last_midi_message = "No message"
        self.setup_midi()
        self.perform_mode = False
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def draw_piano(self):
        white_key_width = SCREEN_WIDTH // (len(WHITE_KEYS) * OCTAVES)
        white_key_height = SCREEN_HEIGHT * 0.8
        black_key_width = white_key_width * 0.6
        black_key_height = white_key_height * 0.6
        
        # Draw white keys
        x = 0
        for octave in range(OCTAVES):
            for key in WHITE_KEYS:
                note = octave * 12 + key
                color = (255, 255, 255)  # Default white
                if note % 12 in self.midi_notes:
                    color = CHROMATIC_COLORS[note % 12] if self.color_mapping == "chromatic" else HARMONIC_COLORS[note % 12]
                
                pygame.draw.rect(self.screen, color, 
                               (x, SCREEN_HEIGHT - white_key_height, 
                                white_key_width, white_key_height))
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (x, SCREEN_HEIGHT - white_key_height, 
                                white_key_width, white_key_height), 2)
                
                # Draw note name
                note_name = NOTE_NAMES[key]
                text = self.font.render(note_name, True, (0, 0, 0))
                text_rect = text.get_rect(center=(x + white_key_width/2, 
                                                SCREEN_HEIGHT - 30))
                self.screen.blit(text, text_rect)
                
                x += white_key_width
        
        # Draw black keys
        x = 0
        for octave in range(OCTAVES):
            for i, key in enumerate(WHITE_KEYS):
                if i < len(WHITE_KEYS) - 1:  # Don't check after last white key
                    if WHITE_KEYS[i + 1] - WHITE_KEYS[i] == 2:
                        note = octave * 12 + key + 1
                        color = (0, 0, 0)  # Default black
                        if note % 12 in self.midi_notes:
                            color = CHROMATIC_COLORS[note % 12] if self.color_mapping == "chromatic" else HARMONIC_COLORS[note % 12]
                        
                        pygame.draw.rect(self.screen, color,
                                       (x + white_key_width - black_key_width/2,
                                        SCREEN_HEIGHT - white_key_height,
                                        black_key_width, black_key_height))
                x += white_key_width

    def handle_mouse_click(self, pos):
        white_key_width = SCREEN_WIDTH // (len(WHITE_KEYS) * OCTAVES)
        white_key_height = SCREEN_HEIGHT * 0.8
        black_key_width = white_key_width * 0.6
        black_key_height = white_key_height * 0.6
        
        # Check black keys first (they're on top)
        x = 0
        for octave in range(OCTAVES):
            for i, key in enumerate(WHITE_KEYS):
                if i < len(WHITE_KEYS) - 1:
                    if WHITE_KEYS[i + 1] - WHITE_KEYS[i] == 2:
                        black_key_x = x + white_key_width - black_key_width/2
                        if (black_key_x < pos[0] < black_key_x + black_key_width and
                            SCREEN_HEIGHT - white_key_height < pos[1] < SCREEN_HEIGHT - white_key_height + black_key_height):
                            note = octave * 12 + key + 1
                            self.midi_notes.add(note % 12)
                            pygame.time.set_timer(pygame.USEREVENT, 500)
                            return
                x += white_key_width
        
        # Then check white keys
        x = 0
        for octave in range(OCTAVES):
            for key in WHITE_KEYS:
                if (x < pos[0] < x + white_key_width and
                    SCREEN_HEIGHT - white_key_height < pos[1] < SCREEN_HEIGHT):
                    note = octave * 12 + key
                    self.midi_notes.add(note % 12)
                    pygame.time.set_timer(pygame.USEREVENT, 500)
                    return
                x += white_key_width

    def get_note_color(self, note: int) -> Tuple[int, int, int]:
        # If note is active (in midi_notes), return its color
        if note % 12 in self.midi_notes:
            if self.color_mapping == "chromatic":
                return CHROMATIC_COLORS[note % 12]
            else:
                return HARMONIC_COLORS[note % 12]
        
        # If note is not active, return black (off)
        return (0, 0, 0)

    def create_wled_data(self) -> List[int]:
        led_data = []
        for note in range(TOTAL_KEYS):
            color = self.get_note_color(note)
            led_data.extend(color)
        return led_data

    def send_udp_packet(self, data: List[int]):
        packet = bytearray([2, 255])  # WARLS protocol with 255 as the second byte
        packet.extend(data)
        self.udp_socket.sendto(packet, (WLED_IP, WLED_PORT))

    def draw_info(self):
        midi_device = self.midi_devices[self.current_midi_device_index] if self.midi_input else "None"
        midi_info = f"MIDI Input Device [M]: {midi_device} [{self.last_midi_message}]"
        
        info_text = (f"Mapping (c): {self.color_mapping.capitalize()} | "
                    f"{midi_info} | "
                    f"Quit (q)")
        text = self.font.render(info_text, True, (200, 200, 200))
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, 20)
        self.screen.blit(text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.color_mapping = "harmonic" if self.color_mapping == "chromatic" else "chromatic"
                elif event.key == pygame.K_m:
                    self.setup_midi()
                elif event.key == pygame.K_q:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            elif event.type == pygame.USEREVENT:
                # Clear temporary notes from mouse clicks
                self.midi_notes.clear()
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Disable the timer
        
        # Handle MIDI input
        if self.midi_input:
            for message in self.midi_input.iter_pending():
                if message.type == 'note_on' and message.velocity > 0:
                    note = message.note % 12
                    self.midi_notes.add(note)
                elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                    self.midi_notes.discard(message.note % 12)
        return True

    def setup_midi(self):
        if self.midi_devices:
            self.current_midi_device_index = (self.current_midi_device_index + 1) % len(self.midi_devices)
            device_name = self.midi_devices[self.current_midi_device_index]
            try:
                if self.midi_input:
                    self.midi_input.close()
                self.midi_input = mido.open_input(device_name)
                print(f"Connected to MIDI input: {device_name}")
                
                # Start MIDI listening thread
                threading.Thread(target=self.midi_listener, daemon=True).start()
            except Exception as e:
                print(f"Error setting up MIDI: {e}")
                self.midi_input = None
        else:
            print("No MIDI input ports available.")

    def midi_listener(self):
        for message in self.midi_input:
            if message.type == 'note_on' and message.velocity > 0:
                self.midi_notes.add(message.note % 12)
            elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                self.midi_notes.discard(message.note % 12)

    def run(self):
        print("Starting main loop...")
        running = True
        try:
            while running:
                running = self.handle_events()
                
                self.screen.fill((0, 0, 0))
                self.draw_piano()
                self.draw_info()
                
                led_data = self.create_wled_data()
                self.send_udp_packet(led_data)
                
                pygame.display.flip()
                self.clock.tick(FPS)
                
        finally:
            print("Closing UDP socket...")
            self.udp_socket.close()
            if self.midi_input:
                print("Closing MIDI input...")
                self.midi_input.close()
            print("Main loop ended. Quitting Pygame...")
            pygame.quit()

if __name__ == "__main__":
    print("Script started.")
    visualizer = PianoVisualizer()
    print("Visualizer created. Running...")
    visualizer.run()
    print("Script ended.")