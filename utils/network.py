"""
Network-related utilities for FlashForge Emulator
"""
import socket

def get_network_interfaces():
    """Get all network interfaces with their IP addresses"""
    interfaces = []
    try:
        # Get all network interfaces using socket.if_nameindex()
        for iface_name in socket.if_nameindex():
            try:
                ip = socket.gethostbyname(socket.gethostname())
                interfaces.append((iface_name[1], ip))
            except:
                pass
    except:
        # Alternative method for Windows
        try:
            # Try to get all IP addresses
            ips = socket.getaddrinfo(socket.gethostname(), None)
            for ip_info in ips:
                if ip_info[0] == socket.AF_INET:  # IPv4 only
                    ip = ip_info[4][0]
                    if not ip.startswith('127.'):  # Skip loopback
                        interfaces.append(("eth", ip))
        except:
            # Fallback: just use the primary IP
            interfaces.append(("eth0", socket.gethostbyname(socket.gethostname())))
    
    # Also explicitly try common IP patterns
    for ip_prefix in ['192.168.', '10.', '172.']:
        for i in range(254):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # This doesn't send any packets but allows us to see what IP would be used
                s.connect((f"{ip_prefix}1.1", 1))
                local_ip = s.getsockname()[0]
                s.close()
                if local_ip.startswith(ip_prefix) and local_ip not in [i[1] for i in interfaces]:
                    interfaces.append(("eth", local_ip))
                break
            except:
                pass
    
    return interfaces

def get_primary_ip(network_interfaces):
    """Get the primary IP address (non-loopback)"""
    # Try common network ranges first
    for prefix in ['192.168.', '10.', '172.']:
        for iface, ip in network_interfaces:
            if ip.startswith(prefix):
                return ip
    
    # If no common network ranges, return the first non-loopback IP
    for iface, ip in network_interfaces:
        if not ip.startswith('127.'):
            return ip
            
    # Last resort: return localhost
    return '127.0.0.1'
