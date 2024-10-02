import pygame
import socket
import time
from typing import List, Tuple

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
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Guitar Fretboard Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        self.current_progression = 0
        self.current_chord = 0
        self.color_mapping = "chromatic"
        self.matrix = self.create_fretboard_matrix()
        
        self.last_chord_change = time.time()

    def create_fretboard_matrix(self) -> List[List[int]]:
        return [[(open_note + fret) % 12 for fret in range(FRETS)] for open_note in STANDARD_TUNING]

    def is_note_active(self, string: int, fret: int, active_notes: List[Tuple[int, int]]) -> bool:
        return any(s == string and f == fret for s, f in active_notes)

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
        
        info_text = f"Progression: {progression['name']} | Chord: {chord['name']} | Mapping: {self.color_mapping}"
        text = self.font.render(info_text, True, (200, 200, 200))
        self.screen.blit(text, (10, 10))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.current_progression = (self.current_progression + 1) % len(CHORD_PROGRESSIONS)
                    self.current_chord = 0
                elif event.key == pygame.K_c:
                    self.color_mapping = "harmonic" if self.color_mapping == "chromatic" else "chromatic"
                elif event.key == pygame.K_q:
                    return False
        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            self.screen.fill((0, 0, 0))
            
            progression = CHORD_PROGRESSIONS[self.current_progression]
            chord = progression["chords"][self.current_chord]
            
            self.draw_fretboard(chord["notes"])
            self.draw_info()
            
            led_data = self.create_wled_data(chord["notes"])
            self.send_udp_packet(led_data)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
            if time.time() - self.last_chord_change > 5:
                self.current_chord = (self.current_chord + 1) % len(progression["chords"])
                self.last_chord_change = time.time()

        pygame.quit()

if __name__ == "__main__":
    visualizer = GuitarFretboardVisualizer()
    visualizer.run()
