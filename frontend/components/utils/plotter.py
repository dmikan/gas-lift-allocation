import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import ceil

class Plotter:
    def __init__(self, optimization_results: dict):
        self.bg_color = "#0e1117"
        self.grid_color = "#37474F"
        self.text_color = "#FFFFFF"
        self.line_color = "#00E676"
        self.marker_color = "#C8E6C9"
        self.optimal_line_color = "#FF5252"
        self.last_value_line_color = "#FF1744"
        self.fluid_line_color = "#E0970E"
        self.marker_test_color = "#29B6F6"
        self.optimization_results = optimization_results
        self.baseline_qgl = None
        self.baseline_production = None

    '''
    Method to create a global optimization chart.
    This method is responsible for creating a global optimization chart using Plotly.
    It creates a line chart with markers for total production and a horizontal line for the last production value.
    '''
    def create_global_curve(self, baseline_qgl=None, baseline_production=None):
        self.baseline_qgl = baseline_qgl
        self.baseline_production = baseline_production
        last_production = self.optimization_results["total_production"][-1] if self.optimization_results["total_production"] else 0

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self.optimization_results["total_qgl"],
                y=self.optimization_results["total_production"],
                mode='lines+markers',
                name='Total Production',
                line=dict(width=3, color=self.line_color),
                marker=dict(color=self.marker_color, size=7),
                showlegend=True
            )
        )

        if self.baseline_qgl is not None and self.baseline_production is not None:
            fig.add_trace(
                go.Scatter(
                    x=[self.baseline_qgl],
                    y=[self.baseline_production],
                    mode='markers+text',
                    name='Last Tests Baseline',
                    marker=dict(color=self.optimal_line_color, size=12, symbol='star'),
                    text=["Baseline (Last Tests)"],
                    textposition="top center",
                    textfont=dict(color=self.optimal_line_color, size=11, weight="bold"),
                    showlegend=True
                )
            )

        fig.add_hline(
            y=last_production,
            line=dict(
                color=self.last_value_line_color,
                width=2,
                dash='dash'
            ),
            annotation_text=f'{last_production:.2f} bbl',
            annotation_position="bottom left",
            annotation_font=dict(color=self.last_value_line_color),
            name='Last Production'
        )

        fig.update_layout(
            xaxis=dict(
                title_text="Total Gas Injection Limit (qgl_limit)",
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                showgrid=True,
                gridwidth=1,
                dtick=1000,
                minor_griddash="dot",
            ),
            yaxis=dict(
                title_text="Total Oil Production (bbl)",
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color)
            ),
            height=600,
            width=900,
            plot_bgcolor=self.bg_color,
            paper_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color=self.text_color)
            ),
            margin=dict(l=50, r=50, b=80, t=80, pad=4)
        )
        return fig


    '''
    Method to create a well curves chart.
    This method is responsible for creating a well curves chart using Plotly.
    It creates a line chart with markers for production and gas injection, as well as optimal lines and optimal points.
    '''
    def create_well_curves(self, well_results, well_tests=None):
        # Create a mapping for quick well test lookup
        well_test_map = {}
        if well_tests:
            for test in well_tests:
                well_name = getattr(test, 'wellbore_ci_name', None)
                if well_name:
                    well_test_map[well_name] = test

        cols = 1
        rows = int(ceil(len(well_results) / cols))
        # Fixed pixel height per subplot and fixed gap; grid height excludes margins
        SUBPLOT_HEIGHT_PX = 300
        GAP_PX = 32
        MARGIN_TOP_PX = 48
        MARGIN_BOTTOM_PX = 60
        grid_height_px = rows * SUBPLOT_HEIGHT_PX + max(0, rows - 1) * GAP_PX
        # vertical_spacing = one gap as fraction of grid height (Plotly uses fraction per gap)
        VERTICAL_SPACING = (GAP_PX / grid_height_px) if rows > 1 else 0.02
        PLOT_HEIGHT = grid_height_px + MARGIN_TOP_PX + MARGIN_BOTTOM_PX
        # Equal row heights so each subplot gets the same share
        row_heights = [1.0] * rows

        fig_prod = make_subplots(
            cols=cols,
            rows=rows,
            subplot_titles=None,
            horizontal_spacing=0.08,
            vertical_spacing=VERTICAL_SPACING,
            row_heights=row_heights,
        )

        for idx, (well_data, well_result) in enumerate(zip(self.optimization_results['plot_data'], well_results)):
            row = (idx // 1) + 1
            col = (idx % 1) + 1

            optimal_qgl = well_result.optimal_gas_injection
            optimal_prod = well_result.optimal_production
            optimal_index = list(well_data["q_gl_common_range"]).index(optimal_qgl)
            optimal_fluid = list(well_data["q_fluid_predicted"])[optimal_index]

            MRP_qgl = self.optimization_results["p_qgl_optim_list"][idx]
            MRP_qgl_index = list(self.optimization_results["q_gl_common_range"]).index(MRP_qgl)
            MRP_fluid = list(well_data["q_fluid_predicted"])[MRP_qgl_index]


            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_common_range"],
                    y=well_data["q_fluid_predicted"],
                    mode='lines',
                    name='Adjusted Fluid Curve',
                    line=dict(width=3, color=self.fluid_line_color),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group1',
                    hovertemplate="QGL: %{x:.0f} mscfd<br>Fluid: %{y:.1f} bfpd<extra></extra>",
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_common_range"],
                    y=well_data["q_oil_predicted"],
                    mode='lines',
                    name='Adjusted Oil Curve',
                    line=dict(width=3, color=self.line_color),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group2',
                    hovertemplate="QGL: %{x:.0f} mscfd<br>Oil: %{y:.1f} bopd<extra></extra>",
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_original"],
                    y=well_data["q_fluid_original"],
                    mode='markers',
                    name='Real Data',
                    marker=dict(
                        color=self.marker_color,
                        size=7,
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group3'
                ),
                row=row, col=col
            )

            # 3. Óptimo según MRP
            fig_prod.add_trace(
                go.Scatter(
                    x=[self.optimization_results["p_qgl_optim_list"][idx], self.optimization_results["p_qgl_optim_list"][idx]],
                    y=[0, MRP_fluid],
                    mode='lines',
                    name='MRP Limit',
                    line=dict(color=self.marker_color, width=2, dash='dash'),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group4'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[self.optimization_results["p_qgl_optim_list"][idx]],
                    y=[self.optimization_results["p_qoil_optim_list"][idx]],
                    mode='markers',
                    name='MRP oil point',
                    marker=dict(
                        color=self.marker_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group8'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[self.optimization_results["p_qgl_optim_list"][idx]],
                    y=[MRP_fluid],
                    mode='markers',
                    name='MRP fluid point',
                    marker=dict(
                        color=self.marker_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group9'
                ),
                row=row, col=col
            )


            # Current actual values from the latest well test
            test_data = well_test_map.get(well_result.well_name)
            if test_data:
                current_qgl = getattr(test_data, 'q_gl', 0)
                current_oil = getattr(test_data, 'q_oil', 0)
                current_fluid = getattr(test_data, 'q_liquid', 0)

                # Marker for Current Oil Point
                fig_prod.add_trace(
                    go.Scatter(
                        x=[current_qgl],
                        y=[current_oil],
                        mode='markers+text',
                        name='Oil Last Test',
                        marker=dict(
                            color="#FF5252",
                            size=12,
                            symbol='diamond'
                        ),
                        text=["Oil Last Test"],
                        textposition="top center",
                        textfont=dict(color="#FF5252", size=11, weight="bold"),
                        showlegend=True if idx == 0 else False,
                        legendgroup='group10'
                    ),
                    row=row, col=col
                )

                # Marker for Current Fluid Point
                fig_prod.add_trace(
                    go.Scatter(
                        x=[current_qgl],
                        y=[current_fluid],
                        mode='markers+text',
                        name='Fluid Last Test',
                        marker=dict(
                            color="#FF5252",
                            size=12,
                            symbol='star'
                        ),
                        text=["Fluid Last Test"],
                        textposition="top center",
                        textfont=dict(color="#FF5252", size=11, weight="bold"),
                        showlegend=True if idx == 0 else False,
                        legendgroup='group11'
                    ),
                    row=row, col=col
                )

            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl, optimal_qgl],
                    y=[0, optimal_fluid],
                    mode='lines',
                    name='Optimal QGL',
                    line=dict(color=self.optimal_line_color, width=2, dash='dash'),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group5'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl],
                    y=[optimal_prod],
                    mode='markers',
                    name='Optimal Oil Point',
                    marker=dict(
                        color=self.optimal_line_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group6'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl],
                    y=[optimal_fluid],
                    mode='markers',
                    name='Optimal Fluid Point',
                    marker=dict(
                        color=self.optimal_line_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group7'
                ),
                row=row, col=col
            )

            # Axis labels only on bottom row (x) and left column (y) to avoid repetition
            x_title = "Gas lift rate (mscfd)" if row == rows else None
            y_title = "Fluid/Oil rate (bfpd/bopd)" if col == 1 else None
            qgl = well_data["q_gl_common_range"]
            if qgl is not None and len(qgl) > 0:
                x_min, x_max = float(min(qgl)), float(max(qgl))
            else:
                x_min, x_max = 0.0, 0.0
            fig_prod.update_xaxes(
                title_text=x_title,
                row=row, col=col,
                range=[x_min, x_max],
                showgrid=True,
                gridwidth=1,
                minor_griddash="dot",
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                showline=True,
                mirror=True,
            )
            fig_prod.update_yaxes(
                title_text=y_title,
                row=row, col=col,
                showgrid=False,
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                showline=True,
                mirror=True,
            )

            # Well name as annotation inside the subplot (top-left), equal margin from top and left
            xref = "x" if row == 1 else f"x{row}"
            yref = "y" if row == 1 else f"y{row}"
            y_vals = list(well_data["q_fluid_predicted"]) + list(well_data["q_oil_predicted"])
            y_min = float(min(y_vals)) if y_vals else 0.0
            y_max = float(max(y_vals)) if y_vals else 1.0
            x_range = x_max - x_min or 1.0
            y_range = y_max - y_min or 1.0
            inset_frac = 0.001
            ann_x = x_min + inset_frac * x_range
            ann_y = y_max - inset_frac * y_range
            fig_prod.add_annotation(
                x=ann_x,
                y=ann_y,
                xref=xref,
                yref=yref,
                text=f"<b>{well_result.well_name}</b>",
                showarrow=False,
                xanchor="left",
                yanchor="top",
                font=dict(size=13, color=self.text_color),
                bgcolor="rgba(34, 39, 46, 0.85)",
                borderpad=6,
                borderwidth=1,
                bordercolor="rgba(128, 128, 128, 0.3)",
            )

        fig_prod.update_layout(
            height=PLOT_HEIGHT,
            width=1200,
            plot_bgcolor=self.bg_color,
            paper_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            margin=dict(
                l=50,
                r=50,
                b=MARGIN_BOTTOM_PX,
                t=MARGIN_TOP_PX,
                pad=4
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color=self.text_color),
            ),
        )
        return fig_prod