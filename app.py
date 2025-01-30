import os
import streamlit as st
from datetime import datetime
import yaml

# Remove pyperclip as it's not well-supported in Streamlit cloud
# Instead, use st.text_area with a copy button

# Function to format date
def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def format_folder_name(folder_name):
    return folder_name.replace("-", " ").title()

def load_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        st.error(f"Error reading file: {file_path}. Details: {e}")
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
                st.error(f"YAML error in {file_path}: {e}")
                return {'tags': []}, content
    return {'tags': []}, content

def extract_title_and_body(markdown_content, filename):
    lines = markdown_content.splitlines()
    title = filename
    body = markdown_content.strip()
    
    for line in lines:
        if line.strip().startswith('# '):
            title = line.strip('# ').strip()
            body = '\n'.join(lines[lines.index(line) + 1:]).strip()
            break
            
    return title, body

def generate_title_from_file(file_path, markdown_content):
    file_name = os.path.basename(file_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    title = file_name_no_ext.replace("-", " ").title()
    
    if markdown_content:
        title, _ = extract_title_and_body(markdown_content, title)
    
    return title

def build_sidebar_navigation(base_path, current_path, level=0):
    try:
        items = sorted(os.listdir(current_path))
        for item in items:
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                if level == 0:
                    st.sidebar.markdown(f"**{format_folder_name(item)}**")
                    build_sidebar_navigation(base_path, item_path, level + 1)
                else:
                    with st.sidebar.expander(format_folder_name(item), expanded=True):
                        build_sidebar_navigation(base_path, item_path, level + 1)
            elif item.endswith('.md'):
                front_matter, markdown_content = load_markdown(item_path)
                title = generate_title_from_file(item_path, markdown_content)
                vision = front_matter.get("vision", "")
                vision_icon = " 🔭" if str(vision).lower() == "yes" else ""
                
                if st.sidebar.button(f"{title}{vision_icon}", key=item_path, use_container_width=True):
                    st.session_state['selected_file'] = item_path
    except Exception as e:
        st.error(f"Error in navigation: {e}")

def main():
    st.set_page_config(page_title="AI Agent Configurations", layout="wide")

    # Initialize session state
    if 'selected_file' not in st.session_state:
        st.session_state['selected_file'] = None
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False

    # Sidebar
    st.sidebar.title("AI Agent Configurations")
    
    # Dark mode toggle
    st.sidebar.checkbox("Dark Mode", key="dark_mode")

    # Base path (modify this to your actual path)
    base_path = "agent-configs"  # or use absolute path

    # Build navigation
    if os.path.exists(base_path):
        build_sidebar_navigation(base_path, base_path)
    else:
        st.error(f"Directory not found: {base_path}")

    # Main content
    st.title("AI Assistant Library")

    if st.session_state['selected_file']:
        try:
            front_matter, markdown_content = load_markdown(st.session_state['selected_file'])
            title = generate_title_from_file(st.session_state['selected_file'], markdown_content)
            
            st.header(title)
            
            # Display tags
            if front_matter.get('tags'):
                st.markdown("**Tags:** " + ", ".join(f"`{tag}`" for tag in front_matter['tags']))
            
            # Display content
            st.markdown(markdown_content)
            
            # Add copy functionality using st.text_area
            st.text_area("Content (Click to copy)", markdown_content, height=100)
            
        except Exception as e:
            st.error(f"Error loading content: {e}")
    else:
        st.write("Select a configuration from the sidebar to view its details.")

if __name__ == "__main__":
    main()