import os
import streamlit as st
import pyperclip
import yaml
from datetime import datetime

# Function to format date
def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Function to convert folder names to readable format
def format_folder_name(folder_name):
    return folder_name.replace("-", " ").title()

# Function to load markdown files and extract YAML front matter and content
def load_markdown(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        st.error(f"Error reading file: {file_path}. Details: {e}")
        return {'tags': []}, ""  # Return empty content and tags on error
    
    # Check for YAML front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            markdown_content = parts[2].strip()
            try:
                front_matter = yaml.safe_load(yaml_content)
                # Ensure tags is a list
                if 'tags' in front_matter:
                    if isinstance(front_matter['tags'], str):
                        front_matter['tags'] = [tag.strip() for tag in front_matter['tags'].split(',')]
                else:
                    front_matter['tags'] = []
                return front_matter, markdown_content
            except yaml.YAMLError as e:
                st.error(f"YAML error in {file_path}: {e}. YAML content: {yaml_content}")
                return {'tags': []}, content
    return {'tags': []}, content

# Function to extract the first header from markdown content
def extract_title_and_body(markdown_content, filename):
    title = filename
    body = markdown_content.strip()
    
    for line in markdown_content.splitlines():
        if line.strip().startswith('# '):
            title = line.strip('# ').strip()
            body = markdown_content[markdown_content.find(line) + len(line):].strip()
            break
        
    return title, body

# Function to generate a title from a file path
def generate_title_from_file(file_path, markdown_content):
        file_name = os.path.basename(file_path)
        file_name_no_ext, _ = os.path.splitext(file_name)
        title = file_name_no_ext.replace("-", " ").title()

        # only attempt H1 if there is content
        if markdown_content:
          title, _ = extract_title_and_body(markdown_content, title)
        
        return title

# Function to recursively build the sidebar navigation
def build_sidebar_navigation(base_path, current_path, level=0):
    items = sorted(os.listdir(current_path)) # sort here
    for item in items:
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            if level == 0: # Top-level directories (no expander)
                st.sidebar.markdown(f"**{format_folder_name(item)}**")
                build_sidebar_navigation(base_path, item_path, level + 1) # Use recursion for nested subfolders
            else: # subdirectories
                 with st.sidebar.expander(format_folder_name(item), expanded=True):
                   build_sidebar_navigation(base_path, item_path, level + 1)
        elif item.endswith('.md'):
            front_matter, markdown_content = load_markdown(item_path)
            title = generate_title_from_file(item_path, markdown_content)
            # Add binoculars icon if vision is enabled
            vision = front_matter.get("vision", "")
            vision_icon = " 🔭" if str(vision).lower() == "yes" else ""
            with st.sidebar.container():
               if st.sidebar.button(f"{title}{vision_icon}", key=item_path, use_container_width=True):
                  st.session_state['selected_file'] = item_path

# Function to search for configurations
def search_configurations(base_path, search_term, selected_tags=None):
    matches = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                front_matter, markdown_content = load_markdown(file_path)
                title = generate_title_from_file(file_path, markdown_content)
                
                # Check if content matches search term and tags
                content_matches = search_term.lower() in markdown_content.lower()
                tags_match = True
                if selected_tags:
                    tags_match = any(tag in front_matter.get('tags', []) for tag in selected_tags)
                
                if content_matches and tags_match:
                    matches.append((file_path, title, front_matter.get('tags', [])))
    return matches

# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title="AI Agent Configurations", layout="wide")

    # Define the base path for agent configurations
    base_path = "agent-configs"

    # Initialize session state
    if 'selected_file' not in st.session_state:
        st.session_state['selected_file'] = None
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False
    if 'favorites' not in st.session_state:
        st.session_state['favorites'] = set()

    # Apply dark mode if enabled
    if st.session_state['dark_mode']:
        st.markdown("""
            <style>
            .stApp {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            .sidebar .sidebar-content {
                background-color: #2D2D2D;
            }
            </style>
            """, unsafe_allow_html=True)

    # Sidebar for navigation and search
    st.sidebar.title("AI Agent Configurations")
    
    # Dark mode toggle
    st.sidebar.checkbox("Dark Mode", key="dark_mode", value=st.session_state['dark_mode'])
    
    # GitHub repository badge in sidebar
    st.sidebar.markdown(
        "[![View on GitHub](https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danielrosehill/LLM-Assistants-Web-Library)",
        unsafe_allow_html=True
    )
    
    # Collect all configurations and their metadata
    all_configs = []
    all_tags = set()
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                front_matter, markdown_content = load_markdown(file_path)
                title = generate_title_from_file(file_path, markdown_content)
                last_modified = os.path.getmtime(file_path)
                all_configs.append({
                    'path': file_path,
                    'title': title,
                    'tags': front_matter.get('tags', []),
                    'last_modified': last_modified
                })
                all_tags.update(front_matter.get('tags', []))
    
    # Sorting options
    sort_options = {
        'Title (A-Z)': lambda x: x['title'].lower(),
        'Title (Z-A)': lambda x: x['title'].lower(),
        'Last Modified (Newest)': lambda x: x['last_modified'],
        'Last Modified (Oldest)': lambda x: x['last_modified']
    }
    sort_by = st.sidebar.selectbox('Sort by', list(sort_options.keys()))
    
    # Sort configurations
    all_configs.sort(key=sort_options[sort_by])
    if sort_by == 'Title (Z-A)' or sort_by == 'Last Modified (Newest)':
        all_configs.reverse()
    
    # Search and filter functionality
    search_term = st.sidebar.text_input("Search configurations")
    selected_tags = st.sidebar.multiselect("Filter by tags", sorted(list(all_tags)))
    
    # Show favorites section if there are any
    if st.session_state['favorites']:
        st.sidebar.markdown("### Favorites")
        for file_path in st.session_state['favorites']:
            front_matter, markdown_content = load_markdown(file_path)
            title = generate_title_from_file(file_path, markdown_content)
            with st.sidebar.container():
               if st.sidebar.button(f"⭐ {title}", key=f"fav_{file_path}", use_container_width=True):
                    st.session_state['selected_file'] = file_path
        st.sidebar.divider()
    
    if search_term or selected_tags:
        matches = search_configurations(base_path, search_term, selected_tags)
        if matches:
            st.sidebar.write("Search Results:")
            for file_path, title, tags in matches:
                with st.sidebar.container():
                   if st.sidebar.button(f"{title} ({', '.join(tags)})", key=f"search_{file_path}", use_container_width=True):
                      st.session_state['selected_file'] = file_path
        else:
            st.sidebar.write("No matches found.")
    else:
        # Build the sidebar navigation
        build_sidebar_navigation(base_path, base_path)

    # Main content area
    st.title("Daniel Rosehill AI Assistant Library")
    st.markdown(
        """
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin: 0;">This microsite contains open source configurations for AI assistants.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state['selected_file']:
        front_matter, markdown_content = load_markdown(st.session_state['selected_file'])
        title, body = extract_title_and_body(markdown_content, title)
        
        # Display title and metadata
        st.markdown(f"# {title}")
        
        # Display tags if present
        if front_matter.get('tags'):
            st.markdown("**Tags:** " + ", ".join(f"`{tag}`" for tag in front_matter['tags']))
        
        # Display last modified date
        last_modified = os.path.getmtime(st.session_state['selected_file'])
        st.markdown(f"**Last Modified:** {format_date(last_modified)}")
        
        # Create a container for buttons
        with st.container():
            st.write("Options:")
            button_col1, button_col2, button_col3, button_col4, _ = st.columns([2, 2, 2, 2, 4])
            
            with button_col1:
                if st.button("📋 Copy Title", 
                           key="copy_title",
                           help="Copy title to clipboard",
                           type="secondary"):
                    pyperclip.copy(title)
                    st.success("Title copied!")
            
            with button_col2:
                if st.button("📄 Copy Content", 
                           key="copy_body",
                           help="Copy full content to clipboard",
                           type="secondary"):
                    pyperclip.copy(body)
                    st.success("Content copied!")
            
            with button_col3:
                is_favorite = st.session_state['selected_file'] in st.session_state['favorites']
                if st.button("⭐ " + ("Unfavorite" if is_favorite else "Favorite"),
                           key="toggle_favorite",
                           help="Add/remove from favorites",
                           type="secondary"):
                    if is_favorite:
                        st.session_state['favorites'].remove(st.session_state['selected_file'])
                    else:
                        st.session_state['favorites'].add(st.session_state['selected_file'])
            
            with button_col4:
                if st.button("🔗 Share",
                           key="share_config",
                           help="Copy shareable link",
                           type="secondary"):
                    share_url = f"https://github.com/danielrosehill/LLM-Assistants-Web-Library/blob/main/{st.session_state['selected_file']}"
                    pyperclip.copy(share_url)
                    st.success("Share link copied!")
        
        st.divider()
        
        # Display markdown content
        st.markdown(body, unsafe_allow_html=True)
    else:
        st.write("Select a configuration from the sidebar to view its details.")
    
    # Footer with GitHub badge
    st.markdown(
        """
        <div style="position: fixed; bottom: 0; width: 100%; background-color: #f0f0f0; padding: 10px; text-align: center;">
            <a href="https://github.com/danielrosehill/LLM-Assistants-Web-Library" target="_blank">
                <img src="https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="View on GitHub">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()