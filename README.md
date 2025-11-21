<div align="center">
  <h1>FlashForge Printer Emulator</h1>
  <p>A comprehensive network protocol emulator for FlashForge 3D printers</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg">
  <img src="https://img.shields.io/badge/Platforms-Win%20%7C%20macOS%20%7C%20Linux-blue">
</p>

<div align="center">
  <p>This tool allows developers to test FlashForge client applications without requiring a physical printer.</p>
</div>

<div align="center">
  <h1>Features</h1>
</div>

<div align="center">

| Feature | Description |
|---------|-------------|
| Complete Protocol Implementation | Fully emulates the FlashForge printer network protocol |
| Discovery Protocol | Emulates the UDP discovery protocol for automatic printer detection |
| Command Interface | Implements all standard G-code commands used by FlashForge printers |
| Print Visualization | Generates model thumbnails for print preview |
| Configurable Parameters | Customize printer name, serial number, temperatures, and more |
| Real-time Simulation | Simulates temperature changes and print progress dynamically |
| Multi-platform | Works on Windows, macOS, and Linux |

</div>

<div align="center">
  <h1>Setup</h1>
</div>

<div align="center">

| Step | Command |
|------|---------|
| Clone the repository | git clone https://github.com/yourusername/FlashForge-Emulator.git |
| Navigate to directory | cd FlashForge-Emulator |
| Install dependencies | pip install -r requirements.txt |

</div>

<div align="center">
  <h1>Usage</h1>
</div>

<div align="center">

| Step | Description |
|------|-------------|
| Start the emulator | Run: python emulator.py |
| Services started | UDP discovery on port 48899, TCP command server on port 8899 |
| Connect client | The emulator will appear in the discovery list and respond to commands |
| Thumbnail generation | A standard thumbnail image is automatically generated |

</div>

<div align="center">
  <h1>Configuration</h1>
</div>

<div align="center">
  <h2>Printer Settings</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Printer Name | Customize the name displayed to client applications |
| Serial Number | Set a unique identifier for the emulated printer |
| Machine Type | Set printer model (e.g., Adventurer 4, Creator Pro, etc.) |
| Firmware Version | Set the reported firmware version |

</div>

<div align="center">
  <h2>Network Configuration</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Network Interface | Select which network interface to use for discovery |
| Discoverability | The emulator will only be discoverable from the selected interface |

</div>

<div align="center">
  <h2>Print Simulation</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Print Status | Set to Idle, Printing, Paused, Completed, or Failed |
| Print Progress | Adjust the reported progress percentage |
| Current File | Set the filename of the "currently printing" model |
| Layer Progress | Automatically calculated based on print progress |

</div>

<div align="center">
  <h2>Temperature Control</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Hotend Temperature | Set current and target temperatures for the hotend |
| Bed Temperature | Set current and target temperatures for the heated bed |
| Simulation | Temperatures are dynamically simulated with realistic heating/cooling rates |

</div>

<div align="center">
  <h1>Supported Commands</h1>
</div>

<div align="center">
  <h2>Status Commands</h2>
</div>

<div align="center">

| Command | Description |
|---------|-------------|
| M115 | Get printer information |
| M105 | Get temperature readings |
| M119 | Get endstop and machine status |
| M27 | Get print status |
| M114 | Get current position |

</div>

<div align="center">
  <h2>Control Commands</h2>
</div>

<div align="center">

| Command | Description |
|---------|-------------|
| M601/M602 | Login/Logout |
| M146 | Control LED |
| M405/M406 | Control filament runout sensor |
| G28 | Home axes |
| G1 | Move printer head |
| M24/M25/M26 | Resume/Pause/Stop print |
| M104/M140 | Set extruder/bed temperature |
| M109/M190 | Set and wait for extruder/bed temperature |
| M661 | List files on printer |
| M662 | Get thumbnail for a file |

</div>

<div align="center">
  <h1>Protocol Details</h1>
</div>

<div align="center">
  <h2>Discovery Protocol</h2>
</div>

<div align="center">

| Property | Value |
|----------|-------|
| Protocol | UDP |
| Port | 48899 |
| Response Format | Binary format with printer name and serial number |
| Purpose | Automatic printer detection by FlashForge clients |

</div>

<div align="center">
  <h2>Command Protocol</h2>
</div>

<div align="center">

| Property | Value |
|----------|-------|
| Protocol | TCP |
| Port | 8899 |
| Command Format | ~GCODE [parameters] |
| Response Format | CMD GCODE Received.[newline][response data][newline]ok |

</div>
