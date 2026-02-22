# 🌐 P2P File Sharing System

A complete Peer-to-Peer (P2P) File Sharing System built with Python using TCP sockets. This system allows multiple peers to share and download files directly from each other with a lightweight tracker server for peer discovery.

## ✨ Features

- **Peer-to-Peer Architecture**: Each peer acts as both client and server
- **TCP Socket Communication**: Reliable file transfers using TCP
- **Tracker Server**: Centralized discovery service for peers and files
- **Concurrent Connections**: Handle multiple clients simultaneously using threads
- **Chunked File Transfer**: Efficient file transfer with progress tracking
- **Integrity Verification**: SHA256 hash verification for downloaded files
- **Interactive CLI**: User-friendly command-line interface
- **Automatic Peer Registration**: Seamless integration with tracker server
- **Network File Discovery**: Browse all available files across the network

## 🏗️ Architecture

```
┌─────────────────┐
│  Tracker Server │
│   (Flask API)   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼──┐  ┌──▼───┐  ┌─▼────┐  ┌▼─────┐
│Peer 1│  │Peer 2│  │Peer 3│  │Peer N│
│ TCP  │◄─┤ TCP  │◄─┤ TCP  │◄─┤ TCP  │
└──────┘  └──────┘  └──────┘  └──────┘
```

## 📁 Project Structure

```
P2P_FILE_SHARING/
├── config.py           # Configuration settings
├── utils.py            # Helper functions (hash, JSON, logging)
├── file_manager.py     # File operations and integrity checks
├── tracker.py          # Tracker server (Flask)
├── peer.py             # Peer application (main)
├── requirements.txt    # Python dependencies
├── README.md          # This file
│
├── shared_peer1/      # Shared files for peer1 (auto-created)
├── downloads_peer1/   # Downloads for peer1 (auto-created)
├── shared_peer2/      # Shared files for peer2 (auto-created)
├── downloads_peer2/   # Downloads for peer2 (auto-created)
└── tracker_data.json  # Tracker database (auto-created)
```

## 🚀 Quick Start

### 🎯 EASIEST WAY - One-Click Launch (Recommended!)

**Just double-click:**
```
LAUNCH_ALL.bat
```

**Or run:**
```bash
python launcher.py --auto
```

This automatically:
- ✅ Installs dependencies
- ✅ Creates test files
- ✅ Starts tracker + 3 peers
- ✅ Opens everything in separate windows

**Done! Switch to any peer window and start sharing!**

📚 **Detailed launcher guide:** See [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md)

---

### 📋 Manual Setup (If you prefer control)

### 1. Installation

```bash
# Clone or navigate to the project directory
cd P2P_FILE_SHARING

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Tracker Server

```bash
python tracker.py
```

The tracker server will start on `http://127.0.0.1:5000`

### 3. Start Peer Nodes

**Terminal 1 - Peer 1:**
```bash
python peer.py --id peer1 --port 6001
```

**Terminal 2 - Peer 2:**
```bash
python peer.py --id peer2 --port 6002
```

**Terminal 3 - Peer 3:**
```bash
python peer.py --id peer3 --port 6003
```

### 4. Share Files

Add files to the shared folders:
- `shared_peer1/` for peer1
- `shared_peer2/` for peer2
- `shared_peer3/` for peer3

### 5. Use the Interactive Menu

Each peer provides an interactive menu:

```
MENU:
  1. List my shared files
  2. List all network files
  3. Download a file
  4. Refresh registration with tracker
  5. Show storage info
  6. Exit
```

## 📖 Detailed Usage

### Command Line Arguments

```bash
python peer.py --help
```

**Arguments:**
- `--id`: Peer ID (required, e.g., "peer1")
- `--host`: Host address (default: 127.0.0.1)
- `--port`: Port number (default: 6000)
- `--shared`: Custom shared folder path
- `--downloads`: Custom downloads folder path
- `--no-tracker`: Run without tracker (standalone mode)

### Examples

**Custom port and folders:**
```bash
python peer.py --id alice --port 7000 --shared ./my_files --downloads ./my_downloads
```

**Standalone mode (without tracker):**
```bash
python peer.py --id bob --port 7001 --no-tracker
```

**Bind to specific IP:**
```bash
python peer.py --id charlie --host 192.168.1.100 --port 7002
```

## 🔧 Configuration

Edit `config.py` to customize:

### Network Settings
```python
TRACKER_HOST = "127.0.0.1"
TRACKER_PORT = 5000
DEFAULT_PEER_PORT = 6000
```

### Transfer Settings
```python
CHUNK_SIZE = 4096  # 4KB chunks
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 10
```

### File Paths
```python
SHARED_FOLDER = "shared"
DOWNLOADS_FOLDER = "downloads"
```

### Features
```python
VERIFY_HASH = True  # Enable SHA256 verification
ENABLE_ENCRYPTION = False  # Placeholder for future
ENABLE_COMPRESSION = False  # Placeholder for future
```

## 🔌 API Endpoints (Tracker)

### `POST /register_peer`
Register a peer with the tracker

**Request:**
```json
{
  "peer_id": "peer1",
  "host": "127.0.0.1",
  "port": 6001,
  "files": [
    {
      "filename": "document.pdf",
      "size": 1024000,
      "hash": "abc123..."
    }
  ]
}
```

### `GET /get_file_peers?filename=<name>`
Find peers that have a specific file

**Response:**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "peer_count": 2,
  "peers": [...]
}
```

### `GET /get_all_files`
Get list of all available files

### `GET /get_all_peers`
Get list of all registered peers

### `GET /status`
Check tracker server status

## 🔐 Security Features

1. **Hash Verification**: SHA256 checksums verify file integrity
2. **Socket Timeouts**: Prevent hanging connections
3. **Connection Limits**: Configurable max concurrent connections
4. **Input Validation**: Sanitize all network inputs
5. **Error Handling**: Robust exception handling throughout

## 🧪 Testing Guide

### Test Scenario 1: Basic File Sharing

1. Start tracker server
2. Start peer1 and peer2
3. Add `test.txt` to `shared_peer1/`
4. On peer1: Select option 1 (list shared files)
5. On peer2: Select option 2 (list network files)
6. On peer2: Select option 3 and download `test.txt`
7. Verify file in `downloads_peer2/`

### Test Scenario 2: Multiple Peers

1. Start 3+ peers
2. Add different files to each peer's shared folder
3. List network files from any peer
4. Download files from different peers
5. Verify all downloads complete successfully

### Test Scenario 3: Large File Transfer

1. Create a large file (100MB+) in shared folder
2. Monitor transfer with progress bar
3. Verify hash after download

### Test Scenario 4: Concurrent Downloads

1. Start 4+ peers
2. Have 3 peers download from 1 peer simultaneously
3. Verify all transfers complete successfully

## 📊 Logging

Logs are automatically generated with:
- Timestamp
- Log level (INFO, WARNING, ERROR)
- Module name
- Message

**Example:**
```
2025-10-26 19:27:04 - INFO - [Peer] - Peer peer1 initialized at 127.0.0.1:6001
2025-10-26 19:27:05 - INFO - [Peer] - Registered with tracker
2025-10-26 19:27:10 - INFO - [FileManager] - Sending file: document.pdf (1.5 MB)
```

## 🐛 Troubleshooting

### Tracker Connection Failed
- Ensure tracker server is running
- Check `TRACKER_HOST` and `TRACKER_PORT` in `config.py`
- Try running peer with `--no-tracker` flag

### Port Already in Use
- Use different port: `--port 6010`
- Check for existing processes: `netstat -an | findstr :6000`

### File Not Found
- Verify file exists in shared folder
- Refresh registration: Menu option 4
- Check file permissions

### Hash Verification Failed
- File may be corrupted during transfer
- Check network stability
- Disable hash verification in `config.py` if needed

### Connection Timeout
- Increase timeout in `config.py`
- Check firewall settings
- Verify peer is running and accessible

## 🎯 Advanced Features (Future Enhancements)

- [ ] AES encryption for secure transfers
- [ ] File compression (gzip/zlib)
- [ ] Resume interrupted downloads
- [ ] Multi-source parallel downloads
- [ ] NAT traversal (hole punching)
- [ ] DHT (Distributed Hash Table)
- [ ] Bandwidth throttling
- [ ] Web-based dashboard
- [ ] Mobile peer support

## 📝 Technical Details

### Protocol Messages

**File Request:**
```json
{
  "type": "REQUEST_FILE",
  "filename": "document.pdf",
  "peer_id": "peer2"
}
```

**File Response:**
```json
{
  "status": "FILE_FOUND",
  "filename": "document.pdf",
  "size": 1024000,
  "hash": "abc123..."
}
```

### File Transfer Flow

1. Client sends REQUEST_FILE message
2. Server sends FILE_FOUND with metadata
3. Server streams file in 4KB chunks
4. Client receives and writes chunks
5. Client verifies SHA256 hash
6. Transfer complete

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This project is for educational purposes. Feel free to use and modify as needed.

## 👥 Authors

Built as a demonstration of P2P networking concepts using Python.

## 🙏 Acknowledgments

- Python socket library
- Flask web framework
- tqdm for progress bars
- Threading for concurrency

---

**Happy File Sharing! 🚀**

For questions or issues, please check the troubleshooting section or create an issue in the repository.
