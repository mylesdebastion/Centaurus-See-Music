import socket
import time

# WLED controller IP and port
WLED_IP = "192.168.8.144"
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

def turn_on_led(index, r, g, b):
    """Turn on a specific LED with R-G-B values."""
    data = bytearray([2, index, r, g, b])
    send_udp_command(data)

def rgb_test_cycle(index, delay=0.5):
    """Cycle through R-G-B colors on a specific LED."""
    # Red
    turn_on_led(index, 255, 0, 0)
    time.sleep(delay)
    # Green
    turn_on_led(index, 0, 255, 0)
    time.sleep(delay)
    # Blue
    turn_on_led(index, 0, 0, 255)
    time.sleep(delay)

def main():
    # Turn off all LEDs
    turn_off_all_leds()
    time.sleep(1)

    # Test LED 1 with R-G-B cycle
    for _ in range(3):  # Repeat the cycle 3 times
        rgb_test_cycle(1)

    # Turn off all LEDs after the test
    turn_off_all_leds()

if __name__ == "__main__":
    main()
    sock.close()
