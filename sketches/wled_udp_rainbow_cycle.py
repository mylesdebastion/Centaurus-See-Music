import socket
import time
import colorsys

# WLED controller IP and port
WLED_IP = "192.168.0.17"
WLED_PORT = 21324

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_command(data):
    """Send a UDP command to the WLED controller."""
    sock.sendto(data, (WLED_IP, WLED_PORT))

def turn_off_all_leds():
    """Turn off all LEDs."""
    data = bytearray([2, 0, 0, 0])  # Format: [Command, LED Index, R, G, B]
    send_udp_command(data)

def set_led_color(index, r, g, b):
    """Set a specific LED with R-G-B values."""
    data = bytearray([2, index, r, g, b])
    send_udp_command(data)

def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB color."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def rainbow_cycle(index, speed=0.01, brightness=1.0):
    """Cycle through the rainbow smoothly on a specific LED."""
    hue = 0.0
    while True:
        # Convert hue to RGB
        r, g, b = hsv_to_rgb(hue, 1.0, brightness)
        # Set LED color
        set_led_color(index, r, g, b)
        # Increment hue
        hue += speed
        if hue > 1.0:
            hue = 0.0
        time.sleep(0.01)  # Short delay for smooth transition

def main():
    # Turn off all LEDs initially
    turn_off_all_leds()
    time.sleep(1)

    # Run the rainbow cycle on LED 1
    try:
        rainbow_cycle(1)
    except KeyboardInterrupt:
        # Turn off all LEDs when exiting
        turn_off_all_leds()
        print("\nRainbow cycle stopped. All LEDs turned off.")

if __name__ == "__main__":
    main()
    sock.close()
