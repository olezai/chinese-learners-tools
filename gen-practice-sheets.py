import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
OUTPUT_FILENAME = "chinese_handwriting_practice.pdf"
FONT_PATH = "NotoSerifSC.ttf"  # Path to your Chinese .ttf font file
FONT_NAME = "ChineseFont"

# Characters to generate (each character gets a row of repetitions)
CHARACTERS = ["掀","熬","搁","罕","梗","撼","揣","瘫","褪","摒"]

# Page setup (Letter size)
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 40  # Margin in points

# Grid layout options
COLS = 7  # Number of character squares per row
BOX_SIZE = (PAGE_WIDTH - 2 * MARGIN) / COLS  # Square cell dimensions
GRID_COLOR = colors.HexColor("#D0D0D0")  # Light gray outer box
INNER_LINE_COLOR = colors.HexColor("#E5E5E5")  # Lighter dashed center cross
TEXT_COLOR = colors.HexColor("#000000")


def setup_font():
    """Register Chinese TrueType font if file exists."""
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    else:
        print(f"Warning: '{FONT_PATH}' not found. Falling back to default font.")


def draw_grid_box(c, x, y, size):
    """Draw a single practice box with dashed central guideline cross."""
    c.saveState()

    # Draw outer box boundary
    c.setStrokeColor(GRID_COLOR)
    c.setLineWidth(0.8)
    c.rect(x, y, size, size)

    # Draw interior horizontal and vertical dashed center lines
    c.setStrokeColor(INNER_LINE_COLOR)
    c.setLineWidth(0.5)
    c.setDash([2, 2], 0)

    # Horizontal midline
    c.line(x, y + size / 2, x + size, y + size / 2)
    # Vertical midline
    c.line(x + size / 2, y, x + size / 2, y + size)

    c.restoreState()


def generate_pdf(filename, characters):
    """Generate the handwriting worksheet PDF."""
    setup_font()
    c = canvas.Canvas(filename, pagesize=letter)

    start_x = MARGIN
    start_y = PAGE_HEIGHT - MARGIN - BOX_SIZE

    font_to_use = FONT_NAME if FONT_NAME in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    font_size = BOX_SIZE * 0.7  # Scale character relative to box size

    c.setFont(font_to_use, font_size)
    c.setFillColor(TEXT_COLOR)

    current_x = start_x
    current_y = start_y

    for char in characters:
        # Fill a row with the current character repeated COLS times
        for _ in range(COLS):
            # Draw box grid
            draw_grid_box(c, current_x, current_y, BOX_SIZE)

            # Center character inside the square box
            text_width = c.stringWidth(char, font_to_use, font_size)
            char_x = current_x + (BOX_SIZE - text_width) / 2
            # Offset baseline vertically for centering
            char_y = current_y + (BOX_SIZE - font_size) / 2 + (font_size * 0.15)

            c.drawString(char_x, char_y, char)
            current_x += BOX_SIZE

        # Advance to the next row
        current_x = start_x
        current_y -= BOX_SIZE

        # Start a new page if content exceeds vertical margin
        if current_y < MARGIN:
            c.showPage()
            c.setFont(font_to_use, font_size)
            c.setFillColor(TEXT_COLOR)
            current_y = start_y

    c.save()
    print(f"PDF successfully created: {filename}")


if __name__ == "__main__":
    generate_pdf(OUTPUT_FILENAME, CHARACTERS)
