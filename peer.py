"""
Peer Node for P2P File Sharing System
Acts as both client and server for file sharing
"""

import socket
import threading
import requests
import time
import sys
from pathlib import Path
from typing import Optional, List, Dict
import config
import utils
from file_manager import FileManager


logger = utils.get_logger("Peer")


class Peer:
    """
    P2P Peer that can both serve and request files
    """
    
    def __init__(self, peer_id: str, host: str, port: int, 
                 shared_folder: str = config.SHARED_FOLDER,
                 downloads_folder: str = config.DOWNLOADS_FOLDER,
                 use_tracker: bool = True):
        """
        Initialize peer
        
        Args:
            peer_id: Unique identifier for this peer
            host: IP address to bind to
            port: Port to listen on
            shared_folder: Path to shared files folder
            downloads_folder: Path to downloads folder
            use_tracker: Whether to use tracker server
        """
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.use_tracker = use_tracker
        
        # File manager
        self.file_manager = FileManager(shared_folder, downloads_folder)
        
        # Server socket
        self.server_socket = None
        self.running = False
        
        # Tracker URL
        self.tracker_url = f"http://{config.TRACKER_HOST}:{config.TRACKER_PORT}"
        
        logger.info(f"Peer {peer_id} initialized at {host}:{port}")
    
    def start_server(self):
        """
        Start the peer server to listen for incoming connections
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(config.MAX_CONNECTIONS)
            
            self.running = True
            logger.info(f"Peer server started on {self.host}:{self.port}")
            
            # Register with tracker if enabled
            if self.use_tracker:
                self.register_with_tracker()
            
            # Start accepting connections
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """
        Stop the peer server
        """
        self.running = False
        
        # Unregister from tracker
        if self.use_tracker:
            self.unregister_from_tracker()
        
        if self.server_socket:
            try:
                self.server_socket.close()
                logger.info("Peer server stopped")
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
    
    def _accept_connections(self):
        """
        Accept incoming connections (runs in separate thread)
        """
        logger.info("Ready to accept connections")
        
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"Connection received from {client_address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """
        Handle a client connection
        
        Args:
            client_socket: Connected client socket
            client_address: Client address tuple (host, port)
        """
        try:
            # Receive request
            request = utils.receive_json(client_socket, timeout=config.CONNECTION_TIMEOUT)
            
            if not request:
                logger.warning(f"Invalid request from {client_address}")
                client_socket.close()
                return
            
            request_type = request.get('type')
            logger.info(f"Request from {client_address}: {request_type}")
            
            if request_type == config.MSG_REQUEST_FILE:
                filename = request.get('filename')
                if filename:
                    self._send_file_to_peer(client_socket, filename)
                else:
                    utils.send_json(client_socket, {
                        'status': config.MSG_ERROR,
                        'message': 'Filename not specified'
                    })
            
            elif request_type == config.MSG_LIST_FILES:
                self._send_file_list(client_socket)
            
            elif request_type == config.MSG_SEND_FILE:
                self._handle_incoming_file(client_socket, request)
            
            else:
                utils.send_json(client_socket, {
                    'status': config.MSG_ERROR,
                    'message': f'Unknown request type: {request_type}'
                })
            
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _send_file_to_peer(self, client_socket: socket.socket, filename: str):
        """
        Send a file to requesting peer
        
        Args:
            client_socket: Socket connection to peer
            filename: Name of file to send
        """
        logger.info(f"Sending file: {filename}")
        success = self.file_manager.send_file(client_socket, filename)
        
        if success:
            logger.info(f"File {filename} sent successfully")
        else:
            logger.error(f"Failed to send file {filename}")
    
    def _send_file_list(self, client_socket: socket.socket):
        """
        Send list of shared files to requesting peer
        
        Args:
            client_socket: Socket connection to peer
        """
        files = self.file_manager.list_shared_files()
        utils.send_json(client_socket, {
            'status': 'success',
            'files': files
        })
        logger.info(f"Sent file list: {len(files)} files")
    
    def register_with_tracker(self) -> bool:
        """
        Register this peer with the tracker server
        
        Returns:
            True if successful, False otherwise
        """
        try:
            files = self.file_manager.list_shared_files()
            
            response = requests.post(
                f"{self.tracker_url}/register_peer",
                json={
                    'peer_id': self.peer_id,
                    'host': self.host,
                    'port': self.port,
                    'files': files
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Registered with tracker: {result.get('message')}")
                print(f"✅ Registered with tracker ({result.get('peer_count')} total peers)")
                return True
            else:
                logger.error(f"Failed to register with tracker: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to tracker: {e}")
            print(f"⚠️  Tracker not available - running in standalone mode")
            return False
    
    def unregister_from_tracker(self) -> bool:
        """
        Unregister this peer from the tracker server
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.tracker_url}/unregister_peer",
                json={'peer_id': self.peer_id},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("Unregistered from tracker")
                return True
            else:
                logger.error(f"Failed to unregister from tracker: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to tracker: {e}")
            return False
    
    def find_peers_with_file(self, filename: str) -> List[Dict]:
        """
        Find peers that have a specific file (using tracker)
        
        Args:
            filename: Name of the file to search for
            
        Returns:
            List of peer information dictionaries
        """
        if not self.use_tracker:
            logger.warning("Tracker not enabled")
            return []
        
        try:
            response = requests.get(
                f"{self.tracker_url}/get_file_peers",
                params={'filename': filename},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                peers = result.get('peers', [])
                logger.info(f"Found {len(peers)} peers with file: {filename}")
                return peers
            else:
                logger.error(f"Error finding peers: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not connect to tracker: {e}")
            return []
    
    def get_all_available_files(self) -> List[Dict]:
        """
        Get list of all files available on the network (from tracker)
        
        Returns:
            List of file dictionaries
        """
        if not self.use_tracker:
            logger.warning("Tracker not enabled")
            return []
        
        try:
            response = requests.get(
                f"{self.tracker_url}/get_all_files",
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                files = result.get('files', [])
                logger.info(f"Retrieved {len(files)} available files from tracker")
                return files
            else:
                logger.error(f"Error getting files: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Could not connect to tracker: {e}")
            return []
    
    def download_file(self, filename: str, peer_host: Optional[str] = None, 
                     peer_port: Optional[int] = None) -> bool:
        """
        Download a file from another peer
        
        Args:
            filename: Name of the file to download
            peer_host: Host of the peer (if known)
            peer_port: Port of the peer (if known)
            
        Returns:
            True if successful, False otherwise
        """
        # If peer info not provided, find peers with the file
        if not peer_host or not peer_port:
            peers = self.find_peers_with_file(filename)
            
            if not peers:
                logger.error(f"No peers found with file: {filename}")
                print(f"❌ No peers have the file: {filename}")
                return False
            
            # Use the first peer
            peer_info = peers[0]
            peer_host = peer_info['host']
            peer_port = peer_info['port']
            
            print(f"📡 Connecting to peer {peer_info['peer_id']} at {peer_host}:{peer_port}")
        
        try:
            # Connect to peer
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(config.CONNECTION_TIMEOUT)
            peer_socket.connect((peer_host, peer_port))
            
            logger.info(f"Connected to peer at {peer_host}:{peer_port}")
            
            # Request file
            utils.send_json(peer_socket, {
                'type': config.MSG_REQUEST_FILE,
                'filename': filename,
                'peer_id': self.peer_id
            })
            
            # Receive response
            response = utils.receive_json(peer_socket, timeout=config.SOCKET_TIMEOUT)
            
            if not response:
                logger.error("No response from peer")
                peer_socket.close()
                return False
            
            status = response.get('status')
            
            if status == config.MSG_FILE_NOT_FOUND:
                logger.error(f"File not found on peer: {filename}")
                print(f"❌ File not found: {filename}")
                peer_socket.close()
                return False
            
            elif status == config.MSG_FILE_FOUND:
                file_size = response.get('size')
                file_hash = response.get('hash')
                
                print(f"📥 Downloading {filename} ({utils.format_bytes(file_size)})...")
                
                # Receive file
                success = self.file_manager.receive_file(
                    peer_socket, filename, file_size, file_hash, show_progress=True
                )
                
                peer_socket.close()
                
                if success:
                    print(f"✅ Successfully downloaded: {filename}")
                    logger.info(f"Successfully downloaded file: {filename}")
                    return True
                else:
                    print(f"❌ Failed to download: {filename}")
                    logger.error(f"Failed to download file: {filename}")
                    return False
            
            else:
                logger.error(f"Unexpected response status: {status}")
                peer_socket.close()
                return False
                
        except socket.timeout:
            logger.error(f"Connection timeout while downloading {filename}")
            print(f"❌ Connection timeout")
            return False
        except ConnectionRefusedError:
            logger.error(f"Connection refused by peer at {peer_host}:{peer_port}")
            print(f"❌ Could not connect to peer")
            return False
        except Exception as e:
            logger.error(f"Error downloading file {filename}: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def _handle_incoming_file(self, client_socket: socket.socket, request: Dict):
        """
        Handle an incoming file push request
        
        Args:
            client_socket: Socket connection
            request: Request dictionary containing file metadata
        """
        filename = request.get('filename')
        file_size = request.get('size')
        file_hash = request.get('hash')
        sender_id = request.get('peer_id', 'Unknown')
        
        # Accept file_size == 0 (zero-byte files). Only treat missing metadata as invalid.
        if not filename or file_size is None:
            logger.error("Invalid file push request: missing filename or size")
            try:
                utils.send_json(client_socket, {
                    'status': config.MSG_ERROR,
                    'message': 'Invalid file push request: missing filename or size'
                })
            except Exception:
                pass
            return
            
        print(f"\n📥 Receiving pushed file '{filename}' from {sender_id} ({utils.format_bytes(file_size)})...")
        
        # Send ready acknowledgment
        utils.send_json(client_socket, {
            'status': config.MSG_READY_TO_RECEIVE,
            'message': 'Ready to receive file'
        })
        
        # Receive file
        success = self.file_manager.receive_file(
            client_socket, filename, file_size, file_hash, show_progress=True
        )
        
        if success:
            print(f"✅ Successfully received pushed file: {filename}")
            logger.info(f"Successfully received pushed file: {filename}")
        else:
            print(f"❌ Failed to receive pushed file: {filename}")
            logger.error(f"Failed to receive pushed file: {filename}")

    def push_file_to_peer(self, target_peer_host: str, target_peer_port: int, filename: str) -> bool:
        """
        Push a file to another peer
        
        Args:
            target_peer_host: Host of the target peer
            target_peer_port: Port of the target peer
            filename: Name of the file to send
            
        Returns:
            True if successful, False otherwise
        """
        # Check if file exists
        print(f"DEBUG: Checking file info for: {filename}")
        file_info = self.file_manager.get_file_info(filename, shared=True)
        print(f"DEBUG: file_info = {file_info}")
        if not file_info:
            print(f"❌ File not found in shared folder: {filename}")
            return False
            
        try:
            print(f"📡 Connecting to peer at {target_peer_host}:{target_peer_port}...")
            
            # Connect to peer
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(config.CONNECTION_TIMEOUT)
            peer_socket.connect((target_peer_host, target_peer_port))
            
            # Send push request
            push_data = {
                'type': config.MSG_SEND_FILE,
                'peer_id': self.peer_id,
                'filename': filename,
                'size': file_info['size'],
                'hash': file_info['hash']
            }
            print(f"DEBUG: Sending push request: {push_data}")
            utils.send_json(peer_socket, push_data)
            
            # Wait for ready response
            response = utils.receive_json(peer_socket, timeout=config.SOCKET_TIMEOUT)
            
            if not response or response.get('status') != config.MSG_READY_TO_RECEIVE:
                print(f"❌ Peer refused to receive file or timed out")
                peer_socket.close()
                return False
                
            print(f"📤 Sending {filename} ({utils.format_bytes(file_info['size'])})...")
            
            # Send file data
            success = self.file_manager.send_file_data(peer_socket, filename)
            
            peer_socket.close()
            
            if success:
                print(f"✅ Successfully sent file: {filename}")
                return True
            else:
                print(f"❌ Failed to send file data")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing file {filename}: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def list_local_files(self):
        """
        Display local shared files
        """
        files = self.file_manager.list_shared_files()
        
        if not files:
            print("\n📂 No files in shared folder")
            return
        
        utils.print_section(f"SHARED FILES ({len(files)})")
        for file_info in files:
            utils.print_file_info(
                file_info['filename'],
                file_info['size'],
                file_info.get('hash')
            )
    
    def list_network_files(self):
        """
        Display all files available on the network
        """
        files = self.get_all_available_files()
        
        if not files:
            print("\n📂 No files available on network")
            return
        
        utils.print_section(f"NETWORK FILES ({len(files)})")
        for file_info in files:
            print(f"\n  📄 {file_info['filename']}")
            print(f"     Size: {utils.format_bytes(file_info['size'])}")
            print(f"     Available from {len(file_info['peers'])} peer(s)")


def run_interactive_mode(peer: Peer):
    """
    Run peer in interactive mode with command menu
    
    Args:
        peer: Peer instance
    """
    utils.print_banner(f"P2P FILE SHARING - PEER: {peer.peer_id}")
    
    print(f"🆔 Peer ID: {peer.peer_id}")
    print(f"🌐 Address: {peer.host}:{peer.port}")
    print(f"📁 Shared folder: {peer.file_manager.shared_folder.absolute()}")
    print(f"📥 Downloads folder: {peer.file_manager.downloads_folder.absolute()}")
    print(f"🔍 Tracker: {'Enabled' if peer.use_tracker else 'Disabled'}\n")
    
    # Start server
    if not peer.start_server():
        print("❌ Failed to start peer server")
        return
    
    print("✅ Peer server is running\n")
    
    # Interactive menu
    while True:
        print("\n" + "─" * 60)
        print("MENU:")
        print("  1. List my shared files")
        print("  2. List all network files")
        print("  3. Download a file")
        print("  4. Refresh registration with tracker")
        print("  5. Show storage info")
        print("  6. Send file to peer")
        print("  7. Exit")
        print("─" * 60)
        
        try:
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                peer.list_local_files()
            
            elif choice == '2':
                peer.list_network_files()
            
            elif choice == '3':
                filename = input("\nEnter filename to download: ").strip()
                if filename:
                    peer.download_file(filename)
                else:
                    print("❌ Invalid filename")
            
            elif choice == '4':
                if peer.use_tracker:
                    peer.register_with_tracker()
                else:
                    print("⚠️  Tracker not enabled")
            
            elif choice == '5':
                info = peer.file_manager.get_storage_info()
                utils.print_section("STORAGE INFO")
                print(f"  Shared: {info['shared_count']} files ({utils.format_bytes(info['shared_size'])})")
                print(f"  Downloads: {info['downloads_count']} files ({utils.format_bytes(info['downloads_size'])})")
                print(f"  Total: {info['total_count']} files ({utils.format_bytes(info['total_size'])})")
            
            elif choice == '6':
                if not peer.use_tracker:
                    print("⚠️  Tracker not enabled. Cannot find peers.")
                    continue
                    
                # Get list of peers
                try:
                    response = requests.get(f"{peer.tracker_url}/get_all_peers", timeout=5)
                    if response.status_code != 200:
                        print(f"❌ Failed to get peers from tracker")
                        continue
                        
                    peers = response.json().get('peers', [])
                    # Filter out self
                    peers = [p for p in peers if p['peer_id'] != peer.peer_id]
                    
                    if not peers:
                        print("❌ No other peers found")
                        continue
                        
                    print("\nAvailable Peers:")
                    for i, p in enumerate(peers):
                        print(f"  {i+1}. {p['peer_id']} ({p['host']}:{p['port']})")
                    
                    try:
                        peer_idx = int(input("\nSelect peer number: ")) - 1
                        if 0 <= peer_idx < len(peers):
                            target_peer = peers[peer_idx]
                            filename = input("Enter filename to send: ").strip()
                            if filename:
                                peer.push_file_to_peer(target_peer['host'], target_peer['port'], filename)
                            else:
                                print("❌ Invalid filename")
                        else:
                            print("❌ Invalid selection")
                    except ValueError:
                        print("❌ Invalid input")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == '7':
                print("\n👋 Shutting down peer...")
                peer.stop_server()
                print("✅ Peer stopped successfully")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-7.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down peer...")
            peer.stop_server()
            print("✅ Peer stopped successfully")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"❌ Error: {e}")


def main():
    """
    Main entry point for peer application
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='P2P File Sharing Peer')
    parser.add_argument('--id', type=str, required=True, help='Peer ID')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address')
    parser.add_argument('--port', type=int, default=config.DEFAULT_PEER_PORT, help='Port number')
    parser.add_argument('--shared', type=str, default=None, help='Shared folder path')
    parser.add_argument('--downloads', type=str, default=None, help='Downloads folder path')
    parser.add_argument('--no-tracker', action='store_true', help='Disable tracker')
    
    args = parser.parse_args()
    
    # Set folder paths
    shared_folder = args.shared or f"{config.SHARED_FOLDER}_{args.id}"
    downloads_folder = args.downloads or f"{config.DOWNLOADS_FOLDER}_{args.id}"
    
    # Create peer
    peer = Peer(
        peer_id=args.id,
        host=args.host,
        port=args.port,
        shared_folder=shared_folder,
        downloads_folder=downloads_folder,
        use_tracker=not args.no_tracker
    )
    
    # Run in interactive mode
    run_interactive_mode(peer)


if __name__ == '__main__':
    main()
