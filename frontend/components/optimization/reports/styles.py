from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

# ----- Layout -----
MARGIN_INCH = 0.5
PAGE_WIDTH = 8.27
FIG_WIDTH_INCH = PAGE_WIDTH - 2 * MARGIN_INCH  # ~7.27"

# ----- Colors -----
COLOR_HEADER_BG = "#1a365d"
COLOR_ROW_ALT = "#f7fafc"
COLOR_TEXT = "#2d3748"
COLOR_BORDER = "#e2e8f0"
COLOR_TABLE_BORDER = "#718096"
COLOR_CAPTION = "#4a5568"
FONT_NAME = "Helvetica"

def get_report_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Heading1"],
        fontSize=20, spaceAfter=6, alignment=TA_CENTER, textColor=colors.HexColor(COLOR_HEADER_BG),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"],
        fontSize=10, spaceAfter=14, alignment=TA_CENTER, textColor=colors.HexColor("#718096"),
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, leading=13, spaceAfter=10, textColor=colors.HexColor(COLOR_TEXT),
    )
    heading_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"],
        fontSize=14, spaceBefore=20, spaceAfter=8, textColor=colors.HexColor(COLOR_HEADER_BG),
    )
    subheading_style = ParagraphStyle(
        "SubHeading", parent=styles["Heading3"],
        fontSize=11, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor(COLOR_TEXT),
    )
    caption_style = ParagraphStyle(
        "Caption", parent=styles["Normal"],
        fontSize=9, leading=11, spaceBefore=4, spaceAfter=14, alignment=TA_CENTER,
        textColor=colors.HexColor(COLOR_CAPTION), fontName=f"{FONT_NAME}-Oblique",
    )
    
    return {
        "styles": styles,
        "title": title_style,
        "subtitle": subtitle_style,
        "body": body_style,
        "heading": heading_style,
        "subheading": subheading_style,
        "caption": caption_style
    }
