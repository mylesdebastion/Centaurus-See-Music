import pygame
import sys
import time

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400
FPS = 30

# WLED settings (update this IP to match your WLED device)
WLED_IP = "192.168.8.106"
WLED_PORT = 21324

def main():
    print("Starting basic test...")
    
    # Initialize Pygame
    print("Initializing Pygame...")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Basic Test")
    clock = pygame.time.Clock()
    
    print("Setup complete. Starting main loop...")
    running = True
    
    try:
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    print(f"Key pressed: {event.key}")
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Draw a simple rectangle that moves
            t = time.time()
            x = int((t * 100) % SCREEN_WIDTH)
            pygame.draw.rect(screen, (255, 0, 0), (x, SCREEN_HEIGHT//2, 50, 50))
            
            # Update display
            pygame.display.flip()
            clock.tick(FPS)
            
    except Exception as e:
        print(f"Error in main loop: {e}")
        
    finally:
        print("Cleaning up...")
        pygame.quit()
        print("Test ended.")

if __name__ == "__main__":
    main() 