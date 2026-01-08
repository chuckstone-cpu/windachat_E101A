"""
Document Tree Builder

Converts extracted PDF text into a tree-structured representation.
Detects section headers and organizes content hierarchically.
Includes logic to balance the tree to avoid overwhelming flat lists.
"""

import re

def is_header(line):
    """
    Determine if a line is likely a section header.
    """
    if not line or not line.strip():
        return False
    
    line = line.strip()
    
    # Check for numbered patterns at the start (e.g., "1.", "2.1", "3.2.1")
    if re.match(r'^\d+(\.\d+)*\.?\s+', line):
        return True
    
    # Check for keywords like CHAPTER, UNIT, etc.
    keywords = ['CHAPTER', 'UNIT', 'SECTION', 'PART', 'LESSON', 'MODULE']
    line_upper = line.upper()
    for keyword in keywords:
        if line_upper.startswith(keyword):
            return True
    
    # Check if line is ALL CAPS (excluding numbers and common punctuation)
    text_only = re.sub(r'[0-9\s\.\,\;\:\!\?\-\(\)]', '', line)
    if text_only and text_only.isupper() and len(text_only) > 3: # Increased min len slightly to reduce false positives
        return True
    
    return False


def chunk_text(text, max_chunk_size=500):
    """Split text into smaller chunks for easier access."""
    if not text or len(text) <= max_chunk_size:
        return [text] if text else []
    
    chunks = []
    
    # First, try to split by sentences
    sentences = re.split(r'([.!?]\s+)', text)
    
    current_chunk = ""
    for i in range(0, len(sentences), 2):
        sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
        if current_chunk and len(current_chunk) + len(sentence) > max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Final pass for very long sentences
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_chunk_size:
            final_chunks.append(chunk)
        else:
            words = chunk.split()
            current_word_chunk = ""
            for word in words:
                if current_word_chunk and len(current_word_chunk) + len(word) + 1 > max_chunk_size:
                    final_chunks.append(current_word_chunk.strip())
                    current_word_chunk = word
                else:
                    current_word_chunk += (" " + word if current_word_chunk else word)
            if current_word_chunk:
                final_chunks.append(current_word_chunk.strip())
    
    return final_chunks


def group_large_sections(sections, max_siblings=15):
    """
    Recursively restructures the tree. If a list of sections (siblings) 
    exceeds max_siblings, it groups them into artificial parent nodes.
    
    Args:
        sections (list): List of section dictionaries.
        max_siblings (int): Maximum allowed siblings before grouping occurs.
        
    Returns:
        list: The restructured list of sections.
    """
    if not sections:
        return []

    # 1. First, recursively optimize children of current sections
    for section in sections:
        if section.get('subsections'):
            section['subsections'] = group_large_sections(section['subsections'], max_siblings)

    # 2. If current level is small enough, return as is
    if len(sections) <= max_siblings:
        return sections

    # 3. If current level is too large, group them
    new_grouped_sections = []
    
    # Determine how many items per group
    # We slice the list into chunks of size 'max_siblings'
    for i in range(0, len(sections), max_siblings):
        chunk = sections[i : i + max_siblings]
        
        # Determine labels for the group wrapper
        first_header = chunk[0]['header']
        last_header = chunk[-1]['header']
        
        # Truncate headers for display if they are too long
        def truncate(s, l=20): return (s[:l] + '..') if len(s) > l else s
        
        group_title = f"📚 Sections: {truncate(first_header)} - {truncate(last_header)}"
        
        # Create a virtual wrapper section
        wrapper_section = {
            'header': group_title,
            'page_number': chunk[0]['page_number'],
            'level': chunk[0]['level'], # Keep same level logic
            'content_chunks': [], # Wrappers usually hold no content directly
            'subsections': chunk,
            'is_wrapper': True # Flag to identify artificial nodes
        }
        
        new_grouped_sections.append(wrapper_section)
        
    return new_grouped_sections


def build_document_tree(pdf_text_list, max_chunk_size=500):
    """
    Builds and balances a tree-structured representation of the PDF.
    """
    if not pdf_text_list:
        return {'metadata': {'total_pages': 0, 'total_sections': 0}, 'sections': []}
    
    # --- Step 1: Flatten Pages to Lines ---
    all_lines = []
    for page_data in pdf_text_list:
        page_num = page_data.get('page_number', 0)
        text = page_data.get('text', '')
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                all_lines.append({'text': line, 'page_number': page_num})
    
    # --- Step 2: Extract Flat List of Sections ---
    sections = []
    current_section = None
    current_content = []
    
    for line_data in all_lines:
        line = line_data['text']
        page_num = line_data['page_number']
        
        if is_header(line):
            # Save previous
            if current_section is not None:
                if current_content:
                    content_text = ' '.join(current_content)
                    current_section['content_chunks'] = chunk_text(content_text, max_chunk_size)
                sections.append(current_section)
            
            # Determine level logic (heuristic)
            level = 1
            match = re.match(r'^(\d+(\.\d+)*)', line)
            if match:
                level = match.group(1).count('.') + 1
            
            current_section = {
                'header': line,
                'page_number': page_num,
                'level': level,
                'content_chunks': [],
                'subsections': [],
                'is_wrapper': False
            }
            current_content = []
        else:
            if current_section is not None:
                current_content.append(line)
            else:
                # Content before first header
                if not current_content:
                    current_section = {
                        'header': 'Introduction / Prologue',
                        'page_number': page_num,
                        'level': 1,
                        'content_chunks': [],
                        'subsections': [],
                        'is_wrapper': False
                    }
                current_content.append(line)
    
    # Save last section
    if current_section is not None:
        if current_content:
            content_text = ' '.join(current_content)
            current_section['content_chunks'] = chunk_text(content_text, max_chunk_size)
        sections.append(current_section)
    
    # --- Step 3: Organize Hierarchy based on explicit levels (1.1, 1.1.1) ---
    organized_sections = []
    section_stack = [] 
    
    for section in sections:
        level = section['level']
        
        # Find correct parent in stack
        while section_stack and section_stack[-1]['level'] >= level:
            section_stack.pop()
        
        if section_stack:
            section_stack[-1]['subsections'].append(section)
        else:
            organized_sections.append(section)
        
        section_stack.append(section)
    
    # --- Step 4: Balance the Tree (The new logic) ---
    # This splits massive lists into smaller groups
    balanced_sections = group_large_sections(organized_sections, max_siblings=15)
    
    # --- Step 5: Count Stats ---
    def count_sections(section_list):
        count = 0
        for s in section_list:
            if not s.get('is_wrapper', False): # Don't count artificial wrappers
                count += 1
            count += count_sections(s.get('subsections', []))
        return count
    
    total_sections = count_sections(balanced_sections)
    total_pages = max([item.get('page_number', 0) for item in pdf_text_list], default=0)
    
    return {
        'metadata': {
            'total_pages': total_pages,
            'total_sections': total_sections
        },
        'sections': balanced_sections
    }