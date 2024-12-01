import pygame
from typing import Set, Dict, Tuple, Optional
from abc import ABC, abstractmethod

class BaseVisualizer(ABC):
    def __init__(self, width: int, height: int, fps: int = 30):
        pygame.init()
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.running = True
        
        # Note storage
        self.local_notes: Set[int] = set()  # Notes from local MIDI
        self.remote_notes: Dict[str, Set[int]] = {}  # Notes from MQTT {source_id: notes}
        
        # Common settings
        self.color_mapping: str = "chromatic"  # or "harmonic"
        self.test_mode: bool = False
        self.last_message: str = "No messages"
        
    @abstractmethod
    def draw(self):
        """Draw the visualization"""
        pass
        
    @abstractmethod
    def handle_events(self) -> bool:
        """Handle pygame events"""
        pass
    
    def handle_remote_notes(self, source_id: str, notes: Set[int]):
        """Handle incoming remote notes"""
        self.remote_notes[source_id] = notes
        
    def handle_local_note(self, note: int, is_on: bool):
        """Handle local MIDI note events"""
        if is_on:
            self.local_notes.add(note)
        else:
            self.local_notes.discard(note)
            
    def draw_info(self, info_text: str):
        """Draw information overlay"""
        text = self.font.render(info_text, True, (200, 200, 200))
        text_rect = text.get_rect()
        text_rect.center = (self.width // 2, 20)
        self.screen.blit(text, text_rect)

    def run(self):
        """Main loop"""
        try:
            while self.running:
                self.running = self.handle_events()
                self.screen.fill((0, 0, 0))
                self.draw()
                pygame.display.flip()
                self.clock.tick(self.fps)
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        pygame.quit()