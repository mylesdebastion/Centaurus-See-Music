import pygame
from typing import Set, Dict, Tuple
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
        
    @abstractmethod
    def draw(self):
        """Draw the visualization"""
        pass
        
    @abstractmethod
    def handle_events(self) -> bool:
        """Handle pygame events"""
        pass
        
    def draw_info(self, info_text: str):
        """Draw information overlay"""
        text = self.font.render(info_text, True, (200, 200, 200))
        text_rect = text.get_rect()
        text_rect.center = (self.width // 2, 20)
        self.screen.blit(text, text_rect)

    def run(self):
        """Main loop"""
        while self.running:
            self.running = self.handle_events()
            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        pygame.quit() 