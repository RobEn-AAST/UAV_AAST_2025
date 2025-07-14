import socket
import subprocess
import ipaddress
import platform
import sys
import importlib.util
import time
import signal
from argparse import ArgumentParser

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'

def ping_host(ip, timeout=1):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    try:
        result = subprocess.run(
            ['ping', param, '1', timeout_param, str(timeout), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 0.5
        )
        return result.returncode == 0
    except Exception:
        return False

def scan_network(subnet, timeout=1, scan_timeout=30):
    active_ips = []
    network = ipaddress.IPv4Network(subnet, strict=False)
    local_ip = get_local_ip()

    print(f"Scanning subnet {subnet} for active hosts...", flush=True)
    start_time = time.time()

    for ip in network.hosts():
        ip = str(ip)
        if ip == local_ip or ip.endswith('.0') or ip.endswith('.255'):
            continue

        if time.time() - start_time > scan_timeout:
            print("Scan timeout reached.", flush=True)
            break

        if ping_host(ip, timeout=timeout):
            print(f"Host alive: {ip}", flush=True)
            active_ips.append(ip)

    return active_ips

def run_mavproxy(target_ips, base_port=14550, master_port=None):
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
        f'--out=udpbcast:0.0.0.0:{base_port}',  # Broadcast
    ]

    for ip in target_ips:
        base_cmd.append(f'--out=udp:{ip}:{base_port}')

    print("\nRunning MAVProxy with command:", ' '.join(base_cmd), flush=True)

    try:
        proc = subprocess.Popen(base_cmd)
        print(f"MAVProxy started (PID: {proc.pid})", flush=True)
        return proc
    except Exception as e:
        print(f"Failed to start MAVProxy: {e}", flush=True)
        sys.exit(1)

def parse_args():
    parser = ArgumentParser(description='MAVProxy launcher with automatic network scanning')
    parser.add_argument('--port', type=int, default=14550, help='UDP port (default: 14550)')
    parser.add_argument('--master-port', type=int, help='Separate master port (default: same as port)')
    parser.add_argument('--scan-timeout', type=int, default=30, help='Scan timeout in seconds (default: 30)')
    parser.add_argument('--subnet', type=str, help='Subnet to scan (default: auto-detect from local IP)')
    return parser.parse_args()

# ✅ This global will be used in signal handler
mavproxy_proc = None

def handle_termination(signum, frame):
    print("\nSignal received, shutting down MAVProxy...", flush=True)
    global mavproxy_proc
    if mavproxy_proc is not None:
        mavproxy_proc.terminate()
        try:
            mavproxy_proc.wait(timeout=3)
            print("MAVProxy terminated cleanly.", flush=True)
        except subprocess.TimeoutExpired:
            mavproxy_proc.kill()
            print("MAVProxy force killed.", flush=True)
    sys.exit(0)

if __name__ == "__main__":
    # ✅ Register signal handler to stop MAVProxy when GUI calls .terminate()
    signal.signal(signal.SIGTERM, handle_termination)

    args = parse_args()
    try:
        local_ip = get_local_ip()
        subnet = args.subnet if args.subnet else '.'.join(local_ip.split('.')[:3]) + '.0/24'

        print(f"Local IP: {local_ip}", flush=True)
        print(f"Using subnet: {subnet}", flush=True)

        active_hosts = scan_network(subnet, scan_timeout=args.scan_timeout)

        if not active_hosts:
            print("No active hosts found in subnet.", flush=True)
        else:
            print(f"Active hosts found: {active_hosts}", flush=True)

        if local_ip not in active_hosts:
            active_hosts.append(local_ip)

        # ✅ Assign the MAVProxy process globally so we can kill it on SIGTERM
        mavproxy_proc = run_mavproxy(active_hosts, base_port=args.port, master_port=args.master_port)

        # Wait forever or until killed
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}", flush=True)
        sys.exit(1)
