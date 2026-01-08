"""
UNIFIED ADAPTIVE LEARNING PLATFORM
Combines:
- Document navigation and tree structure
- GPU-accelerated AI tutoring
- Adaptive learning strategies
- Student profiling and tracking
- Image generation for visual learning
- Memory optimization
"""

import streamlit as st

st.set_page_config(
    page_title="Unified Adaptive Learning Platform",
    page_icon="🧠",
    layout="wide"
)

from document_tree_builder import build_document_tree
from student_database import StudentDatabase
from adaptive_engine import AdaptiveEngine
from image_engine import ImageGenerator
import requests
import io
from pypdf import PdfReader
import time
import os
import tempfile
import gc
import psutil
import warnings

# Silence warnings
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configuration
DEFAULT_MODEL_PATH = "F:\\hacktide hackathon"
INACTIVITY_TIMEOUT = 300  # 5 minutes
MAX_CHAT_HISTORY = 10
MEMORY_THRESHOLD_MB = 6000


def get_memory_usage():
    """Get current RAM usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def cleanup_memory():
    """Aggressive memory cleanup."""
    gc.collect()


def check_and_cleanup_memory():
    """Check memory and auto-cleanup if needed."""
    memory_mb = get_memory_usage()
    
    if memory_mb > MEMORY_THRESHOLD_MB:
        if st.session_state.get('tutor') is not None:
            st.session_state.tutor = None
            cleanup_memory()
            st.warning(f"⚠️ AI unloaded (RAM: {memory_mb:.0f}MB → Freeing memory)")
            time.sleep(1)
            return True
    return False


def check_inactivity():
    """Auto-unload AI after inactivity."""
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = time.time()
        return False
    
    current_time = time.time()
    inactive_duration = current_time - st.session_state.last_activity
    
    if inactive_duration > INACTIVITY_TIMEOUT and st.session_state.get('tutor') is not None:
        st.session_state.tutor = None
        cleanup_memory()
        st.info(f"⏰ AI unloaded after {int(inactive_duration/60)} min inactivity")
        return True
    return False


def update_activity():
    """Update last activity timestamp."""
    st.session_state.last_activity = time.time()


def trim_chat_history():
    """Keep only last N messages to save RAM."""
    if 'messages' in st.session_state and len(st.session_state.messages) > MAX_CHAT_HISTORY:
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-MAX_CHAT_HISTORY:]


def search_and_download_pdf(book_title):
    """Search and download PDF from open sources."""
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
        raise Exception(f"Error reading PDF: {str(e)}")


def load_pdf_from_book_name(book_name):
    """Load PDF by downloading from internet."""
    try:
        pdf_content, title = search_and_download_pdf(book_name)
        if pdf_content is None:
            raise Exception("Could not find book in open sources.")
        
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


def save_pdf_temporarily(uploaded_file):
    """Save uploaded PDF to temp file for RAG engine."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.write(uploaded_file.getvalue())
    temp_file.close()
    return temp_file.name


def add_message(role, content, metadata=None, msg_type="text", caption=None):
    """Add message to chat history."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append({
        'role': role,
        'content': content,
        'metadata': metadata,
        'type': msg_type,
        'caption': caption,
        'timestamp': time.time()
    })
    
    trim_chat_history()


def send_prompt(prompt_text):
    """Helper function to send a prompt programmatically."""
    st.session_state.pending_prompt = prompt_text
    update_activity()


def toggle_node(node_id):
    """Toggle tree node expansion."""
    if node_id in st.session_state.expanded_nodes:
        st.session_state.expanded_nodes.remove(node_id)
    else:
        st.session_state.expanded_nodes.add(node_id)
    update_activity()


def recursive_tree_renderer(sections, level=0, path_prefix="root"):
    """Recursively render document tree."""
    indent_unit = "　　"
    current_indent = indent_unit * level

    for idx, section in enumerate(sections):
        node_id = f"{path_prefix}.{idx}"
        has_children = len(section.get('subsections', [])) > 0
        
        if has_children:
            is_expanded = node_id in st.session_state.expanded_nodes
            state_icon = "▼" if is_expanded else "▶"
            type_icon = "📂" if section.get('is_wrapper') else "📕"
            label = f"{current_indent}{state_icon} {type_icon} {section['header']} (Pg. {section['page_number']})"
            
            if st.button(label, key=f"btn_node_{node_id}", use_container_width=True):
                toggle_node(node_id)
                st.rerun()
            
            if is_expanded:
                if section.get('content_chunks'):
                    content_indent = current_indent + indent_unit
                    content_label = f"{content_indent}📄 View: {section['header']}"
                    
                    if st.button(content_label, key=f"btn_view_{node_id}", use_container_width=True):
                        st.session_state.selected_section = section
                        add_message('user', f"Show me: {section['header']}")
                        add_message('assistant', f"Here's **{section['header']}**:", metadata='section_content')
                        update_activity()
                        st.rerun()
                
                recursive_tree_renderer(section['subsections'], level + 1, path_prefix=node_id)
        else:
            label = f"{current_indent}📄 {section['header']} (Pg. {section['page_number']})"
            
            if st.button(label, key=f"btn_leaf_{node_id}", use_container_width=True):
                st.session_state.selected_section = section
                add_message('user', f"Show me: {section['header']}")
                add_message('assistant', f"Here's **{section['header']}**:", metadata='section_content')
                update_activity()
                st.rerun()


def render_section_content(section_data):
    """Render section content."""
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
        st.info("_This section serves as a container._")


def initialize_session_state():
    """Initialize session state."""
    if 'db' not in st.session_state:
        st.session_state.db = StudentDatabase()
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        add_message('assistant', 
                   "🧠 Welcome to the Unified Adaptive Learning Platform!\n\n"
                   "**Features:**\n"
                   "📚 Document navigation with tree structure\n"
                   "🎯 Adaptive learning tailored to your level\n"
                   "🎮 GPU-accelerated AI tutoring\n"
                   "🎨 Visual learning with generated images\n\n"
                   "Get started by selecting your profile and uploading a document!")
    
    if 'document_loaded' not in st.session_state:
        st.session_state.document_loaded = False
        st.session_state.document_tree = None
    
    if 'awaiting_input' not in st.session_state:
        st.session_state.awaiting_input = None
    
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    
    if 'expanded_nodes' not in st.session_state:
        st.session_state.expanded_nodes = set()
    
    if 'tutor' not in st.session_state:
        st.session_state.tutor = None
    
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    
    if 'pending_prompt' not in st.session_state:
        st.session_state.pending_prompt = None
    
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = time.time()
    
    if 'hf_token' not in st.session_state:
        st.session_state.hf_token = None


def initialize_ai_tutor(model_path):
    """Initialize AI tutor with GPU support."""
    try:
        import torch
        
        gpu_available = torch.cuda.is_available()
        
        if gpu_available:
            vram_free = torch.cuda.get_device_properties(0).total_memory / 1024**3
            st.info(f"🎮 GPU detected! {vram_free:.1f}GB VRAM available")
        else:
            st.warning("⚠️ GPU not detected. Using CPU (slower)")
        
        memory_before = get_memory_usage()
        
        if memory_before > 5000 and not gpu_available:
            return False, f"RAM too high ({memory_before:.0f}MB). Close other apps or enable GPU."
        
        with st.spinner("🤖 Loading AI..." if gpu_available else "🤖 Loading AI on CPU..."):
            from adaptive_chat import AdaptiveTutor
            st.session_state.tutor = AdaptiveTutor(model_path=model_path, use_gpu=True)
        
        if gpu_available:
            vram_used = torch.cuda.memory_allocated() / 1024**3
            return True, f"✅ AI loaded on GPU! Using {vram_used:.1f}GB VRAM"
        else:
            memory_after = get_memory_usage()
            memory_used = memory_after - memory_before
            return True, f"✅ AI loaded on CPU! Using {memory_used:.0f}MB RAM"
            
    except Exception as e:
        cleanup_memory()
        return False, f"Error: {str(e)}"


def main():
    
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
    check_inactivity()
    check_and_cleanup_memory()
    
    # Sidebar
    with st.sidebar:
        st.title("🧠 Adaptive Learning")
        st.caption("v3.0 | Unified Platform")
        
        # Memory Monitor
        memory_mb = get_memory_usage()
        memory_color = "🟢" if memory_mb < 3000 else "🟡" if memory_mb < 5000 else "🔴"
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{memory_color} RAM", f"{memory_mb:.0f} MB")
        with col2:
            try:
                import torch
                if torch.cuda.is_available():
                    vram_used = torch.cuda.memory_allocated() / 1024**2
                    vram_color = "🟢" if vram_used < 2000 else "🟡" if vram_used < 3500 else "🔴"
                    st.metric(f"{vram_color} VRAM", f"{vram_used:.0f} MB")
                else:
                    st.metric("🔴 GPU", "N/A")
            except:
                st.metric("GPU", "N/A")
        
        st.divider()
        
        # Student Profile Selection
        st.subheader("👤 Student Profile")
        names = ["Select Profile..."] + [s['name'] for s in st.session_state.db.get_student_list()]
        
        default_index = 0
        if st.session_state.user_profile:
            current_name = st.session_state.user_profile['name']
            if current_name in names:
                default_index = names.index(current_name)
        
        selected_user = st.selectbox("Active Profile", names, index=default_index)
        
        if selected_user != "Select Profile...":
            sid, data = st.session_state.db.get_student_by_name(selected_user)
            st.session_state.user_profile = data
            st.session_state.user_id = sid
            st.success(f"✅ {data['name']}")
            st.progress(data['mastery'] / 100)
            st.caption(f"Mastery: {data['mastery']}%")
        
        st.divider()
        
        # Model Configuration
        st.subheader("🤖 AI Model")
        st.caption("🎮 GPU Accelerated")
        
        model_path = st.text_input(
            "Model Directory",
            value=DEFAULT_MODEL_PATH,
            help="Folder containing GGUF models"
        )
        
        if st.session_state.tutor is None:
            if st.button("🚀 Load AI Model", use_container_width=True):
                success, message = initialize_ai_tutor(model_path)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.success("✅ AI Active")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ Unload", use_container_width=True):
                    st.session_state.tutor = None
                    cleanup_memory()
                    st.success("Unloaded!")
                    st.rerun()
            with col_b:
                try:
                    import torch
                    device = "🎮 GPU" if torch.cuda.is_available() and st.session_state.tutor else "💻 CPU"
                    st.caption(device)
                except:
                    pass
        
        st.divider()
        
        # Document Upload
        st.subheader("📄 Knowledge Base")
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="pdf_uploader")
        
        if uploaded_file and not st.session_state.document_loaded:
            with st.spinner("📖 Processing..."):
                try:
                    pdf_text_list = load_pdf_from_file(uploaded_file)
                    document_tree = build_document_tree(pdf_text_list)
                    
                    st.session_state.document_tree = document_tree
                    st.session_state.document_loaded = True
                    st.session_state.awaiting_input = None
                    
                    # Create RAG engine
                    temp_path = save_pdf_temporarily(uploaded_file)
                    from rag_engine import RAGEngine
                    st.session_state.rag_engine = RAGEngine(temp_path)
                    
                    add_message('assistant', f"✅ Loaded '{uploaded_file.name}'!")
                    cleanup_memory()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if st.session_state.document_loaded:
            st.success("✅ Document Active")
            if st.button("🔄 New Document", use_container_width=True):
                st.session_state.document_loaded = False
                st.session_state.document_tree = None
                st.session_state.rag_engine = None
                st.session_state.expanded_nodes = set()
                cleanup_memory()
                st.rerun()
        
        st.divider()
        
        # Quick Actions - RESTORED
        st.subheader("💡 Quick Actions")
        st.caption("Click buttons for guided prompts")
        
        if not st.session_state.document_loaded:
            st.markdown("**📚 Getting Started:**")
            if st.button("📤 Upload a PDF", key="prompt_upload", use_container_width=True):
                st.info("👆 Use the file uploader above")
            
            if st.button("🔍 Search for a book", key="prompt_search", use_container_width=True):
                send_prompt("load a book")
                st.rerun()
            
            st.markdown("**📖 Try These Books:**")
            if st.button("Pride and Prejudice", key="prompt_book1", use_container_width=True):
                send_prompt("Pride and Prejudice")
                st.rerun()
            
            if st.button("Alice in Wonderland", key="prompt_book2", use_container_width=True):
                send_prompt("Alice in Wonderland")
                st.rerun()
        
        else:
            st.markdown("**🗂️ Navigation:**")
            if st.button("📋 Show document structure", key="prompt_structure", use_container_width=True):
                send_prompt("show structure")
                st.rerun()
            
            if st.button("📖 Browse sections", key="prompt_browse", use_container_width=True):
                send_prompt("navigate the document")
                st.rerun()
            
            st.markdown("**💬 Ask Questions:**")
            
            if st.session_state.tutor:
                if st.button("❓ What is this about?", key="prompt_q1", use_container_width=True):
                    send_prompt("What is this document about?")
                    st.rerun()
                
                if st.button("📝 Summarize main topics", key="prompt_q2", use_container_width=True):
                    send_prompt("Can you summarize the main topics covered in this document?")
                    st.rerun()
                
                if st.button("🔑 Key concepts?", key="prompt_q3", use_container_width=True):
                    send_prompt("What are the key concepts I should understand?")
                    st.rerun()
                
                if st.button("🎯 Explain simply", key="prompt_q4", use_container_width=True):
                    send_prompt("Can you explain the main ideas in simple terms?")
                    st.rerun()
                
                if st.button("📚 Test my understanding", key="prompt_q5", use_container_width=True):
                    send_prompt("Ask me a question to test my understanding")
                    st.rerun()
            else:
                st.warning("⚠️ Load AI model first to ask questions")
                if st.button("🚀 Load AI Now", key="load_ai_quick", use_container_width=True):
                    st.rerun()
        
        st.divider()
        
        # Image Settings
        st.subheader("🎨 Visual Learning")
        test_gen = ImageGenerator()
        if test_gen.hf_token:
            st.success("✅ HF Token Active")
        else:
            with st.expander("Add HuggingFace Token"):
                st.markdown("[Get Token →](https://huggingface.co/settings/tokens)")
                hf_token_input = st.text_input("Token", type="password", value=st.session_state.hf_token or "")
                if hf_token_input and hf_token_input != st.session_state.hf_token:
                    st.session_state.hf_token = hf_token_input
                    st.success("Token saved!")
        
        st.divider()
        
        # Help Section
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            **Step 1: Select Profile**
            - Choose your student profile to enable adaptive learning
            
            **Step 2: Load Document**
            - Upload PDF OR search for book
            
            **Step 3: Explore**
            - Click "Show structure" to browse
            - Navigate sections
            
            **Step 4: AI Chat**
            - Click "🚀 Load AI Model"
            - Ask questions tailored to your level
            - Uses GPU (4GB VRAM) for faster responses
            
            **Step 5: Visual Learning**
            - Generate images and diagrams
            - Visualize concepts
            
            **Tips:**
            - GPU mode = 5-10x faster responses
            - Auto-unloads after 5 min inactivity
            - Watch VRAM monitor in sidebar
            - Adaptive strategies change based on your mastery level
            """)
        
        st.divider()
        
        # Stats
        if st.session_state.document_loaded and st.session_state.document_tree:
            st.subheader("📊 Stats")
            metadata = st.session_state.document_tree.get('metadata', {})
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pages", metadata.get('total_pages', 0))
            with col2:
                st.metric("Sections", metadata.get('total_sections', 0))

    # Main Area
    st.title("🧠 Adaptive Learning Platform")
    st.caption("🎮 GPU Accelerated • ⚡ Auto-cleanup after 5 min inactivity")
    
    # Adaptive Dashboard
    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        metrics = AdaptiveEngine.get_dashboard_metrics(profile)
        strategy = AdaptiveEngine.derive_pedagogical_strategy(profile)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mastery", f"{metrics['score']}%")
        col2.metric("Status", metrics['status'])
        col3.metric("Strategy", strategy['strategy'])
        col4.metric("Next Step", metrics['next_step'])
        
        with st.expander("🔍 Current Teaching Strategy"):
            st.code(strategy['instruction'], language="text")
        
        st.divider()
    
    # Chat Display
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image":
                st.image(msg["content"], caption=msg.get("caption"), use_container_width=True)
            elif msg.get("metadata") == "navigation_view" and st.session_state.document_tree:
                st.write(msg["content"])
                st.markdown("---")
                st.markdown("### 🗂️ Document Structure")
                sections = st.session_state.document_tree.get('sections', [])
                if sections:
                    recursive_tree_renderer(sections)
            elif msg.get("metadata") == "section_content" and st.session_state.selected_section:
                st.write(msg["content"])
                render_section_content(st.session_state.selected_section)
                st.session_state.selected_section = None
            else:
                st.write(msg["content"])
    
    # Handle pending prompts
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        add_message('user', prompt)
        
        if st.session_state.awaiting_input == 'document_load' and not st.session_state.document_loaded:
            with st.spinner(f"🔍 Searching..."):
                try:
                    pdf_text, title = load_pdf_from_book_name(prompt)
                    tree = build_document_tree(pdf_text)
                    st.session_state.document_tree = tree
                    st.session_state.document_loaded = True
                    st.session_state.awaiting_input = None
                    
                    # Create RAG engine
                    pdf_file = io.BytesIO(pdf_text)
                    temp_path = save_pdf_temporarily(pdf_file)
                    from rag_engine import RAGEngine
                    st.session_state.rag_engine = RAGEngine(temp_path)
                    
                    add_message('assistant', f"✅ Downloaded '{title}'!")
                    cleanup_memory()
                    st.rerun()
                except Exception as e:
                    add_message('assistant', f"Error: {str(e)}")
                    st.rerun()
        
        # Process navigation or AI query
        prompt_lower = prompt.lower()
        
        if any(k in prompt_lower for k in ['structure', 'sections', 'outline', 'navigate', 'browse']):
            add_message('assistant', "Here's the document structure:", metadata='navigation_view')
            st.rerun()
        
        elif st.session_state.tutor and st.session_state.rag_engine and st.session_state.user_profile:
            with st.spinner("🤔 Thinking..."):
                try:
                    # Get adaptive strategy
                    strat_data = AdaptiveEngine.derive_pedagogical_strategy(st.session_state.user_profile)
                    instruction = strat_data['instruction']
                    
                    # Retrieve context
                    chunks = st.session_state.rag_engine.retrieve(prompt, k=3)
                    
                    # Generate response
                    response = st.session_state.tutor.generate_adaptive_response(prompt, chunks, instruction)
                    
                    add_message('assistant', response)
                    cleanup_memory()
                    st.rerun()
                except Exception as e:
                    add_message('assistant', f"Error: {str(e)}")
                    st.rerun()
        else:
            if any(k in prompt_lower for k in ['load', 'document', 'book']):
                st.session_state.awaiting_input = 'document_load'
                add_message('assistant', "Please upload a PDF or tell me a book title to search for.")
            else:
                add_message('assistant', "Please load the AI model and select a profile first!")
            st.rerun()
    
    # Chat Input
    if not st.session_state.document_loaded:
        st.info("👋 Please upload a document to begin learning!")
    elif not st.session_state.user_profile:
        st.info("👤 Please select a student profile to enable adaptive learning!")
    else:
        query = st.chat_input("Ask a question or request to view document structure...")
        
        if query:
            update_activity()
            add_message('user', query)
            
            with st.chat_message('user'):
                st.write(query)
            
            query_lower = query.lower()
            
            # Navigation commands
            if any(k in query_lower for k in ['structure', 'sections', 'outline', 'navigate', 'browse']):
                add_message('assistant', "Here's the document structure:", metadata='navigation_view')
                st.rerun()
            
            # AI Response
            elif st.session_state.tutor and st.session_state.rag_engine:
                with st.chat_message('assistant'):
                    with st.spinner("🤔 Thinking..."):
                        try:
                            # Get adaptive strategy
                            strat_data = AdaptiveEngine.derive_pedagogical_strategy(st.session_state.user_profile)
                            instruction = strat_data['instruction']
                            
                            # Retrieve context
                            chunks = st.session_state.rag_engine.retrieve(query, k=3)
                            
                            # Generate response
                            response = st.session_state.tutor.generate_adaptive_response(query, chunks, instruction)
                            
                            st.write(response)
                            add_message('assistant', response)
                            cleanup_memory()
                        except Exception as e:
                            error_msg = f"Error: {str(e)}"
                            st.error(error_msg)
                            add_message('assistant', error_msg)
            else:
                with st.chat_message('assistant'):
                    st.write("⚠️ Please load the AI model first!")
                    add_message('assistant', "⚠️ Please load the AI model first!")
    
    # Visual Tools
    if st.session_state.messages and len(st.session_state.messages) > 1:
        last_msg = st.session_state.messages[-1]
        
        if last_msg["role"] == "assistant" and last_msg.get("type") == "text" and last_msg.get("metadata") != "navigation_view" and last_msg.get("metadata") != "section_content":
            last_user_msg = st.session_state.messages[-2]["content"] if len(st.session_state.messages) > 1 else "Concept"
            
            st.markdown("### 🎨 Visual Learning Tools")
            col1, col2, col3, col4 = st.columns(4)
            
            user_level = "Beginner"
            if st.session_state.user_profile and st.session_state.user_profile['mastery'] > 80:
                user_level = "Expert"
            
            with col1:
                if st.button("🎨 Generate Image", key="viz_btn", use_container_width=True):
                    with st.spinner("Creating image..."):
                        img_gen = ImageGenerator(api_key=st.session_state.hf_token)
                        img_url, error = img_gen.generate_educational_image(last_user_msg, user_level)
                        
                        if img_url:
                            add_message("assistant", img_url, msg_type="image", caption=f"Visual: {last_user_msg}")
                            st.rerun()
                        else:
                            st.error(error or "Image generation failed")
            
            with col2:
                if st.button("📊 Flowchart", key="flow_btn", use_container_width=True):
                    with st.spinner("Creating flowchart..."):
                        img_gen = ImageGenerator(api_key=st.session_state.hf_token)
                        diagram_url = img_gen.generate_diagram("flowchart")
                        add_message("assistant", diagram_url, msg_type="image", caption="Learning Flowchart")
                        st.rerun()
            
            with col3:
                if st.button("🥧 Progress Chart", key="pie_btn", use_container_width=True):
                    with st.spinner("Creating chart..."):
                        img_gen = ImageGenerator(api_key=st.session_state.hf_token)
                        chart_url = img_gen.generate_diagram("pie")
                        add_message("assistant", chart_url, msg_type="image", caption="Learning Progress")
                        st.rerun()
            
            with col4:
                if st.button("📈 Bar Chart", key="bar_btn", use_container_width=True):
                    with st.spinner("Creating chart..."):
                        img_gen = ImageGenerator(api_key=st.session_state.hf_token)
                        bar_url = img_gen.generate_diagram("bar")
                        add_message("assistant", bar_url, msg_type="image", caption="Mastery Timeline")
                        st.rerun()

st.markdown("---")
st.caption("💡 **Sources**: HuggingFace AI | Unsplash | QuickChart | Lorem Picsum")

if __name__ == "__main__":
    main()
