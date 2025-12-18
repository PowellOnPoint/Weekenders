#!/usr/bin/env python3
import os
import subprocess
import hashlib
import logging
from pathlib import Path
import time
from tqdm import tqdm

# Configuration
PHOTOS_LIBRARY = Path.home() / "Pictures" / "Photos Library.photoslibrary"
DESTINATION = Path("Pictures Auto Backup") # Edit target directory here
LOG_FILE = Path.home() / "photo_backup.log"

# Supported file extensions
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".mov", ".mp4", ".m4v", ".gif", ".raw", ".aaf"}

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def check_mount():
    """Verify the destination drive is mounted."""
    if not DESTINATION.exists():
        logging.error(f"Destination {DESTINATION} is not mounted.")
        raise FileNotFoundError(f"Destination {DESTINATION} is not mounted.")
    logging.info(f"Destination {DESTINATION} is mounted.")

def check_permissions():
    """Check if the script has access to the Photos Library."""
    try:
        os.listdir(PHOTOS_LIBRARY)
        logging.info(f"Access to {PHOTOS_LIBRARY} confirmed.")
        return True
    except PermissionError:
        logging.error(f"Permission denied accessing {PHOTOS_LIBRARY}.")
        print(f"Permission denied for {PHOTOS_LIBRARY}. Please grant access in System Settings > Privacy & Security > Photos for Python or Terminal.")
        input("Press Enter after granting permissions, or Ctrl+C to exit...")
        try:
            os.listdir(PHOTOS_LIBRARY)
            logging.info(f"Access to {PHOTOS_LIBRARY} granted after retry.")
            return True
        except PermissionError:
            logging.error(f"Still no access to {PHOTOS_LIBRARY} after retry.")
            return False

def get_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logging.error(f"Failed to hash {file_path}: {e}")
        return None

def build_destination_hash_cache(dest_dir):
    """Build a cache of file hashes for all files in the destination directory."""
    hash_cache = {}
    logging.info(f"Building hash cache for {dest_dir}")
    for dest_file in dest_dir.rglob("*"):
        if dest_file.is_file():
            file_hash = get_file_hash(dest_file)
            if file_hash:
                hash_cache[file_hash] = dest_file
    logging.info(f"Hash cache built with {len(hash_cache)} entries")
    return hash_cache

def check_duplicate(src_file, hash_cache, dest_dir):
    """Check if a file already exists in the destination by size and hash."""
    src_size = src_file.stat().st_size
    src_hash = None
    for dest_file in dest_dir.rglob("*"):
        if dest_file.is_file() and dest_file.stat().st_size == src_size:
            if src_hash is None:  # Compute source hash only if needed
                src_hash = get_file_hash(src_file)
                if not src_hash:
                    return False
            if src_hash in hash_cache:
                logging.info(f"Duplicate found: {src_file} matches {hash_cache[src_hash]}")
                return True
    return False

def rsync_file(src, dest):
    """Use rsync to copy a single file efficiently."""
    try:
        subprocess.run(
            ["rsync", "-a", str(src), str(dest)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f"Successfully copied {src} to {dest}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to copy {src}: {e.stderr}")
        raise

def find_originals_path():
    """Find the folder containing original files."""
    possible_paths = [
        PHOTOS_LIBRARY / "originals",
        PHOTOS_LIBRARY / "Masters",
        PHOTOS_LIBRARY / "resources" / "media"
    ]
    for path in possible_paths:
        try:
            if path.exists():
                logging.info(f"Found originals folder: {path}")
                return path
        except PermissionError:
            logging.warning(f"Permission denied accessing {path}")
    logging.error(f"No accessible originals folder found in {PHOTOS_LIBRARY}")
    raise FileNotFoundError(f"No accessible originals folder found in {PHOTOS_LIBRARY}")

def process_photos():
    """Process and copy photos from the Photos Library."""
    check_mount()
    if not check_permissions():
        raise PermissionError(f"Cannot access {PHOTOS_LIBRARY}. Please grant permissions and try again.")
    
    originals_path = find_originals_path()
    logging.debug(f"Scanning folder: {originals_path}")
    DESTINATION.mkdir(parents=True, exist_ok=True)

    hash_cache = build_destination_hash_cache(DESTINATION)
    total_files = sum(1 for _ in originals_path.rglob("*") if _.is_file())
    copied_files = 0
    skipped_files = 0
    start_time = time.time()

    with tqdm(total=total_files, desc="Processing files") as pbar:
        for root, _, files in os.walk(originals_path):
            for file in files:
                src_file = Path(root) / file
                pbar.update(1)

                if src_file.suffix.lower() not in VALID_EXTENSIONS:
                    logging.debug(f"Skipping non-media file: {src_file}")
                    skipped_files += 1
                    continue

                if check_duplicate(src_file, hash_cache, DESTINATION):
                    logging.info(f"Skipping duplicate: {src_file}")
                    skipped_files += 1
                    continue

                rel_path = src_file.relative_to(originals_path)
                dest_file = DESTINATION / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                try:
                    rsync_file(src_file, dest_file.parent)
                    copied_files += 1
                    src_hash = get_file_hash(src_file)
                    if src_hash:
                        hash_cache[src_hash] = dest_file
                except Exception as e:
                    logging.error(f"Error copying {src_file}: {str(e)}")

    elapsed_time = time.time() - start_time
    logging.info(
        f"Backup complete: {copied_files} files copied, {skipped_files} files skipped, "
        f"Total: {total_files} files, Time: {elapsed_time:.2f} seconds"
    )
    print(f"Backup complete. Check {LOG_FILE} for details.")

if __name__ == "__main__":
    try:
        process_photos()
    except Exception as e:
        logging.error(f"Backup failed: {str(e)}")
        print(f"Backup failed: {str(e)}. Check {LOG_FILE} for details.")