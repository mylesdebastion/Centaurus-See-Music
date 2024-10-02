import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 3001)  # Listen on all interfaces on port 3001
sock.bind(server_address)

print(f"Listening for UDP packets on {server_address}")

while True:
    data, address = sock.recvfrom(4096)
    print(f"Received {data} from {address}")
