"""
Automated Demo Script
Demonstrates P2P file sharing capabilities
"""

import time
import subprocess
import sys
import os
import requests
from pathlib import Path


def print_step(step_num, description):
    """Print a demo step"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*70}")


def check_tracker():
    """Check if tracker is running"""
    try:
        response = requests.get("http://127.0.0.1:5000/status", timeout=2)
        if response.status_code == 200:
            print("✅ Tracker is running")
            return True
        return False
    except:
        return False


def check_peer(port):
    """Check if a peer is running on given port"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


def get_all_files():
    """Get all files from tracker"""
    try:
        response = requests.get("http://127.0.0.1:5000/get_all_files", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('files', [])
        return []
    except:
        return []


def get_all_peers():
    """Get all peers from tracker"""
    try:
        response = requests.get("http://127.0.0.1:5000/get_all_peers", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('peers', [])
        return []
    except:
        return []


def main():
    """Run the demo"""
    print("\n" + "="*70)
    print(" "*15 + "P2P FILE SHARING SYSTEM DEMO")
    print("="*70)
    
    print("\nThis demo will guide you through the P2P file sharing system.")
    print("Make sure you have already:")
    print("  1. Installed dependencies (pip install -r requirements.txt)")
    print("  2. Run test_setup.py to create sample files")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Check Tracker
    print_step(1, "Checking Tracker Server")
    
    if not check_tracker():
        print("❌ Tracker is not running!")
        print("\n🚀 Auto-starting tracker server...")
        
        # Auto-start tracker
        if sys.platform == 'win32':
            subprocess.Popen(
                ['cmd', '/c', 'start', 'cmd', '/k', 'python tracker.py'],
                cwd=os.getcwd()
            )
        else:
            subprocess.Popen(
                [sys.executable, 'tracker.py'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Wait for it to start
        print("⏳ Waiting for tracker", end="", flush=True)
        for _ in range(15):
            time.sleep(1)
            print(".", end="", flush=True)
            if check_tracker():
                print(" ✅")
                print("\n✅ Tracker started successfully!")
                break
        else:
            print("\n⚠️  Tracker taking longer than expected")
            print("Please check the tracker window for errors.")
            input("\nPress Enter to continue anyway...")
    
    # Step 2: Check Files
    print_step(2, "Checking Sample Files")
    
    sample_folders = ['shared_peer1', 'shared_peer2', 'shared_peer3']
    files_exist = all(Path(folder).exists() for folder in sample_folders)
    
    if not files_exist:
        print("⚠️  Sample files not found!")
        print("\nRun test setup:")
        print("  python test_setup.py")
        input("\nPress Enter after creating test files...")
    
    # Count files
    total_files = 0
    for folder in sample_folders:
        folder_path = Path(folder)
        if folder_path.exists():
            count = len(list(folder_path.glob('*.*')))
            print(f"  📁 {folder}: {count} files")
            total_files += count
    
    print(f"\n✅ Total sample files: {total_files}")
    
    # Step 3: Check Peers
    print_step(3, "Checking Peer Status")
    
    peers_to_check = [
        ("Peer 1", 6001, "start_peer1.bat"),
        ("Peer 2", 6002, "start_peer2.bat"),
        ("Peer 3", 6003, "start_peer3.bat")
    ]
    
    running_peers = []
    
    for peer_name, port, batch_file in peers_to_check:
        if check_peer(port):
            print(f"  ✅ {peer_name} is running on port {port}")
            running_peers.append(peer_name)
        else:
            print(f"  ❌ {peer_name} is NOT running on port {port}")
            print(f"     Start with: python peer.py --id {peer_name.lower().replace(' ', '')} --port {port}")
            print(f"     Or double-click: {batch_file}")
    
    if len(running_peers) < 2:
        print("\n⚠️  You need at least 2 peers running for the demo.")
        print("Please start the peers in separate terminals.")
        input("\nPress Enter after starting peers...")
    
    # Step 4: Query Tracker
    print_step(4, "Querying Tracker for Network Status")
    
    time.sleep(2)  # Give peers time to register
    
    peers = get_all_peers()
    print(f"\n📊 Registered Peers: {len(peers)}")
    for peer in peers:
        print(f"  • {peer['peer_id']} @ {peer['host']}:{peer['port']}")
        print(f"    Files: {len(peer['files'])}")
    
    # Step 5: List Available Files
    print_step(5, "Listing All Available Files on Network")
    
    files = get_all_files()
    print(f"\n📄 Available Files: {len(files)}")
    
    for i, file_info in enumerate(files[:10], 1):  # Show first 10
        print(f"\n  {i}. {file_info['filename']}")
        print(f"     Size: {file_info['size']} bytes")
        print(f"     Available from: {len(file_info['peers'])} peer(s)")
        for peer in file_info['peers']:
            print(f"       - {peer['peer_id']} ({peer['host']}:{peer['port']})")
    
    if len(files) > 10:
        print(f"\n  ... and {len(files) - 10} more files")
    
    # Step 6: Demo Instructions
    print_step(6, "Manual Testing Instructions")
    
    print("""
Now you can test the system manually:

1. Go to any peer terminal
2. Select option 2: "List all network files"
3. Select option 3: "Download a file"
4. Enter a filename from the list
5. Watch the progress bar as the file downloads!
6. Select option 1 to verify the downloaded file

Example files to try:
  • peer1_small.txt (quick test)
  • peer2_medium.txt (shows progress)
  • peer3_large.txt (stress test)
  • common_file.txt (available from all peers)

Advanced Tests:
  • Download same file from multiple peers simultaneously
  • Add your own files to shared folders
  • Select option 4 to refresh registration
  • Monitor hash verification in logs
    """)
    
    # Step 7: System Info
    print_step(7, "System Information")
    
    print("""
📋 Configuration:
  • Tracker: http://127.0.0.1:5000
  • Chunk Size: 4096 bytes (4 KB)
  • Hash Verification: Enabled (SHA256)
  • Max Concurrent Connections: 10
  • Connection Timeout: 10 seconds

📁 Folder Structure:
  • shared_peer1/ → Files shared by peer1
  • downloads_peer1/ → Files downloaded by peer1
  • shared_peer2/ → Files shared by peer2
  • downloads_peer2/ → Files downloaded by peer2
  • shared_peer3/ → Files shared by peer3
  • downloads_peer3/ → Files downloaded by peer3

🔍 API Endpoints:
  • POST /register_peer
  • GET /get_file_peers?filename=<name>
  • GET /get_all_files
  • GET /get_all_peers
  • GET /status

🌐 Access tracker in browser:
  http://127.0.0.1:5000
    """)
    
    # Final message
    print("\n" + "="*70)
    print(" "*20 + "DEMO COMPLETE!")
    print("="*70)
    print("\n✨ The P2P File Sharing System is ready to use!")
    print("💡 Check README.md for detailed documentation")
    print("🚀 Happy file sharing!\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
