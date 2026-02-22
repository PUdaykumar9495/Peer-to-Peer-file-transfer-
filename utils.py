"""
Utility functions for the P2P File Sharing System
"""

import hashlib
import json
import socket
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name
    
    Args:
        name: Name for the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def compute_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Compute hash of a file for integrity verification
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(config.CHUNK_SIZE)
                if not chunk:
                    break
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        raise Exception(f"Error computing hash for {file_path}: {e}")


def compute_data_hash(data: bytes, algorithm: str = 'sha256') -> str:
    """
    Compute hash of raw data
    
    Args:
        data: Binary data to hash
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.new(algorithm)
    hash_func.update(data)
    return hash_func.hexdigest()


def send_json(sock: socket.socket, data: Dict[str, Any]) -> bool:
    """
    Send JSON data over a socket
    
    Args:
        sock: Socket connection
        data: Dictionary to send as JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        json_data = json.dumps(data)
        json_bytes = json_data.encode('utf-8')
        
        # Send length first (4 bytes)
        length = len(json_bytes)
        sock.sendall(length.to_bytes(4, byteorder='big'))
        
        # Send actual data
        sock.sendall(json_bytes)
        return True
    except Exception as e:
        get_logger("utils").error(f"Error sending JSON: {e}")
        return False


def receive_json(sock: socket.socket, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Receive JSON data from a socket
    
    Args:
        sock: Socket connection
        timeout: Optional timeout in seconds
        
    Returns:
        Dictionary parsed from JSON, or None if error
    """
    try:
        if timeout:
            sock.settimeout(timeout)
        
        # Receive length first (4 bytes)
        length_bytes = receive_all(sock, 4)
        if not length_bytes:
            return None
        
        length = int.from_bytes(length_bytes, byteorder='big')
        
        # Receive actual data
        json_bytes = receive_all(sock, length)
        if not json_bytes:
            return None
        
        json_data = json_bytes.decode('utf-8')
        return json.loads(json_data)
    except socket.timeout:
        get_logger("utils").warning("Socket timeout while receiving JSON")
        return None
    except Exception as e:
        get_logger("utils").error(f"Error receiving JSON: {e}")
        return None


def receive_all(sock: socket.socket, size: int) -> Optional[bytes]:
    """
    Receive exactly 'size' bytes from a socket
    
    Args:
        sock: Socket connection
        size: Number of bytes to receive
        
    Returns:
        Bytes received, or None if connection closed
    """
    data = b''
    while len(data) < size:
        try:
            chunk = sock.recv(min(size - len(data), config.BUFFER_SIZE))
            if not chunk:
                return None
            data += chunk
        except Exception as e:
            get_logger("utils").error(f"Error receiving data: {e}")
            return None
    return data


def format_bytes(size: int) -> str:
    """
    Format bytes into human-readable format
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def print_banner(text: str):
    """
    Print a formatted banner
    
    Args:
        text: Text to display in banner
    """
    width = max(60, len(text) + 4)
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def print_section(title: str):
    """
    Print a section header
    
    Args:
        title: Section title
    """
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def print_peer_info(peer_id: str, host: str, port: int):
    """
    Print peer information in a formatted way
    
    Args:
        peer_id: Peer identifier
        host: Peer host address
        port: Peer port number
    """
    print(f"  🔹 Peer ID: {peer_id}")
    print(f"  🔹 Address: {host}:{port}")


def print_file_info(filename: str, size: int, file_hash: Optional[str] = None):
    """
    Print file information in a formatted way
    
    Args:
        filename: Name of the file
        size: Size in bytes
        file_hash: Optional file hash
    """
    print(f"  📄 {filename}")
    print(f"     Size: {format_bytes(size)}")
    if file_hash:
        print(f"     Hash: {file_hash[:16]}...")


def get_timestamp() -> str:
    """
    Get current timestamp as formatted string
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_port(port: int) -> bool:
    """
    Validate if port number is valid
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 1024 <= port <= 65535


def get_local_ip() -> str:
    """
    Get local IP address of the machine
    
    Returns:
        Local IP address string
    """
    try:
        # Connect to an external address (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"
