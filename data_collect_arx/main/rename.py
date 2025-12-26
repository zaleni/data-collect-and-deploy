#!/usr/bin/env python3
import os

def rename_files_in_tissue_folder(tissue_folder):
    """
    Rename all files in the specified tissue folder to match the naming pattern 'tissue_X.hdf5'.

    Args:
        tissue_folder (str): Path to the tissue folder containing the files to rename.
    """
    if not os.path.exists(tissue_folder):
        print(f"Error: Folder '{tissue_folder}' does not exist!")
        return

    # List all files in the folder
    files = [f for f in os.listdir(tissue_folder) if os.path.isfile(os.path.join(tissue_folder, f))]
    files.sort()  # Sort files to ensure consistent renaming order
    tissue_count = 1

    for file_name in files:
        # Get the full path of the current file
        old_file_path = os.path.join(tissue_folder, file_name)
        
        # Generate the new file name
        new_file_name = f"Vida_{tissue_count}.hdf5"
        new_file_path = os.path.join(tissue_folder, new_file_name)
        
        # Rename the file
        os.rename(old_file_path, new_file_path)
        print(f"Renamed: {old_file_path} -> {new_file_path}")
        
        tissue_count += 1

    print(f"Renamed {tissue_count - 1} files in '{tissue_folder}'.")

if __name__ == "__main__":
    # Specify the tissue folder path
    tissue_folder = "/home/go2/ARX_X5/main/Vida_1225/processed"
    rename_files_in_tissue_folder(tissue_folder)