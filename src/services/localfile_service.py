import os
import shutil
from pathlib import Path
from typing import List, Optional

class LocalFileService:

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file at the specified path."""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return True
            return False
        
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    @staticmethod
    def move_file(source_path: str, destination_path: str) -> bool:
        """
        Move a file from source_path to destination_path.
        Creates the destination directory if it doesn't exist.

        Args:
        - source_path: The path of the file to be moved.
        - destination_path: The path where the file should be moved to.

        Returns:- True if the file was moved successfully, False otherwise.
        """
        try:
            if not os.path.isfile(source_path):
                print("The original file does not exist.")
                return False

            destination_dir = os.path.dirname(destination_path)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            shutil.move(source_path, destination_path)
            return True
        
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
        
    @staticmethod
    def create_folder(path: str, folder_name: str) -> Optional[str]:
        """
        Create a folder at the specified path.
        """
        try:
            if not os.path.isdir(path):
                print("The original path does not exist.")
                return False

            full_path = os.path.join(path, folder_name)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
            return full_path
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None

    @staticmethod
    def is_valid_path(path: str) -> bool:
        """
        Verify if the path is valid and accessible.
        """
        return os.path.exists(path) and os.access(path, os.R_OK | os.W_OK)
    
    @staticmethod
    def create_empty_file(path: str, file_name: str) -> bool:
        """
        Create an empty file at the specified path.
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path)

            full_path = os.path.join(path, file_name)

            with open(full_path, 'w') as f:
                pass

            return True
        except Exception as e:
            print(f"Error creating empty file: {e}")
            return False
        
    @staticmethod
    def move_all_files(src_folder: str, dest_folder: str) -> bool:
        """
        Move all files from the source folder to the destination folder.
        """
        try:
            if not os.path.isdir(src_folder):
                print("The source folder does not exist.")
                return False

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            moved_any = False
            for filename in os.listdir(src_folder):
                src_file = os.path.join(src_folder, filename)
                dest_file = os.path.join(dest_folder, filename)

                if os.path.isfile(src_file):
                    shutil.move(src_file, dest_file)
                    moved_any = True

            return moved_any
        
        except Exception as e:
            print(f"Error moving files: {e}")
            return False