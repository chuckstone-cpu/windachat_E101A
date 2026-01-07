from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def draw_header(c, text, y_pos):
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(72, y_pos, text)
    c.setFillColor(colors.black)
    c.setFont("Times-Roman", 12)
    return y_pos - 25

def draw_sub_header(c, text, y_pos):
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawString(72, y_pos, text)
    c.setFont("Times-Roman", 12)
    return y_pos - 20

def draw_text(c, text, y_pos):
    c.setFont("Times-Roman", 12)
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        # Simple wrapping logic for demo
        if len(line) > 85:
            # Split long lines roughly
            part1 = line[:85] + "-"
            part2 = line[85:]
            c.drawString(72, y_pos, part1)
            y_pos -= 15
            c.drawString(72, y_pos, part2)
        else:
            c.drawString(72, y_pos, line)
        y_pos -= 15
    return y_pos - 10

def create_textbook_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = 750 # Start from top

    # --- PAGE 1: TITLE & INTRO ---
    c.setFont("Times-Bold", 24)
    c.drawCentredString(width/2, y, "Chapter 1: The Fundamental Unit of Life")
    y -= 50
    
    y = draw_header(c, "1.1 Introduction to Cell Biology", y)
    text = """
    Cell biology is the study of cells, their physiological properties, their structure, 
    the organelles they contain, interactions with their environment, their life cycle, 
    division, death and cell function. This is done both on a microscopic and molecular level.
    
    Knowing the components of cells and how cells work is fundamental to all biological sciences. 
    It is also essential for research in bio-medical fields such as cancer, and other diseases.
    Research in cell biology is closely related to genetics, biochemistry, molecular biology, 
    immunology, and developmental biology.
    """
    y = draw_text(c, text, y)

    y = draw_sub_header(c, "1.1.1 The Cell Theory", y)
    text = """
    The cell theory, first developed in 1839 by Schleiden and Schwann, states that:
    1. All living organisms are composed of one or more cells.
    2. The cell is the basic unit of structure and organization in organisms.
    3. Cells arise from pre-existing cells.
    """
    y = draw_text(c, text, y)
    c.showPage() # END PAGE 1

    # --- PAGE 2: TYPES OF CELLS ---
    y = 750
    y = draw_header(c, "1.2 Types of Cells", y)
    
    text = """
    Cells can be subdivided into two major categories: prokaryotic and eukaryotic. 
    The main difference between the two is that eukaryotic cells contain a nucleus 
    and membrane-bound organelles, while prokaryotic cells do not.
    """
    y = draw_text(c, text, y)

    y = draw_sub_header(c, "1.2.1 Prokaryotic Cells", y)
    text = """
    Prokaryotes include bacteria and archaea. They are much simpler than eukaryotes. 
    A prokaryotic cell has three architectural regions:
    - Envelopes (capsule, cell wall, and plasma membrane).
    - Cytoplasmic region (contains the genome or DNA).
    - Appendages (flagella and pili).
    """
    y = draw_text(c, text, y)
    
    y = draw_sub_header(c, "1.2.2 Eukaryotic Cells", y)
    text = """
    Plants, animals, fungi, slime moulds, protozoa, and algae are all eukaryotic. 
    These cells are about fifteen times wider than a typical prokaryote and can be as much 
    as a thousand times greater in volume. The main distinguishing feature is the presence 
    of a membrane-bound nucleus.
    """
    y = draw_text(c, text, y)
    c.showPage() # END PAGE 2

    # --- PAGE 3: ORGANELLES ---
    y = 750
    y = draw_header(c, "1.3 Key Organelles", y)

    y = draw_sub_header(c, "1.3.1 The Nucleus", y)
    text = """
    The nucleus is the information center of the cell and houses the cell's chromosomes, 
    which are the linear DNA strands. It is surrounded by a double membrane called the 
    nuclear envelope.
    """
    y = draw_text(c, text, y)

    y = draw_sub_header(c, "1.3.2 Mitochondria", y)
    text = """
    Mitochondria are often described as the "powerhouse of the cell" because they generate 
    most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy. 
    In addition to supplying cellular energy, mitochondria are involved in other tasks, 
    such as signaling, cellular differentiation, and cell death.
    """
    y = draw_text(c, text, y)

    y = draw_sub_header(c, "1.3.3 Ribosomes", y)
    text = """
    The ribosome is a large complex of RNA and protein molecules. They act as an assembly line 
    where RNA from the nucleus is used to synthesize proteins from amino acids. Ribosomes can 
    be found either floating freely or bound to the endoplasmic reticulum.
    """
    y = draw_text(c, text, y)
    c.showPage() # END PAGE 3

    # --- PAGE 4: CONCLUSION ---
    y = 750
    y = draw_header(c, "1.4 Conclusion", y)
    text = """
    Understanding cell structure and function is critical for modern biology. 
    From the simplicity of prokaryotes to the complexity of eukaryotic organelles like 
    mitochondria and the nucleus, life is built upon these microscopic units.
    """
    y = draw_text(c, text, y)
    
    c.save()
    print(f"✅ Created {filename} successfully!")

if __name__ == "__main__":
    create_textbook_pdf("biology_chapter.pdf")