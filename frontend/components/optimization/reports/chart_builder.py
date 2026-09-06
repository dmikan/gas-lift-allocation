from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from frontend.components.optimization.reports.styles import FIG_WIDTH_INCH

def fig_to_image_buffer(fig, dpi: int = 150) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    plt.close(fig)
    return buf

def fig_to_pdf_buffer(fig) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="pdf", bbox_inches="tight", facecolor="white")
    buf.seek(0)
    plt.close(fig)
    return buf

def build_global_curve_figure(
    global_results: dict,
    baseline_qgl: float | None = None,
    baseline_production: float | None = None,
    oil_opt_at_baseline: float | None = None,
):
    total_qgl = list(global_results.get("total_qgl") or [])
    total_production = list(global_results.get("total_production") or [])
    if not total_qgl or not total_production:
        return None
    last_prod, last_qgl = total_production[-1], total_qgl[-1]

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_INCH, 5.0))
    ax.plot(total_qgl, total_production, "o-", color="#2b6cb0", linewidth=1.2, markersize=5, label="Max total production")
    ax.axhline(y=last_prod, color="#c53030", linestyle="--", linewidth=1.0, label=f"Physical productionlimit: {last_prod:.0f} bopd")

    # Baseline (last well tests) star marker — mirrors the UI Plotly chart
    if baseline_qgl is not None and baseline_production is not None:
        ax.plot(
            baseline_qgl, baseline_production,
            marker="*", color="#FF5252", markersize=10, linestyle="None",
            label=f"Baseline tests",
        )
        ax.annotate(
            f"({baseline_qgl:.0f}, {baseline_production:.0f})",
            xy=(baseline_qgl, baseline_production),
            xytext=(-30, -10),
            textcoords="offset points",
            fontsize=8,
            color="#FF5252",
        )

    # Green + marker for optimized production at baseline QGL limit
    if baseline_qgl is not None and oil_opt_at_baseline is not None:
        ax.plot(
            baseline_qgl, oil_opt_at_baseline,
            marker="+", color="#276749", markersize=12, markeredgewidth=2.5, linestyle="None",
            label="Maximal oil production with current gas available",
        )
        ax.annotate(
            f"({baseline_qgl:.0f}, {oil_opt_at_baseline:.0f})",
            xy=(baseline_qgl, oil_opt_at_baseline),
            xytext=(10, -10),
            textcoords="offset points",
            fontsize=8,
            color="#276749",
        )

    #TODO: modify name qgl_limit to qgl_available in UI and backend for clarity
    ax.set_xlabel("Total gas injection available (mscfd)", fontsize=10)
    ax.set_ylabel("Maximal oil production (bopd)", fontsize=10)
    ax.minorticks_on()
    ax.grid(True, which="major", linestyle=":", alpha=0.6)
    ax.grid(True, which="minor", linestyle="--", alpha=0.35)
    ax.legend(loc="lower right", ncol=1, fontsize=8, framealpha=0.0)
    ax.set_facecolor("#fafafa")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    return fig

def build_well_curves_figure(constrained_results: dict, well_results: list, well_tests: list | None = None) -> list:
    plot_data = constrained_results.get("plot_data") or []
    p_qgl_list = constrained_results.get("p_qgl_optim_list") or []
    p_qoil_list = constrained_results.get("p_qoil_optim_list") or []
    q_gl_common = constrained_results.get("q_gl_common_range")
    if not plot_data or not well_results or q_gl_common is None or len(q_gl_common) == 0:
        return []

    # Build a name→test lookup, matching the Plotter logic
    test_map = {}
    for t in (well_tests or []):
        name = getattr(t, "wellbore_ci_name", None) or getattr(t, "well_name", "")
        if name:
            test_map[name] = t

    figs = []
    for idx, well_result in enumerate(well_results):
        fig, ax = plt.subplots(figsize=(FIG_WIDTH_INCH, 5.0))
        well_data = plot_data[idx] if idx < len(plot_data) else {}
        qgl = list(well_data.get("q_gl_common_range") or [])
        fluid = list(well_data.get("q_fluid_predicted") or [])
        oil = list(well_data.get("q_oil_predicted") or [])

        if qgl and (fluid or oil):
            ax.plot(qgl, fluid, "-", color="#dd6b20", linewidth=1.4, label="Fluid")
            ax.plot(qgl, oil, "-", color="#276749", linewidth=1.4, label="Oil")
            orig_qgl = list(well_data.get("q_gl_original") or [])
            orig_fluid = list(well_data.get("q_fluid_original") or [])
            if orig_qgl and orig_fluid:
                wct = well_data.get("wct", 0.0)
                orig_oil = [y_val * (1 - wct) for y_val in orig_fluid]
                ax.plot(orig_qgl, orig_fluid, "o", color="#dd6b20", markersize=5, alpha=0.5, label="Fluid Tests")
                ax.plot(orig_qgl, orig_oil, "o", color="#276749", markersize=5, alpha=0.5, label="Oil Tests")

            # Subtle fills under the curves up to opt_qgl
            opt_qgl = getattr(well_result, "optimal_gas_injection", None)
            if opt_qgl is not None:
                qgl_arr = np.array(qgl)
                oil_arr = np.array(oil)
                fluid_arr = np.array(fluid)
                if len(oil_arr) > 0 and len(fluid_arr) > 0:
                    valid_idx = np.where(oil_arr > 0.1)[0]
                    start_idx = valid_idx[0] if len(valid_idx) > 0 else 0
                    
                    fill_mask = (qgl_arr >= qgl_arr[start_idx]) & (qgl_arr <= opt_qgl)
                    if np.any(fill_mask):
                        fill_qgl = qgl_arr[fill_mask]
                        fill_oil = oil_arr[fill_mask]
                        fill_fluid = fluid_arr[fill_mask]
                        if fill_qgl[-1] < opt_qgl:
                            opt_oil_val = np.interp(opt_qgl, qgl_arr, oil_arr)
                            opt_fluid_val = np.interp(opt_qgl, qgl_arr, fluid_arr)
                            fill_qgl = np.append(fill_qgl, opt_qgl)
                            fill_oil = np.append(fill_oil, opt_oil_val)
                            fill_fluid = np.append(fill_fluid, opt_fluid_val)
                        
                        # Fill Fluid area in subtle orange
                        ax.fill_between(fill_qgl, fill_fluid, color="#dd6b20", alpha=0.10)
                        # Fill Oil area in subtle green
                        ax.fill_between(fill_qgl, fill_oil, color="#276749", alpha=0.15)

        opt_qgl = getattr(well_result, "optimal_gas_injection", None)
        opt_prod = getattr(well_result, "optimal_production", None)
        if opt_qgl is not None and fluid and qgl:
            qgl_arr = np.array(qgl)
            fluid_arr = np.array(fluid)
            opt_fluid_val = np.interp(opt_qgl, qgl_arr, fluid_arr)

            # Green dashed line from y=0 to y=opt_prod (Oil)
            ax.vlines(x=opt_qgl, ymin=0, ymax=opt_prod, colors="#05693A", linestyles="--", linewidths=1.0)
            # Orange dashed line from y=opt_prod to y=opt_fluid (Fluid)
            ax.vlines(x=opt_qgl, ymin=opt_prod, ymax=opt_fluid_val, colors="#dd6b20", linestyles="--", linewidths=1.0)

            # Oil intersection marker (+)
            ax.plot(opt_qgl, opt_prod, "+", color="#05693A", markersize=10, markeredgewidth=2.5, label=f"Opt. Oil")
            # Fluid intersection marker (+)
            ax.plot(opt_qgl, opt_fluid_val, "+", color="#dd6b20", markersize=10, markeredgewidth=2.5, label=f"Opt. Fluid")
            ax.annotate(f"({opt_qgl:.0f}, {opt_prod:.0f})", xy=(opt_qgl, opt_prod), xytext=(-50, 6), textcoords="offset points", fontsize=8, color="#05693A")
            ax.annotate(f"({opt_qgl:.0f}, {opt_fluid_val:.0f})", xy=(opt_qgl, opt_fluid_val), xytext=(-50, 6), textcoords="offset points", fontsize=8, color="#dd6b20")

        mrp_qgl = p_qgl_list[idx] if idx < len(p_qgl_list) else None
        if mrp_qgl is not None and fluid and qgl:
            qgl_arr_mrp = np.array(qgl)
            fluid_arr_mrp = np.array(fluid)
            mrp_fluid_val = np.interp(mrp_qgl, qgl_arr_mrp, fluid_arr_mrp)
            # Dashed line from y=0 to fluid curve intersection
            ax.vlines(x=mrp_qgl, ymin=0, ymax=mrp_fluid_val, colors="#4a5568", linestyles="--", linewidths=1.0, label="MRP limit")
            #ax.plot(mrp_qgl, mrp_fluid_val, "+", color="#4a5568", markersize=10, markeredgewidth=2.5)
            #ax.annotate(f"({mrp_qgl:.0f}, {mrp_fluid_val:.0f})", xy=(mrp_qgl, mrp_fluid_val), xytext=(-50, 6), textcoords="offset points", fontsize=8, color="#4a5568")

        # ---- Baseline test markers (mirrors Oil Last Test ♦ and Fluid Last Test ★ in UI) ----
        test = test_map.get(getattr(well_result, "well_name", ""))
        if test:
            t_qgl = getattr(test, "q_gl", 0)
            t_oil = getattr(test, "q_oil", 0)
            t_fluid = getattr(test, "q_liquid", 0)
            # Oil Last Test — red diamond
            ax.plot(t_qgl, t_oil, marker="D", color="#FF5252", markersize=7, linestyle="None",
                    label="Oil Last Test")
            ax.annotate(f"({t_qgl:.0f}, {t_oil:.0f})", xy=(t_qgl, t_oil),
                        xytext=(8, 6), textcoords="offset points", fontsize=8, color="#FF5252")
            # Fluid Last Test — red star
            ax.plot(t_qgl, t_fluid, marker="*", color="#FF5252", markersize=10, linestyle="None",
                    label="Fluid Last Test")
            ax.annotate(f"({t_qgl:.0f}, {t_fluid:.0f})", xy=(t_qgl, t_fluid),
                        xytext=(8, 6), textcoords="offset points", fontsize=8, color="#FF5252")

        well_name = getattr(well_result, "well_name", f"Well {idx + 1}")
        num_labels = len(ax.get_legend_handles_labels()[1])
        ax.set_title(well_name, fontsize=10, fontweight="bold", loc="left", pad=4)
        ax.set_ylabel("Fluid / Oil rate (bfpd / bopd)", fontsize=10)
        ax.set_xlabel("Gas lift rate (mscfd)", fontsize=10)
        ax.tick_params(axis="both", labelsize=9)
        ax.legend(loc="upper left", ncol=1, fontsize=8, framealpha=0.0)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_facecolor("#fafafa")
        fig.patch.set_facecolor("white")
        plt.tight_layout(pad=1.2)
        figs.append(fig)

    return figs
