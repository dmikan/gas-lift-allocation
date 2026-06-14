from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer

from frontend.components.optimization.reports.styles import get_report_styles, MARGIN_INCH, FIG_WIDTH_INCH
from frontend.components.optimization.reports.chart_builder import (
    build_well_curves_figure,
    build_global_curve_figure,
)
from frontend.components.optimization.reports.table_builder import create_styled_table
from frontend.components.optimization.reports.pdf_merger import merge_pdf_appendices
from svglib.svglib import svg2rlg
import matplotlib.pyplot as plt

def fig_to_vector_drawing(fig) -> Any:
    buf = BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", facecolor="white")
    buf.seek(0)
    drawing = svg2rlg(buf)
    plt.close(fig)
    return drawing

class OptimizationReportGenerator:
    """Builds a PDF report with reportlab; figures as vector Drawings."""

    def __init__(
        self,
        constrained_optimization_results: Optional[dict] = None,
        well_results: Optional[list] = None,
        global_optimization_results: Optional[dict] = None,
        list_info: Optional[list] = None,
        well_tests: Optional[list] = None,
        oil_opt_at_baseline: Optional[float] = None,
    ):
        self.constrained_results = constrained_optimization_results
        self.well_results = well_results or []
        self.global_results = global_optimization_results
        self.list_info = list_info or ["Unknown Field"]
        self.well_tests = well_tests or []
        self.oil_opt_at_baseline = oil_opt_at_baseline

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_pdf(self) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN_INCH * inch,
            leftMargin=MARGIN_INCH * inch,
            topMargin=MARGIN_INCH * inch,
            bottomMargin=MARGIN_INCH * inch,
        )

        cfg = get_report_styles()
        styles = cfg["styles"]
        title_style = cfg["title"]
        subtitle_style = cfg["subtitle"]
        body_style = cfg["body"]
        heading_style = cfg["heading"]
        subheading_style = cfg["subheading"]
        caption_style = cfg["caption"]

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
            and "summary" in self.constrained_results
            and bool(self.well_results)
        )
        has_global = self.global_results is not None and "summary" in self.global_results

        if has_constrained:
            self._add_constrained_section(story, heading_style, subheading_style, body_style, caption_style, styles)
        if has_global:
            self._add_global_section(story, heading_style, subheading_style, body_style, caption_style, styles)
        if not has_constrained and not has_global:
            story.append(Paragraph("No optimization results available for this report.", styles["Normal"]))

        doc.build(story)
        buffer.seek(0)

        return merge_pdf_appendices(
            buffer.getvalue(),
            has_constrained,
            has_global,
            self.constrained_results,
            self.well_results,
            self.global_results,
        )

    def save_pdf(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.build_pdf())

    # ------------------------------------------------------------------
    # Constrained section
    # ------------------------------------------------------------------

    def _add_constrained_section(self, story, heading_style, subheading_style, body_style, caption_style, styles):
        story.append(Paragraph("1. Constrained Optimization", heading_style))
        story.append(Paragraph(
            "Under a fixed total gas lift limit, the optimizer allocates gas across wells to maximize "
            "total oil production. The table below compares the latest well test values against the "
            "recommended optimal allocation, followed by well-level production curves.",
            body_style,
        ))
        story.append(Spacer(1, 0.08 * inch))

        # ---- Summary metrics ----
        summary = self.constrained_results["summary"]
        story.append(Paragraph("Summary metrics", subheading_style))
        story.append(Spacer(1, 0.04 * inch))

        summary_rows = [
            ("Total Production (bopd)", f"{summary['total_production']:.0f}"),
            ("QGL Input (mscfd)", f"{summary['qgl_limit']:.0f}"),
        ]

        # Marginal productivity — mirrors display_constrained_results.show_summary_metrics
        if self.well_tests:
            total_test_oil = sum(getattr(t, "q_oil", 0) for t in self.well_tests)
            total_test_qgl = sum(getattr(t, "q_gl", 0) for t in self.well_tests)
            baseline_mp = (total_test_oil / total_test_qgl) if total_test_qgl > 0 else 0

            optimized_oil = summary["total_production"]
            optimized_qgl = summary.get("total_qgl", 0)
            optimized_mp = (optimized_oil / optimized_qgl) if optimized_qgl > 0 else 0

            summary_rows.append(("Baseline Marginal Productivity (bopd/mscfd)", f"{baseline_mp:.2f}"))

            if baseline_mp > 0:
                delta_pct = ((optimized_mp - baseline_mp) / baseline_mp) * 100
                optimized_mp_label = f"{optimized_mp:.2f}  ({delta_pct:+.1f}% efficiency)"
            else:
                optimized_mp_label = f"{optimized_mp:.2f}"
            summary_rows.append(("Optimized Marginal Productivity (bopd/mscfd)", optimized_mp_label))

        df_summary = pd.DataFrame(summary_rows, columns=["Metric", "Value"])
        story.append(create_styled_table(df_summary, [3.6 * inch, 2.4 * inch]))
        story.append(Spacer(1, 0.22 * inch))

        # ---- Test vs. Optimal comparison table ----
        story.append(Paragraph("Well test values vs. optimal allocation", subheading_style))
        story.append(Paragraph(
            "Columns show the latest production test data alongside the recommended gas lift and oil "
            "rates from the constrained optimization.",
            body_style,
        ))
        story.append(Spacer(1, 0.06 * inch))
        story.append(self._build_comparison_table(styles))
        story.append(Spacer(1, 0.22 * inch))

        # ---- Production performance curves ----
        story.append(Paragraph("Production performance by well", subheading_style))
        story.append(Paragraph(
            "Predicted fluid and oil rate vs. gas lift rate for each well. "
            "Dashed vertical line: optimal allocation; dotted: MRP.",
            body_style,
        ))
        story.append(Spacer(1, 0.06 * inch))
        try:
            figs = build_well_curves_figure(self.constrained_results, self.well_results, well_tests=self.well_tests)
            if figs:
                for fig in figs:
                    drawing = fig_to_vector_drawing(fig)
                    story.append(drawing)
                    story.append(Spacer(1, 0.15 * inch))
                story.append(Paragraph(
                    "Figure 1. Predicted fluid and oil rate vs. gas lift rate by well. "
                    "Dashed vertical line: optimal allocation; dotted: MRP point.",
                    caption_style,
                ))
            else:
                story.append(Paragraph("[Insufficient data for well curves.]", styles["Normal"]))
        except Exception as e:
            story.append(Paragraph(f"[Well curves could not be generated: {e}]", styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))

    def _build_comparison_table(self, styles):
        """Build a flat ReportLab table that mirrors the multi-index Streamlit dataframe."""
        # Map well_tests by well name for O(1) lookup
        test_map = {}
        for t in self.well_tests:
            name = getattr(t, "wellbore_ci_name", None) or getattr(t, "well_name", "")
            test_map[name] = t

        rows = []
        total_test_qgl = 0.0
        total_test_oil = 0.0
        total_test_fluid = 0.0
        total_opt_qgl = 0.0
        total_opt_oil = 0.0

        for r in self.well_results:
            wname = getattr(r, "well_name", "N/A")
            t = test_map.get(wname)
            test_date = str(getattr(t, "test_date", "N/A"))[:10] if t else "N/A"
            t_qgl = getattr(t, "q_gl", 0) if t else 0
            t_oil = getattr(t, "q_oil", 0) if t else 0
            t_fluid = getattr(t, "q_liquid", 0) if t else 0
            o_qgl = getattr(r, "optimal_gas_injection", 0)
            o_oil = getattr(r, "optimal_production", 0)

            rows.append([
                wname,
                test_date,
                f"{t_qgl:.0f}",
                f"{t_oil:.0f}",
                f"{t_fluid:.0f}",
                f"{o_qgl:.0f}",
                f"{o_oil:.0f}",
            ])
            total_test_qgl += t_qgl
            total_test_oil += t_oil
            total_test_fluid += t_fluid
            total_opt_qgl += o_qgl
            total_opt_oil += o_oil

        # Totals row
        rows.append([
            "Total", "",
            f"{total_test_qgl:.0f}",
            f"{total_test_oil:.0f}",
            f"{total_test_fluid:.0f}",
            f"{total_opt_qgl:.0f}",
            f"{total_opt_oil:.0f}",
        ])

        headers = [
            "Well",
            "Test Date",
            "Test QGL\n(mscfd)",
            "Test Oil\n(bopd)",
            "Test Fluid\n(bfpd)",
            "Opt. QGL\n(mscfd)",
            "Opt. Oil\n(bopd)",
        ]
        col_widths = [1.1 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch]

        df = pd.DataFrame(rows, columns=headers)
        return create_styled_table(df, col_widths, bold_last_row=True)

    # ------------------------------------------------------------------
    # Global section
    # ------------------------------------------------------------------

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

        # ---- Summary metrics (mirrors display_global_results) ----
        story.append(Paragraph("Summary metrics", subheading_style))
        story.append(Spacer(1, 0.04 * inch))

        summary_rows = [
            ("Physical oil production limit (bopd)", f"{summary['total_production']:.0f}"),
            ("Total QGL to achieve physical limit (mscfd)", f"{summary['total_qgl']:.0f}"),
        ]

        # Incremental production vs. last well tests
        if self.well_tests:
            total_test_oil = sum(getattr(t, "q_oil", 0) for t in self.well_tests)
            optimized_oil = summary["total_production"]
            incremental = optimized_oil - total_test_oil
            if total_test_oil > 0:
                pct = (incremental / total_test_oil) * 100
                inc_label = f"{incremental:+.0f}  ({pct:+.1f}% vs last tests)"
            else:
                inc_label = f"{incremental:+.0f}"
            summary_rows.append(("Incremental Production (bopd)", inc_label))

            if self.oil_opt_at_baseline is not None:
                baseline_qgl = sum(getattr(t, "q_gl", 0) for t in self.well_tests)
                diff_bopd = self.oil_opt_at_baseline - total_test_oil
                diff_pct = (diff_bopd / total_test_oil * 100) if total_test_oil > 0 else 0.0
                summary_rows.append(("QGL Baseline", f"{baseline_qgl:.0f} mscfd"))
                summary_rows.append(("Opt. Gain at Baseline QGL", f"{diff_bopd:+.0f} bopd ({diff_pct:+.1f}% vs baseline)"))
                

        df_summary = pd.DataFrame(summary_rows, columns=["Metric", "Value"])
        story.append(create_styled_table(df_summary, [3.6 * inch, 2.4 * inch]))
        story.append(Spacer(1, 0.2 * inch))

        # ---- Global curve ----
        story.append(Paragraph("Total production vs gas injection limit", subheading_style))
        story.append(Paragraph(
            "Total oil production as a function of the total gas injection limit. "
            "The horizontal line indicates production at the last evaluated limit. "
            "★ marks the baseline (last well tests); + marks the optimized baseline QGL.",
            body_style,
        ))
        story.append(Spacer(1, 0.06 * inch))
        try:
            # Compute baseline totals from well tests for the chart
            baseline_qgl = None
            baseline_prod = None
            if self.well_tests:
                baseline_qgl = sum(getattr(t, "q_gl", 0) for t in self.well_tests)
                baseline_prod = sum(getattr(t, "q_oil", 0) for t in self.well_tests)

            fig = build_global_curve_figure(
                self.global_results,
                baseline_qgl=baseline_qgl,
                baseline_production=baseline_prod,
                oil_opt_at_baseline=self.oil_opt_at_baseline,
            )
            if fig is not None:
                drawing = fig_to_vector_drawing(fig)
                story.append(drawing)
                story.append(Paragraph(
                    "Figure 2. Total oil production vs. total gas injection limit (Mscf). "
                    "The horizontal line marks production at the last limit. "
                    "★ = baseline from last well tests; + = optimized at baseline QGL.",
                    caption_style,
                ))
            else:
                story.append(Paragraph("[Insufficient data for global curve.]", styles["Normal"]))
        except Exception as e:
            story.append(Paragraph(f"[Global curve could not be generated: {e}]", styles["Normal"]))
