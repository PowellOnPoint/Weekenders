# Prompt-Engineering
Programs engineered through advanced and descriptive AI prompts

# Photo Backup Script

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Contributions](https://img.shields.io/badge/contributions-welcome-brightgreen)

A Python script to efficiently back up photos and videos from a macOS .PhotosLibrary to an external or network drive, with duplicate detection to avoid redundant copies. Optimized for modest hardware, this script uses `rsync` for reliable file transfers and SHA-256 hashing for duplicate checking.

Who needs iCloud when you have a terminal!

We welcome feedback, bug reports, and contributions to make this tool even better!
## Features
- Backs up photos and videos from macOS Photos Library (`*.photoslibrary`).
- Supports common media formats (`.jpg`, `.png`, `.heic`, `.mov`, etc.).
- Checks for duplicates using file size and SHA-256 hashing to save space.
- Uses `rsync` for efficient, incremental file transfers.
- Includes a progress bar for user-friendly monitoring.
- Optimized for single-threaded execution, suitable for low-end systems, or background run.
- Ready for adjacent operating system optimization (RaspberryPy, Linux, Third Party devices).
- Retains the .PhotoLibrary file structure for importing back into your personal devices. 
- Detailed logging for debugging and tracking.

## Prerequisites
- **macOS**: The script is designed for macOS, targeting the Photos Library structure.
- **Python 3.6+**: Ensure Python is installed (check with `python3 --version`).
- **rsync**: Pre-installed on macOS.
- **tqdm**: For the progress bar (installed via `pip`).
- **Permissions**: Full Disk Access for Python or Terminal in `System Settings > Privacy & Security > Full Disk Access`, for .Photolibrary file structure nuances. 
