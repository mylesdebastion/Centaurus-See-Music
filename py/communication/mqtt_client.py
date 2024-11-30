import paho.mqtt.client as mqtt
import json
from typing import Callable, Dict, Set
import threading
import time

class MusicMQTTClient:
    def __init__(self, client_id: str, instrument_type: str):
        """
        Initialize MQTT client for music communication
        
        Args:
            client_id: Unique identifier for this client
            instrument_type: Type of instrument ('piano', 'guitar', etc.)
        """
        self.client_id = client_id
        self.instrument_type = instrument_type
        self.client = mqtt.Client(client_id)
        self.active_notes: Set[int] = set()
        self.callbacks: Dict[str, Callable] = {}
        
        # MQTT topics
        self.base_topic = "centaurus/music"
        self.notes_topic = f"{self.base_topic}/notes/{instrument_type}"
        self.status_topic = f"{self.base_topic}/status/{instrument_type}/{client_id}"
        
        # Set up MQTT callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Threading control
        self.running = False
        self.thread = None

    def connect(self, broker: str = "localhost", port: int = 1883):
        """Connect to MQTT broker"""
        try:
            self.client.connect(broker, port)
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            
            # Publish online status
            self.client.publish(
                self.status_topic,
                json.dumps({"status": "online", "client_id": self.client_id}),
                retain=True
            )
            return True
        except Exception as e:
            print(f"MQTT Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # Publish offline status
        self.client.publish(
            self.status_topic,
            json.dumps({"status": "offline", "client_id": self.client_id}),
            retain=True
        )
        self.client.disconnect()

    def publish_notes(self, notes: Set[int], velocity: int = 127):
        """Publish active notes"""
        message = {
            "client_id": self.client_id,
            "instrument": self.instrument_type,
            "notes": list(notes),
            "velocity": velocity,
            "timestamp": time.time()
        }
        self.client.publish(self.notes_topic, json.dumps(message))

    def register_callback(self, instrument_type: str, callback: Callable):
        """Register callback for receiving notes from specific instrument type"""
        topic = f"{self.base_topic}/notes/{instrument_type}"
        self.callbacks[topic] = callback
        self.client.subscribe(topic)

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection to broker"""
        if rc == 0:
            print(f"Connected to MQTT broker (ID: {self.client_id})")
            # Subscribe to all instrument channels
            self.client.subscribe(f"{self.base_topic}/notes/#")
        else:
            print(f"Connection failed with code {rc}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        try:
            data = json.loads(msg.payload)
            if data["client_id"] != self.client_id:  # Ignore own messages
                if msg.topic in self.callbacks:
                    self.callbacks[msg.topic](data)
        except Exception as e:
            print(f"Error processing message: {e}")

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection from broker"""
        print(f"Disconnected from MQTT broker with code: {rc}")
        if rc != 0:
            print("Unexpected disconnection. Attempting to reconnect...")
            self.connect()

    def _run_loop(self):
        """Run the MQTT client loop"""
        while self.running:
            try:
                self.client.loop()
                time.sleep(0.001)
            except Exception as e:
                print(f"Error in MQTT loop: {e}")
                break