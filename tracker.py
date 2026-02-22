"""
Tracker Server for P2P File Sharing System
Acts as a directory service for peer discovery
"""

import json
import os
from flask import Flask, request, jsonify
from datetime import datetime
from typing import Dict, List, Optional
import config
import utils


logger = utils.get_logger("Tracker")


class TrackerServer:
    """
    Tracker server that maintains a registry of peers and their shared files
    """
    
    def __init__(self, data_file: str = config.TRACKER_DATA_FILE):
        """
        Initialize tracker server
        
        Args:
            data_file: Path to JSON file for storing tracker data
        """
        self.data_file = data_file
        self.peers = {}  # {peer_id: peer_info}
        self.load_data()
        logger.info("Tracker server initialized")
    
    def load_data(self):
        """Load tracker data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.peers = data.get('peers', {})
                logger.info(f"Loaded data for {len(self.peers)} peers from {self.data_file}")
            except Exception as e:
                logger.error(f"Error loading tracker data: {e}")
                self.peers = {}
        else:
            logger.info("No existing tracker data found, starting fresh")
    
    def save_data(self):
        """Save tracker data to file"""
        try:
            data = {
                'peers': self.peers,
                'last_updated': utils.get_timestamp()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("Tracker data saved successfully")
        except Exception as e:
            logger.error(f"Error saving tracker data: {e}")
    
    def register_peer(self, peer_id: str, host: str, port: int, files: List[Dict]) -> Dict:
        """
        Register or update a peer
        
        Args:
            peer_id: Unique identifier for the peer
            host: IP address of the peer
            port: Port number the peer is listening on
            files: List of files the peer is sharing
            
        Returns:
            Response dictionary
        """
        try:
            self.peers[peer_id] = {
                'peer_id': peer_id,
                'host': host,
                'port': port,
                'files': files,
                'registered_at': utils.get_timestamp(),
                'last_seen': utils.get_timestamp()
            }
            self.save_data()
            
            logger.info(f"Registered peer: {peer_id} at {host}:{port} with {len(files)} files")
            
            return {
                'status': 'success',
                'message': f'Peer {peer_id} registered successfully',
                'peer_count': len(self.peers)
            }
        except Exception as e:
            logger.error(f"Error registering peer {peer_id}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def unregister_peer(self, peer_id: str) -> Dict:
        """
        Unregister a peer
        
        Args:
            peer_id: Identifier of the peer to remove
            
        Returns:
            Response dictionary
        """
        if peer_id in self.peers:
            del self.peers[peer_id]
            self.save_data()
            logger.info(f"Unregistered peer: {peer_id}")
            return {
                'status': 'success',
                'message': f'Peer {peer_id} unregistered successfully'
            }
        else:
            return {
                'status': 'error',
                'message': f'Peer {peer_id} not found'
            }
    
    def get_file_peers(self, filename: str) -> List[Dict]:
        """
        Find all peers that have a specific file
        
        Args:
            filename: Name of the file to search for
            
        Returns:
            List of peer information dictionaries
        """
        peers_with_file = []
        
        for peer_id, peer_info in self.peers.items():
            for file_info in peer_info['files']:
                if file_info['filename'] == filename:
                    peers_with_file.append({
                        'peer_id': peer_id,
                        'host': peer_info['host'],
                        'port': peer_info['port'],
                        'file_info': file_info
                    })
                    break
        
        logger.info(f"Found {len(peers_with_file)} peers with file: {filename}")
        return peers_with_file
    
    def get_all_files(self) -> List[Dict]:
        """
        Get a list of all available files across all peers
        
        Returns:
            List of file dictionaries with peer information
        """
        all_files = {}
        
        for peer_id, peer_info in self.peers.items():
            for file_info in peer_info['files']:
                filename = file_info['filename']
                
                if filename not in all_files:
                    all_files[filename] = {
                        'filename': filename,
                        'size': file_info.get('size', 0),
                        'hash': file_info.get('hash'),
                        'peers': []
                    }
                
                all_files[filename]['peers'].append({
                    'peer_id': peer_id,
                    'host': peer_info['host'],
                    'port': peer_info['port']
                })
        
        return list(all_files.values())
    
    def get_all_peers(self) -> List[Dict]:
        """
        Get information about all registered peers
        
        Returns:
            List of peer information dictionaries
        """
        return list(self.peers.values())


# Create Flask app
app = Flask(__name__)
tracker = TrackerServer()


@app.route('/')
def index():
    """Home endpoint"""
    return jsonify({
        'message': 'P2P File Sharing Tracker Server',
        'version': '1.0',
        'endpoints': [
            'POST /register_peer',
            'POST /unregister_peer',
            'GET /get_file_peers?filename=<filename>',
            'GET /get_all_files',
            'GET /get_all_peers',
            'GET /status'
        ]
    })


@app.route('/register_peer', methods=['POST'])
def register_peer():
    """
    Register a peer with the tracker
    
    Expected JSON body:
    {
        "peer_id": "peer1",
        "host": "127.0.0.1",
        "port": 6000,
        "files": [{"filename": "file.txt", "size": 1234, "hash": "..."}]
    }
    """
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['peer_id', 'host', 'port', 'files']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: peer_id, host, port, files'
            }), 400
        
        result = tracker.register_peer(
            data['peer_id'],
            data['host'],
            data['port'],
            data['files']
        )
        
        status_code = 200 if result['status'] == 'success' else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in register_peer endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/unregister_peer', methods=['POST'])
def unregister_peer():
    """
    Unregister a peer from the tracker
    
    Expected JSON body:
    {
        "peer_id": "peer1"
    }
    """
    try:
        data = request.get_json()
        
        if 'peer_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: peer_id'
            }), 400
        
        result = tracker.unregister_peer(data['peer_id'])
        status_code = 200 if result['status'] == 'success' else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in unregister_peer endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/get_file_peers', methods=['GET'])
def get_file_peers():
    """
    Get list of peers that have a specific file
    
    Query parameter: filename
    """
    try:
        filename = request.args.get('filename')
        
        if not filename:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameter: filename'
            }), 400
        
        peers = tracker.get_file_peers(filename)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'peer_count': len(peers),
            'peers': peers
        })
        
    except Exception as e:
        logger.error(f"Error in get_file_peers endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/get_all_files', methods=['GET'])
def get_all_files():
    """Get list of all available files"""
    try:
        files = tracker.get_all_files()
        
        return jsonify({
            'status': 'success',
            'file_count': len(files),
            'files': files
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_files endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/get_all_peers', methods=['GET'])
def get_all_peers():
    """Get list of all registered peers"""
    try:
        peers = tracker.get_all_peers()
        
        return jsonify({
            'status': 'success',
            'peer_count': len(peers),
            'peers': peers
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_peers endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Get tracker server status"""
    return jsonify({
        'status': 'online',
        'peer_count': len(tracker.peers),
        'timestamp': utils.get_timestamp()
    })


def run_tracker(host: str = config.TRACKER_HOST, port: int = config.TRACKER_PORT):
    """
    Run the tracker server
    
    Args:
        host: Host address to bind to
        port: Port number to listen on
    """
    utils.print_banner("P2P FILE SHARING - TRACKER SERVER")
    logger.info(f"Starting tracker server on {host}:{port}")
    print(f"🚀 Tracker server running at http://{host}:{port}")
    print(f"📊 Currently tracking {len(tracker.peers)} peers\n")
    
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    run_tracker()
