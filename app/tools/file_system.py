import os
import glob

# The main runner script will ensure this directory exists.
# Tools should operate relative to this base or expect absolute paths within it.
WORKSPACE_DIR = "workspace"

def _get_safe_path(filename: str) -> str:
    """
    Ensures the path is within the WORKSPACE_DIR and resolves it.
    Prevents directory traversal.
    """
    # Normalize the path to resolve '..' etc.
    # Then ensure it's truly within the workspace.
    base_path = os.path.abspath(WORKSPACE_DIR)
    target_path = os.path.abspath(os.path.join(base_path, filename))

    if os.path.commonprefix([target_path, base_path]) != base_path:
        raise ValueError(f"Attempted file access outside workspace: {filename}")
    return target_path

def read_file(filepath: str) -> str | None:
    """
    Reads content from a file in the WORKSPACE_DIR.
    filepath is relative to the WORKSPACE_DIR.
    Returns content as a string, or None if an error occurs.
    """
    safe_filepath = _get_safe_path(filepath)
    print(f"  [FileSystem] Reading file: {safe_filepath}")
    try:
        with open(safe_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"  [FileSystem] Error: File not found at {safe_filepath}")
        return None
    except Exception as e:
        print(f"  [FileSystem] Error reading file {safe_filepath}: {e}")
        return None

def write_file(filepath: str, content: str) -> bool:
    """
    Writes content to a file in the WORKSPACE_DIR.
    filepath is relative to the WORKSPACE_DIR.
    Creates subdirectories if they don't exist.
    Returns True if successful, False otherwise.
    """
    safe_filepath = _get_safe_path(filepath)
    print(f"  [FileSystem] Writing to file: {safe_filepath}")
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(safe_filepath), exist_ok=True)
        with open(safe_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [FileSystem] Content written to {safe_filepath}")
        return True
    except Exception as e:
        print(f"  [FileSystem] Error writing file {safe_filepath}: {e}")
        return False

def list_files(dirpath: str = ".") -> list[str]:
    """
    Lists all files and directories within the given path relative to WORKSPACE_DIR.
    Returns a list of relative paths from the dirpath.
    """
    safe_dirpath = _get_safe_path(dirpath)
    print(f"  [FileSystem] Listing files in: {safe_dirpath}")
    try:
        if not os.path.isdir(safe_dirpath):
            print(f"  [FileSystem] Error: {safe_dirpath} is not a directory.")
            return []

        items = []
        for item in os.listdir(safe_dirpath):
            # To make it consistent with how `ls` tool works (trailing slash for dirs)
            if os.path.isdir(os.path.join(safe_dirpath, item)):
                items.append(item + "/")
            else:
                items.append(item)
        return items
    except Exception as e:
        print(f"  [FileSystem] Error listing files in {safe_dirpath}: {e}")
        return []

if __name__ == '__main__':
    print("--- Testing File System Tools ---")

    # Setup a dummy workspace for testing this module directly
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    # Test write_file
    test_content = "Hello from the file system tool!\nThis is a test."
    test_filepath = "test_document.txt"
    nested_filepath = "subdir/another_doc.txt"

    print(f"\nTesting write_file with '{test_filepath}'...")
    success_write = write_file(test_filepath, test_content)
    print(f"Write successful: {success_write}")

    print(f"\nTesting write_file with nested path '{nested_filepath}'...")
    success_nested_write = write_file(nested_filepath, "Nested content here.")
    print(f"Nested write successful: {success_nested_write}")

    # Test read_file
    print(f"\nTesting read_file with '{test_filepath}'...")
    retrieved_content = read_file(test_filepath)
    if retrieved_content:
        print("Retrieved content:")
        print(retrieved_content)
        assert retrieved_content == test_content
    else:
        print("Failed to retrieve content or file not found.")

    print(f"\nTesting read_file with non-existent file:")
    read_file("non_existent.txt")

    # Test list_files
    print("\nTesting list_files for workspace root:")
    root_files = list_files(".") # or list_files()
    print(f"Files in workspace: {root_files}")
    assert test_filepath in root_files
    assert "subdir/" in root_files

    print("\nTesting list_files for 'subdir':")
    subdir_files = list_files("subdir")
    print(f"Files in subdir: {subdir_files}")
    assert "another_doc.txt" in subdir_files

    # Test path safety
    print("\nTesting path safety (attempting to write outside workspace):")
    try:
        write_file("../outside_workspace.txt", "danger")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\n--- File System Test Complete ---")
    # Clean up dummy workspace if needed, or let run_task.py handle it
    # import shutil
    # if os.path.exists(WORKSPACE_DIR):
    #     shutil.rmtree(WORKSPACE_DIR)
