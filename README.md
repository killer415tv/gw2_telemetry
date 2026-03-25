# GW2 UDP Telemetry

A Python-based telemetry client for Guild Wars 2 that reads player position data via MumbleLink and sends it to a UDP server in real-time.

## Overview

This script captures the player's in-game position (X, Y, Z coordinates) from Guild Wars 2 using the MumbleLink shared memory interface and broadcasts it via UDP. This enables real-time tracking of player positions for applications like:

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

3. **UDP Sending**: Position data is sent to a configurable UDP server in JSON format with a configurable update rate.

4. **Rate Limiting**: The script includes rate limiting (default: 500ms minimum between updates) to prevent flooding the UDP server.

## Requirements

- Python 3.x
- Guild Wars 2 game client (running in-game)
- No additional Python packages required (uses built-in `socket` module)

## Installation

### Option 1: Using the provided launcher (Windows)

Simply run the provided batch file:

```
run_gw2_telemetry.bat
```

This will:
- Create a virtual environment (if not exists)
- Launch the telemetry client

### Option 2: Manual installation

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate.bat

# Or on Linux/Mac
source venv/bin/activate

# Run the script
python gw2_udp_telemetry.py
```

## Configuration

Edit the configuration section at the top of [`gw2_udp_telemetry.py`](gw2_udp_telemetry.py):

```python
# UDP Settings (same as speedometer)
UDP_HOST = "www.beetlerank.com"  # UDP server address
UDP_PORT = 41234                 # UDP port (same as speedometer)

# Update frequency (seconds)
MIN_UPDATE_INTERVAL = 0.5   # Minimum time between updates (500ms)
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `UDP_HOST` | UDP server hostname or IP | `www.beetlerank.com` |
| `UDP_PORT` | UDP server port | `41234` |
| `MIN_UPDATE_INTERVAL` | Minimum seconds between updates | `0.5` |

## Output Format

The script sends JSON messages in the following format (compatible with speedometer.py):

```json
{
    "option": "position",
    "x": 1234.56,
    "y": 5678.90,
    "z": 100.0,
    "speed": 0,
    "angle": 0,
    "user": "CharacterName",
    "sessionCode": "event_code",
    "map": "",
    "color": "#00FF00"
}
```

**Note**: `speed` and `angle` are set to 0 as they are not used in this project.

## Usage

1. Make sure Guild Wars 2 is running and you are logged into a character
2. Run the telemetry script
3. Enter the event code (session code) when prompted
4. The script will connect to the UDP server and start sending position updates
5. Press `Ctrl+C` to stop the script

## Troubleshooting

### "Failed to initialize MumbleLink"
- Ensure Guild Wars 2 is running and you are in-game (not at character select)

### "Failed to create UDP socket"
- Check that the network configuration allows UDP connections
- Verify your network can reach the UDP server

### High CPU usage
- The script includes a 50ms sleep to prevent CPU spinning
- Adjust `MIN_UPDATE_INTERVAL` if needed

## Files

| File | Description |
|------|-------------|
| [`gw2_udp_telemetry.py`](gw2_udp_telemetry.py) | Main telemetry client script |
| [`mumblelink.py`](mumblelink.py) | MumbleLink shared memory reader |
| [`run_gw2_telemetry.bat`](run_gw2_telemetry.bat) | Windows launcher script |

## Protocol

This client uses the same UDP protocol as [gw2_speedometer](https://github.com/beetlerank/gw2_speedometer):

- **Host**: `www.beetlerank.com`
- **Port**: `41234` (UDP)
- **Protocol**: JSON over UDP

## License

This project is provided as-is for Guild Wars 2 telemetry and community tools.
