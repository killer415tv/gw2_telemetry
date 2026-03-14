#!/usr/bin/env python3
"""
GW2 Player Position Telemetry via MQTT
Reads player position from Guild Wars 2 via MumbleLink and publishes to MQTT broker.

Based on the working implementation from speedometer.py
"""

import json
import time
import paho.mqtt.client as mqtt
from mumblelink import MumbleLink
from datetime import datetime

# ======================
# CONFIGURATION SECTION
# ======================

# MQTT Settings
MQTT_BROKER = "www.beetlerank.com"  # Your public MQTT server
MQTT_PORT = 1883                    # Default MQTT port
MQTT_TOPIC = "gw2/players/position" # Topic to publish position data
MQTT_CLIENT_ID = f"gw2_player_{int(time.time())}"  # Unique client ID
# MQTT_USERNAME = "your_username"   # Uncomment if needed
# MQTT_PASSWORD = "your_password"   # Uncomment if needed

# Update frequency (seconds)
MIN_UPDATE_INTERVAL = 0.5   # Minimum time between updates (500ms) - won't publish faster than this

# ======================
# MQTT CALLBACKS
# ======================

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the MQTT broker."""
    if rc == 0:
        print(f"Connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the MQTT broker."""
    print(f"Disconnected from MQTT broker with result code {rc}")

def on_publish(client, userdata, mid):
    """Callback for when a message is published."""
    pass  # Uncomment for debug: print(f"Message {mid} published")

# ======================
# MAIN APPLICATION
# ======================

def main():
    """Main application loop."""
    print("Starting GW2 MQTT Telemetry Client")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic: {MQTT_TOPIC}")
    print(f"Min Update Interval: {MIN_UPDATE_INTERVAL}s")
    print("-" * 50)
    
    # Setup MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    
    # Uncomment if authentication is required
    # if MQTT_USERNAME and MQTT_PASSWORD:
    #     client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Connect to broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        print("Please check:")
        print("1. The broker address and port are correct")
        print("2. The broker is accessible from your network")
        print("3. No firewall is blocking the connection")
        return
    
    # Start the MQTT network loop in a separate thread
    client.loop_start()
    
    print("Connected to MQTT broker. Waiting for Guild Wars 2...")
    print("Make sure Guild Wars 2 is running and you're in-game.")
    print("-" * 50)
    
    # Initialize MumbleLink reader
    try:
        ml = MumbleLink()
        print("Successfully initialized MumbleLink connection")
    except Exception as e:
        print(f"Failed to initialize MumbleLink: {e}")
        print("Make sure Guild Wars 2 is running")
        client.loop_stop()
        client.disconnect()
        return
    
    last_position = None
    last_update_time = 0
    update_count = 0
    
    try:
        while True:
            # Read position data from MumbleLink
            ml.read()
            
            # Extract character name from identity JSON
            # The identity field contains JSON with character info including the name
            identity_str = ml.data.identity.rstrip('\x00')
            try:
                identity_data = json.loads(identity_str)
                character_name = identity_data.get("name", "Unknown")
            except (json.JSONDecodeError, AttributeError):
                character_name = "Unknown"
            
            # Extract position data (avatar position) - with 2 decimal places
            position_data = {
                'x': round(ml.data.fAvatarPosition[0], 2),
                'y': round(ml.data.fAvatarPosition[1], 2),
                'z': round(ml.data.fAvatarPosition[2], 2),
                'mapId': ml.context.mapId,
                'name': character_name,  # Use character name from identity JSON
                'timestamp': datetime.now().isoformat()
            }
            
            # Check if position changed
            position_changed = False
            if last_position is None:
                position_changed = True
            elif (position_data['x'] != last_position['x'] or
                  position_data['y'] != last_position['y'] or
                  position_data['z'] != last_position['z']):
                position_changed = True
            
            # Check if enough time has passed
            current_time = time.time()
            time_since_last_update = current_time - last_update_time
            can_update = time_since_last_update >= MIN_UPDATE_INTERVAL
            
            # Only publish if position changed AND enough time has passed
            if position_changed and can_update:
                # Prepare MQTT payload with coordinates (2 decimals) and mapId
                payload = json.dumps({
                    'x': position_data['x'],
                    'y': position_data['y'],
                    'z': position_data['z'],
                    'mapId': position_data['mapId'],
                    'name': position_data['name'],
                    'color': 0x00ff00,  # Green color for marker
                    'timestamp': position_data['timestamp']
                })
                
                # Publish to MQTT
                result = client.publish(MQTT_TOPIC, payload)
                
                # Check if publish was successful
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    update_count += 1
                    if update_count % 10 == 0:  # Print every 10 updates
                        print(f"Published position update #{update_count}: "
                              f"({position_data['x']}, {position_data['y']}, {position_data['z']}) "
                              f"mapId:{position_data['mapId']} "
                              f"[{position_data['name']}]")
                else:
                    print(f"Failed to publish message: {result.rc}")
                
                last_position = position_data.copy()
                last_update_time = current_time
            
            # Wait before next check (short sleep to prevent CPU spinning)
            time.sleep(0.05)  # 50ms check interval
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Cleanup
        ml.close()
        client.loop_stop()
        client.disconnect()
        print("Disconnected from MQTT broker. Goodbye!")

if __name__ == "__main__":
    main()