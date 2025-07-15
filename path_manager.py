import os
import json
import platform
from pathlib import Path
from typing import Dict, Optional

class PathManager:
    """
    Smart path management system that automatically adapts to different environments
    and provides consistent file paths across different operating systems and developers.
    """
    
    def __init__(self, project_name: str = "UAV_AAST_2025"):
        self.project_name = project_name
        self.project_root = self._find_project_root()
        self.os_type = platform.system().lower()
        self._paths_cache = {}
        
    def _find_project_root(self) -> Path:
        """
        Automatically find the project root directory by looking for specific markers.
        """
        current_dir = Path(__file__).resolve()
        
        # Look for project markers (files/folders that indicate project root)
        project_markers = [
            'backend',
            'frontend', 
            'files',
            'data.json',
            '.git',
            'requirements.txt'
        ]
        
        # Traverse up the directory tree
        for parent in [current_dir] + list(current_dir.parents):
            if any((parent / marker).exists() for marker in project_markers):
                return parent
                
        # Fallback: assume we're in the project root
        return current_dir.parent if current_dir.name in ['backend', 'frontend'] else current_dir
    
    def get_project_path(self, relative_path: str = "") -> str:
        """
        Get absolute path relative to project root.
        
        Args:
            relative_path: Path relative to project root (e.g., "files/data.json")
            
        Returns:
            Absolute path as string
        """
        if relative_path in self._paths_cache:
            return self._paths_cache[relative_path]
            
        full_path = self.project_root / relative_path
        result = str(full_path.resolve())
        self._paths_cache[relative_path] = result
        return result
    
    def get_files_dir(self) -> str:
        """Get the files directory path."""
        return self.get_project_path("files")
    
    def get_backend_dir(self) -> str:
        """Get the backend directory path."""
        return self.get_project_path("backend")
    
    def get_frontend_dir(self) -> str:
        """Get the frontend directory path."""
        return self.get_project_path("frontend")
    
    def get_output_dir(self, subdir: str = "Output") -> str:
        """Get or create output directory path."""
        output_path = self.get_project_path(f"files/{subdir}")
        os.makedirs(output_path, exist_ok=True)
        return output_path
    
    def get_file_path(self, filename: str, subdirectory: str = "files") -> str:
        """
        Get full path for a file in the specified subdirectory.
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory within project (default: "files")
            
        Returns:
            Full path to the file
        """
        return self.get_project_path(f"{subdirectory}/{filename}")
    
    def load_config(self, config_file: str = "data.json") -> Dict:
        """
        Load configuration file and update paths to be system-independent.
        
        Args:
            config_file: Name of config file (default: "data.json")
            
        Returns:
            Configuration dictionary with updated paths
        """
        config_path = self.get_file_path(config_file)
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update all file paths in config to use smart paths
            config = self._update_config_paths(config)
            return config
            
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            return self._create_default_config()
        except json.JSONDecodeError:
            print(f"Invalid JSON in config file: {config_path}")
            return self._create_default_config()
    
    def _update_config_paths(self, config: Dict) -> Dict:
        """Update hardcoded paths in config to use smart paths."""
        
        # Define path mappings
        path_mappings = {
            # Waypoint files
            'waypoints_file_waypoint': 'files/mission1.waypoints',
            'waypoints_file_csv': 'files/waypoints.csv',
            'fence_file_waypoint': 'files/fence.waypoints', 
            'fence_file_csv': 'files/fence.csv',
            'payload_file_waypoint': 'files/payload.waypoints',
            'payload_file_csv': 'files/payload.csv',
            'network_ips_csv': 'files/network_ips.csv',
            'obs_csv': 'files/obstacles.csv',
            'obs_waypoints': 'files/obstacles.waypoints',
            'wp_plus_obs_csv': 'files/wp_plus_obs.csv',
            'survey_csv': 'files/survey.csv',
            'survey_waypoints': 'files/survey.waypoints',
            
            # Special files
            'pdf_mission': 'files/mission.pdf',
            'docx_file': 'backend/modules/entries/pdf_reader_files/Output/new_converted.docx'
        }
        
        # Update paths
        for key, relative_path in path_mappings.items():
            if key in config:
                config[key] = self.get_project_path(relative_path)
        
        return config
    
    def _create_default_config(self) -> Dict:
        """Create a default configuration with smart paths."""
        return {
            # File paths (auto-generated)
            "waypoints_file_waypoint": self.get_file_path("mission1.waypoints"),
            "waypoints_file_csv": self.get_file_path("waypoints.csv"),
            "fence_file_waypoint": self.get_file_path("fence.waypoints"),
            "fence_file_csv": self.get_file_path("fence.csv"),
            "payload_file_waypoint": self.get_file_path("payload.waypoints"),
            "payload_file_csv": self.get_file_path("payload.csv"),
            "network_ips_csv": self.get_file_path("network_ips.csv"),
            "obs_csv": self.get_file_path("obstacles.csv"),
            "obs_waypoints": self.get_file_path("obstacles.waypoints"),
            "wp_plus_obs_csv": self.get_file_path("wp_plus_obs.csv"),
            "survey_csv": self.get_file_path("survey.csv"),
            "survey_waypoints": self.get_file_path("survey.waypoints"),
            "pdf_mission": self.get_file_path("mission.pdf"),
            "docx_file": self.get_project_path("backend/modules/entries/pdf_reader_files/Output/new_converted.docx"),
            
            # Configuration parameters
            "home_lat": 29.8146013,
            "home_long": 30.8256198,
            "take_off_alt": 40,
            "take_off_angle": 15,
            "do_jump_repeat_count": 8,
            "ip_range": "192.168.1.1/24",
            "sim_connection_string": "172.26.16.1:14550",
            "telem_link": "com5",
            "raspberry_pi_connection_string": "coco",
            "aircraftAltitude": 80,
            "aircraftVelocity": 22,
            "windSpeed": 0,
            "windBearing": 190,
            "payload_servo_no": 10,
            "PAYLOAD_OPEN_PWM_VALUE": 2000,
            "PAYLOAD_CLOSE_PWM_VALUE": 1200,
            "Sensor_width": 0.0235,
            "sensor_height": 0.0156,
            "survey_alt": 70,
            "image_width": 6000,
            "focal_length_max": 0.05,
            "focal_length_min": 0.016,
            "start_land_dist": 100,
            "loiter_target_alt": 20,
            "loiter_rad": 50,
            "drop_close_delay": 2,
            "obs_safe_dist": 5,
            "bank_angle": 40,
            "obs_raduies": 5
        }
    
    def save_config(self, config: Dict, config_file: str = "data.json") -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            config_file: Name of config file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = self.get_file_path(config_file)
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def ensure_directories_exist(self):
        """Create necessary directories if they don't exist."""
        directories = [
            "files",
            "files/Output",
            "backend/modules/entries/pdf_reader_files/Output",
            "frontend/utils/Output"
        ]
        
        for directory in directories:
            dir_path = self.get_project_path(directory)
            os.makedirs(dir_path, exist_ok=True)
    
    def get_connection_string_for_platform(self, base_string: str) -> str:
        """
        Adapt connection strings for different platforms.
        
        Args:
            base_string: Base connection string
            
        Returns:
            Platform-appropriate connection string
        """
        if self.os_type == "windows":
            # Windows serial ports
            if base_string.startswith("/dev/"):
                return base_string.replace("/dev/ttyUSB", "COM").replace("/dev/ttyACM", "COM")
        else:
            # Linux/Mac serial ports
            if base_string.startswith("COM"):
                return f"/dev/ttyUSB{base_string[3:]}" if "COM" in base_string else base_string
                
        return base_string
    
    def __str__(self) -> str:
        return f"PathManager(project_root={self.project_root}, os={self.os_type})"


# Global instance for easy access
path_manager = PathManager()


# Convenience functions for backward compatibility
def get_project_path(relative_path: str = "") -> str:
    """Get absolute path relative to project root."""
    return path_manager.get_project_path(relative_path)

def get_config_path() -> str:
    """Get the data.json config file path."""
    return path_manager.get_file_path("data.json")

def load_smart_config() -> Dict:
    """Load configuration with smart path resolution."""
    return path_manager.load_config()


if __name__ == "__main__":
    # Example usage and testing
    pm = PathManager()
    
    print(f"Project root: {pm.project_root}")
    print(f"Files directory: {pm.get_files_dir()}")
    print(f"Config path: {pm.get_file_path('data.json')}")
    
    # Ensure directories exist
    pm.ensure_directories_exist()
    
    # Load and display config
    config = pm.load_config()
    print(f"\nSample config paths:")
    print(f"Waypoints CSV: {config.get('waypoints_file_csv')}")
    print(f"Fence CSV: {config.get('fence_file_csv')}")
    
    # Test platform-specific connection strings
    test_connections = ["com5", "/dev/ttyUSB0", "172.26.16.1:14550"]
    print(f"\nConnection string adaptation for {pm.os_type}:")
    for conn in test_connections:
        adapted = pm.get_connection_string_for_platform(conn)
        print(f"  {conn} -> {adapted}")