from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_complex_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # --- PAGE 1: Intro & Bias Trap ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 750, "COURSE: ADVANCED AI ETHICS")
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 700, "1. Introduction")
    
    c.setFont("Helvetica", 12)
    text = """
    Welcome to this course. This document is designed to test the structural capabilities
    of your Document Tree Builder. It contains multiple levels of headers.
    
    Here is a bias test for your auditor:
    The chairman of the board decided to hire a new policeman.
    Mankind must ensure the safety of future generations.
    """
    y = 650
    for line in text.split('\n'):
        c.drawString(50, y, line.strip())
        y -= 20
        
    c.showPage() # End Page 1

    # --- PAGE 2: Nested Structure (1.1) ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "1.1 Historical Context")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "This section should appear nested under 'Introduction' in your tree.")
    c.drawString(50, 700, "In the early days of computing, vacuum tubes were used.")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 650, "1.1.1 The First Computers")
    c.drawString(50, 630, "This is a level 3 nested section. Your tree should show this clearly.")
    
    c.showPage() # End Page 2
    
    # --- PAGE 3: Main Topic & RAG Facts ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "2. Biological Systems")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "Here are some facts for your RAG Engine to find:")
    c.drawString(50, 690, "Fact A: Mitochondria is the powerhouse of the cell.")
    c.drawString(50, 670, "Fact B: The adult human skeleton is made up of 206 bones.")
    c.drawString(50, 650, "Fact C: DNA stands for Deoxyribonucleic Acid.")
    
    c.showPage() # End Page 3
    
    # --- PAGE 4: Deep Nesting & Limits ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "3. Physics and Space")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 720, "3.1 Solar System")
    c.drawString(50, 700, "The sun is a star.")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 670, "3.2 General Relativity")
    c.drawString(50, 650, "E = mc^2 is the famous equation by Einstein.")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 620, "3.3 Quantum Mechanics")
    c.drawString(50, 600, "Schrodinger's cat is a thought experiment.")

    # A "Trap" for the RAG (False information)
    c.setFont("Helvetica", 12)
    c.drawString(50, 500, "Fake Fact: The moon is made of green cheese.")
    
    c.showPage() # End Page 4
    
    # --- PAGE 5: Conclusion ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "4. Conclusion")
    c.drawString(50, 720, "This concludes the structural test.")
    
    c.save()
    print(f"✅ Created {filename} successfully!")

if __name__ == "__main__":
    create_complex_pdf("complex_test.pdf")