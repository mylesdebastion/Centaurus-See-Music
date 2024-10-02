import time
import socket
import json
from typing import List, Tuple

# WLED Controller settings
WLED_IP = "192.168.0.17"
WLED_PORT = 21324  # Default WLED UDP port

# Guitar fretboard settings
FRETS = 25
STRINGS = 6

# Note and color mappings
NOTE_NAMES = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']
CHROMATIC_COLORS = [
    (255, 0, 0), (255, 69, 0), (255, 165, 0), (255, 215, 0), (255, 255, 0), (173, 255, 47),
    (0, 255, 0), (0, 206, 209), (0, 0, 255), (138, 43, 226), (148, 0, 211), (199, 21, 133)
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
    # Add more progressions here if needed
]

def create_fretboard_matrix() -> List[List[int]]:
    return [[(open_note + fret) % 12 for fret in range(FRETS)] for open_note in STANDARD_TUNING]

def is_note_active(string: int, fret: int, active_notes: List[Tuple[int, int]]) -> bool:
    return any(s == string and f == fret for s, f in active_notes)

def get_note_color(note: int, active: bool) -> Tuple[int, int, int]:
    color = CHROMATIC_COLORS[note]
    return color if active else tuple(max(1, c // 10) for c in color)

def create_wled_data(matrix: List[List[int]], active_notes: List[Tuple[int, int]]) -> List[int]:
    led_data = []
    for string in range(STRINGS):
        for fret in range(FRETS):
            note = matrix[string][fret]
            active = is_note_active(string, fret, active_notes)
            color = get_note_color(note, active)
            led_data.extend(color)
    return led_data

def send_udp_packet(data: List[int]):
    packet = bytearray([2, 4])  # WARLS protocol
    packet.extend(data)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(packet, (WLED_IP, WLED_PORT))

def main():
    matrix = create_fretboard_matrix()
    progression = CHORD_PROGRESSIONS[0]  # Use the first progression
    
    while True:
        for chord in progression["chords"]:
            print(f"Playing chord: {chord['name']}")
            led_data = create_wled_data(matrix, chord["notes"])
            send_udp_packet(led_data)
            time.sleep(5)  # Wait for 5 seconds before the next chord

if __name__ == "__main__":
    main()
