"""
PDF export utility for converting text summaries into downloadable PDF files.
Uses reportlab for PDF generation with clean formatting.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import black, HexColor
from typing import List


def export_summary_to_pdf(summary_text: str, output_path: str):
    """
    Convert a text summary (Markdown-style) into a formatted PDF document.
    
    The PDF includes:
    - Title page with proper heading
    - Formatted sections and subsections
    - Bullet points preserved
    - Automatic page breaks for long content
    - Readable fonts and clean layout
    
    Args:
        summary_text (str): The summary text in Markdown-style format
        output_path (str): Path where the PDF file will be saved
    """
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Get base styles and create custom styles
    styles = getSampleStyleSheet()
    
    # Define custom styles for different elements
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=black,
        spaceAfter=12,
        leading=14,
        fontName='Helvetica'
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        textColor=black,
        spaceAfter=8,
        leftIndent=20,
        bulletIndent=10,
        leading=14,
        fontName='Helvetica'
    )
    
    # Build PDF content
    story = []
    
    # Parse and add content
    lines = summary_text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacing)
        if not line:
            story.append(Spacer(1, 6))
            i += 1
            continue
        
        # Parse different Markdown-style elements
        
        # Title (H1 with #)
        if line.startswith('# ') and not line.startswith('##'):
            title_text = line[2:].strip()
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 20))
        
        # Heading 1 (##)
        elif line.startswith('## '):
            heading_text = line[3:].strip()
            story.append(Paragraph(heading_text, heading1_style))
        
        # Heading 2 (###)
        elif line.startswith('### '):
            heading_text = line[4:].strip()
            story.append(Paragraph(heading_text, heading2_style))
        
        # Bullet points (- or *)
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:].strip()
            # Handle bold text in bullets (**text**)
            bullet_text = _format_bold_text(bullet_text)
            story.append(Paragraph(f"• {bullet_text}", bullet_style))
        
        # Numbered list
        elif line and line[0].isdigit() and '. ' in line[:5]:
            parts = line.split('. ', 1)
            if len(parts) == 2:
                numbered_text = parts[1].strip()
                numbered_text = _format_bold_text(numbered_text)
                story.append(Paragraph(f"{parts[0]}. {numbered_text}", bullet_style))
        
        # Horizontal rule (---)
        elif line.startswith('---'):
            story.append(Spacer(1, 12))
            story.append(PageBreak())
            story.append(Spacer(1, 12))
        
        # Italic text (lines starting with *)
        elif line.startswith('*') and line.endswith('*') and len(line) > 2:
            italic_text = line[1:-1].strip()
            italic_para = Paragraph(f"<i>{italic_text}</i>", normal_style)
            story.append(italic_para)
        
        # Regular paragraph text
        else:
            # Format bold text and other inline formatting
            formatted_text = _format_bold_text(line)
            story.append(Paragraph(formatted_text, normal_style))
        
        i += 1
    
    # Build PDF
    doc.build(story)


def _format_bold_text(text: str) -> str:
    """
    Convert Markdown-style bold (**text**) to HTML bold tags for reportlab.
    
    Args:
        text: Text string that may contain **bold** markers
    
    Returns:
        Text with HTML bold tags
    """
    # Replace **text** with <b>text</b>
    import re
    # Pattern to match **text** but not nested
    pattern = r'\*\*(.+?)\*\*'
    formatted = re.sub(pattern, r'<b>\1</b>', text)
    return formatted
