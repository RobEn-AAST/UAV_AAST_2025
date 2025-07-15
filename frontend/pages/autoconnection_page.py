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


from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QProgressBar
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QTimer
import subprocess
import sys

class AutoConnectionWorker(QObject):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, subnet, port, master_port, scan_timeout):
        super().__init__()
        self.subnet = subnet
        self.port = port
        self.master_port = master_port
        self.scan_timeout = scan_timeout
        self.process = None
    
    def run_scan_and_mavproxy(self):
        try:
            self.log_signal.emit("Starting network scan...")
            active_hosts = scan_network(self.subnet, scan_timeout=self.scan_timeout)
            
            if not active_hosts:
                self.log_signal.emit("No active hosts found.")
                active_hosts = [get_local_ip()]
            
            self.log_signal.emit(f"Found {len(active_hosts)} active hosts")
            for host in active_hosts:
                self.log_signal.emit(f"  - {host}")
            
            self.log_signal.emit("Starting MAVProxy...")
            self.process = run_mavproxy(active_hosts, self.port, self.master_port)
            self.log_signal.emit(f"MAVProxy started (PID: {self.process.pid})")
            
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
        finally:
            self.finished_signal.emit()
    
    def stop_mavproxy(self):
        if self.process:
            try:
                self.process.terminate()
                self.log_signal.emit("MAVProxy terminated")
            except:
                pass

class AutoConnectionPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.thread = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Automatic Network Connection & MAVProxy")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Settings section
        settings_layout = QVBoxLayout()
        
        # Subnet input
        subnet_layout = QHBoxLayout()
        subnet_layout.addWidget(QLabel("Subnet:"))
        self.subnet_input = QLineEdit("192.168.1.0/24")
        subnet_layout.addWidget(self.subnet_input)
        settings_layout.addLayout(subnet_layout)
        
        # Port settings
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(14550)
        port_layout.addWidget(self.port_spin)
        
        port_layout.addWidget(QLabel("Master Port:"))
        self.master_port_spin = QSpinBox()
        self.master_port_spin.setRange(1024, 65535)
        self.master_port_spin.setValue(14550)
        port_layout.addWidget(self.master_port_spin)
        settings_layout.addLayout(port_layout)
        
        # Scan timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Scan Timeout (sec):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        timeout_layout.addWidget(self.timeout_spin)
        settings_layout.addLayout(timeout_layout)
        
        layout.addLayout(settings_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Auto Connection")
        self.start_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_auto_connection)
        
        self.stop_button = QPushButton("Stop MAVProxy")
        self.stop_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px;")
        self.stop_button.clicked.connect(self.stop_auto_connection)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Log display
        layout.addWidget(QLabel("Log:"))
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(200)
        layout.addWidget(self.log_display)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def start_auto_connection(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.show()
        self.status_label.setText("Scanning network and starting MAVProxy...")
        
        # Create worker and thread
        self.worker = AutoConnectionWorker(
            self.subnet_input.text(),
            self.port_spin.value(),
            self.master_port_spin.value(),
            self.timeout_spin.value()
        )
        self.thread = QThread()
        
        # Connect signals
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_scan_and_mavproxy)
        self.worker.log_signal.connect(self.log_message)
        self.worker.finished_signal.connect(self.on_connection_finished)
        self.worker.finished_signal.connect(self.thread.quit)
        self.worker.finished_signal.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.thread.start()
    
    def stop_auto_connection(self):
        if self.worker:
            self.worker.stop_mavproxy()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.hide()
        self.status_label.setText("Stopped")
        self.log_message("Auto connection stopped by user")
    
    def on_connection_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(True)  # Keep enabled to allow stopping MAVProxy
        self.progress_bar.hide()
        self.status_label.setText("MAVProxy running")
    
    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")