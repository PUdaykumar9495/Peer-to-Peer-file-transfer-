# 🚀 Quick Start Guide

Get your P2P File Sharing System running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Test Files (30 seconds)

**Option A - Run script:**
```bash
python test_setup.py
```

**Option B - Use batch file (Windows):**
```bash
setup_test_files.bat
```

This creates sample files for testing in `shared_peer1/`, `shared_peer2/`, and `shared_peer3/` folders.

## Step 3: Start Components (1 minute)

### Terminal 1 - Start Tracker
```bash
python tracker.py
```
**Or double-click:** `start_tracker.bat`

Wait for: `🚀 Tracker server running at http://127.0.0.1:5000`

### Terminal 2 - Start Peer 1
```bash
python peer.py --id peer1 --port 6001
```
**Or double-click:** `start_peer1.bat`

### Terminal 3 - Start Peer 2
```bash
python peer.py --id peer2 --port 6002
```
**Or double-click:** `start_peer2.bat`

### Terminal 4 - Start Peer 3 (Optional)
```bash
python peer.py --id peer3 --port 6003
```
**Or double-click:** `start_peer3.bat`

## Step 4: Test File Sharing (2 minutes)

### On Peer 1:
1. Enter `1` → See files in shared_peer1/
2. You should see files like `peer1_small.txt`, `peer1_medium.txt`, etc.

### On Peer 2:
1. Enter `2` → See all files on the network
2. You should see files from peer1, peer2, and peer3
3. Enter `3` → Download a file
4. Type: `peer1_medium.txt`
5. Watch the progress bar!
6. Enter `1` → Verify downloaded file

### Test Hash Verification:
1. Download a large file
2. Check the logs - hash should be verified automatically
3. Files in `downloads_peer2/` are verified safe!

## 🎯 Common Operations

### List My Files
```
Choice: 1
```

### Browse Network
```
Choice: 2
```

### Download a File
```
Choice: 3
Filename: peer1_small.txt
```

### Check Storage
```
Choice: 5
```

### Exit
```
Choice: 6
```

## 🧪 Testing Scenarios

### Scenario 1: Basic Download
1. Start tracker + 2 peers
2. Peer2 downloads file from Peer1
3. Verify file integrity

### Scenario 2: Multiple Downloads
1. Start tracker + 3 peers
2. Peer3 downloads from Peer1 and Peer2
3. Check concurrent handling

### Scenario 3: Same File, Multiple Peers
1. All peers have `common_file.txt`
2. Download from any peer
3. Tracker shows multiple sources

## ❓ Troubleshooting

### "Tracker not available"
- Is tracker.py running?
- Check `http://127.0.0.1:5000/status` in browser

### "Port already in use"
- Use different port: `--port 6010`

### "No peers have the file"
- Refresh peer registration (option 4)
- Check file is in shared folder
- Verify tracker connection

## 🎊 Success Checklist

- ✅ Tracker shows "online" status
- ✅ Peers register successfully
- ✅ Network files list shows files from all peers
- ✅ Download completes with progress bar
- ✅ Hash verification passes
- ✅ File appears in downloads folder

## 📚 Next Steps

- Read full [README.md](README.md) for advanced features
- Customize [config.py](config.py) for your needs
- Try downloading large files (create with test_setup.py)
- Test with real files in shared folders

---

**You're ready to go! Happy file sharing! 🎉**
