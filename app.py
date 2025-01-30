import os
import streamlit as st
from datetime import datetime
import yaml

# Function to format date
def format_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Function to format folder names
def format_folder_name(folder_name):
    return folder_name.replace("-", " ").title()

# Function to load markdown files
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

# Function to extract title and body
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

# Function to generate title from file
def generate_title_from_file(file_path, markdown_content):
    file_name = os.path.basename(file_path)
    file_name_no_ext = os.path.splitext(file_name)[0]
    title = file_name_no_ext.replace("-", " ").title()
    
    if markdown_content:
        title, _ = extract_title_and_body(markdown_content, title)
    
    return title

# Function to build sidebar navigation
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

# Custom CSS for better UI
def local_css():
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .info-box {
            background-color: #f8f9fa;
            border-left: 5px solid #0066cc;
            padding: 1.2rem;
            border-radius: 5px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tag-box {
            padding: 0.2rem 0.6rem;
            background-color: #e9ecef;
            border-radius: 15px;
            margin-right: 0.5rem;
            font-size: 0.9rem;
        }
        .metadata {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .copy-button {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .copy-button:hover {
            background-color: #e9ecef;
            border-color: #adb5bd;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 1rem;
            text-align: center;
            border-top: 1px solid #dee2e6;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            border: 1px solid #dee2e6;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="AI Agent Configurations",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    local_css()

    # Initialize session state
    if 'selected_file' not in st.session_state:
        st.session_state['selected_file'] = None
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False

    # Sidebar
    with st.sidebar:
        st.title("🤖 AI Agent Configurations")
        
        st.markdown("""
            <div style="margin: 1rem 0;">
                <a href="https://github.com/danielrosehill/LLM-Assistants-Web-Library" target="_blank">
                    <img src="https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="View on GitHub">
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        # Dark mode toggle with custom styling
        st.markdown("### 🎨 Theme")
        st.checkbox("Dark Mode", key="dark_mode")
        
        st.markdown("### 📁 Configurations")

    # Base path
    base_path = "agent-configs"

    # Build navigation
    if os.path.exists(base_path):
        build_sidebar_navigation(base_path, base_path)
    else:
        st.error("⚠️ Configuration directory not found!")

    # Main content
    st.markdown('<h1 class="main-header">AI Assistant Library</h1>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="info-box">
            <h3 style="margin-top: 0;">Welcome to the AI Assistant Library</h3>
            <p>This microsite contains open source configurations for AI assistants.</p>
            <p>All configurations by: <a href="https://danielrosehill.com" target="_blank">Daniel Rosehill</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state['selected_file']:
        try:
            front_matter, markdown_content = load_markdown(st.session_state['selected_file'])
            title, body = extract_title_and_body(markdown_content, "")
            
            # Metadata section
            st.markdown('<div class="metadata">', unsafe_allow_html=True)
            
            # Tags with custom styling
            if front_matter.get('tags'):
                st.markdown("**🏷️ Tags:**")
                tags_html = " ".join([f'<span class="tag-box">{tag}</span>' for tag in front_matter['tags']])
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Last modified date
            last_modified = os.path.getmtime(st.session_state['selected_file'])
            st.markdown(f"**🕒 Last Modified:** {format_date(last_modified)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy buttons with improved layout
            col1, col2, col3 = st.columns([2, 2, 8])
            
            with col1:
                if st.button("📋 Copy Title", help="Copy title to clipboard", key="copy_title"):
                    st.code(title, language=None)
                    st.success("Title copied!")
                    
            with col2:
                if st.button("📄 Copy Config", help="Copy configuration to clipboard", key="copy_config"):
                    st.code(body, language=None)
                    st.success("Configuration copied!")

            st.divider()
            
            # Display content with better formatting
            st.markdown(
                f'<div style="background-color: white; padding: 2rem; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{markdown_content}</div>',
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"Error loading content: {e}")
    else:
        st.info("👈 Select a configuration from the sidebar to view its details.")

    # Footer
    st.markdown(
        """
        <div class="footer">
            <a href="https://github.com/danielrosehill/LLM-Assistants-Web-Library" target="_blank">
                <img src="https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="View on GitHub">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()