#!/usr/bin/env python3
"""
Configuration Migration Script
Converts hardcoded paths in data.json to use the smart path system.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Import the path manager
from path_manager import PathManager

def backup_config(config_path: str) -> str:
    """Create a backup of the existing config file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{config_path}.backup_{timestamp}"
    shutil.copy2(config_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def migrate_config():
    """Main migration function."""
    path_manager = PathManager()
    config_path = path_manager.get_file_path("data.json")
    
    print("=" * 60)
    print("UAV Project Configuration Migrator")
    print("=" * 60)
    print(f"Project root: {path_manager.project_root}")
    print(f"Target OS: {path_manager.os_type}")
    print(f"Config file: {config_path}")
    print()
    
    # Check if config exists
    if not os.path.exists(config_path):
        print("❌ No existing data.json found.")
        print("📝 Creating new configuration with smart paths...")
        
        # Create default config
        new_config = path_manager._create_default_config()
        success = path_manager.save_config(new_config)
        
        if success:
            print("✅ New configuration created successfully!")
            print_config_summary(new_config)
        else:
            print("❌ Failed to create new configuration.")
        return
    
    # Load existing config
    try:
        print("📖 Loading existing configuration...")
        with open(config_path, 'r') as f:
            old_config = json.load(f)
        
        # Create backup
        backup_path = backup_config(config_path)
        
        # Migrate paths
        print("🔄 Migrating paths to smart path system...")
        new_config = path_manager._update_config_paths(old_config.copy())
        
        # Preserve all other settings
        for key, value in old_config.items():
            if key not in ['waypoints_file_waypoint', 'waypoints_file_csv', 
                          'fence_file_waypoint', 'fence_file_csv',
                          'payload_file_waypoint', 'payload_file_csv',
                          'network_ips_csv', 'obs_csv', 'obs_waypoints',
                          'wp_plus_obs_csv', 'survey_csv', 'survey_waypoints',
                          'pdf_mission', 'docx_file']:
                new_config[key] = value
        
        # Save migrated config
        success = path_manager.save_config(new_config)
        
        if success:
            print("✅ Configuration migrated successfully!")
            print_config_summary(new_config)
            verify_files(new_config)
        else:
            print("❌ Failed to save migrated configuration.")
            print(f"🔙 Restoring backup from: {backup_path}")
            shutil.copy2(backup_path, config_path)
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'backup_path' in locals():
            print(f"🔙 Restoring backup from: {backup_path}")
            shutil.copy2(backup_path, config_path)

def print_config_summary(config: dict):
    """Print a summary of the migrated configuration."""
    print("\n" + "=" * 40)
    print("📋 Configuration Summary")
    print("=" * 40)
    
    file_paths = [
        'waypoints_file_csv', 'fence_file_csv', 'payload_file_csv',
        'obs_csv', 'survey_csv', 'pdf_mission'
    ]
    
    for key in file_paths:
        if key in config:
            path = config[key]
            exists = "✓" if os.path.exists(path) else "✗"
            print(f"{exists} {key}: {path}")
    
    print(f"\n🏠 Home coordinates: ({config.get('home_lat', 'N/A')}, {config.get('home_long', 'N/A')})")
    print(f"🛰️  Default connection: {config.get('sim_connection_string', 'N/A')}")
    
def verify_files(config: dict):
    """Verify that referenced files exist and suggest creating missing ones."""
    print("\n" + "=" * 40)
    print("📁 File Verification")
    print("=" * 40)
    
    required_files = {
        'waypoints_file_csv': 'Waypoints CSV file',
        'fence_file_csv': 'Fence boundary CSV file', 
        'payload_file_csv': 'Payload drop CSV file',
        'obs_csv': 'Obstacles CSV file',
        'survey_csv': 'Survey area CSV file'
    }
    
    missing_files = []
    
    for key, description in required_files.items():
        if key in config:
            path = config[key]
            if os.path.exists(path):
                print(f"✓ {description}: Found")
            else:
                print(f"✗ {description}: Missing")
                missing_files.append((key, path, description))
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} files are missing.")
        print("💡 You can create these files using the frontend 'Reading' page")
        print("   or place your CSV files in the 'files' directory.")
        
        # Create empty CSV files with headers
        print("\n🔧 Creating template CSV files...")
        create_template_files(missing_files)
    else:
        print("\n✅ All required files found!")

def create_template_files(missing_files):
    """Create template CSV files for missing files."""
    templates = {
        'waypoints_file_csv': ['lat,long,alt', '29.8146013,30.8256198,70'],
        'fence_file_csv': ['lat,long', '29.8146013,30.8256198'],
        'payload_file_csv': ['lat,long,alt', '29.8163887,30.8234739,70'],
        'obs_csv': ['lat,long,radius', '29.8150000,30.8250000,5'],
        'survey_csv': ['lat,long,alt', '29.8146013,30.8256198,70']
    }
    
    for key, path, description in missing_files:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Create template file
            if key in templates:
                with open(path, 'w') as f:
                    f.write('\n'.join(templates[key]) + '\n')
                print(f"  ✓ Created template: {os.path.basename(path)}")
            else:
                # Create empty file
                with open(path, 'w') as f:
                    f.write('')
                print(f"  ✓ Created empty: {os.path.basename(path)}")
                
        except Exception as e:
            print(f"  ✗ Failed to create {os.path.basename(path)}: {e}")

def test_path_system():
    """Test the path system functionality."""
    print("\n" + "=" * 40) 
    print("🧪 Testing Path System")
    print("=" * 40)
    
    path_manager = PathManager()
    
    # Test basic paths
    test_paths = [
        ("Project root", ""),
        ("Files directory", "files"),
        ("Backend directory", "backend"), 
        ("Frontend directory", "frontend"),
        ("Config file", "files/data.json"),
        ("Output directory", "files/Output")
    ]
    
    for name, relative_path in test_paths:
        try:
            full_path = path_manager.get_project_path(relative_path)
            exists = "✓" if os.path.exists(full_path) else "✗"
            print(f"{exists} {name}: {full_path}")
        except Exception as e:
            print(f"✗ {name}: Error - {e}")
    
    # Test connection string adaptation
    print(f"\n🔌 Connection String Adaptation ({path_manager.os_type}):")
    test_connections = [
        "com5", 
        "/dev/ttyUSB0", 
        "172.26.16.1:14550",
        "COM4",
        "udp:127.0.0.1:14550"
    ]
    
    for conn in test_connections:
        adapted = path_manager.get_connection_string_for_platform(conn)
        if conn != adapted:
            print(f"  {conn} → {adapted}")
        else:
            print(f"  {conn} (unchanged)")

def interactive_setup():
    """Interactive setup for first-time users."""
    print("\n" + "=" * 40)
    print("🚀 Interactive Setup")
    print("=" * 40)
    
    path_manager = PathManager()
    config = path_manager.load_config()
    
    print("Let's configure some basic settings for your UAV project:")
    
    # Home coordinates
    try:
        lat_input = input(f"\nHome Latitude [{config.get('home_lat', 29.8146013)}]: ").strip()
        if lat_input:
            config['home_lat'] = float(lat_input)
            
        lon_input = input(f"Home Longitude [{config.get('home_long', 30.8256198)}]: ").strip()
        if lon_input:
            config['home_long'] = float(lon_input)
    except ValueError:
        print("⚠️  Invalid coordinates, keeping defaults")
    
    # Connection preferences
    print(f"\nCurrent platform: {path_manager.os_type}")
    if path_manager.os_type == "windows":
        conn_input = input(f"Default connection [{config.get('sim_connection_string', 'COM5')}]: ").strip()
    else:
        conn_input = input(f"Default connection [{config.get('sim_connection_string', '/dev/ttyUSB0')}]: ").strip()
    
    if conn_input:
        config['sim_connection_string'] = conn_input
    
    # Save updated config
    if path_manager.save_config(config):
        print("✅ Configuration updated successfully!")
    else:
        print("❌ Failed to save configuration")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='UAV Project Configuration Migrator')
    parser.add_argument('--migrate', action='store_true', help='Migrate existing config')
    parser.add_argument('--test', action='store_true', help='Test path system')
    parser.add_argument('--setup', action='store_true', help='Interactive setup')
    parser.add_argument('--all', action='store_true', help='Run migration, test, and setup')
    
    args = parser.parse_args()
    
    if args.all:
        migrate_config()
        test_path_system() 
        interactive_setup()
    elif args.migrate:
        migrate_config()
    elif args.test:
        test_path_system()
    elif args.setup:
        interactive_setup()
    else:
        # Default behavior - run migration
        migrate_config()
        
        # Ask if user wants to run tests
        response = input("\n🧪 Would you like to test the path system? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            test_path_system()
            
        # Ask if user wants interactive setup
        response = input("\n⚙️  Would you like to run interactive setup? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_setup()
    
    print("\n" + "=" * 60)
    print("🎉 Migration completed!")
    print("💡 Your project now uses smart path management.")
    print("📝 All team members can use the same code without path changes.")
    print("=" * 60)

if __name__ == "__main__":
    main()