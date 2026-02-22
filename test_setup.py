"""
Test Setup Script
Creates sample files for testing the P2P system
"""

import os
from pathlib import Path
import random
import string


def generate_random_text(size_kb: int) -> str:
    """
    Generate random text of specified size
    
    Args:
        size_kb: Size in kilobytes
        
    Returns:
        Random text string
    """
    size_bytes = size_kb * 1024
    return ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size_bytes))


def create_sample_files(folder: str, peer_id: str):
    """
    Create sample files in a folder
    
    Args:
        folder: Path to folder
        peer_id: Peer identifier for naming
    """
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Creating sample files in {folder}/")
    
    # Small text file
    file1 = folder_path / f"{peer_id}_small.txt"
    with open(file1, 'w') as f:
        f.write(f"This is a small test file from {peer_id}.\n")
        f.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n")
    print(f"  ✅ Created {file1.name} (< 1 KB)")
    
    # Medium text file
    file2 = folder_path / f"{peer_id}_medium.txt"
    with open(file2, 'w') as f:
        f.write(generate_random_text(50))  # 50 KB
    print(f"  ✅ Created {file2.name} (~50 KB)")
    
    # Large text file
    file3 = folder_path / f"{peer_id}_large.txt"
    with open(file3, 'w') as f:
        f.write(generate_random_text(500))  # 500 KB
    print(f"  ✅ Created {file3.name} (~500 KB)")
    
    # Sample document
    file4 = folder_path / f"{peer_id}_document.md"
    with open(file4, 'w') as f:
        f.write(f"# Document from {peer_id}\n\n")
        f.write("## Section 1\n")
        f.write("This is a sample markdown document for testing.\n\n")
        f.write("## Section 2\n")
        f.write("It contains multiple sections and formatting.\n\n")
        f.write("### Subsection\n")
        f.write("- Bullet point 1\n")
        f.write("- Bullet point 2\n")
        f.write("- Bullet point 3\n")
    print(f"  ✅ Created {file4.name}")
    
    # Binary-like file
    file5 = folder_path / f"{peer_id}_data.bin"
    with open(file5, 'wb') as f:
        f.write(os.urandom(10240))  # 10 KB of random bytes
    print(f"  ✅ Created {file5.name} (~10 KB binary)")


def setup_test_environment():
    """
    Set up complete test environment with sample files for multiple peers
    """
    print("=" * 60)
    print("P2P FILE SHARING - TEST SETUP")
    print("=" * 60)
    
    # Create files for 3 peers
    peers = [
        ('shared_peer1', 'peer1'),
        ('shared_peer2', 'peer2'),
        ('shared_peer3', 'peer3')
    ]
    
    for folder, peer_id in peers:
        create_sample_files(folder, peer_id)
    
    # Create empty download folders
    print(f"\n📥 Creating download folders...")
    for i in range(1, 4):
        folder = Path(f"downloads_peer{i}")
        folder.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created downloads_peer{i}/")
    
    # Create a shared file across multiple peers
    print(f"\n📄 Creating shared file across peers...")
    shared_content = "This file is shared by multiple peers for testing.\n" * 100
    
    for i in range(1, 4):
        shared_file = Path(f"shared_peer{i}") / "common_file.txt"
        with open(shared_file, 'w') as f:
            f.write(shared_content)
    print(f"  ✅ Created common_file.txt in all peer folders")
    
    print("\n" + "=" * 60)
    print("✅ Test environment setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the tracker: python tracker.py")
    print("2. Start peer1: python peer.py --id peer1 --port 6001")
    print("3. Start peer2: python peer.py --id peer2 --port 6002")
    print("4. Start peer3: python peer.py --id peer3 --port 6003")
    print("\nHappy testing! 🚀\n")


if __name__ == '__main__':
    setup_test_environment()
