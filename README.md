# FlashForge Printer Emulator

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

A comprehensive network protocol emulator for FlashForge 3D printers. This tool allows developers to test FlashForge client applications without requiring a physical printer.

## Features

- **Complete Protocol Implementation**: Fully emulates the FlashForge printer network protocol
- **Discovery Protocol**: Emulates the UDP discovery protocol for automatic printer detection
- **Command Interface**: Implements all standard G-code commands used by FlashForge printers
- **Print Visualization**: Generates model thumbnails for print preview
- **Configurable Parameters**: Customize printer name, serial number, temperatures, and more
- **Real-time Simulation**: Simulates temperature changes and print progress dynamically
- **Multi-platform**: Works on Windows, macOS, and Linux

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/FlashForge-Emulator.git
   cd FlashForge-Emulator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the emulator:
   ```bash
   python emulator.py
   ```

2. The emulator will:
   - Generate a standard thumbnail image
   - Start UDP discovery service on port 48899
   - Start TCP command server on port 8899
   - Display its interface for monitoring and configuration

3. Connect your FlashForge client application:
   - The emulator will appear in the discovery list
   - All API commands will receive appropriate responses

## Configuration

### Printer Settings

- **Printer Name**: Customize the name displayed to client applications
- **Serial Number**: Set a unique identifier for the emulated printer
- **Machine Type**: Set printer model (e.g., Adventurer 4, Creator Pro, etc.)
- **Firmware Version**: Set the reported firmware version

### Network Configuration

- **Network Interface**: Select which network interface to use for discovery
- The emulator will only be discoverable from the selected interface

### Print Simulation

- **Print Status**: Set to Idle, Printing, Paused, Completed, or Failed
- **Print Progress**: Adjust the reported progress percentage
- **Current File**: Set the filename of the "currently printing" model
- **Layer Progress**: Automatically calculated based on print progress

### Temperature Control

- **Hotend/Bed Temperature**: Set current and target temperatures
- Temperatures are dynamically simulated with realistic heating/cooling rates

## Supported Commands

The emulator supports all primary FlashForge TCP API commands:

### Status Commands
- `M115` - Get printer information
- `M105` - Get temperature readings
- `M119` - Get endstop and machine status
- `M27` - Get print status
- `M114` - Get current position

### Control Commands
- `M601/M602` - Login/Logout
- `M146` - Control LED
- `M405/M406` - Control filament runout sensor
- `G28` - Home axes
- `G1` - Move printer head
- `M24/M25/M26` - Resume/Pause/Stop print
- `M104/M140` - Set extruder/bed temperature
- `M109/M190` - Set and wait for extruder/bed temperature
- `M661` - List files on printer
- `M662` - Get thumbnail for a file

## Protocol Details

### Discovery Protocol

The emulator implements the FlashForge discovery protocol:
- UDP port 48899
- Responds to standard FlashForge discovery packet format
- Returns printer name and serial number in the correct binary format

### Command Protocol

- TCP port 8899
- Command format: `~GCODE [parameters]`
- Response format:
  ```
  CMD GCODE Received.
  [response data]
  ok
  ```
