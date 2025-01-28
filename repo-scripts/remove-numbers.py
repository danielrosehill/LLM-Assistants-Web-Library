import os
import re

def rename_markdown_files(directory):
    # Compile a regex pattern to match the filenames
    pattern = re.compile(r'^\d{3}-(.+\.md)$')

    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # Check if the file is a markdown file and matches the pattern
            if filename.endswith('.md') and pattern.match(filename):
                # Extract the new filename by removing the numeric identifier and hyphen
                new_filename = pattern.match(filename).group(1)
                
                # Get the full paths for the old and new filenames
                old_file_path = os.path.join(root, filename)
                new_file_path = os.path.join(root, new_filename)
                
                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f'Renamed: {old_file_path} -> {new_file_path}')

# Specify the directory to start the recursion
directory_path = '/home/daniel/Git/llm-assistants-web-library/agent-configs'

# Call the function to rename the markdown files
rename_markdown_files(directory_path)