<div align="center">
  <h1>FlashForge Printer Emulator</h1>
  <p>A comprehensive dual-protocol network emulator for FlashForge 3D printers</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg">
  <img src="https://img.shields.io/badge/Platforms-Win%20%7C%20macOS%20%7C%20Linux-blue">
  <img src="https://img.shields.io/badge/Protocols-TCP%20%2B%20HTTP-green">
</p>

<div align="center">
  <p>Test FlashForge client applications without physical hardware</p>
  <p>Full support for both legacy TCP protocol and modern HTTP API</p>
</div>

<div align="center">
  <h1>Protocol Support</h1>
</div>

<div align="center">

| Protocol | Port | Status | Description |
|----------|------|--------|-------------|
| UDP Discovery | 48899 | Full Support | Automatic printer detection on network |
| TCP Commands | 8899 | Full Support | Legacy G-code protocol for all FlashForge printers |
| HTTP API | 8898 | Full Support | Modern REST API for Adventurer 5M/Pro/5X series |
| Dual-Mode | All | Full Support | Run both protocols simultaneously |

</div>

<div align="center">
  <h1>Printer Mode Emulation</h1>
</div>

<div align="center">

| Printer Model | Emulation Status | Camera Support | Material Station | Filtration System |
|---------------|------------------|----------------|------------------|-------------------|
| Adventurer 5M | Full | No | No | No |
| Adventurer 5M Pro | Full | Yes | No | Yes |
| Adventurer 5X | Full | Yes | Yes (4-slot IFS) | Yes |
| Legacy Models (3/4) | Full | No | No | No |

</div>

<div align="center">
  <h1>Features</h1>
</div>

<div align="center">
  <h2>Core Capabilities</h2>
</div>

<div align="center">

| Feature | Description |
|---------|-------------|
| Dual Protocol Operation | Run TCP and HTTP servers simultaneously or independently |
| Complete Protocol Implementation | Fully emulates both FlashForge network protocols |
| Discovery Protocol | UDP broadcast for automatic printer detection |
| Material Station Emulation | 4-slot IFS support for AD5X multi-color printing |
| Enhanced File Management | File metadata, thumbnails, and upload support |
| Persistent Configuration | JSON-based auto-save/load configuration system |
| Cumulative Statistics | Track lifetime print time and filament usage |
| Real-time Simulation | Dynamic temperature changes and print progress |
| Multi-platform | Windows, macOS, and Linux support |

</div>

<div align="center">
  <h2>HTTP API Endpoints</h2>
</div>

<div align="center">

| Endpoint | Method | Description |
|----------|--------|-------------|
| /product | POST | Get printer control states and capabilities |
| /detail | POST | Get comprehensive printer status and metrics |
| /control | POST | Send control commands (temperature, LED, fans, etc) |
| /gcodeList | POST | Get list of recent and local files |
| /gcodeThumb | POST | Get base64 thumbnail for file preview |
| /uploadGcode | POST | Upload new G-code files to printer |
| /printGcode | POST | Start printing a file from storage |

</div>

<div align="center">
  <h2>Advanced Features</h2>
</div>

<div align="center">

| Feature | Description |
|---------|-------------|
| HTTP Monitoring UI | Real-time inspection of all API requests and responses |
| Network Simulation | Simulate latency, packet loss, and connection failures |
| Print Status State Machine | Multiple states: ready, busy, printing, paused, completed, cancelled, error |
| Temperature Simulation | Realistic heating and cooling curves |
| Material Station Control | Manage filament slots, colors, and material types for multi-color prints |
| File Metadata Management | Track print time, filament usage, layer counts, and tool configurations |
| Configuration Auto-save | Automatic persistence with restart scheduling |

</div>

<div align="center">
  <h1>Setup</h1>
</div>

<div align="center">

| Step | Command |
|------|---------|
| Clone the repository | git clone https://github.com/Parallel-7/FlashForgeEmulator.git |
| Navigate to directory | cd FlashForgeEmulator |
| Install dependencies | pip install -r requirements.txt |

</div>

<div align="center">
  <h1>Usage</h1>
</div>

<div align="center">

| Step | Command / Description |
|------|----------------------|
| Start the emulator | python main.py |
| GUI Application | Modern ttkbootstrap interface with tabbed controls |
| UDP Discovery | Automatically broadcasts on port 48899 |
| TCP Server | Listens on port 8899 for legacy G-code commands |
| HTTP Server | Listens on port 8898 for REST API requests |
| Protocol Mode | Choose TCP-only, HTTP-only, or Dual-mode operation |

</div>

<div align="center">
  <h1>Configuration</h1>
</div>

<div align="center">
  <h2>Printer Identity</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Printer Name | Customize the name displayed to client applications |
| Serial Number | Set a unique identifier for the emulated printer |
| Machine Type | Set printer model (5M, 5M Pro, 5X, etc) |
| Firmware Version | Set the reported firmware version |
| MAC Address | Required for HTTP API clients |
| Check Code | Authentication code for HTTP API |

</div>

<div align="center">
  <h2>Protocol Configuration</h2>
</div>

<div align="center">

| Mode | TCP Server | HTTP Server | Use Case |
|------|------------|-------------|----------|
| TCP Only | Running | Stopped | Test legacy clients and older printers |
| HTTP Only | Stopped | Running | Test modern API clients (5M/Pro/5X) |
| Dual Mode | Running | Running | Test comprehensive client compatibility |

</div>

<div align="center">
  <h2>Printer Mode Selection</h2>
</div>

<div align="center">

| Mode | Model Emulated | Camera | Filtration | Material Station |
|------|----------------|--------|------------|------------------|
| 5M | Adventurer 5M | No | No | No |
| 5M Pro | Adventurer 5M Pro | Yes | Yes | No |
| AD5X | Adventurer 5X | Yes | Yes | Yes (4-slot IFS) |

</div>

<div align="center">
  <h2>Material Station (AD5X Mode)</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Slot Count | Number of filament slots (default: 4) |
| Current Slot | Active slot being used for printing |
| Slot Configuration | Configure material type, color, and presence per slot |
| Material Mappings | Define tool-to-slot mappings for multi-color prints |
| Loading State | Simulate filament loading and unloading operations |

</div>

<div align="center">
  <h2>Print Simulation</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Print Status | Set to ready, busy, printing, paused, completed, cancelled, or error |
| Print Progress | Adjust the reported progress percentage (0-100) |
| Current File | Set the filename of the currently printing model |
| Layer Progress | Automatically calculated based on print progress |
| Print Duration | Elapsed time for current print job |
| Remaining Time | Estimated time remaining for print completion |
| Filament Estimates | Set total filament length and weight for current job |

</div>

<div align="center">
  <h2>Temperature Control</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Hotend Temperature | Set current and target temperatures for the hotend |
| Bed Temperature | Set current and target temperatures for the heated bed |
| Chamber Temperature | Set chamber temperature (Pro/5X models) |
| Simulation Mode | Realistic heating and cooling curves with configurable rates |
| Idle Temperatures | Default temperatures when not printing |

</div>

<div align="center">
  <h2>Network Simulation</h2>
</div>

<div align="center">

| Setting | Description |
|---------|-------------|
| Network Interface | Select which network interface to use for discovery |
| Latency Simulation | Add artificial delay to responses (testing robustness) |
| Packet Loss | Simulate random connection failures |
| Connection Failures | Test client retry and error handling |

</div>

<div align="center">
  <h2>Statistics Tracking</h2>
</div>

<div align="center">

| Statistic | Description |
|-----------|-------------|
| Cumulative Print Time | Total lifetime print time in minutes |
| Cumulative Filament | Total lifetime filament usage in meters |
| Job History | Track completed prints and their metadata |
| Auto-persistence | Statistics saved automatically to configuration file |

</div>

<div align="center">
  <h1>Supported Commands</h1>
</div>

<div align="center">
  <h2>TCP Protocol - Status Commands</h2>
</div>

<div align="center">

| Command | Description |
|---------|-------------|
| M115 | Get printer information and capabilities |
| M105 | Get current temperature readings |
| M119 | Get endstop and machine status |
| M27 | Get print status and progress |
| M114 | Get current position (X/Y/Z) |

</div>

<div align="center">
  <h2>TCP Protocol - Control Commands</h2>
</div>

<div align="center">

| Command | Description |
|---------|-------------|
| M601/M602 | Login and logout authentication |
| M146 | Control LED on/off |
| M405/M406 | Control filament runout sensor |
| G28 | Home all axes |
| G1 | Move printer head to position |
| M24/M25/M26 | Resume, pause, and stop print |
| M104/M140 | Set extruder and bed temperature |
| M109/M190 | Set and wait for temperature targets |
| M661 | List files on printer storage |
| M662 | Get thumbnail image for a file |

</div>

<div align="center">
  <h2>HTTP API - Control Commands</h2>
</div>

<div align="center">

| Command | Parameters | Description |
|---------|------------|-------------|
| switchLight | status: open/close | Control printer LED |
| setTargetTemperature | heaterIndex, temperature | Set target temperature for extruder or bed |
| setChamberTemperature | temperature | Set chamber target temperature (Pro/5X) |
| setExternalFan | status: open/close | Control external filtration fan (Pro/5X) |
| setInternalFan | status: open/close | Control internal filtration fan (Pro/5X) |
| pause | - | Pause current print |
| resume | - | Resume paused print |
| cancel | - | Cancel current print |

</div>

<div align="center">
  <h1>User Interface</h1>
</div>

<div align="center">

| Tab | Description |
|-----|-------------|
| Main | Basic controls, server start/stop, protocol mode selection, status logging |
| Configuration | Printer identity, protocol mode, printer mode, virtual file management |
| Printer State | Temperature controls, print status, progress simulation, filament estimates |
| Material Station | 4-slot IFS configuration for multi-color printing (AD5X mode) |
| HTTP Monitor | Real-time inspection of all HTTP API requests and responses |
| Network | Interface selection, network simulation settings |
| Printer Details | Hardware specifications and dimensions |
| Filesystem | Virtual file system and metadata management |
| Logs | Application logging and debugging output |

</div>

<div align="center">
  <h1>Protocol Details</h1>
</div>

<div align="center">
  <h2>UDP Discovery Protocol</h2>
</div>

<div align="center">

| Property | Value |
|----------|-------|
| Protocol | UDP Broadcast |
| Port | 48899 |
| Response Format | Binary format with printer name and serial number |
| Purpose | Automatic printer detection by FlashForge clients |
| Compatibility | All FlashForge printers and client software |

</div>

<div align="center">
  <h2>TCP Command Protocol</h2>
</div>

<div align="center">

| Property | Value |
|----------|-------|
| Protocol | TCP |
| Port | 8899 |
| Command Format | ~GCODE [parameters] |
| Response Format | CMD GCODE Received.[newline][response data][newline]ok |
| Use Case | Legacy protocol for Adventurer 3/4 and older models |
| Client Compatibility | FlashPrint, OrcaSlicer (legacy mode), custom clients |

</div>

<div align="center">
  <h2>HTTP REST API</h2>
</div>

<div align="center">

| Property | Value |
|----------|-------|
| Protocol | HTTP/1.1 |
| Port | 8898 |
| Format | JSON request/response bodies |
| Authentication | Serial number and check code validation |
| Use Case | Modern protocol for Adventurer 5M/Pro/5X series |
| Client Compatibility | FlashForgeUI, OrcaSlicer (new API mode), custom clients |

</div>

<div align="center">
  <h1>File Management</h1>
</div>

<div align="center">

| Feature | Description |
|---------|-------------|
| Virtual Files | Pre-configured test files with metadata |
| File Upload | Simulate file uploads via HTTP API |
| Thumbnail Storage | Base64-encoded preview images |
| File Metadata | Track print time, filament usage, layer counts |
| Multi-color Files | Support for Material Station tool mappings |
| Recent Files | Return last 10 files for client display |
| Local Files | Full file list with detailed metadata (mode-dependent) |

</div>

<div align="center">
  <h2>File Metadata Fields</h2>
</div>

<div align="center">

| Field | Description |
|-------|-------------|
| gcodeFileName | Name of the G-code file |
| printingTime | Estimated print duration in seconds |
| uploadTime | ISO timestamp of file upload |
| fileSize | File size in bytes |
| totalFilamentWeight | Total filament weight in grams |
| useMatlStation | Whether file uses Material Station (multi-color) |
| gcodeToolCnt | Number of tools/extruders used |
| gcodeToolDatas | Array of tool configurations with slot mappings |

</div>

<div align="center">
  <h1>Testing Coverage</h1>
</div>

<div align="center">

| Client Software | Protocol | Testing Status | Notes |
|----------------|----------|----------------|-------|
| FlashForgeUI | HTTP API | Fully Tested | All printer modes supported |
| OrcaSlicer | TCP + HTTP | Fully Tested | Both legacy and new API modes |
| Orca-FlashForge | TCP | Fully Tested | Legacy protocol support |
| FlashPrint | TCP | Fully Tested | Official FlashForge software |
| Custom Clients | Both | Supported | Full protocol documentation available |

</div>

<div align="center">
  <h1>Development</h1>
</div>

<div align="center">

| Tool | Purpose |
|------|---------|
| Claude Code Integration | CLAUDE.md file provides AI assistant context |
| Configuration Persistence | JSON auto-save prevents data loss |
| Hot Reload | Configuration changes applied without restart where possible |
| HTTP Monitoring | Built-in request/response inspection for debugging |
| Network Simulation | Test client robustness under adverse conditions |

</div>

<div align="center">
  <h2>Architecture</h2>
</div>

<div align="center">

| Component | File | Description |
|-----------|------|-------------|
| Core Emulator | emulator/printer.py | Central state management and coordination |
| TCP Server | emulator/server.py | Legacy protocol server |
| HTTP Server | emulator/http_server_async.py | Async HTTP API server using aiohttp |
| Command Processing | emulator/commands.py | G-code command parser and dispatcher |
| HTTP Responses | emulator/http_responses.py | JSON response generation for REST API |
| File Manager | emulator/file_manager.py | Enhanced file and metadata management |
| Printer Modes | emulator/printer_modes.py | Mode-specific features and Material Station |
| Configuration | config.py | Centralized configuration and defaults |

</div>

<div align="center">
  <h2>Dependencies</h2>
</div>

<div align="center">

| Package | Purpose |
|---------|---------|
| ttkbootstrap | Modern GUI theming and widgets |
| Pillow | Thumbnail image processing |
| aiohttp | Async HTTP server implementation |
| Standard Library | asyncio, threading, json, socket, struct |

</div>
