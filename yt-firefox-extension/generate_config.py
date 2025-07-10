#!/usr/bin/env python3
"""
Script to generate config.js from .env file
Run this script to automatically update the extension configuration
"""

import os
import sys
from pathlib import Path

def read_env_file(env_path):
    """Read .env file and return a dictionary of key-value pairs"""
    env_vars = {}
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('\'"')
                    env_vars[key.strip()] = value
    except FileNotFoundError:
        print(f"Error: .env file not found at {env_path}")
        return None
    except Exception as e:
        print(f"Error reading .env file: {e}")
        return None
    
    return env_vars

def generate_config_js(env_vars, output_path):
    """Generate config.js file from environment variables"""
    
    # Get YouTube API key from env file
    youtube_api_key = env_vars.get('YT-API', 'YOUR_API_KEY_HERE')
    
    config_content = f"""// Configuration file for the Firefox extension
// This file is auto-generated from .env file
// DO NOT edit manually - run generate_config.py instead

const CONFIG = {{
  // YouTube Data API key
  YOUTUBE_API_KEY: '{youtube_api_key}',
  
  // Sentiment analysis API endpoint
  API_URL: 'http://23.20.221.231:8080/',
  
  // Alternative endpoints for development
  // API_URL: 'http://localhost:5000/',
  
  // Maximum number of comments to fetch
  MAX_COMMENTS: 500,
  
  // Comments per API request
  COMMENTS_PER_REQUEST: 100
}};"""

    try:
        with open(output_path, 'w') as f:
            f.write(config_content)
        print(f"✅ Successfully generated {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing config.js: {e}")
        return False

def main():
    # Get the script directory
    script_dir = Path(__file__).parent
    
    # Path to .env file (parent directory)
    env_path = script_dir.parent / '.env'
    
    # Path to config.js (same directory as script)
    config_path = script_dir / 'config.js'
    
    print("🔄 Generating config.js from .env file...")
    print(f"📁 Reading .env from: {env_path}")
    print(f"📝 Writing config.js to: {config_path}")
    
    # Read environment variables
    env_vars = read_env_file(env_path)
    if env_vars is None:
        sys.exit(1)
    
    # Check if YouTube API key exists
    if 'YT-API' not in env_vars:
        print("⚠️  Warning: YT-API not found in .env file")
        print("Make sure your .env file contains: YT-API=your_api_key_here")
    
    # Generate config.js
    if generate_config_js(env_vars, config_path):
        print("🎉 Configuration updated successfully!")
        print("🔧 You can now load the Firefox extension")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
