import subprocess
import socket
import ipaddress
import time
import platform  # For OS detection

def get_local_ip():
    """Get the local IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'

def scan_network(subnet, timeout=1, scan_timeout=30):
    """Scan network for active hosts"""
    active_ips = []
    network = ipaddress.IPv4Network(subnet, strict=False)
    
    print(f"Scanning {subnet}...")
    
    start_time = time.time()
    for ip in network.hosts():
        ip = str(ip)
        
        # Skip network/broadcast addresses
        if ip.endswith(('.0', '.1', '.255')):
            continue
            
        if time.time() - start_time > scan_timeout:
            break
            
        try:
            # Platform detection
            is_windows = platform.system().lower() == 'windows'
            
            # Ping command construction
            param = '-n' if is_windows else '-c'
            timeout_param = '-w' if is_windows else '-W'
            timeout_val = str(timeout * 1000) if is_windows else str(timeout)
            
            subprocess.run(
                ['ping', param, '1', timeout_param, timeout_val, ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout + 0.5,
                check=True
            )
            active_ips.append(ip)
            print(f"Found active host: {ip}")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            continue
    
    return active_ips

def start_mavproxy(master_connection):
    """
    Start MAVProxy with UDP outputs for IP range 192.168.1.1-15
    Args:
        master_connection (str): --master connection string (e.g., "udp:172.26.16.1:14550")
    """
    # MAVProxy executable (Windows/Linux compatible)
    mavproxy_cmd = "mavproxy.exe" if platform.system().lower() == "windows" else "mavproxy.py"
    
    # Generate --out arguments for all target IPs
    base_ip = "192.168.1."
    target_ips = [f"{base_ip}{i}" for i in range(1, 16)]  # 192.168.1.1 to 192.168.1.15
    
    # Build the full command
    command = [mavproxy_cmd, f"--master={master_connection}"]
    command += [f"--out=udp:{ip}:14550" for ip in target_ips]
    
    # Launch in new terminal (Windows)
    if platform.system().lower() == "windows":
        subprocess.Popen(["start", "cmd", "/k"] + command, shell=True)
    else:  # Linux/Mac
        subprocess.Popen(["x-terminal-emulator", "-e"] + command)