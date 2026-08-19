import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
OUTPUT_FILENAME = "chinese_handwriting_practice.pdf"
FONT_PATH = "NotoSerifSC-Regular.ttf"
FONT_NAME = "ChineseFont"

CHARACTERS = ["我", "喜", "歡", "寫", "漢", "字", "我", "喜", "欢", "写", "汉", "字"]

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 40
COLS = 7
BOX_SIZE = (PAGE_WIDTH - 2 * MARGIN) / COLS

GRID_COLOR = colors.HexColor("#D0D0D0")
INNER_LINE_COLOR = colors.HexColor("#E5E5E5")

# Colors for prompt vs. tracing characters
TEXT_COLOR_MAIN = colors.HexColor("#000000")  # Fully visible
TEXT_COLOR_TRACE = colors.HexColor("#D3D3D3")  # Faded gray for tracing


def setup_font():
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


def draw_grid_box(c, x, y, size):
    c.saveState()
    c.setStrokeColor(GRID_COLOR)
    c.setLineWidth(0.8)
    c.rect(x, y, size, size)

    c.setStrokeColor(INNER_LINE_COLOR)
    c.setLineWidth(0.5)
    c.setDash([2, 2], 0)
    c.line(x, y + size / 2, x + size, y + size / 2)
    c.line(x + size / 2, y, x + size / 2, y + size)
    c.restoreState()


def generate_pdf(filename, characters):
    setup_font()
    c = canvas.Canvas(filename, pagesize=letter)

    start_x = MARGIN
    start_y = PAGE_HEIGHT - MARGIN - BOX_SIZE

    font_to_use = (
        FONT_NAME
        if FONT_NAME in pdfmetrics.getRegisteredFontNames()
        else "Helvetica"
    )
    font_size = BOX_SIZE * 0.7

    c.setFont(font_to_use, font_size)

    current_x = start_x
    current_y = start_y

    for char in characters:
        for col_idx in range(COLS):
            draw_grid_box(c, current_x, current_y, BOX_SIZE)

            # Column 0 is fully visible; remaining columns are faded
            if col_idx == 0:
                c.setFillColor(TEXT_COLOR_MAIN)
            else:
                c.setFillColor(TEXT_COLOR_TRACE)

            text_width = c.stringWidth(char, font_to_use, font_size)
            char_x = current_x + (BOX_SIZE - text_width) / 2
            char_y = current_y + (BOX_SIZE - font_size) / 2 + (font_size * 0.15)

            c.drawString(char_x, char_y, char)
            current_x += BOX_SIZE

        current_x = start_x
        current_y -= BOX_SIZE

        if current_y < MARGIN:
            c.showPage()
            c.setFont(font_to_use, font_size)
            current_y = start_y

    c.save()


if __name__ == "__main__":
    generate_pdf(OUTPUT_FILENAME, CHARACTERS)
