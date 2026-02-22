# 🚀 Launcher Guide - One-Click Startup

## The Easiest Way to Start

The **Launcher** is your one-stop solution to get the entire P2P system running with a single command!

---

## 🎯 Quick Start Options

### Option 1: Automatic Launch Everything (EASIEST!)

**Windows:**
```batch
LAUNCH_ALL.bat
```
Double-click `LAUNCH_ALL.bat` or run in terminal.

**Command Line:**
```bash
python launcher.py --auto
```

This will:
- ✅ Check and install dependencies
- ✅ Create test files if needed
- ✅ Start tracker server
- ✅ Start 3 peer nodes (peer1, peer2, peer3)
- ✅ Open everything in separate windows

**Then just switch to any peer window and start sharing files!**

---

### Option 2: Interactive Menu

**Windows:**
```batch
START_INTERACTIVE.bat
```

**Command Line:**
```bash
python launcher.py
```

This gives you a menu:
```
1. Launch everything (tracker + 3 peers)
2. Launch tracker only
3. Launch single peer
4. Setup test files
5. Show system status
6. Exit
```

Pick what you want to start!

---

### Option 3: Check System Status

```bash
python launcher.py --status
```

Shows if tracker is online, how many peers are registered, and how many files are available.

---

## 📺 What Happens When You Launch?

### Automatic Mode (`LAUNCH_ALL.bat` or `--auto`)

```
🔍 Checking dependencies...
✅ All dependencies installed

📁 Checking test files...
⚙️  Setting up test environment...
✅ Test files created

🚀 Starting Tracker Server...
⏳ Waiting for tracker to start..........✅

🚀 Starting PEER1 on port 6001...
✅ PEER1 started

🚀 Starting PEER2 on port 6002...
✅ PEER2 started

🚀 Starting PEER3 on port 6003...
✅ PEER3 started

🎉 ALL COMPONENTS STARTED!

📊 System Status:
  • Tracker Server: http://127.0.0.1:5000
  • Peer 1: 127.0.0.1:6001
  • Peer 2: 127.0.0.1:6002
  • Peer 3: 127.0.0.1:6003
```

You'll see **4 new windows** pop up:
1. Tracker Server
2. Peer 1
3. Peer 2
4. Peer 3

---

## 🎮 Using the System After Launch

### In Any Peer Window:

**See all files on the network:**
```
Choice: 2
```

**Download a file:**
```
Choice: 3
Filename: peer1_medium.txt
```

**Watch the progress bar and hash verification!**

---

## 🛠️ Advanced Usage

### Launch Custom Peers

Using interactive menu:
```
Choice: 3
Enter peer ID: alice
Enter port: 7000
```

### Launch Only Tracker

```
Choice: 2
```

### Check Status Anytime

While launcher is running, press `Ctrl+C` to see shutdown menu with status option.

Or run separately:
```bash
python launcher.py --status
```

---

## 🌐 URLs to Check

After launching, you can open these in your browser:

- **Tracker Home:** http://127.0.0.1:5000
- **System Status:** http://127.0.0.1:5000/status
- **All Files:** http://127.0.0.1:5000/get_all_files
- **All Peers:** http://127.0.0.1:5000/get_all_peers

---

## 🎬 Complete Workflow Example

### 1. First Time Setup (1 minute)

```bash
# Double-click LAUNCH_ALL.bat
# Or run:
python launcher.py --auto
```

Wait 10-15 seconds for everything to start.

### 2. Switch to Peer2 Window

You'll see the menu:
```
MENU:
  1. List my shared files
  2. List all network files
  3. Download a file
  4. Refresh registration with tracker
  5. Show storage info
  6. Exit
```

### 3. Browse Network Files

```
Enter choice: 2
```

You'll see files from all peers!

### 4. Download a File

```
Enter choice: 3
Enter filename: peer1_medium.txt
```

Watch the magic:
```
📡 Connecting to peer peer1 at 127.0.0.1:6001
📥 Downloading peer1_medium.txt (50.0 KB)...
peer1_medium.txt: 100%|████████████| 50.0KB/50.0KB [00:00<00:00, 2.5MB/s]
✅ Successfully downloaded: peer1_medium.txt
```

### 5. Verify Download

```
Enter choice: 5
```

See your storage stats including the downloaded file!

---

## ⚙️ What the Launcher Does

1. **Dependency Check**
   - Verifies Flask, tqdm, cryptography are installed
   - Auto-installs if missing

2. **Test File Setup**
   - Checks if sample files exist
   - Runs `test_setup.py` if needed

3. **Coordinated Startup**
   - Starts tracker first
   - Waits for tracker to be ready
   - Starts peers one by one with delays
   - Ensures proper registration

4. **Window Management**
   - Opens each component in separate window
   - Keeps them running independently
   - You can close launcher without stopping components

---

## 🔧 Troubleshooting

### "Could not start component"

**Windows:** Make sure Python is in your PATH
```bash
python --version
```

**Linux/Mac:** You might need xterm or gnome-terminal
```bash
sudo apt-get install gnome-terminal  # Ubuntu
```

### "Port already in use"

Something is already running on that port. Check:
```bash
# Windows
netstat -an | findstr :5000
netstat -an | findstr :6001

# Linux/Mac
lsof -i :5000
lsof -i :6001
```

Kill the process or use different ports in interactive mode.

### "Tracker won't start"

Check if port 5000 is available. Try manually:
```bash
python tracker.py
```

Look for error messages.

### "Peers not registering"

1. Make sure tracker is running (check http://127.0.0.1:5000/status)
2. Try refreshing in peer menu (option 4)
3. Check firewall settings

---

## 💡 Pro Tips

### Tip 1: Keep Launcher Running
The launcher can monitor the system. Press `Ctrl+C` to access the shutdown menu without killing components.

### Tip 2: Start What You Need
Don't need 3 peers? Use interactive mode and start just tracker + 2 peers.

### Tip 3: Check Status First
Before launching, run:
```bash
python launcher.py --status
```
to see if anything is already running.

### Tip 4: Add Your Own Files
While system is running, just drop files into `shared_peer1/`, `shared_peer2/`, etc., then refresh registration (peer menu option 4).

### Tip 5: Browser Access
Open http://127.0.0.1:5000/get_all_files in browser for a JSON view of all available files.

---

## 📊 Comparison: Manual vs Launcher

| Task | Manual Method | With Launcher |
|------|---------------|---------------|
| Install deps | `pip install -r requirements.txt` | Automatic |
| Create test files | `python test_setup.py` | Automatic |
| Start tracker | `python tracker.py` | Automatic |
| Start peer1 | `python peer.py --id peer1 --port 6001` | Automatic |
| Start peer2 | `python peer.py --id peer2 --port 6002` | Automatic |
| Start peer3 | `python peer.py --id peer3 --port 6003` | Automatic |
| **Total commands** | **6 commands, 4 terminals** | **1 command!** |

---

## 🎉 You're Ready!

The launcher makes running a complete P2P network as easy as:

```bash
LAUNCH_ALL.bat
```

That's it! Everything else is automatic.

**Start sharing files now! 🚀**
