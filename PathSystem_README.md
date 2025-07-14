# Smart Path Management System

## Overview

The Smart Path Management System automatically resolves file paths for the UAV project, eliminating the need for manual path configuration across different development environments and operating systems.

## Features

- ✅ **Cross-platform compatibility** (Windows, Linux, macOS)
- ✅ **Automatic project root detection**
- ✅ **Platform-specific connection string adaptation**
- ✅ **Smart config file migration**
- ✅ **Template file generation**
- ✅ **Zero configuration for team members**

## Quick Start

### 1. Migration (One-time setup)

Run the migration script to convert your existing `data.json`:

```bash
# Run from project root
python path_manager.py
# or
python config_migrator.py --migrate
```

### 2. Using in Your Code

Replace hardcoded paths with the smart path manager:

```python
# Old way (don't do this)
config_path = "C:\\Users\\maria\\UAV project\\UAV_AAST_2025\\files\\data.json"

# New way (recommended)
from path_manager import PathManager
path_manager = PathManager()
config_path = path_manager.get_file_path("data.json")
config = path_manager.load_config()
```

### 3. Backend Integration

Your backend main.py should now use:

```python
from path_manager import PathManager

def main():
    path_manager = PathManager()
    config = path_manager.load_config()  # Auto-resolves all paths
    # ... rest of your code
```

### 4. Frontend Integration

Frontend pages can access smart paths:

```python
from path_manager import PathManager

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.path_manager = PathManager()
        config_path = self.path_manager.get_file_path("data.json")
```

## API Reference

### PathManager Class

#### Core Methods

```python
path_manager = PathManager()

# Get project root
root = path_manager.project_root

# Get absolute path from relative path
abs_path = path_manager.get_project_path("files/waypoints.csv")

# Get specific directories
files_dir = path_manager.get_files_dir()
backend_dir = path_manager.get_backend_dir()
frontend_dir = path_manager.get_frontend_dir()

# Get file paths
config_path = path_manager.get_file_path("data.json")
waypoints_path = path_manager.get_file_path("waypoints.csv")

# Load configuration with auto-resolved paths
config = path_manager.load_config()

# Save configuration
path_manager.save_config(config)

# Ensure directories exist
path_manager.ensure_directories_exist()

# Adapt connection strings for platform
adapted_conn = path_manager.get_connection_string_for_platform("COM5")
```

#### Convenience Functions

```python
from path_manager import get_project_path, get_config_path, load_smart_config

# Quick access functions
project_root = get_project_path()
config_file = get_config_path()
config = load_smart_config()
```

## Migration Features

The migration script (`config_migrator.py`) provides:

### Automatic Migration
```bash
python config_migrator.py --migrate
```
- Backs up existing `data.json`
- Converts hardcoded paths to smart paths
- Preserves all configuration values
- Creates missing directories

### Path System Testing
```bash
python config_migrator.py --test
```
- Verifies all paths resolve correctly
- Tests platform-specific adaptations
- Checks file/directory existence

### Interactive Setup
```bash
python config_migrator.py --setup
```
- Guided configuration setup
- Platform-appropriate defaults
- Validates user inputs

### Complete Setup
```bash
python config_migrator.py --all
```
- Runs migration, testing, and setup

## Platform Adaptations

### Connection Strings

The system automatically adapts connection strings:

**Windows:**
- `com5` → `com5`
- `/dev/ttyUSB0` → `COM0`
- IP addresses unchanged

**Linux/macOS:**
- `COM5` → `/dev/ttyUSB5`
- `/dev/ttyUSB0` → `/dev/ttyUSB0`
- IP addresses unchanged

### File Paths

All paths are automatically converted to the correct format:
- Windows: `C:\Project\files\data.json`
- Linux/macOS: `/home/user/Project/files/data.json`

## Directory Structure

The system expects this structure (auto-created if missing):

```
UAV_AAST_2025/
├── backend/
│   ├── modules/
│   └── main.py
├── frontend/
│   ├── pages/
│   └── main.py
├── files/
│   ├── data.json
│   ├── waypoints.csv
│   ├── fence.csv
│   └── Output/
├── path_manager.py
└── config_migrator.py
```

## Configuration File Format

After migration, your `data.json` will contain platform-independent paths:

```json
{
    "waypoints_file_csv": "/absolute/path/to/UAV_AAST_2025/files/waypoints.csv",
    "fence_file_csv": "/absolute/path/to/UAV_AAST_2025/files/fence.csv",
    "home_lat": 29.8146013,
    "home_long": 30.8256198,
    "sim_connection_string": "172.26.16.1:14550"
}
```

## Team Workflow

### For New Team Members

1. Clone the repository
2. Run: `python config_migrator.py`
3. Start developing - no path configuration needed!

### For Existing Team Members

1. Run migration once: `python config_migrator.py --migrate`
2. Update code to use `PathManager`
3. Commit changes (excluding personal `data.json` changes)

## Troubleshooting

### Common Issues

**Q: "Project root not found"**
A: Ensure you're running from within the project directory

**Q: "Config file not found"**
A: Run the migrator to create a default config

**Q: "Permission denied"**
A: Check file permissions on the `files/` directory

**Q: "Paths still hardcoded"**
A: Update your code to use `PathManager` instead of hardcoded paths

### Debug Information

Add debug output to see what the path manager is doing:

```python
path_manager = PathManager()
print(f"Project root: {path_manager.project_root}")
print(f"OS type: {path_manager.os_type}")
print(f"Config path: {path_manager.get_file_path('data.json')}")
```

## Best Practices

1. **Always use PathManager** instead of hardcoded paths
2. **Import at module level** for better performance
3. **Use relative paths** when calling path manager methods
4. **Don't commit** personal configuration changes
5. **Test on multiple platforms** when making path-related changes

## Migration Checklist

- [ ] Run `python config_migrator.py --migrate`
- [ ] Update backend main.py to use PathManager
- [ ] Update frontend pages to use PathManager
- [ ] Test on your platform
- [ ] Verify all file operations work
- [ ] Update team members about the change

## Examples

### Before (Hardcoded)
```python
config_path = "C:\\Users\\maria\\UAV project\\UAV_AAST_2025\\files\\data.json"
with open(config_path, 'r') as f:
    config = json.load(f)
waypoints_file = config['waypoints_file_csv']
```

### After (Smart Paths)
```python
from path_manager import PathManager

path_manager = PathManager()
config = path_manager.load_config()  # Auto-resolves all paths
waypoints_file = config['waypoints_file_csv']  # Already absolute path
```

---

**Benefits for Your Team:**
- No more "it works on my machine" issues
- Instant setup for new developers
- Cross-platform compatibility
- Cleaner, more maintainable code