import subprocess
import socket
import ipaddress
import time
import platform  # For OS detection

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

def start_mavproxy(master_connection, baudrate=115200):
    """
    Start MAVProxy with UDP outputs for IP range 192.168.1.1-15 and localhost
    Args:
        master_connection (str): --master connection string (e.g., "com5" or "udp:172.26.16.1:14550")
        baudrate (int): Serial baud rate (default: 115200)
    """
    import platform

    mavproxy_cmd = "mavproxy.exe" if platform.system().lower() == "windows" else "mavproxy.py"
    
    base_ip = "192.168.1."
    target_ips = [f"{base_ip}{i}" for i in range(1, 16)]
    target_ips.append("127.0.0.1")
    
    command = [mavproxy_cmd]
    
    if ":" in master_connection:
        command.append(f"--master={master_connection}")
    else:
        command.extend([f"--master={master_connection}", f"--baudrate={baudrate}"])
    
    command.extend([f"--out=udp:{ip}:14550" for ip in target_ips])

    if platform.system().lower() == "windows":
        # Build the full PowerShell command string
        full_command_str = " ".join(command)

        subprocess.Popen([
            "powershell", "-NoExit", "-Command", full_command_str
        ])
    else:
        subprocess.Popen(['x-terminal-emulator', '-e'] + command)