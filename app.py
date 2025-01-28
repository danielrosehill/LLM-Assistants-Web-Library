import os
import streamlit as st
import pyperclip

# Function to convert folder names to readable format
def format_folder_name(folder_name):
    return folder_name.replace("-", " ").title()

# Function to load markdown files and extract the first header as the title
def load_markdown_title(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('# '):
                return line.strip('# ').strip()
    return os.path.basename(file_path).replace(".md", "").replace("-", " ").title()

# Function to load markdown content
def load_markdown_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to recursively build the sidebar navigation
def build_sidebar_navigation(base_path, current_path):
    items = os.listdir(current_path)
    for item in sorted(items):
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            with st.sidebar.expander(format_folder_name(item)):
                build_sidebar_navigation(base_path, item_path)
        elif item.endswith('.md'):
            title = load_markdown_title(item_path)
            if st.sidebar.button(title, key=item_path):
                st.session_state['selected_file'] = item_path

# Function to search for configurations
def search_configurations(base_path, search_term):
    matches = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                content = load_markdown_content(file_path)
                if search_term.lower() in content.lower():
                    matches.append((file_path, load_markdown_title(file_path)))
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
    if st.session_state['selected_file']:
        st.title(load_markdown_title(st.session_state['selected_file']))
        content = load_markdown_content(st.session_state['selected_file'])
        st.markdown(content, unsafe_allow_html=True)
        if st.button("Copy to Clipboard"):
            pyperclip.copy(content)
            st.success("Configuration copied to clipboard!")
    else:
        st.write("Select a configuration from the sidebar to view its details.")

if __name__ == "__main__":
    main()