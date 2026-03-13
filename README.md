# GW2 MQTT Telemetry

A Python-based telemetry client for Guild Wars 2 that reads player position data via MumbleLink and publishes it to an MQTT broker in real-time.

## Overview

This script captures the player's in-game position (X, Y, Z coordinates) from Guild Wars 2 using the MumbleLink shared memory interface and broadcasts it via MQTT. This enables real-time tracking of player positions for applications like:

- Real-time map overlays
- Party/raid position tracking
- Speed farming analytics
- Community tools like BeetleRank

## How It Works

1. **MumbleLink Integration**: The script reads from Guild Wars 2's MumbleLink shared memory map, which provides real-time game data including player position, character name, and other metadata.

2. **Data Extraction**: The script extracts:
   - Avatar position (X, Y, Z coordinates)
   - Character name from the identity JSON data
   - Timestamp of each update

3. **MQTT Publishing**: Position data is published to a configurable MQTT broker/topic in JSON format with a configurable update rate.

4. **Rate Limiting**: The script includes rate limiting (default: 500ms minimum between updates) to prevent flooding the MQTT broker.

## Requirements

- Python 3.x
- Guild Wars 2 game client (running in-game)
- MQTT broker (local or remote)
- Required Python packages:
  - `paho-mqtt`

## Installation

### Option 1: Using the provided launcher (Windows)

Simply run the provided batch file:

```
run_gw2_telemetry.bat
```

This will:
- Create a virtual environment (if not exists)
- Install required dependencies
- Launch the telemetry client

### Option 2: Manual installation

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate.bat

# Or on Linux/Mac
source venv/bin/activate

# Install dependencies
pip install paho-mqtt

# Run the script
python gw2_mqtt_telemetry.py
```

## Configuration

Edit the configuration section at the top of [`gw2_mqtt_telemetry.py`](gw2_mqtt_telemetry.py):

```python
# MQTT Settings
MQTT_BROKER = "www.beetlerank.com"  # Your public MQTT server
MQTT_PORT = 1883                    # Default MQTT port
MQTT_TOPIC = "gw2/players/position" # Topic to publish position data
MQTT_CLIENT_ID = f"gw2_player_{int(time.time())}"  # Unique client ID

# Update frequency (seconds)
MIN_UPDATE_INTERVAL = 0.5   # Minimum time between updates (500ms)
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MQTT_BROKER` | MQTT broker hostname or IP | `www.beetlerank.com` |
| `MQTT_PORT` | MQTT broker port | `1883` |
| `MQTT_TOPIC` | MQTT topic for position data | `gw2/players/position` |
| `MQTT_CLIENT_ID` | Unique client identifier | Auto-generated timestamp |
| `MIN_UPDATE_INTERVAL` | Minimum seconds between updates | `0.5` |

### Authentication (Optional)

If your MQTT broker requires authentication, uncomment and configure:

```python
# MQTT_USERNAME = "your_username"
# MQTT_PASSWORD = "your_password"
```

And in the `main()` function:

```python
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
```

## Output Format

The script publishes JSON messages in the following format:

```json
{
    "x": 1234,
    "y": 5678,
    "z": 9012,
    "name": "CharacterName",
    "color": 65280,
    "timestamp": "2024-01-15T10:30:45.123456"
}
```

## Usage

1. Make sure Guild Wars 2 is running and you are logged into a character
2. Run the telemetry script
3. The script will connect to the MQTT broker and start publishing position updates
4. Press `Ctrl+C` to stop the script

## Troubleshooting

### "Failed to initialize MumbleLink"
- Ensure Guild Wars 2 is running and you are in-game (not at character select)

### "Failed to connect to MQTT broker"
- Check that the broker address and port are correct
- Verify your network can reach the broker
- Check if any firewall is blocking the connection

### High CPU usage
- The script includes a 50ms sleep to prevent CPU spinning
- Adjust `MIN_UPDATE_INTERVAL` if needed

## Files

| File | Description |
|------|-------------|
| [`gw2_mqtt_telemetry.py`](gw2_mqtt_telemetry.py) | Main telemetry client script |
| [`mumblelink.py`](mumblelink.py) | MumbleLink shared memory reader |
| [`run_gw2_telemetry.bat`](run_gw2_telemetry.bat) | Windows launcher script |

## License

This project is provided as-is for Guild Wars 2 telemetry and community tools.
