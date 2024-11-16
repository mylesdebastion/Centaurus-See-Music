import pygame
import socket
import time
from typing import List, Tuple
import pygame.gfxdraw
import mido

# WLED Controller settings
WLED_IP = "192.168.8.145"
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

TUNINGS = {
    "E Standard": [4, 9, 2, 7, 11, 4],    # E A D G B E
    "D Standard": [2, 7, 0, 5, 9, 2],     # D G C F A D
    "Drop D": [2, 9, 2, 7, 11, 4],        # D A D G B E
}

class GuitarFretboardVisualizer:
    def __init__(self):
        print("Initializing GuitarFretboardVisualizer...")
        pygame.init()
        print("Pygame initialized.")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Guitar Fretboard Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        
        self.color_mapping = "chromatic"
        self.current_tuning = "E Standard"
        self.matrix = self.create_fretboard_matrix()
        
        self.initial_brightness = 0.50
        self.midi_input = None
        self.midi_notes = set()
        self.midi_devices = mido.get_input_names()
        self.current_midi_device_index = -1
        self.last_midi_message = "No message"
        self.setup_midi()
        self.perform_mode = False
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def create_fretboard_matrix(self) -> List[List[int]]:
        print(f"Creating fretboard matrix for {self.current_tuning}...")
        return [[
            (open_note + fret) % 12 
            for fret in range(FRETS)
        ] for open_note in TUNINGS[self.current_tuning]]

    def cycle_tuning(self):
        # Get list of tunings and find current index
        tunings = list(TUNINGS.keys())
        current_index = tunings.index(self.current_tuning)
        # Cycle to next tuning
        self.current_tuning = tunings[(current_index + 1) % len(tunings)]
        # Update the fretboard matrix for new tuning
        self.matrix = self.create_fretboard_matrix()
        print(f"Switched to {self.current_tuning} tuning")

    def is_note_active(self, string: int, fret: int, active_notes: List[Tuple[int, int]]) -> bool:
        return any(s - 1 == string and f == fret for s, f in active_notes)

    def get_note_color(self, note: int) -> Tuple[int, int, int]:
        if self.perform_mode:
            # In perform mode, only show active MIDI notes
            if note % 12 in self.midi_notes:
                return CHROMATIC_COLORS[note] if self.color_mapping == "chromatic" else HARMONIC_COLORS[note]
            else:
                return (0, 0, 0)  # Off

        # Highlight MIDI input notes in white
        if note % 12 in self.midi_notes:
            return (255, 255, 255)  # White color for MIDI notes

        # Determine the base color for the note based on the current color mapping
        colors = CHROMATIC_COLORS if self.color_mapping == "chromatic" else HARMONIC_COLORS
        color = colors[note]
        
        # Return the color at initial brightness
        return tuple(int(c * self.initial_brightness) for c in color)

    def create_wled_data(self) -> List[int]:
        led_data = []
        for string in range(STRINGS):
            for fret in range(FRETS):
                note = self.matrix[string][fret]
                color = self.get_note_color(note)
                led_data.extend(color)
        return led_data

    def send_udp_packet(self, data: List[int]):
        packet = bytearray([2, 255])  # WARLS protocol with 255 as the second byte
        packet.extend(data)
        self.udp_socket.sendto(packet, (WLED_IP, WLED_PORT))

    def draw_fretboard(self):
        fret_width = SCREEN_WIDTH // FRETS
        string_height = SCREEN_HEIGHT // (STRINGS + 1)
        
        for string in range(STRINGS):
            for fret in range(FRETS):
                note = self.matrix[string][fret]
                x = fret * fret_width
                y = (string + 1) * string_height
                center = (x + fret_width // 2, y)
                
                # Determine colors based on current mapping
                outline_color = CHROMATIC_COLORS[note] if self.color_mapping == "chromatic" else HARMONIC_COLORS[note]
                
                # Draw base circle with outline
                pygame.draw.circle(self.screen, outline_color, center, fret_width // 3, 2)
                
                # If note is active via MIDI, highlight it
                if note % 12 in self.midi_notes:
                    pygame.draw.circle(self.screen, outline_color, center, fret_width // 3)
                    pygame.draw.circle(self.screen, (255, 255, 255), center, fret_width // 4, 2)
                
                # Draw note name
                note_name = NOTE_NAMES[note]
                text = self.font.render(note_name, True, outline_color)
                text_rect = text.get_rect(center=center)
                self.screen.blit(text, text_rect)

        # Draw fret numbers
        for fret in range(FRETS):
            text = self.font.render(str(fret), True, (200, 200, 200))
            self.screen.blit(text, (fret * fret_width + fret_width // 2 - 10, SCREEN_HEIGHT - 30))

    def draw_info(self):
        midi_device = self.midi_devices[self.current_midi_device_index] if self.midi_input else "None"
        midi_info = f"MIDI Input Device [M]: {midi_device} [{self.last_midi_message}]"
        
        info_text = (f"Mapping (c): {self.color_mapping.capitalize()} | "
                    f"Tuning (t): {self.current_tuning} | "
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
                elif event.key == pygame.K_t:
                    self.cycle_tuning()
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

    def handle_mouse_click(self, pos):
        fret_width = SCREEN_WIDTH // FRETS
        string_height = SCREEN_HEIGHT // (STRINGS + 1)
        
        for string in range(STRINGS):
            for fret in range(FRETS):
                x = fret * fret_width
                y = (string + 1) * string_height
                
                if (x < pos[0] < x + fret_width) and (y - string_height // 2 < pos[1] < y + string_height // 2):
                    note = self.matrix[string][fret]
                    # Add the note to midi_notes temporarily
                    self.midi_notes.add(note % 12)
                    # Optional: Remove the note after a short delay
                    pygame.time.set_timer(pygame.USEREVENT, 500)  # 500ms delay
                    return

    def highlight_and_send_led(self, string, fret):
        led_data = [0] * (FRETS * STRINGS * 3)  # Initialize all LEDs as off
        note = self.matrix[string][fret]
        color = self.get_note_color(note, True, True)
        index = (string * FRETS + fret) * 3
        led_data[index:index+3] = color
        self.send_udp_packet(led_data)

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
                self.draw_fretboard()
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
    visualizer = GuitarFretboardVisualizer()
    print("Visualizer created. Running...")
    visualizer.run()
    print("Script ended.")