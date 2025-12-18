import shutil

def copy_file_to_backup(source_path, destination_path):
    try:
        # Copy the file from source to destination
        shutil.copy2(source_path, destination_path)
        print(f"File successfully copied from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"Error: The file at {source_path} was not found.")
    except PermissionError:
        print(f"Error: Permission denied when trying to write to {destination_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage:
source_file = "/path/to/your/source/file.txt"
backup_location = "/path/to/your/backup/file.txt"
copy_file_to_backup(source_file, backup_location)