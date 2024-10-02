import pygame
import socket
import time
import math
from typing import List, Tuple
import numpy as np

# WLED Controller settings
WLED_IP = "192.168.0.17"
WLED_PORT = 21324  # Default WLED UDP port

# Guitar fretboard settings
FRETS = 25
STRINGS = 6

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400
FPS = 30

# Audio settings
SAMPLE_RATE = 44100
DURATION = 0.5  # Duration of each note in seconds
VOLUME = 0.5  # Volume of the notes (0.0 to 1.0)

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
STANDARD_TUNING = [4, 9, 2, 7, 11, 4]  # E A D G B E

CHORD_PROGRESSIONS = [
    {
        "name": "Jazz ii-V-I in C",
        "chords": [
            {"name": "Dm7", "notes": [[1, 1], [2, 1], [3, 2], [4, 3]]},
            {"name": "G7", "notes": [[1, 1], [2, 0], [3, 0], [4, 0], [5, 2]]},
            {"name": "Cmaj7", "notes": [[1, 0], [2, 3], [3, 2], [4, 0], [5, 0]]},
        ]
    },
    {
        "name": "Blues in A",
        "chords": [
            {"name": "A7", "notes": [[1, 0], [2, 2], [3, 0], [4, 2], [5, 0]]},
            {"name": "D7", "notes": [[1, 2], [2, 1], [3, 2], [4, 0], [5, 2]]},
            {"name": "E7", "notes": [[1, 0], [2, 0], [3, 1], [4, 0], [5, 2], [6, 0]]},
        ]
    },
    {
        "name": "Pop I-V-vi-IV in G",
        "chords": [
            {"name": "G", "notes": [[1, 3], [2, 0], [3, 0], [4, 0], [5, 2], [6, 3]]},
            {"name": "D", "notes": [[1, 2], [2, 3], [3, 2], [4, 0], [5, 0]]},
            {"name": "Em", "notes": [[1, 0], [2, 0], [3, 0], [4, 2], [5, 2]]},
            {"name": "C", "notes": [[1, 0], [2, 1], [3, 0], [4, 2], [5, 3]]},
        ]
    }
]

class GuitarFretboardVisualizer:
    def __init__(self):
        print("Initializing GuitarFretboardVisualizer...")
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
        print("Pygame initialized.")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Guitar Fretboard Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.current_progression = 0
        self.current_chord = 0
        self.color_mapping = "chromatic"
        self.matrix = self.create_fretboard_matrix()
        
        self.last_chord_change = time.time()
        print("Generating tones...")
        self.generate_tones()
        print("Initialization complete.")

    def create_fretboard_matrix(self) -> List[List[int]]:
        print("Creating fretboard matrix...")
        return [[(open_note + fret) % 12 for fret in range(FRETS)] for open_note in STANDARD_TUNING]

    def generate_tones(self):
        self.tones = {}
        for i in range(12):
            frequency = 440 * (2 ** ((i - 9) / 12))  # A4 = 440Hz
            samples = np.arange(int(SAMPLE_RATE * DURATION)) / SAMPLE_RATE
            wave = np.sin(2 * np.pi * frequency * samples)
            envelope = np.exp(-samples * 4)  # Add a simple decay envelope
            sound = (wave * envelope * 32767).astype(np.int16)
            stereo_sound = np.column_stack((sound, sound))  # Create stereo sound
            self.tones[i] = pygame.sndarray.make_sound(stereo_sound)
        print(f"Generated {len(self.tones)} tones.")

    def play_note(self, note: int):
        self.tones[note].play()

    def play_chord(self, chord_notes: List[Tuple[int, int]]):
        for string, fret in chord_notes:
            # Adjust string number to 0-based index
            string_index = string - 1
            if 0 <= string_index < STRINGS and 0 <= fret < FRETS:
                note = self.matrix[string_index][fret]
                self.play_note(note)
            else:
                print(f"Warning: Invalid string or fret number: string {string}, fret {fret}")

    def is_note_active(self, string: int, fret: int, active_notes: List[Tuple[int, int]]) -> bool:
        return any(s - 1 == string and f == fret for s, f in active_notes)

    def get_note_color(self, note: int, active: bool) -> Tuple[int, int, int]:
        colors = CHROMATIC_COLORS if self.color_mapping == "chromatic" else HARMONIC_COLORS
        color = colors[note]
        return color if active else tuple(max(1, c // 10) for c in color)

    def create_wled_data(self, active_notes: List[Tuple[int, int]]) -> List[int]:
        led_data = []
        for string in range(STRINGS):
            for fret in range(FRETS):
                note = self.matrix[string][fret]
                active = self.is_note_active(string, fret, active_notes)
                color = self.get_note_color(note, active)
                led_data.extend(color)
        return led_data

    def send_udp_packet(self, data: List[int]):
        packet = bytearray([2, 255])  # WARLS protocol with 255 as the second byte
        packet.extend(data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(packet, (WLED_IP, WLED_PORT))

    def draw_fretboard(self, active_notes: List[Tuple[int, int]]):
        fret_width = SCREEN_WIDTH // FRETS
        string_height = SCREEN_HEIGHT // (STRINGS + 1)
        
        for string in range(STRINGS):
            for fret in range(FRETS):
                note = self.matrix[string][fret]
                active = self.is_note_active(string, fret, active_notes)
                color = self.get_note_color(note, active)
                
                x = fret * fret_width
                y = (string + 1) * string_height
                
                pygame.draw.circle(self.screen, color, (x + fret_width // 2, y), fret_width // 3)
                
                if active:
                    pygame.draw.circle(self.screen, (255, 255, 255), (x + fret_width // 2, y), fret_width // 4, 2)

        # Draw fret numbers
        for fret in range(FRETS):
            text = self.font.render(str(fret), True, (200, 200, 200))
            self.screen.blit(text, (fret * fret_width + fret_width // 2 - 10, SCREEN_HEIGHT - 30))

    def draw_info(self):
        progression = CHORD_PROGRESSIONS[self.current_progression]
        chord = progression["chords"][self.current_chord]
        
        info_text = f"Progression (n): {progression['name']} | Chord: {chord['name']} | Mapping (c): {self.color_mapping.capitalize()} | Quit (q)"
        text = self.font.render(info_text, True, (200, 200, 200))
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, 20)  # Center the text horizontally and position it at the top
        self.screen.blit(text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.current_progression = (self.current_progression + 1) % len(CHORD_PROGRESSIONS)
                    self.current_chord = 0
                    # Play the first chord of the new progression
                    new_chord = CHORD_PROGRESSIONS[self.current_progression]["chords"][self.current_chord]
                    self.play_chord(new_chord["notes"])
                elif event.key == pygame.K_c:
                    self.color_mapping = "harmonic" if self.color_mapping == "chromatic" else "chromatic"
                elif event.key == pygame.K_q:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
        return True

    def handle_mouse_click(self, pos):
        fret_width = SCREEN_WIDTH // FRETS
        string_height = SCREEN_HEIGHT // (STRINGS + 1)
        
        for string in range(STRINGS):
            for fret in range(FRETS):
                x = fret * fret_width
                y = (string + 1) * string_height
                
                if (x < pos[0] < x + fret_width) and (y - string_height // 2 < pos[1] < y + string_height // 2):
                    note = self.matrix[string][fret]
                    self.play_note(note)
                    self.highlight_and_send_led(string, fret)
                    return

    def highlight_and_send_led(self, string, fret):
        led_data = [0] * (FRETS * STRINGS * 3)  # Initialize all LEDs as off
        note = self.matrix[string][fret]
        color = self.get_note_color(note, True)
        index = (string * FRETS + fret) * 3
        led_data[index:index+3] = color
        self.send_udp_packet(led_data)

    def run(self):
        print("Starting main loop...")
        running = True
        last_chord = None
        while running:
            running = self.handle_events()
            
            self.screen.fill((0, 0, 0))
            
            progression = CHORD_PROGRESSIONS[self.current_progression]
            chord = progression["chords"][self.current_chord]
            
            # Play chord if it has changed
            if chord != last_chord:
                self.play_chord(chord["notes"])
                last_chord = chord
            
            self.draw_fretboard(chord["notes"])
            self.draw_info()
            
            led_data = self.create_wled_data(chord["notes"])
            self.send_udp_packet(led_data)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
            if time.time() - self.last_chord_change > 5:
                self.current_chord = (self.current_chord + 1) % len(progression["chords"])
                self.last_chord_change = time.time()

        print("Main loop ended. Quitting Pygame...")
        pygame.quit()

if __name__ == "__main__":
    print("Script started.")
    visualizer = GuitarFretboardVisualizer()
    print("Visualizer created. Running...")
    visualizer.run()
    print("Script ended.")
