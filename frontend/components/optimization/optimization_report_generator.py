"""
Generate a high-quality PDF report from the same data used by the plotter.
Uses reportlab for layout, matplotlib for figures, and pypdf to append
vector-figure pages as an optional appendix; no LaTeX.

Usage:
    gen = OptimizationReportGenerator(
        constrained_optimization_results=...,
        well_results=...,
        global_optimization_results=...,
        list_info=...,
    )
    gen.save_pdf("optimization_report.pdf")
    # or: pdf_bytes = gen.build_pdf()
"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional

import numpy as np
import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image as RLImage,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.enums import TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# ----- Layout -----
MARGIN_INCH = 0.5
PAGE_WIDTH = 8.27
FIG_WIDTH_INCH = PAGE_WIDTH - 2 * MARGIN_INCH  # ~7.27"

# ----- Report colors -----
COLOR_HEADER_BG = "#1a365d"
COLOR_ROW_ALT = "#f7fafc"
COLOR_TEXT = "#2d3748"
COLOR_BORDER = "#e2e8f0"
COLOR_TABLE_BORDER = "#718096"  # darker, more visible borders for tables
COLOR_CAPTION = "#4a5568"
FONT_NAME = "Helvetica"


def _fig_to_image_buffer(fig, dpi: int = 150) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    plt.close(fig)
    return buf
def _fig_to_pdf_buffer(fig) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="pdf", bbox_inches="tight", facecolor="white")
    buf.seek(0)
    plt.close(fig)
    return buf


def _build_global_curve_figure(global_results: dict):
    _tq = global_results.get("total_qgl")
    _tp = global_results.get("total_production")
    total_qgl = list(_tq) if _tq is not None else []
    total_production = list(_tp) if _tp is not None else []
    if len(total_qgl) == 0 or len(total_production) == 0:
        return None
    last_production = total_production[-1] if total_production else 0
    last_qgl = total_qgl[-1] if total_qgl else 0
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_INCH, 5.0))
    ax.plot(total_qgl, total_production, "o-", color="#2b6cb0", linewidth=1.2, markersize=5, label="Total production")
    ax.axhline(y=last_production, color="#c53030", linestyle="--", linewidth=1.0, label=f"Last: {last_production:.2f} bbl")
    ax.plot(last_qgl, last_production, "+", color="#c53030", markersize=12, markeredgewidth=2.5)
    ax.annotate(f"({last_qgl:.0f}, {last_production:.2f})", xy=(last_qgl, last_production), xytext=(-8, -12), textcoords="offset points", fontsize=9, color="#c53030", horizontalalignment="right")
    ax.set_xlabel("Total gas injection limit (Mscf)", fontsize=11)
    ax.set_ylabel("Total oil production (bbl)", fontsize=11)
    ax.tick_params(axis="both", labelsize=10)
    ax.minorticks_on()
    ax.grid(True, which="major", linestyle=":", alpha=0.6)
    ax.grid(True, which="minor", linestyle="--", alpha=0.35)
    ax.legend(loc="lower right", ncol=2, fontsize=10, framealpha=0.95)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    return fig


def _build_well_curves_figure(constrained_results: dict, well_results: list):
    plot_data = constrained_results.get("plot_data") or []
    p_qgl_list = constrained_results.get("p_qgl_optim_list") or []
    p_qoil_list = constrained_results.get("p_qoil_optim_list") or []
    q_gl_common = constrained_results.get("q_gl_common_range")
    if not plot_data or not well_results or q_gl_common is None or len(q_gl_common) == 0:
        return None
    n = len(well_results)
    ncols = 2
    nrows = max(1, (n + ncols - 1) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(FIG_WIDTH_INCH, 2.35 * nrows))
    axes = np.atleast_2d(axes).flatten()
    for idx in range(len(well_results)):
        ax = axes[idx]
        well_data = plot_data[idx] if idx < len(plot_data) else {}
        well_result = well_results[idx]
        _q = well_data.get("q_gl_common_range")
        _f = well_data.get("q_fluid_predicted")
        _o = well_data.get("q_oil_predicted")
        _qo = well_data.get("q_gl_original")
        _fo = well_data.get("q_fluid_original")
        qgl = list(_q) if _q is not None else []
        fluid = list(_f) if _f is not None else []
        oil = list(_o) if _o is not None else []
        qgl_orig = list(_qo) if _qo is not None else []
        fluid_orig = list(_fo) if _fo is not None else []
        if len(qgl) > 0 and (len(fluid) > 0 or len(oil) > 0):
            ax.plot(qgl, fluid, "-", color="#dd6b20", linewidth=1.2, label="Fluid")
            ax.plot(qgl, oil, "-", color="#276749", linewidth=1.2, label="Oil")
            if len(qgl_orig) > 0 and len(fluid_orig) > 0:
                ax.plot(qgl_orig, fluid_orig, "o", color="#2b6cb0", markersize=5, label="_nolegend_")
        optimal_qgl = getattr(well_result, "optimal_gas_injection", None)
        optimal_prod = getattr(well_result, "optimal_production", None)
        if optimal_qgl is not None and len(fluid) > 0 and len(qgl) > 0:
            try:
                i_opt = list(qgl).index(optimal_qgl)
                opt_fluid = fluid[i_opt] if i_opt < len(fluid) else 0
            except (ValueError, IndexError):
                opt_fluid = 0
            ax.axvline(x=optimal_qgl, color="#c53030", linestyle="--", linewidth=1.0)
            ax.plot(optimal_qgl, optimal_prod, "+", color="#c53030", markersize=10, markeredgewidth=2.5)
            ax.annotate(f"({optimal_qgl:.0f}, {optimal_prod:.1f})", xy=(optimal_qgl, optimal_prod), xytext=(8, -10), textcoords="offset points", fontsize=8, color="#c53030")
        mrp_qgl = p_qgl_list[idx] if idx < len(p_qgl_list) else None
        if mrp_qgl is not None and len(fluid) > 0 and len(qgl) > 0:
            try:
                i_mrp = list(q_gl_common).index(mrp_qgl)
                mrp_fluid = fluid[i_mrp] if i_mrp < len(fluid) else 0
            except (ValueError, IndexError, TypeError):
                mrp_fluid = 0
            mrp_oil = p_qoil_list[idx] if idx < len(p_qoil_list) else 0
            ax.axvline(x=mrp_qgl, color="#4a5568", linestyle="--", linewidth=1.0)
            ax.plot(mrp_qgl, mrp_fluid, "+", color="#4a5568", markersize=5)
            ax.plot(mrp_qgl, mrp_oil, "+", color="#4a5568", markersize=10, markeredgewidth=2.5)
            ax.annotate(f"({mrp_qgl:.0f}, {mrp_oil:.1f})", xy=(mrp_qgl, mrp_oil), xytext=(8, -10), textcoords="offset points", fontsize=8, color="#4a5568")
        well_name = getattr(well_result, "well_name", f"Well {idx+1}")
        ax.text(0.02, 0.98, well_name, transform=ax.transAxes, fontsize=9, verticalalignment="top", horizontalalignment="left")
        if idx % ncols == 0:
            ax.set_ylabel("Fluid / Oil rate", fontsize=10)
        else:
            ax.set_ylabel("")
        if idx >= n - ncols:
            ax.set_xlabel("Gas lift rate (Mscf)", fontsize=10)
        else:
            ax.set_xlabel("")
        ax.tick_params(axis="both", labelsize=9)
        ax.legend(loc="lower right", ncol=2, fontsize=8, framealpha=0.95)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_facecolor("#fafafa")
    for idx in range(len(well_results), len(axes)):
        axes[idx].set_visible(False)
    fig.patch.set_facecolor("white")
    plt.tight_layout(pad=1.0, h_pad=0.3, w_pad=0.25)
    return fig


class OptimizationReportGenerator:
    """Builds a PDF report with reportlab; figures as vector PDF (pdfrw) or PNG."""

    def __init__(
        self,
        constrained_optimization_results: Optional[dict] = None,
        well_results: Optional[list] = None,
        global_optimization_results: Optional[dict] = None,
        list_info: Optional[list] = None,
    ):
        self.constrained_results = constrained_optimization_results
        self.well_results = well_results or []
        self.global_results = global_optimization_results
        self.list_info = list_info or ["Unknown Field"]

    def build_pdf(self) -> bytes:
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("reportlab is required. Install with: pip install reportlab")
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN_INCH * inch,
            leftMargin=MARGIN_INCH * inch,
            topMargin=MARGIN_INCH * inch,
            bottomMargin=MARGIN_INCH * inch,
        )
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

        story: List[Any] = []
        story.append(Paragraph("Gas Lift Optimization Report", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        story.append(Spacer(1, 0.12 * inch))
        story.append(Paragraph(
            "This report presents the results of gas lift allocation optimization for the selected field. "
            "Section 1 summarizes the constrained optimization under a fixed total gas injection limit and "
            "provides well-by-well performance curves and optimal allocations. Section 2 presents the global "
            "optimization curve relating total gas limit to total production.",
            body_style,
        ))
        story.append(Spacer(1, 0.1 * inch))

        has_constrained = (
            self.constrained_results is not None
            and "summary" in (self.constrained_results or {})
            and self.well_results
        )
        has_global = self.global_results is not None and "summary" in (self.global_results or {})

        if has_constrained:
            self._add_constrained_section(story, heading_style, subheading_style, body_style, caption_style, styles)
        if has_global:
            self._add_global_section(story, heading_style, subheading_style, body_style, caption_style, styles)
        if not has_constrained and not has_global:
            story.append(Paragraph("No optimization results available for this report.", styles["Normal"]))

        doc.build(story)
        buffer.seek(0)
        base_pdf_bytes = buffer.getvalue()

        # Optionally append vector-figure pages as an appendix using pypdf
        if not PYPDF_AVAILABLE:
            return base_pdf_bytes

        writer = PdfWriter()
        main_reader = PdfReader(BytesIO(base_pdf_bytes))
        for page in main_reader.pages:
            writer.add_page(page)

        # Append figures as full-page vector PDFs (one page per figure)
        if has_constrained:
            fig = _build_well_curves_figure(self.constrained_results, self.well_results)
            if fig is not None:
                wells_buf = _fig_to_pdf_buffer(fig)
                wells_reader = PdfReader(wells_buf)
                for p in wells_reader.pages:
                    writer.add_page(p)

        if has_global:
            fig = _build_global_curve_figure(self.global_results)
            if fig is not None:
                global_buf = _fig_to_pdf_buffer(fig)
                global_reader = PdfReader(global_buf)
                for p in global_reader.pages:
                    writer.add_page(p)

        out = BytesIO()
        writer.write(out)
        out.seek(0)
        return out.getvalue()

    def _add_constrained_section(self, story, heading_style, subheading_style, body_style, caption_style, styles):
        story.append(Paragraph("1. Constrained Optimization", heading_style))
        story.append(Paragraph(
            "Under a fixed total gas lift limit, the optimizer allocates gas across wells to maximize "
            "total oil production. The following table summarizes aggregate results; the allocation table "
            "and curves show the recommended rate per well and the predicted response.",
            body_style,
        ))
        story.append(Spacer(1, 0.08 * inch))
        summary = self.constrained_results["summary"]
        df_summary = pd.DataFrame({
            "Metric": ["Gas lift rate (mscfd)", "Oil rate (bopd)"],
            "Value": [f"{summary['total_qgl']:.2f}", f"{summary['total_production']:.2f}"],
        })
        table_data = [df_summary.columns.tolist()] + df_summary.values.tolist()
        t = Table(table_data, colWidths=[3.2 * inch, 1.8 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER_BG)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), f"{FONT_NAME}-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(COLOR_ROW_ALT)]),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor(COLOR_TABLE_BORDER)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Optimal allocation by well", subheading_style))
        story.append(Paragraph(
            "Recommended gas lift rate and predicted oil rate for each well under the configured total gas limit.",
            body_style,
        ))
        story.append(Spacer(1, 0.06 * inch))
        well_data = [
            {
                "Well identifier": getattr(r, "well_name", "N/A"),
                "Gas lift rate (Mscf)": getattr(r, "optimal_gas_injection", 0),
                "Oil rate (bopd)": getattr(r, "optimal_production", 0),
            }
            for r in self.well_results
        ]
        df_wells = pd.DataFrame(well_data)
        table_data = [df_wells.columns.tolist()] + [
            [str(row["Well identifier"]), f"{row['Gas lift rate (Mscf)']:.0f}", f"{row['Oil rate (bopd)']:.0f}"]
            for _, row in df_wells.iterrows()
        ]
        tw = Table(table_data, colWidths=[1.2 * inch, 1.6 * inch, 1.4 * inch])
        tw.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER_BG)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), f"{FONT_NAME}-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(COLOR_ROW_ALT)]),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor(COLOR_TABLE_BORDER)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tw)
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Production performance by well", subheading_style))
        story.append(Paragraph(
            "Predicted fluid and oil rate vs. gas lift rate for each well. Dashed vertical line: optimal allocation; dotted: MRP.",
            body_style,
        ))
        story.append(Spacer(1, 0.06 * inch))
        try:
            fig = _build_well_curves_figure(self.constrained_results, self.well_results)
            if fig is not None:
                nrows = max(1, (len(self.well_results) + 1) // 2)
                w_pt = FIG_WIDTH_INCH * inch
                h_pt = min(2.35 * inch * nrows, 8 * inch)
                buf = _fig_to_image_buffer(fig, dpi=300)
                story.append(RLImage(buf, width=w_pt, height=h_pt))
                story.append(Paragraph(
                    "Figure 1. Predicted fluid and oil rate vs. gas lift rate by well. "
                    "Dashed vertical line: optimal allocation; dotted: MRP point. Adjusted curves and real data where available.",
                    caption_style,
                ))
            else:
                story.append(Paragraph("[Insufficient data for well curves.]", styles["Normal"]))
        except Exception as e:
            story.append(Paragraph(f"[Well curves could not be generated: {e}]", styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))

    def _add_global_section(self, story, heading_style, subheading_style, body_style, caption_style, styles):
        story.append(Paragraph("2. Global Optimization", heading_style))
        story.append(Paragraph(
            "The global optimization explores how total production varies with the total gas injection limit. "
            "The curve below shows the production frontier; the horizontal line indicates the production level "
            "at the last evaluated limit.",
            body_style,
        ))
        story.append(Spacer(1, 0.08 * inch))
        summary = self.global_results["summary"]
        df_summary = pd.DataFrame({
            "Metric": ["Gas lift rate (mscfd)", "Oil rate (bopd)"],
            "Value": [f"{summary['total_qgl']:.2f}", f"{summary['total_production']:.2f}"],
        })
        table_data = [df_summary.columns.tolist()] + df_summary.values.tolist()
        t = Table(table_data, colWidths=[3.2 * inch, 1.8 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER_BG)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), f"{FONT_NAME}-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(COLOR_ROW_ALT)]),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor(COLOR_TABLE_BORDER)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Total production vs gas injection limit", subheading_style))
        story.append(Paragraph(
            "Total oil production as a function of the total gas injection limit. The horizontal line indicates production at the last evaluated limit.",
            body_style,
        ))
        story.append(Spacer(1, 0.06 * inch))
        try:
            fig = _build_global_curve_figure(self.global_results)
            if fig is not None:
                w_pt = FIG_WIDTH_INCH * inch
                h_pt = 4.75 * inch
                buf = _fig_to_image_buffer(fig, dpi=300)
                story.append(RLImage(buf, width=w_pt, height=h_pt))
                story.append(Paragraph(
                    "Figure 2. Total oil production vs. total gas injection limit (Mscf). "
                    "The horizontal line marks production at the last limit.",
                    caption_style,
                ))
            else:
                story.append(Paragraph("[Insufficient data for global curve.]", styles["Normal"]))
        except Exception as e:
            story.append(Paragraph(f"[Global curve could not be generated: {e}]", styles["Normal"]))

    def save_pdf(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.build_pdf())