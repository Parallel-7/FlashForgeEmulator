"""
Async HTTP Server implementation using aiohttp for FlashForge API emulation.
This replaces the slow http.server implementation with instant startup.
"""
import asyncio
import json
import threading
from typing import Optional, Callable
from aiohttp import web
import config
from .http_responses import (
    generate_product_response,
    generate_detail_response,
    generate_control_response,
    generate_gcode_list_response,
    generate_thumbnail_response,
    generate_upload_response,
    generate_print_gcode_response,
    create_error_response,
    process_control_command
)
from .printer_modes import ModeFeatures


class FlashForgeHTTPServerAsync:
    """Fast async HTTP server for FlashForge API emulation using aiohttp"""

    def __init__(self, printer_emulator, file_manager, logger: Optional[Callable] = None, http_tab_logger = None):
        self.printer_emulator = printer_emulator
        self.file_manager = file_manager
        self.logger = logger
        self.http_tab_logger = http_tab_logger  # Reference to HttpTab for detailed logging

        # Server components
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

        # Event loop management
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.loop_thread: Optional[threading.Thread] = None

        # State tracking
        self._state = "stopped"
        self._state_lock = threading.Lock()
        self._port = None

    def get_state(self) -> str:
        """Get current server state (thread-safe)"""
        with self._state_lock:
            return self._state

    def _set_state(self, state: str):
        """Set server state (thread-safe)"""
        with self._state_lock:
            self._state = state

    @property
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.get_state() == "running"

    def _validate_auth(self, data: dict) -> bool:
        """Validate authentication credentials"""
        serial_number = data.get('serialNumber', '')
        check_code = data.get('checkCode', '')

        configured_serial = self.printer_emulator.config.get('serial_number', config.DEFAULT_SERIAL_NUMBER)
        configured_check_code = self.printer_emulator.config.get('check_code', config.HTTP_CONFIG['check_code'])

        if not configured_serial or not configured_check_code:
            return False

        return serial_number == configured_serial and check_code == configured_check_code

    @web.middleware
    async def logging_middleware(self, request: web.Request, handler):
        """Middleware to log all HTTP requests"""
        client_ip = request.remote
        method = request.method
        path = request.path

        # Read request body for logging (if JSON)
        request_body = None
        try:
            if request.content_type == 'application/json':
                # Clone request body for logging without consuming it
                body_bytes = await request.read()
                if body_bytes:
                    request_body = json.loads(body_bytes.decode('utf-8'))
                # Re-create request with body for handler
                request = request.clone(read=lambda: asyncio.coroutine(lambda: body_bytes)())
        except:
            pass

        # Process request
        response = await handler(request)

        # Log to main logger (simple)
        if self.logger:
            self.logger(f"HTTP {method} {path} from {client_ip} -> {response.status}")

        # Log to HTTP tab (detailed) if available
        if self.http_tab_logger and hasattr(self.http_tab_logger, 'log_http_request'):
            response_body = None
            if response.status != 200:
                try:
                    # Try to get response body for error logging
                    response_body = response.body
                except:
                    pass

            self.http_tab_logger.log_http_request(
                method=method,
                path=path,
                client_ip=client_ip,
                status_code=response.status,
                request_body=request_body,
                response_body=response_body
            )

        return response

    # ============================================================================
    # Route Handlers
    # ============================================================================

    async def handle_product(self, request: web.Request) -> web.Response:
        """Handle /product endpoint"""
        try:
            data = await request.json()

            if not self._validate_auth(data):
                return web.json_response(create_error_response(1, "Authentication failed"))

            current_mode = self.printer_emulator.config.get('printer_mode', config.PrinterMode.STANDARD_5M)
            mode_features = ModeFeatures(current_mode)
            response = generate_product_response(self.printer_emulator.config, mode_features)

            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /product: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    async def handle_detail(self, request: web.Request) -> web.Response:
        """Handle /detail endpoint"""
        try:
            data = await request.json()

            if not self._validate_auth(data):
                return web.json_response(create_error_response(1, "Authentication failed"))

            current_mode = self.printer_emulator.config.get('printer_mode', config.PrinterMode.STANDARD_5M)
            material_station = getattr(self.printer_emulator, 'material_station', None)

            response = generate_detail_response(self.printer_emulator.config, current_mode, material_station)

            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /detail: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    async def handle_control(self, request: web.Request) -> web.Response:
        """Handle /control endpoint"""
        try:
            data = await request.json()

            if not self._validate_auth(data):
                return web.json_response(create_error_response(1, "Authentication failed"))

            payload = data.get('payload', {})
            command = payload.get('cmd', '')
            args = payload.get('args', {})

            if self.logger:
                self.logger(f"Control command: {command} with args: {args}")

            success = process_control_command(self.printer_emulator.config, command, args)
            response = generate_control_response(success, "" if success else f"Unknown command: {command}")

            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /control: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    async def handle_gcode_list(self, request: web.Request) -> web.Response:
        """Handle /gcodeList endpoint"""
        try:
            data = await request.json()

            if not self._validate_auth(data):
                return web.json_response(create_error_response(1, "Authentication failed"))

            current_mode = self.printer_emulator.config.get('printer_mode', config.PrinterMode.STANDARD_5M)
            response = generate_gcode_list_response(self.file_manager, current_mode)

            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /gcodeList: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    async def handle_gcode_thumb(self, request: web.Request) -> web.Response:
        """Handle /gcodeThumb endpoint"""
        try:
            data = await request.json()

            if not self._validate_auth(data):
                return web.json_response(create_error_response(1, "Authentication failed"))

            filename = data.get('fileName', '')
            if not filename:
                return web.json_response(create_error_response(1, "Filename required"))

            response = generate_thumbnail_response(self.file_manager, filename)

            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /gcodeThumb: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    async def handle_upload_gcode(self, request: web.Request) -> web.Response:
        """Handle /uploadGcode endpoint with multipart upload"""
        try:
            # Extract auth from headers
            serial_number = request.headers.get('serialNumber', '')
            check_code = request.headers.get('checkCode', '')

            configured_serial = self.printer_emulator.config.get('serial_number', config.DEFAULT_SERIAL_NUMBER)
            configured_check_code = self.printer_emulator.config.get('check_code', config.HTTP_CONFIG['check_code'])

            if serial_number != configured_serial or check_code != configured_check_code:
                return web.json_response(create_error_response(1, "Authentication failed"))

            # Read multipart data
            reader = await request.multipart()
            file_data = None
            filename = None

            async for part in reader:
                if part.name == 'gcodeFile':
                    filename = part.filename
                    file_data = await part.read()
                    break

            if not file_data or not filename:
                return web.json_response(create_error_response(1, "No file data received"))

            if self.logger:
                self.logger(f"Uploading file: {filename}, size: {len(file_data)} bytes")

            # Process upload metadata from headers
            metadata = {
                'printingTime': int(request.headers.get('printingTime', 0)),
                'totalLayers': int(request.headers.get('totalLayers', 0)),
                'gcodeToolCnt': int(request.headers.get('gcodeToolCnt', 1)),
            }

            # Add file to file manager
            self.file_manager.add_uploaded_file(filename, file_data, metadata)

            # Start print if requested
            print_now = request.headers.get('printNow', 'false').lower() == 'true'
            if print_now:
                leveling = request.headers.get('levelingBeforePrint', 'false').lower() == 'true'
                self._start_print_job(filename, leveling, metadata)

            response = generate_upload_response(True)
            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /uploadGcode: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    async def handle_print_gcode(self, request: web.Request) -> web.Response:
        """Handle /printGcode endpoint"""
        try:
            data = await request.json()

            if not self._validate_auth(data):
                return web.json_response(create_error_response(1, "Authentication failed"))

            filename = data.get('fileName', '')
            if not filename or not self.file_manager.file_exists(filename):
                return web.json_response(create_error_response(1, "File not found"))

            leveling = data.get('levelingBeforePrint', False)
            use_matl_station = data.get('useMatlStation', False)
            material_mappings = data.get('materialMappings', [])

            if self.logger:
                self.logger(f"Starting print: {filename}, leveling: {leveling}")

            metadata = self.file_manager.get_file_metadata(filename)
            if use_matl_station:
                metadata['materialMappings'] = material_mappings

            success = self._start_print_job(filename, leveling, metadata)
            response = generate_print_gcode_response(success)

            return web.json_response(response)

        except Exception as e:
            if self.logger:
                self.logger(f"Error in /printGcode: {e}")
            return web.json_response(create_error_response(500, str(e)), status=500)

    def _start_print_job(self, filename: str, leveling: bool, metadata: dict = None) -> bool:
        """Start a print job"""
        try:
            self.printer_emulator.config['current_file'] = filename
            self.printer_emulator.config['print_status'] = 'printing'
            self.printer_emulator.config['print_progress'] = 0.0
            self.printer_emulator.config['current_layer'] = 0
            self.printer_emulator.config['print_duration'] = 0

            if metadata:
                self.printer_emulator.config['total_layers'] = metadata.get('totalLayers', 100)
                self.printer_emulator.config['estimated_print_time'] = metadata.get('printingTime', 3600)

            if hasattr(self.printer_emulator, 'start_print'):
                self.printer_emulator.start_print(filename)

            return True
        except Exception as e:
            if self.logger:
                self.logger(f"Error starting print job: {e}")
            return False

    # ============================================================================
    # Server Lifecycle
    # ============================================================================

    def _setup_routes(self):
        """Setup all HTTP routes"""
        self.app.router.add_post('/product', self.handle_product)
        self.app.router.add_post('/detail', self.handle_detail)
        self.app.router.add_post('/control', self.handle_control)
        self.app.router.add_post('/gcodeList', self.handle_gcode_list)
        self.app.router.add_post('/gcodeThumb', self.handle_gcode_thumb)
        self.app.router.add_post('/uploadGcode', self.handle_upload_gcode)
        self.app.router.add_post('/printGcode', self.handle_print_gcode)

    async def _start_server_async(self, port: int):
        """Start the HTTP server (async, runs in event loop)"""
        try:
            # Create application with logging middleware
            self.app = web.Application(middlewares=[self.logging_middleware])
            self._setup_routes()

            # Create runner and setup
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            # Create site and start (this is FAST with aiohttp)
            self.site = web.TCPSite(
                self.runner,
                '0.0.0.0',
                port,
                reuse_address=True
            )
            await self.site.start()

            self._set_state("running")

            if self.logger:
                self.logger(f"HTTP API server started on port {port}")

        except OSError as e:
            self._set_state("error")
            if self.logger:
                if e.errno == 98 or e.errno == 10048:
                    self.logger(f"ERROR: Port {port} is already in use")
                else:
                    self.logger(f"Socket error starting HTTP server: {e}")
        except Exception as e:
            self._set_state("error")
            if self.logger:
                self.logger(f"Error starting HTTP server: {e}")

    def _run_event_loop(self, port: int):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_server_async(port))
        self.loop.run_forever()

    def start(self, port: int = None) -> bool:
        """Start the HTTP server (non-blocking, returns immediately)"""
        if self.get_state() in ("running", "starting"):
            return True

        try:
            port = port or config.HTTP_PORT
            self._port = port

            # Set state immediately
            self._set_state("starting")

            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()

            # Start event loop in background thread
            self.loop_thread = threading.Thread(
                target=self._run_event_loop,
                args=(port,),
                daemon=True
            )
            self.loop_thread.start()

            # Wait a tiny bit for server to actually start (aiohttp is fast)
            import time
            time.sleep(0.05)  # 50ms - enough for aiohttp to bind socket

            return True

        except Exception as e:
            self._set_state("error")
            if self.logger:
                self.logger(f"Error launching HTTP server: {e}")
            return False

    def stop(self) -> bool:
        """Stop the HTTP server"""
        if self.get_state() == "stopped":
            return True

        try:
            if self.loop and self.loop.is_running():
                # Schedule shutdown in the event loop
                asyncio.run_coroutine_threadsafe(self._stop_server_async(), self.loop)

                # Wait a bit for clean shutdown
                import time
                time.sleep(0.1)

                # Stop the event loop
                self.loop.call_soon_threadsafe(self.loop.stop)

            self._set_state("stopped")

            if self.logger:
                self.logger("HTTP API server stopped")

            return True

        except Exception as e:
            self._set_state("error")
            if self.logger:
                self.logger(f"Error stopping HTTP server: {e}")
            return False

    async def _stop_server_async(self):
        """Stop the server (async)"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    def restart(self, port: int = None) -> bool:
        """Restart the HTTP server"""
        self.stop()
        import time
        time.sleep(0.2)
        return self.start(port)
