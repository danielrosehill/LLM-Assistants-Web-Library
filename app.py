import os
import streamlit as st
import pyperclip
import yaml

# Function to convert folder names to readable format
def format_folder_name(folder_name):
    return folder_name.replace("-", " ").title()

# Function to load markdown files and extract YAML front matter and content
def load_markdown(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Check for YAML front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            markdown_content = parts[2].strip()
            try:
                front_matter = yaml.safe_load(yaml_content)
                return front_matter, markdown_content
            except yaml.YAMLError:
                return {}, content
    return {}, content

# Function to extract the first header from markdown content
def extract_title_and_body(markdown_content):
    lines = markdown_content.split('\n')
    title = "Untitled Configuration"
    body = markdown_content
    
    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line.strip('# ').strip()
            body = '\n'.join(lines[i+1:]).strip()
            break
    
    return title, body

# Function to recursively build the sidebar navigation
def build_sidebar_navigation(base_path, current_path):
    items = os.listdir(current_path)
    for item in sorted(items):
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            with st.sidebar.expander(format_folder_name(item)):
                build_sidebar_navigation(base_path, item_path)
        elif item.endswith('.md'):
            front_matter, markdown_content = load_markdown(item_path)
            title, _ = extract_title_and_body(markdown_content)
            # Add binoculars icon if vision is enabled
            vision = front_matter.get("vision", "")
            vision_icon = " 🔭" if str(vision).lower() == "yes" else ""
            if st.sidebar.button(f"{title}{vision_icon}", key=item_path):
                st.session_state['selected_file'] = item_path

# Function to search for configurations
def search_configurations(base_path, search_term):
    matches = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                _, markdown_content = load_markdown(file_path)
                title, body = extract_title_and_body(markdown_content)
                if search_term.lower() in markdown_content.lower():
                    matches.append((file_path, title))
    return matches

# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title="AI Agent Configurations", layout="wide")

    # Define the base path for agent configurations
    base_path = "agent-configs"

    # Initialize session state for selected file
    if 'selected_file' not in st.session_state:
        st.session_state['selected_file'] = None

    # Sidebar for navigation and search
    st.sidebar.title("AI Agent Configurations")
    
    # GitHub repository badge in sidebar
    st.sidebar.markdown(
        "[![View on GitHub](https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danielrosehill/LLM-Assistants-Web-Library)",
        unsafe_allow_html=True
    )
    
    # Search functionality
    search_term = st.sidebar.text_input("Search configurations")
    if search_term:
        matches = search_configurations(base_path, search_term)
        if matches:
            st.sidebar.write("Search Results:")
            for file_path, title in matches:
                if st.sidebar.button(title, key=f"search_{file_path}"):
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
        title, body = extract_title_and_body(markdown_content)
        
        # Display title
        st.markdown(f"# {title}")
        
        # Create a container for copy buttons
        with st.container():
            st.write("Copy options:")
            button_col1, button_col2, _ = st.columns([2, 2, 8])
            
            with button_col1:
                if st.button("📋  Copy Title", 
                           key="copy_title",
                           help="Copy title to clipboard",
                           type="secondary"):
                    pyperclip.copy(title)
                    st.success("Title copied!")
            
            with button_col2:
                if st.button("📄  Copy Content", 
                           key="copy_body",
                           help="Copy full content to clipboard",
                           type="secondary"):
                    pyperclip.copy(body)
                    st.success("Content copied!")
        
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
