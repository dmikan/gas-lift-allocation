from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from frontend.components.optimization.reports.styles import COLOR_HEADER_BG, COLOR_ROW_ALT, COLOR_TABLE_BORDER, FONT_NAME


def create_styled_table(df, col_widths, bold_last_row: bool = False):
    """Create a styled ReportLab table from a DataFrame.

    Args:
        df: pandas DataFrame whose columns become the header row.
        col_widths: list of column widths (ReportLab units).
        bold_last_row: if True, the last data row is rendered bold (useful for totals).
    """
    table_data = [df.columns.tolist()] + df.values.tolist()
    last_row_idx = len(table_data) - 1

    style_cmds = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER_BG)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), f"{FONT_NAME}-Bold"),
        # Base font / size for all cells
        ("FONTNAME", (0, 1), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        # Alignment: first column left, rest right-aligned
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        # Alternating row backgrounds
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(COLOR_ROW_ALT)]),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_TABLE_BORDER)),
        # Padding
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]

    if bold_last_row and last_row_idx >= 1:
        style_cmds += [
            ("FONTNAME", (0, last_row_idx), (-1, last_row_idx), f"{FONT_NAME}-Bold"),
            ("BACKGROUND", (0, last_row_idx), (-1, last_row_idx), colors.HexColor("#e8eaf0")),
        ]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style_cmds))
    return t
