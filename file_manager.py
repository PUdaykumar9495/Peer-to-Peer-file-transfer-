"""
File Manager for P2P File Sharing System
Handles file operations, chunked transfers, and integrity verification
"""

import os
import socket
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm
import config
import utils


logger = utils.get_logger("FileManager")


class FileManager:
    """
    Manages file operations for the P2P system
    """
    
    def __init__(self, shared_folder: str, downloads_folder: str):
        """
        Initialize FileManager
        
        Args:
            shared_folder: Path to folder containing files to share
            downloads_folder: Path to folder for downloaded files
        """
        self.shared_folder = Path(shared_folder)
        self.downloads_folder = Path(downloads_folder)
        
        # Create folders if they don't exist
        self.shared_folder.mkdir(parents=True, exist_ok=True)
        self.downloads_folder.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileManager initialized")
        logger.info(f"Shared folder: {self.shared_folder.absolute()}")
        logger.info(f"Downloads folder: {self.downloads_folder.absolute()}")
    
    def _get_safe_path(self, filename: str, shared: bool = True) -> Optional[Path]:
        """
        Get a safe path for a file, preventing path traversal
        
        Args:
            filename: Name of the file
            shared: If True, look in shared folder; else in downloads folder
            
        Returns:
            Resolved Path object if safe, None otherwise
        """
        try:
            folder = self.shared_folder if shared else self.downloads_folder
            # Resolve the folder path to absolute path
            folder = folder.resolve()
            
            # Join folder with filename
            file_path = (folder / filename).resolve()
            
            # Check if the resolved path is within the intended folder
            if not str(file_path).startswith(str(folder)):
                logger.warning(f"Path traversal attempt detected: {filename}")
                return None
                
            return file_path
        except Exception as e:
            logger.error(f"Error resolving path for {filename}: {e}")
            return None
    
    def list_shared_files(self) -> List[Dict[str, any]]:
        """
        List all files in the shared folder with their metadata
        
        Returns:
            List of dictionaries containing file information
        """
        files = []
        
        try:
            for file_path in self.shared_folder.iterdir():
                if file_path.is_file():
                    file_info = self.get_file_info(file_path.name, shared=True)
                    if file_info:
                        files.append(file_info)
            
            logger.info(f"Found {len(files)} shared files")
            return files
        except Exception as e:
            logger.error(f"Error listing shared files: {e}")
            return []
    
    def get_file_info(self, filename: str, shared: bool = True) -> Optional[Dict[str, any]]:
        """
        Get information about a specific file
        
        Args:
            filename: Name of the file
            shared: If True, look in shared folder; else in downloads folder
            
        Returns:
            Dictionary with file info or None if file doesn't exist
        """
        try:
            file_path = self._get_safe_path(filename, shared)
            
            if not file_path or not file_path.exists() or not file_path.is_file():
                return None
            
            size = file_path.stat().st_size
            file_hash = utils.compute_file_hash(str(file_path)) if config.VERIFY_HASH else None
            
            return {
                'filename': filename,
                'size': size,
                'hash': file_hash,
                'path': str(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file info for {filename}: {e}")
            return None
    
    def file_exists(self, filename: str, shared: bool = True) -> bool:
        """
        Check if a file exists
        
        Args:
            filename: Name of the file
            shared: If True, check in shared folder; else in downloads folder
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self._get_safe_path(filename, shared)
        return file_path is not None and file_path.exists() and file_path.is_file()
    
    def read_file_chunks(self, filename: str) -> Optional[bytes]:
        """
        Read a file in chunks (generator)
        
        Args:
            filename: Name of the file to read
            
        Yields:
            Chunks of file data
        """
        file_path = self._get_safe_path(filename, shared=True)
        
        if not file_path or not file_path.exists():
            logger.error(f"File not found or invalid path: {filename}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(config.CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk
            logger.info(f"File {filename} read successfully")
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            return None
    
    def send_file_data(self, sock: socket.socket, filename: str) -> bool:
        """
        Send the raw data of a file over a socket
        
        Args:
            sock: Socket connection
            filename: Name of the file to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_safe_path(filename, shared=True)
            if not file_path:
                return False
                
            bytes_sent = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(config.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    sock.sendall(chunk)
                    bytes_sent += len(chunk)
            
            logger.info(f"File data for {filename} sent successfully ({utils.format_bytes(bytes_sent)})")
            return True
        except Exception as e:
            logger.error(f"Error sending file data for {filename}: {e}")
            return False

    def send_file(self, sock: socket.socket, filename: str) -> bool:
        """
        Send a file over a socket connection in chunks (Protocol: Metadata -> Data)
        
        Args:
            sock: Socket connection
            filename: Name of the file to send
            
        Returns:
            True if successful, False otherwise
        """
        file_info = self.get_file_info(filename, shared=True)
        
        if not file_info:
            logger.error(f"Cannot send file {filename}: File not found or invalid path")
            utils.send_json(sock, {
                'status': config.MSG_FILE_NOT_FOUND,
                'message': f'File {filename} not found'
            })
            return False
        
        try:
            # Send file metadata first
            utils.send_json(sock, {
                'status': config.MSG_FILE_FOUND,
                'filename': filename,
                'size': file_info['size'],
                'hash': file_info['hash']
            })
            
            logger.info(f"Sending file: {filename} ({utils.format_bytes(file_info['size'])})")
            
            # Send file data
            return self.send_file_data(sock, filename)
            
        except Exception as e:
            logger.error(f"Error sending file {filename}: {e}")
            return False
    
    def receive_file(self, sock: socket.socket, filename: str, file_size: int, 
                    file_hash: Optional[str] = None, show_progress: bool = True) -> bool:
        """
        Receive a file over a socket connection in chunks
        
        Args:
            sock: Socket connection
            filename: Name of the file to save
            file_size: Expected size of the file
            file_hash: Expected hash for verification (optional)
            show_progress: Whether to show progress bar
            
        Returns:
            True if successful and verified, False otherwise
        """
        # Ensure filename is safe (no path traversal)
        safe_filename = Path(filename).name
        if safe_filename != filename:
            logger.warning(f"Sanitized filename from {filename} to {safe_filename}")
            filename = safe_filename
            
        file_path = self._get_safe_path(filename, shared=False)
        if not file_path:
            logger.error(f"Invalid path for receiving file: {filename}")
            return False
        
        try:
            logger.info(f"Receiving file: {filename} ({utils.format_bytes(file_size)})")
            
            bytes_received = 0
            
            # Progress bar
            if show_progress:
                pbar = tqdm(total=file_size, unit='B', unit_scale=True, 
                           desc=filename, ncols=80)
            
            with open(file_path, 'wb') as f:
                while bytes_received < file_size:
                    chunk_size = min(config.CHUNK_SIZE, file_size - bytes_received)
                    chunk = sock.recv(chunk_size)
                    
                    if not chunk:
                        logger.error("Connection closed before file transfer completed")
                        if show_progress:
                            pbar.close()
                        return False
                    
                    f.write(chunk)
                    bytes_received += len(chunk)
                    
                    if show_progress:
                        pbar.update(len(chunk))
            
            if show_progress:
                pbar.close()
            
            logger.info(f"File {filename} received successfully ({utils.format_bytes(bytes_received)})")
            
            # Verify hash if provided
            if config.VERIFY_HASH and file_hash:
                computed_hash = utils.compute_file_hash(str(file_path))
                if computed_hash != file_hash:
                    logger.error(f"Hash verification failed for {filename}")
                    logger.error(f"Expected: {file_hash}")
                    logger.error(f"Computed: {computed_hash}")
                    # Delete corrupted file
                    file_path.unlink()
                    return False
                logger.info(f"Hash verification successful for {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error receiving file {filename}: {e}")
            # Clean up partial file
            if file_path and file_path.exists():
                file_path.unlink()
            return False
    
    def delete_file(self, filename: str, shared: bool = False) -> bool:
        """
        Delete a file
        
        Args:
            filename: Name of the file to delete
            shared: If True, delete from shared folder; else from downloads folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_safe_path(filename, shared)
            
            if file_path and file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {filename}")
                return True
            else:
                logger.warning(f"File not found or invalid path: {filename}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, any]:
        """
        Get storage information for shared and downloads folders
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            shared_size = sum(f.stat().st_size for f in self.shared_folder.iterdir() if f.is_file())
            downloads_size = sum(f.stat().st_size for f in self.downloads_folder.iterdir() if f.is_file())
            shared_count = sum(1 for f in self.shared_folder.iterdir() if f.is_file())
            downloads_count = sum(1 for f in self.downloads_folder.iterdir() if f.is_file())
            
            return {
                'shared_size': shared_size,
                'downloads_size': downloads_size,
                'shared_count': shared_count,
                'downloads_count': downloads_count,
                'total_size': shared_size + downloads_size,
                'total_count': shared_count + downloads_count
            }
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
            return {}
