import threading
import time
import os
import shutil
import sys
from pathlib import Path
import config
from tracker import TrackerServer, app
from peer import Peer

# Redirect stdout/stderr to file
log_file = open("verify_log.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

# Setup directories
def setup_dirs():
    if os.path.exists("shared_p1"): shutil.rmtree("shared_p1")
    if os.path.exists("downloads_p1"): shutil.rmtree("downloads_p1")
    if os.path.exists("shared_p2"): shutil.rmtree("shared_p2")
    if os.path.exists("downloads_p2"): shutil.rmtree("downloads_p2")
    
    os.makedirs("shared_p1")
    os.makedirs("downloads_p1")
    os.makedirs("shared_p2")
    os.makedirs("downloads_p2")
    
    # Create a test file for Peer 1
    with open("shared_p1/test_push.txt", "w") as f:
        f.write("This is a pushed file content.")

# Run Tracker
def run_tracker():
    try:
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Tracker error: {e}")

# Test
def run_test():
    try:
        setup_dirs()
        
        print("Starting Tracker...")
        # Start Tracker in a separate thread
        tracker_thread = threading.Thread(target=run_tracker, daemon=True)
        tracker_thread.start()
        time.sleep(2) # Wait for tracker to start
        
        print("Starting Peer 1...")
        # Start Peer 1
        peer1 = Peer("p1", "127.0.0.1", 6001, "shared_p1", "downloads_p1")
        peer1.start_server()
        
        print("Starting Peer 2...")
        # Start Peer 2
        peer2 = Peer("p2", "127.0.0.1", 6002, "shared_p2", "downloads_p2")
        peer2.start_server()
        
        time.sleep(1)
        
        print("\n--- Testing Push File ---")
        # Peer 1 pushes to Peer 2
        success = peer1.push_file_to_peer("127.0.0.1", 6002, "test_push.txt")
        
        if success:
            print("✅ Push command successful")
        else:
            print("❌ Push command failed")
        
        time.sleep(2)
        
        # Verify file exists in Peer 2 downloads
        downloaded_file = Path("downloads_p2/test_push.txt")
        if downloaded_file.exists():
            print(f"✅ File found in Peer 2 downloads. Size: {downloaded_file.stat().st_size}")
            with open(downloaded_file, "r") as f:
                content = f.read()
                if content == "This is a pushed file content.":
                    print("✅ Content verified")
                else:
                    print(f"❌ Content mismatch: '{content}'")
        else:
            print("❌ File not found in Peer 2 downloads")

        # Cleanup
        peer1.stop_server()
        peer2.stop_server()
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_file.close()

if __name__ == "__main__":
    run_test()
