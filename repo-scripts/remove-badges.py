import os
import re

def remove_badges_and_yaml_front_matter(directory):
    # Regex pattern to match GitHub badges
    badge_pattern = re.compile(r'\[!\[.*?\]\(.*?\)\]\(.*?\)')
    
    # Regex pattern to match YAML front matter (enclosed between ---)
    yaml_front_matter_pattern = re.compile(r'^---\n.*?\n---\n', re.DOTALL)

    # Walk through the directory recursively
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Remove YAML front matter
                content = yaml_front_matter_pattern.sub('', content)

                # Remove GitHub badges
                content = badge_pattern.sub('', content)

                # Write the cleaned content back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

                print(f'Processed: {file_path}')

# Specify the directory to start the recursion
directory_path = '/home/daniel/Git/llm-assistants-web-library/agent-configs'

# Call the function to remove badges and YAML front matter
remove_badges_and_yaml_front_matter(directory_path)