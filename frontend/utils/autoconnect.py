import socket
import subprocess
import ipaddress
import platform
import sys
import importlib.util
import time
from argparse import ArgumentParser

def get_local_ip():
    """Get the local IP address with better fallback handling"""
    try:
        # Try to connect to a dummy address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
    except Exception:
        try:
            # Fallback to hostname resolution
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            # Ultimate fallback
            return '127.0.0.1'

def is_mavproxy_host(ip, port=14550, timeout=1):
    """Check if a host is actually running MAVProxy by testing the port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(b'\x00', (ip, port))  # Send dummy packet
            s.recvfrom(1024)  # See if anything responds
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception:
        return False

def scan_network(subnet, timeout=1, scan_timeout=30):
    """Scan network and filter for likely MAVProxy hosts"""
    active_ips = []
    network = ipaddress.IPv4Network(subnet, strict=False)
    
    print(f"Scanning {subnet}...", flush=True)
    
    start_time = time.time()
    for ip in network.hosts():
        ip = str(ip)
        
        # Skip common non-drone IPs
        if ip.endswith('.0') or ip.endswith('.1') or ip.endswith('.255'):
            continue
            
        if time.time() - start_time > scan_timeout:
            break
            
        try:
            # First do a ping check
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
            subprocess.run(
                ['ping', param, '1', timeout_param, str(timeout), ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout+0.5
            )
            
            # Then verify MAVProxy port
            if is_mavproxy_host(ip):
                active_ips.append(ip)
                print(f"Found MAVProxy host: {ip}", flush=True)
                
        except Exception:
            continue
    
    return active_ips

def run_mavproxy(other_ips, base_port=14550, master_port=None):
    """Run MAVProxy with proper error handling"""
    try:
        import MAVProxy
        mavproxy_path = importlib.util.find_spec('MAVProxy').origin
    except ImportError:
        print("Error: MAVProxy is not installed.", flush=True)
        print("Install with: pip install MAVProxy", flush=True)
        sys.exit(1)

    if master_port is None:
        master_port = base_port
        
    base_cmd = [
        sys.executable,
        mavproxy_path,
        f'--master=udp:0.0.0.0:{master_port}',
        '--out=udpbcast:0.0.0.0:{base_port}'
    ]
    
    for ip in other_ips:
        base_cmd.append(f'--out=udp:{ip}:{base_port}')
    
    print("\nRunning MAVProxy with:", ' '.join(base_cmd), flush=True)
    
    try:
        process = subprocess.Popen(base_cmd)
        print(f"MAVProxy started (PID: {process.pid})", flush=True)
        return process
    except Exception as e:
        print(f"Failed to start MAVProxy: {str(e)}", flush=True)
        sys.exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = ArgumentParser(description='MAVProxy network autoconfiguration tool')
    parser.add_argument('--port', type=int, default=14550,
                       help='Base UDP port (default: 14550)')
    parser.add_argument('--master-port', type=int,
                       help='Separate master port')
    parser.add_argument('--scan-timeout', type=int, default=30,
                       help='Scan timeout in seconds (default: 30)')
    parser.add_argument('--subnet', type=str,
                       help='Force subnet (e.g., 192.168.1.0/24)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    try:
        my_ip = get_local_ip()
        subnet = args.subnet if args.subnet else '.'.join(my_ip.split('.')[:3]) + '.0/24'
        
        print(f"Local IP: {my_ip}", flush=True)
        print(f"Scanning: {subnet}", flush=True)
        
        other_ips = scan_network(subnet, scan_timeout=args.scan_timeout)
        
        if not other_ips:
            print("No active MAVProxy hosts found", flush=True)
        else:
            print(f"\nActive hosts ({len(other_ips)}):", flush=True)
            for ip in other_ips:
                print(f"  - {ip}", flush=True)
        
        process = run_mavproxy(
            other_ips,
            base_port=args.port,
            master_port=args.master_port
        )
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...", flush=True)
            process.terminate()
            process.wait()
            print("Clean exit", flush=True)
            
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)
        sys.exit(1)