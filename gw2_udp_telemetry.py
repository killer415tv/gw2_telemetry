#!/usr/bin/env python3
"""
GW2 Player Position Telemetry via UDP
Reads player position from Guild Wars 2 via MumbleLink and sends to UDP server.

Based on the UDP protocol from speedometer.py (gw2_speedometer)
"""

import json
import time
import socket
from mumblelink import MumbleLink
from datetime import datetime

# ======================
# CONFIGURATION SECTION
# ======================

# UDP Settings (same as speedometer)
UDP_HOST = "www.beetlerank.com"  # UDP server address
UDP_PORT = 41234                 # UDP port (same as speedometer)

# Update frequency (seconds)
MIN_UPDATE_INTERVAL = 0.1   # Minimum time between updates (500ms) - won't send faster than this
KEEPALIVE_INTERVAL = 2   # Send position every 2 seconds even if player hasn't moved (keepalive)

# ======================
# MAIN APPLICATION
# ======================

def main():
    """Main application loop."""
    print("Starting GW2 UDP Telemetry Client")
    
    # Ask for event code (used as sessionCode for UDP)
    event_code = input("Enter event code: ").strip()
    if not event_code:
        print("Error: Event code cannot be empty")
        return
    
    print(f"UDP Server: {UDP_HOST}:{UDP_PORT}")
    print(f"Session Code: {event_code}")
    print(f"Min Update Interval: {MIN_UPDATE_INTERVAL}s")
    print(f"Keepalive Interval: {KEEPALIVE_INTERVAL}s")
    print("-" * 50)
    
    # Create UDP socket
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Created UDP socket")
    except Exception as e:
        print(f"Failed to create UDP socket: {e}")
        return
    
    print("UDP socket ready. Waiting for Guild Wars 2...")
    print("Make sure Guild Wars 2 is running and you're in-game.")
    print("-" * 50)
    
    # Initialize MumbleLink reader
    try:
        ml = MumbleLink()
        print("Successfully initialized MumbleLink connection")
    except Exception as e:
        print(f"Failed to initialize MumbleLink: {e}")
        print("Make sure Guild Wars 2 is running")
        udp_socket.close()
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
                'user': character_name,  # Use character name from identity JSON
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
            
            # Check if keepalive timeout reached (send position every 5 minutes regardless of movement)
            keepalive_reached = time_since_last_update >= KEEPALIVE_INTERVAL
            
            # Only send if position changed AND enough time has passed, OR keepalive timeout reached
            if (position_changed and can_update) or keepalive_reached:
                # Prepare UDP payload with position data
                # Protocol compatible with speedometer.py
                payload = {
                    "option": "position",
                    "x": position_data['x'],
                    "y": position_data['y'],
                    "z": position_data['z'],
                    "speed": 0,  # Not used in this project
                    "angle": 0,  # Not used in this project
                    "user": position_data['user'],
                    "sessionCode": event_code,
                    "map": "",  # Map name not available
                    "color": "#00FF00"  # Green color for marker
                }
                
                # Send via UDP
                try:
                    json_data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
                    udp_socket.sendto(json_data, (UDP_HOST, UDP_PORT))
                    
                    update_count += 1
                except Exception as e:
                    print(f"Failed to send UDP message: {e}")
                
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
        udp_socket.close()
        print("Closed UDP socket. Goodbye!")

if __name__ == "__main__":
    main()
