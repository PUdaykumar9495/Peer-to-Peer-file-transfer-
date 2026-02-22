"""
Master Launcher for P2P File Sharing System
Launches all components in a coordinated manner
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path
import threading


def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print(" "*15 + "P2P FILE SHARING SYSTEM LAUNCHER")
    print("="*70 + "\n")


def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    try:
        import flask
        import tqdm
        import cryptography
        print("✅ All dependencies installed\n")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True


def setup_test_files():
    """Check and create test files if needed"""
    print("📁 Checking test files...")
    
    if not Path("shared_peer1").exists() or not Path("shared_peer2").exists():
        print("⚙️  Setting up test environment...\n")
        subprocess.run([sys.executable, "test_setup.py"])
        print()
    else:
        print("✅ Test files already exist\n")


def is_tracker_running():
    """Check if tracker is already running"""
    try:
        response = requests.get("http://127.0.0.1:5000/status", timeout=1)
        return response.status_code == 200
    except:
        return False


def start_tracker():
    """Start tracker server in new window"""
    print("🚀 Starting Tracker Server...")
    
    if is_tracker_running():
        print("✅ Tracker already running\n")
        return None
    
    if sys.platform == 'win32':
        # Windows: Start in new command window
        process = subprocess.Popen(
            ['cmd', '/c', 'start', 'cmd', '/k', 
             f'python tracker.py'],
            cwd=os.getcwd()
        )
    else:
        # Linux/Mac: Start in background
        process = subprocess.Popen(
            [sys.executable, 'tracker.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    # Wait for tracker to start
    print("⏳ Waiting for tracker to start", end="", flush=True)
    for _ in range(10):
        time.sleep(1)
        print(".", end="", flush=True)
        if is_tracker_running():
            print(" ✅\n")
            return process
    
    print("\n⚠️  Tracker may take longer to start\n")
    return process


def start_peer(peer_id, port):
    """Start a peer in new window"""
    print(f"🚀 Starting {peer_id.upper()} on port {port}...")
    
    if sys.platform == 'win32':
        # Windows: Start in new command window
        process = subprocess.Popen(
            ['cmd', '/c', 'start', 'cmd', '/k', 
             f'python peer.py --id {peer_id} --port {port}'],
            cwd=os.getcwd()
        )
    else:
        # Linux/Mac: Start in new terminal (requires xterm or gnome-terminal)
        try:
            process = subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c',
                 f'python peer.py --id {peer_id} --port {port}; exec bash']
            )
        except FileNotFoundError:
            try:
                process = subprocess.Popen(
                    ['xterm', '-e', f'python peer.py --id {peer_id} --port {port}']
                )
            except FileNotFoundError:
                print(f"⚠️  Please start {peer_id} manually: python peer.py --id {peer_id} --port {port}")
                return None
    
    time.sleep(1)
    print(f"✅ {peer_id.upper()} started\n")
    return process


def launch_all():
    """Launch all components"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Setup test files
    setup_test_files()
    
    print("="*70)
    print("STARTING ALL COMPONENTS")
    print("="*70 + "\n")
    
    # Start tracker
    tracker_process = start_tracker()
    
    # Start peers
    peer1_process = start_peer("peer1", 6001)
    time.sleep(1)
    
    peer2_process = start_peer("peer2", 6002)
    time.sleep(1)
    
    peer3_process = start_peer("peer3", 6003)
    
    print("="*70)
    print("🎉 ALL COMPONENTS STARTED!")
    print("="*70 + "\n")
    
    print("📊 System Status:")
    print(f"  • Tracker Server: http://127.0.0.1:5000")
    print(f"  • Peer 1: 127.0.0.1:6001")
    print(f"  • Peer 2: 127.0.0.1:6002")
    print(f"  • Peer 3: 127.0.0.1:6003\n")
    
    print("💡 What to do next:")
    print("  1. Switch to any peer window")
    print("  2. Press 2 to list network files")
    print("  3. Press 3 to download a file")
    print("  4. Try downloading files between peers!\n")
    
    print("📚 Useful URLs:")
    print("  • Tracker Status: http://127.0.0.1:5000/status")
    print("  • All Files: http://127.0.0.1:5000/get_all_files")
    print("  • All Peers: http://127.0.0.1:5000/get_all_peers\n")
    
    print("⚠️  Press Ctrl+C to show shutdown menu\n")
    
    # Keep script running and monitor
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("SHUTDOWN MENU")
        print("="*70)
        print("\n1. Keep everything running and exit launcher")
        print("2. Show system status")
        print("3. Exit launcher (peers will keep running)\n")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "2":
            show_status()
        
        print("\n✅ Launcher exiting. Components are still running in their windows.")
        print("💡 Close individual windows to stop components.\n")


def show_status():
    """Show current system status"""
    print("\n" + "="*70)
    print("SYSTEM STATUS")
    print("="*70 + "\n")
    
    # Check tracker
    if is_tracker_running():
        print("✅ Tracker: ONLINE")
        try:
            response = requests.get("http://127.0.0.1:5000/get_all_peers", timeout=2)
            if response.status_code == 200:
                data = response.json()
                peer_count = data.get('peer_count', 0)
                print(f"   Registered peers: {peer_count}")
                
            response = requests.get("http://127.0.0.1:5000/get_all_files", timeout=2)
            if response.status_code == 200:
                data = response.json()
                file_count = data.get('file_count', 0)
                print(f"   Available files: {file_count}")
        except:
            pass
    else:
        print("❌ Tracker: OFFLINE")
    
    print()


def launch_interactive():
    """Interactive launcher with menu"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    while True:
        print("="*70)
        print("LAUNCHER MENU")
        print("="*70)
        print("\n1. Launch everything (tracker + 3 peers)")
        print("2. Launch tracker only")
        print("3. Launch single peer")
        print("4. Setup test files")
        print("5. Show system status")
        print("6. Exit\n")
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == "1":
            launch_all()
            break
        
        elif choice == "2":
            print()
            start_tracker()
            print("✅ Tracker launched\n")
        
        elif choice == "3":
            peer_id = input("\nEnter peer ID (e.g., peer1): ").strip()
            port = input("Enter port (e.g., 6001): ").strip()
            try:
                port = int(port)
                print()
                start_peer(peer_id, port)
            except ValueError:
                print("❌ Invalid port number\n")
        
        elif choice == "4":
            print()
            setup_test_files()
        
        elif choice == "5":
            show_status()
        
        elif choice == "6":
            print("\n👋 Goodbye!\n")
            break
        
        else:
            print("\n❌ Invalid choice\n")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            # Auto mode: launch everything
            launch_all()
        elif sys.argv[1] == "--status":
            # Status check only
            show_status()
        else:
            print("Usage:")
            print("  python launcher.py          - Interactive menu")
            print("  python launcher.py --auto   - Launch everything automatically")
            print("  python launcher.py --status - Show system status")
    else:
        # Interactive mode
        launch_interactive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
