#!/usr/bin/env python3
"""
Test using PowerShell
"""

import subprocess
import sys

def test_endpoint():
    """Test endpoint using PowerShell"""
    try:
        print("Testing endpoint with PowerShell...")
        
        # Test with PowerShell
        cmd = [
            "powershell", "-Command",
            "Invoke-WebRequest -Uri 'http://localhost:8000/optimize-rag-meal' -Method POST"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()
