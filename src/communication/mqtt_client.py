import paho.mqtt.client as mqtt
import json
from typing import Dict, Callable, Set
import threading
import time

class MusicMQTTClient:
    def __init__(self, client_id: str, instrument_type: str):
        self.client_id = client_id
        self.instrument_type = instrument_type
        
        # Create MQTT client with protocol v5
        self.client = mqtt.Client(
            client_id=client_id,
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        
        # MQTT topics
        self.base_topic = "centaurus/music"
        self.notes_topic = f"{self.base_topic}/notes/{instrument_type}"
        self.status_topic = f"{self.base_topic}/status/{instrument_type}/{client_id}"
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.callbacks: Dict[str, Callable] = {}
        self.connected = False

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback when connected to MQTT broker"""
        if reason_code.is_successful:
            print(f"Connected to MQTT broker with result code: {reason_code}")
            self.connected = True
            # Resubscribe to topics
            for topic in self.callbacks.keys():
                self.client.subscribe(topic)
        else:
            print(f"Failed to connect to MQTT broker: {reason_code}")

    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            if msg.topic in self.callbacks:
                payload = json.loads(msg.payload.decode())
                self.callbacks[msg.topic](payload)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """Callback when disconnected"""
        print(f"Disconnected from MQTT broker with result code: {reason_code}")
        self.connected = False

    def connect(self, broker: str = "localhost", port: int = 1883) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client.connect(broker, port)
            self.client.loop_start()
            
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
        if self.connected:
            # Publish offline status
            self.client.publish(
                self.status_topic,
                json.dumps({"status": "offline", "client_id": self.client_id}),
                retain=True
            )
            self.client.loop_stop()
            self.client.disconnect()

    def publish_notes(self, notes: Set[int]):
        """Publish current notes"""
        if self.connected:
            try:
                payload = json.dumps({
                    "client_id": self.client_id,
                    "instrument": self.instrument_type,
                    "notes": list(notes)
                })
                self.client.publish(self.notes_topic, payload)
            except Exception as e:
                print(f"Error publishing notes: {e}")

    def register_callback(self, instrument_type: str, callback: Callable):
        """Register callback for receiving notes from specific instrument type"""
        topic = f"{self.base_topic}/notes/{instrument_type}"
        self.callbacks[topic] = callback
        if self.connected:
            self.client.subscribe(topic)