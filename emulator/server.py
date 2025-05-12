"""
Network server implementation for FlashForge Emulator
"""
import socket
import threading
import binascii
import time
from .commands import process_command
import config

class EmulatorServer:
    """Server implementation for FlashForge Emulator"""
    
    def __init__(self, printer_config, virtual_files, thumbnail_path, logger=None):
        self.config = printer_config
        self.virtual_files = virtual_files
        self.thumbnail_path = thumbnail_path
        self.log = logger if logger else print
        
        # Server state
        self.discovery_server = None
        self.tcp_server = None
        self.tcp_clients = []
        self.is_running = False
    
    def start(self):
        """Start the discovery and TCP command servers"""
        try:
            # Start discovery server (UDP)
            self.discovery_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_server.bind(('0.0.0.0', config.DISCOVERY_PORT))
            threading.Thread(target=self.handle_discovery, daemon=True).start()
            
            # Start TCP command server
            self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_server.bind(('0.0.0.0', config.COMMAND_PORT))
            self.tcp_server.listen(5)
            threading.Thread(target=self.handle_tcp_connections, daemon=True).start()
            
            self.is_running = True
            self.log(f"Emulator services started on {self.config['ip_address']}")
            self.log(f"Discovery service running on UDP port {config.DISCOVERY_PORT}")
            self.log(f"TCP API service running on port {config.COMMAND_PORT}")
            
            return True
        except Exception as e:
            self.log(f"Error starting servers: {str(e)}")
            self.stop()
            return False
    
    def stop(self):
        """Stop all server threads"""
        try:
            # Stop discovery server
            if self.discovery_server:
                self.discovery_server.close()
                self.discovery_server = None
            
            # Close all client connections
            for client in self.tcp_clients:
                try:
                    client.close()
                except:
                    pass
            self.tcp_clients = []
            
            # Stop TCP server
            if self.tcp_server:
                self.tcp_server.close()
                self.tcp_server = None
            
            self.is_running = False
            self.log("Emulator services stopped")
            return True
        except Exception as e:
            self.log(f"Error stopping servers: {str(e)}")
            return False
    
    def handle_discovery(self):
        """Handle printer discovery UDP requests"""
        self.log("Discovery service started")
        
        # Get the primary network interface IP - our emulated printer will only be available on this IP
        emulator_ip = self.config['ip_address']
        
        try:
            while self.discovery_server:
                try:
                    # Wait for an incoming discovery packet
                    data, addr = self.discovery_server.recvfrom(1024)
                    
                    # Check if this is the expected discovery packet format
                    if not data.startswith(b'www.usr'):
                        continue
                    
                    # Log the discovery request
                    discovery_hex = binascii.hexlify(data).decode('ascii')
                    self.log(f"Discovery request from {addr[0]}:{addr[1]} - Data: {discovery_hex}")
                    
                    # Only respond from the primary network interface
                    # Determine the local IP we would use to reach this address
                    local_ip = None
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect((addr[0], 1))
                        local_ip = s.getsockname()[0]
                        s.close()
                    except:
                        pass
                    
                    # If we're responding with an IP different from our configured one, skip it
                    if local_ip and local_ip != emulator_ip:
                        self.log(f"Skipping response from {local_ip} (not our primary emulator IP {emulator_ip})")
                        continue
                    
                    # Create the discovery response packet
                    response = bytearray(0xC4)  # Response length 196 bytes
                    
                    # Set printer name at offset 0x00 (32 bytes)
                    name_bytes = self.config['printer_name'].encode('ascii')
                    response[0:len(name_bytes)] = name_bytes
                    
                    # Set serial number at offset 0x92 (32 bytes)
                    serial_bytes = self.config['serial_number'].encode('ascii')
                    response[0x92:0x92+len(serial_bytes)] = serial_bytes
                    
                    # Send the response back
                    self.discovery_server.sendto(response, addr)
                    self.log(f"Sent discovery response to {addr[0]}:{addr[1]} from {emulator_ip}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.discovery_server:  # Only log if still running
                        self.log(f"Discovery error: {str(e)}")
        except Exception as e:
            self.log(f"Discovery service error: {str(e)}")
        
        self.log("Discovery service stopped")
    
    def handle_tcp_connections(self):
        """Accept and handle TCP connections for printer commands"""
        self.log("TCP server started")
        
        try:
            while self.tcp_server:
                try:
                    # Accept a new connection
                    client_socket, addr = self.tcp_server.accept()
                    client_socket.settimeout(60)  # 60 second timeout
                    self.tcp_clients.append(client_socket)
                    
                    # Start a new thread to handle this client
                    threading.Thread(
                        target=self.handle_client_commands,
                        args=(client_socket, addr),
                        daemon=True
                    ).start()
                    
                    self.log(f"New client connected: {addr[0]}:{addr[1]}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.tcp_server:  # Only log if still running
                        self.log(f"TCP server error: {str(e)}")
        except Exception as e:
            self.log(f"TCP server error: {str(e)}")
        
        self.log("TCP server stopped")
    
    def handle_client_commands(self, client_socket, addr):
        """Handle commands from a specific client"""
        try:
            while True:
                # Receive command
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Parse command
                command = data.decode('ascii', errors='replace').strip()
                self.log(f"Received command from {addr[0]}: {command}")
                
                # Process command and get response
                response = process_command(command, self.config, self.thumbnail_path, 
                                         self.virtual_files, self.log)
                
                # Log the command and response type (for debugging)
                #if command == "~M115" or command == "~M119":
                #    self.log(f"Command {command} - generating status response")
                
                # Send response
                if isinstance(response, str):
                    client_socket.sendall(response.encode('ascii'))
                elif isinstance(response, bytes):
                    client_socket.sendall(response)
                else:
                    client_socket.sendall(response)
                
                if isinstance(response, str):
                    # Only truncate extremely long responses
                    log_response = response
                    if len(log_response) > 500:  # Increased from 100 to 500
                        # Try to find a line break near the truncation point
                        truncate_pos = log_response[:500].rfind('\n')
                        if truncate_pos < 0:
                            truncate_pos = 500
                        log_response = f"{log_response[:truncate_pos]}\n... (truncated, {len(response)} bytes total)"
                    self.log(f"Sent response: \n{log_response}")
                else:
                    self.log(f"Sent binary response: {len(response)} bytes")
        except Exception as e:
            self.log(f"Error handling client {addr[0]}: {str(e)}")
        finally:
            # Clean up
            try:
                client_socket.close()
                if client_socket in self.tcp_clients:
                    self.tcp_clients.remove(client_socket)
            except:
                pass
            
            self.log(f"Client disconnected: {addr[0]}:{addr[1]}")
