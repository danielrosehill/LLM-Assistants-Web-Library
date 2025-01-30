import os
import streamlit as st
from datetime import datetime
import yaml

# [Previous helper functions remain the same until main()]

def main():
    st.set_page_config(page_title="AI Agent Configurations", layout="wide")

    # Initialize session state
    if 'selected_file' not in st.session_state:
        st.session_state['selected_file'] = None
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False

    # Sidebar
    st.sidebar.title("AI Agent Configurations")
    
    # GitHub repository link in sidebar
    st.sidebar.markdown(
        "[![View on GitHub](https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danielrosehill/LLM-Assistants-Web-Library)",
        unsafe_allow_html=True
    )
    
    # Dark mode toggle
    st.sidebar.checkbox("Dark Mode", key="dark_mode")

    # Base path
    base_path = "agent-configs"

    # Build navigation
    if os.path.exists(base_path):
        build_sidebar_navigation(base_path, base_path)
    else:
        st.error(f"Directory not found: {base_path}")

    # Main content
    st.title("AI Assistant Library")
    st.markdown(
        """
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin: 0;">This microsite contains open source configurations for AI assistants.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state['selected_file']:
        try:
            front_matter, markdown_content = load_markdown(st.session_state['selected_file'])
            title, body = extract_title_and_body(markdown_content, "")
            
            # Display tags if present
            if front_matter.get('tags'):
                st.markdown("**Tags:** " + ", ".join(f"`{tag}`" for tag in front_matter['tags']))
            
            # Last modified date
            last_modified = os.path.getmtime(st.session_state['selected_file'])
            st.markdown(f"**Last Modified:** {format_date(last_modified)}")
            
            # Copy buttons in columns
            col1, col2, col3, col4 = st.columns([2, 2, 2, 6])
            
            with col1:
                if st.button("📋 Copy Title", help="Copy title to clipboard"):
                    st.code(title, language=None)
                    
            with col2:
                if st.button("📄 Copy Config", help="Copy configuration to clipboard"):
                    st.code(body, language=None)

            st.divider()
            
            # Display content
            st.markdown(markdown_content)
            
        except Exception as e:
            st.error(f"Error loading content: {e}")
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