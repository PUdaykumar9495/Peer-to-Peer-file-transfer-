# 🎯 START HERE - Your 30-Second Guide

## Want to run the P2P system RIGHT NOW?

### Just do this:

#### Windows Users:
```
Double-click: LAUNCH_ALL.bat
```

#### Everyone:
```bash
python launcher.py --auto
```

---

## That's it! ✨

In 30 seconds, you'll have:
- ✅ A running tracker server
- ✅ Three peer nodes ready to share
- ✅ Sample files to test with
- ✅ Everything in separate windows

---

## What happens next?

You'll see **4 new windows** open:

### Window 1: Tracker Server
```
🚀 Tracker server running at http://127.0.0.1:5000
📊 Currently tracking 0 peers
```
**Just leave this running. Don't touch it.**

### Windows 2, 3, 4: Peer Nodes
Each shows a menu:
```
MENU:
  1. List my shared files
  2. List all network files
  3. Download a file
  4. Refresh registration with tracker
  5. Show storage info
  6. Exit

Enter your choice (1-6):
```

---

## Try it out! (2 minutes)

### In Peer 2 Window:

**Step 1:** Press `2` and Enter
```
You'll see all files from all peers!
```

**Step 2:** Press `3` and Enter
```
Enter filename: peer1_medium.txt
```

**Step 3:** Watch the magic! 🎩✨
```
📡 Connecting to peer peer1...
📥 Downloading peer1_medium.txt...
[████████████████████] 100%
✅ Successfully downloaded!
```

---

## 🎉 Congratulations!

You just:
- ✅ Set up a complete P2P network
- ✅ Registered peers with tracker
- ✅ Downloaded a file peer-to-peer
- ✅ Verified file integrity with SHA256

**You're now running a real P2P file sharing system!**

---

## Want to learn more?

### Quick References:
- **📖 LAUNCHER_GUIDE.md** - Everything about the launcher
- **📖 QUICKSTART.md** - 5-minute detailed guide
- **📖 README.md** - Complete documentation
- **📖 GETTING_STARTED.txt** - Quick reference card

### Advanced:
- **📖 PROJECT_SUMMARY.md** - Technical deep dive
- **🔧 config.py** - Customize settings

---

## Common Questions

### Q: What if something goes wrong?
**A:** Close all windows and run `LAUNCH_ALL.bat` again. Fresh start!

### Q: Can I add my own files?
**A:** Yes! Just put files in `shared_peer1/`, `shared_peer2/`, or `shared_peer3/` folders, then press 4 in any peer to refresh.

### Q: How do I stop everything?
**A:** Just close each window, or press 6 in each peer window.

### Q: Can I use different ports or settings?
**A:** Yes! Run `python launcher.py` (without --auto) for interactive menu with custom options.

### Q: Where are my downloaded files?
**A:** Check `downloads_peer1/`, `downloads_peer2/`, or `downloads_peer3/` depending on which peer you used.

---

## Troubleshooting

### "Python is not recognized"
Install Python from python.org and add it to PATH.

### "Port already in use"
Something is already using that port. Restart your computer or use:
```bash
python launcher.py
# Then choose option 3 to start peers on custom ports
```

### "Tracker not starting"
Open a terminal and run:
```bash
python tracker.py
```
Look for error messages.

---

## System URLs

Once running, you can visit these in your browser:

- **http://127.0.0.1:5000** - Tracker home
- **http://127.0.0.1:5000/status** - System status
- **http://127.0.0.1:5000/get_all_files** - All available files (JSON)
- **http://127.0.0.1:5000/get_all_peers** - All registered peers (JSON)

---

## You're All Set! 🚀

The system is designed to "just work" - no complex configuration needed.

**Enjoy your P2P file sharing experience!**

---

### Need Help?
Check the detailed guides mentioned above, or look at the code comments - everything is well documented!

**Happy file sharing! 🎊**
