# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FlashForge Printer Emulator is a Python-based network protocol emulator for FlashForge 3D printers. It provides a complete implementation of the FlashForge printer discovery and command protocols, allowing developers to test client applications without physical hardware.

## Core Architecture

### Main Components
- **PrinterEmulator** (`emulator/printer.py`): Core emulation logic handling printer state, temperature simulation, and file management
- **EmulatorServer** (`emulator/server.py`): Network layer handling UDP discovery (port 48899) and TCP commands (port 8899)
- **Command Processing** (`emulator/commands.py`): G-code command parser and dispatcher
- **Response Generation** (`emulator/responses.py`): Standard FlashForge protocol response formatting
- **GUI Interface** (`ui/main_window.py`): Main application window with tabbed interface

### UI Structure
The GUI uses ttkbootstrap with a tabbed interface:
- **MainTab**: Basic controls and logging
- **ConfigTab**: Printer configuration and virtual file management
- **PrinterStateTab**: Temperature and print status controls
- **NetworkTab**: Network simulation settings (latency, failures)
- **PrinterDetailsTab**: Hardware specification settings
- **FilesystemTab**: Virtual file system management
- **LogsTab**: Application logging

## Commands

### Running the Application
```bash
python main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Key Dependencies
- `ttkbootstrap` for modern GUI theming
- `Pillow` for thumbnail image processing

## Protocol Implementation

### Discovery Protocol
- UDP broadcast on port 48899
- Responds with printer name and serial in binary format
- Handles automatic printer detection by FlashForge clients

### Command Protocol
- TCP server on port 8899
- Command format: `~GCODE [parameters]`
- Response format: `CMD GCODE Received.\n[data]\nok`

### Supported G-codes
- Status: M115 (info), M105 (temps), M119 (endstops), M27 (print status), M114 (position)
- Control: M601/M602 (login/logout), M24/M25/M26 (print control), M104/M140 (temp setting)
- Files: M661 (list files), M662 (get thumbnail)

## Configuration

Configuration is centralized in `config.py` with defaults for:
- Network ports (DISCOVERY_PORT=48899, COMMAND_PORT=8899)
- Printer identification (name, serial, machine type, firmware version)
- Temperature defaults
- Virtual file list
- UI dimensions

## Key Design Patterns

### State Management
The PrinterEmulator class maintains all printer state and provides methods for:
- Temperature simulation with realistic heating/cooling curves
- Print progress tracking
- Virtual file system management
- Server lifecycle management

### Event-Driven Updates
UI components update printer state through the emulator instance, which propagates changes to the network server and updates the GUI in real-time.

### Network Simulation
The NetworkTab allows simulation of network conditions (latency, packet loss, connection failures) for testing client robustness.