"""
AI Teaching Agent - Interactive Learning Assistant
"""

import streamlit as st
from document_tree_builder import build_document_tree
import requests
import io
from pypdf import PdfReader
import time


def search_and_download_pdf(book_title):
    """Search for and download a PDF from open sources."""
    try:
        search_url = "https://archive.org/advancedsearch.php"
        params = {
            'q': f'title:({book_title}) AND mediatype:texts AND format:pdf',
            'fl[]': ['identifier', 'title'],
            'rows': 5,
            'page': 1,
            'output': 'json'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            if docs:
                for doc in docs:
                    identifier = doc.get('identifier')
                    title = doc.get('title', 'Unknown')
                    download_url = f"https://archive.org/download/{identifier}/{identifier}.pdf"
                    
                    pdf_response = requests.get(download_url, timeout=30)
                    if pdf_response.status_code == 200:
                        return pdf_response.content, title
    except Exception:
        pass
    
    return None, None


def load_pdf_from_file(uploaded_file):
    """Load PDF from uploaded file."""
    try:
        pdf_reader = PdfReader(uploaded_file)
        pdf_text_list = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            pdf_text_list.append({
                'page_number': page_num,
                'text': text
            })
        return pdf_text_list
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")


def load_pdf_from_book_name(book_name):
    """Load PDF by searching and downloading from the internet."""
    try:
        pdf_content, title = search_and_download_pdf(book_name)
        if pdf_content is None:
            raise Exception("Could not find or download the book from open sources.")
        
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PdfReader(pdf_file)
        
        pdf_text_list = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            pdf_text_list.append({
                'page_number': page_num,
                'text': text
            })
        return pdf_text_list, title
    except Exception as e:
        raise Exception(f"Error loading PDF: {str(e)}")


def add_message(role, content, metadata=None):
    """Add a message to the chat history."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append({
        'role': role,
        'content': content,
        'metadata': metadata,
        'timestamp': time.time()
    })


def render_section_content(section_data):
    """Render the content of a selected section."""
    st.markdown(f"### 📖 {section_data['header']}")
    st.caption(f"Page {section_data['page_number']}")
    st.divider()
    
    if section_data['content_chunks']:
        st.write("**Content:**")
        for i, chunk in enumerate(section_data['content_chunks'], 1):
            st.text_area(
                label=f"Chunk {i}",
                value=chunk,
                height=150,
                key=f"content_{hash(section_data['header'])}_{i}_{time.time()}",
                disabled=True
            )
    else:
        st.info("_This section serves as a container or header and has no direct text content._")


def toggle_node(node_id):
    """Toggle the expanded/collapsed state of a tree node."""
    if node_id in st.session_state.expanded_nodes:
        st.session_state.expanded_nodes.remove(node_id)
    else:
        st.session_state.expanded_nodes.add(node_id)


def recursive_tree_renderer(sections, level=0, path_prefix="root"):
    """
    Recursively renders the tree using indented buttons and custom state management.
    Replacing 'st.expander' to avoid nesting errors.
    """
    # Define indentation spacing (Em Spaces to prevent trimming)
    indent_unit = "  " 
    current_indent = indent_unit * level

    for idx, section in enumerate(sections):
        # Create a unique ID for this specific node position
        node_id = f"{path_prefix}.{idx}"
        
        has_children = len(section.get('subsections', [])) > 0
        
        if has_children:
            # Check if currently expanded
            is_expanded = node_id in st.session_state.expanded_nodes
            
            # Icons
            state_icon = "▼" if is_expanded else "▶"
            type_icon = "📂" if section.get('is_wrapper') else "📑"
            
            # Label
            label = f"{current_indent}{state_icon} {type_icon} {section['header']} (Pg. {section['page_number']})"
            
            # Parent Node Button (Toggles expansion)
            if st.button(label, key=f"btn_node_{node_id}", use_container_width=True):
                toggle_node(node_id)
                st.rerun()
            
            # If expanded, render children
            if is_expanded:
                # OPTIONAL: If the parent node ITSELF has content, show a "View This Section" button
                if section.get('content_chunks'):
                    content_indent = current_indent + indent_unit
                    content_label = f"{content_indent}📄 View Content: {section['header']}"
                    
                    if st.button(content_label, key=f"btn_view_{node_id}", use_container_width=True):
                        st.session_state.selected_section = section
                        add_message('user', f"Show me: {section['header']}")
                        add_message('assistant', f"Here's the content for **{section['header']}**:", metadata='section_content')
                        st.rerun()
                
                # Render children recursively
                recursive_tree_renderer(section['subsections'], level + 1, path_prefix=node_id)
        
        else:
            # Leaf Node (No children)
            label = f"{current_indent}📄 {section['header']} (Pg. {section['page_number']})"
            
            if st.button(label, key=f"btn_leaf_{node_id}", use_container_width=True):
                st.session_state.selected_section = section
                add_message('user', f"Show me: {section['header']}")
                add_message('assistant', f"Here's the content for **{section['header']}**:", metadata='section_content')
                st.rerun()


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        add_message('assistant', 
                   "👋 Hello! I'm your AI Teaching Agent.\n\n"
                   "📚 **Load a document** - Upload PDF or search for a book\n"
                   "🔍 **Navigate structure** - Browse the interactive tree\n\n"
                   "How would you like to start?")
    
    if 'document_loaded' not in st.session_state:
        st.session_state.document_loaded = False
        st.session_state.document_tree = None
    
    if 'awaiting_input' not in st.session_state:
        st.session_state.awaiting_input = None
    
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
        
    # NEW: Track expanded nodes for the custom tree view
    if 'expanded_nodes' not in st.session_state:
        st.session_state.expanded_nodes = set()


def process_user_message(user_input):
    """Process user messages."""
    user_input_lower = user_input.lower()
    
    if any(k in user_input_lower for k in ['load', 'upload', 'document', 'book']):
        st.session_state.awaiting_input = 'document_load'
        return "Great! You can upload a PDF in the sidebar or tell me a book title here."
    
    elif st.session_state.awaiting_input == 'document_load' and not st.session_state.document_loaded:
        return f"Searching for '{user_input}'..."
    
    elif st.session_state.document_loaded and any(k in user_input_lower for k in ['structure', 'sections', 'outline', 'show', 'navigate']):
        return "navigation_view"
    
    elif 'help' in user_input_lower:
        return "I can help you explore documents! Try saying 'Load a document' or 'Show structure'."
    
    else:
        if not st.session_state.document_loaded:
            return "Please load a document first (Say 'load document')."
        return "You can ask me to navigate the structure or show specific sections."


def main():
    st.set_page_config(page_title="AI Teaching Agent", page_icon="🎓", layout="wide")
    
    # Custom CSS to align text left in buttons (looks more like a tree)
    st.markdown("""
        <style>
        .stButton>button { 
            text-align: left; 
            border: none;
            background-color: transparent;
        }
        .stButton>button:hover {
            border: 1px solid #ccc;
        }
        </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🎓 Teaching Agent")
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="pdf_uploader")
        
        if uploaded_file and not st.session_state.document_loaded:
            with st.spinner("Processing tree structure..."):
                try:
                    pdf_text_list = load_pdf_from_file(uploaded_file)
                    # Pass the PDF text to builder
                    document_tree = build_document_tree(pdf_text_list)
                    
                    st.session_state.document_tree = document_tree
                    st.session_state.document_loaded = True
                    st.session_state.awaiting_input = None
                    
                    add_message('assistant', f"✅ Loaded '{uploaded_file.name}'! Ask me to show the structure.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if st.session_state.document_loaded:
            st.success("✅ Document Active")
            if st.button("🔄 Reset"):
                st.session_state.document_loaded = False
                st.session_state.document_tree = None
                st.session_state.expanded_nodes = set()
                st.rerun()

    # Main Chat
    st.title("🤖 AI Teaching Agent")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.write(message['content'])
                
                # Navigation View
                if message.get('metadata') == 'navigation_view' and st.session_state.document_tree:
                    st.markdown("---")
                    st.markdown("### 🗂️ Document Structure")
                    st.caption("Click arrow buttons (▶) to expand sections. Click items to read.")
                    
                    tree = st.session_state.document_tree
                    sections = tree.get('sections', [])
                    
                    if sections:
                        # Call the custom recursive renderer
                        recursive_tree_renderer(sections)
                    else:
                        st.warning("No sections detected.")
                
                # Section Content View
                elif message.get('metadata') == 'section_content' and st.session_state.selected_section:
                    render_section_content(st.session_state.selected_section)
                    st.session_state.selected_section = None

    # Input Area
    if prompt := st.chat_input("Type message..."):
        add_message('user', prompt)
        with st.chat_message('user'):
            st.write(prompt)
            
        # Logic
        if st.session_state.awaiting_input == 'document_load' and not st.session_state.document_loaded:
            # Book search logic
            with st.chat_message('assistant'):
                with st.spinner(f"Downloading '{prompt}'..."):
                    try:
                        pdf_text, title = load_pdf_from_book_name(prompt)
                        tree = build_document_tree(pdf_text)
                        st.session_state.document_tree = tree
                        st.session_state.document_loaded = True
                        st.session_state.awaiting_input = None
                        
                        msg = f"✅ Downloaded '{title}'! Ask to show structure."
                        add_message('assistant', msg)
                        st.write(msg)
                        st.rerun()
                    except Exception as e:
                        st.error("Could not download book.")
        else:
            response = process_user_message(prompt)
            with st.chat_message('assistant'):
                if response == "navigation_view":
                    st.write("Here is the document structure:")
                    add_message('assistant', "Here is the document structure:", metadata='navigation_view')
                    st.rerun()
                else:
                    st.write(response)
                    add_message('assistant', response)

if __name__ == "__main__":
    main()