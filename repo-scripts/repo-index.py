import os
import yaml
from datetime import datetime

def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_folder_name(folder_name):
    return folder_name.replace("-", " ").title()

def load_markdown(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file: {file_path}. Details: {e}")
        return {'tags': []}, ""
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            markdown_content = parts[2].strip()
            try:
                front_matter = yaml.safe_load(yaml_content)
                if 'tags' in front_matter:
                    if isinstance(front_matter['tags'], str):
                        front_matter['tags'] = [tag.strip() for tag in front_matter['tags'].split(',')]
                else:
                    front_matter['tags'] = []
                return front_matter, markdown_content
            except yaml.YAMLError as e:
                print(f"YAML error in {file_path}: {e}. YAML content: {yaml_content}")
                return {'tags': []}, content
    return {'tags': []}, content

def extract_title_and_body(markdown_content, filename):
    title = filename
    body = markdown_content.strip()
    
    for line in markdown_content.splitlines():
        if line.strip().startswith('# '):
            title = line.strip('# ').strip()
            body = markdown_content[markdown_content.find(line) + len(line):].strip()
            break
        
    return title, body

def generate_title_from_file(file_path, markdown_content):
        file_name = os.path.basename(file_path)
        file_name_no_ext, _ = os.path.splitext(file_name)
        title = file_name_no_ext.replace("-", " ").title()

        if markdown_content:
          title, _ = extract_title_and_body(markdown_content, title)
        
        return title

def generate_markdown_index(base_path, repo_root, level=0):
    index_content = ""
    items = sorted(os.listdir(base_path))
    for item in items:
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
          if level == 0:
              index_content += f"{'  ' * level}- **{format_folder_name(item)}**\n"
              index_content += generate_markdown_index(item_path, repo_root, level + 1) # Recurse through subdirectories
          else:
              index_content += f"{'  ' * level}- {format_folder_name(item)}\n"
              index_content += generate_markdown_index(item_path, repo_root, level + 1)
        elif item.endswith('.md'):
            front_matter, markdown_content = load_markdown(item_path)
            title = generate_title_from_file(item_path, markdown_content)
            relative_path = os.path.relpath(item_path, repo_root)
            vision = front_matter.get("vision", "")
            vision_icon = " 🔭" if str(vision).lower() == "yes" else ""
            index_content += f"{'  ' * level}- [{title}{vision_icon}]({relative_path})\n"
            
    return index_content

def update_readme(index_content, readme_path):
    try:
        with open(readme_path, 'r') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"Warning: README not found at {readme_path}. Creating new file")
        readme_content = ""
    
    # Add a marker to know where to insert/update the index content
    start_marker = "<!-- INDEX_START -->\n"
    end_marker = "<!-- INDEX_END -->\n"
    
    start_index = readme_content.find(start_marker)
    end_index = readme_content.find(end_marker)
    
    if start_index != -1 and end_index != -1:
        # update the existing index
        updated_readme = readme_content[:start_index + len(start_marker)]
        updated_readme += index_content
        updated_readme += readme_content[end_index:]
    else:
        # add new index content
        updated_readme = readme_content + "\n" + start_marker + index_content + end_marker

    with open(readme_path, 'w') as f:
        f.write(updated_readme)
    print(f"README updated with new index at {readme_path}")


if __name__ == "__main__":
    base_path = "/home/daniel/Git/llm-assistants-web-library/agent-configs"  # Replace with the actual path
    repo_root = "/home/daniel/Git/llm-assistants-web-library" # Path to the root of your repo
    readme_path = "/home/daniel/Git/llm-assistants-web-library/README.md"  # Replace with your readme path
    index_content = generate_markdown_index(base_path, repo_root)
    
    with open("index.md", "w") as f:
        f.write(index_content)
    print("index.md generated")

    update_readme(index_content, readme_path)