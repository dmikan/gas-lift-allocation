import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.feature_selection import mutual_info_regression

class HistoricalDataComponents:
    def __init__(self):
        self.url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRmXvqD6GKOM9XTV5AH5pdmrH-oYssC-mPQFPiKjQCECuJ6jngOtU3_h8Cs7H1GByGaHtguupTPe6RO/pub?output=csv'
        self.df = self.load_and_clean_data()
    
    def load_and_clean_data(self):
        """Carga y limpia los datos"""
        df = pd.read_csv(self.url)
        df = df.dropna()
        return df
    
    def render_scatter_plot(self):
        """Renderiza el gráfico de dispersión qgl vs ql"""
        st.subheader("Relación entre Gas y Líquido por Pozo")
        
        fig = px.scatter(
            self.df,
            x='qgl',
            y='ql',
            color='name',
            labels={'qgl': 'Caudal de Gas (qgl)', 'ql': 'Caudal de Líquido (ql)'},
            title='Relación entre Caudal de Gas y Líquido por Pozo'
        )
        
        fig.update_layout(
            height=600,
            width=800,
            legend_title_text='Pozo'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_mutual_info_heatmap(self):
        """Renderiza el heatmap compacto con ordenamiento descendente"""
        st.subheader("Importancia de Variables por Pozo (Mutual Information)")
        
        # Lista de pozos a analizar
        pozos = list(pd.unique(self.df['name']))
        resultados = []

        for well in pozos:
            df_pozo = self.df[self.df['name'] == well]
            X = df_pozo.drop(columns=['ql', 'name', 'date'], errors='ignore')
            y = df_pozo['ql']
            X = X.dropna(axis=1)
            
            if len(X) > 3 and not X.empty:
                mi_scores = mutual_info_regression(X, y, random_state=0)
                for var, score in zip(X.columns, mi_scores):
                    resultados.append({'Pozo': well, 'Variable': var, 'MI_Score': score})

        if not resultados:
            st.warning("No se pudieron calcular los scores de información mutua.")
            return

        mi_df = pd.DataFrame(resultados)
        heatmap_data = mi_df.pivot(index='Pozo', columns='Variable', values='MI_Score').fillna(0)
        
        if not heatmap_data.empty:
            # Ordenar columnas por importancia total
            heatmap_data = heatmap_data[heatmap_data.sum().sort_values(ascending=False).index]
            
            # Configuración inicial del orden (primera columna descendente)
            if 'sort_column' not in st.session_state:
                st.session_state.sort_column = heatmap_data.columns[0]
            
            # Crear botones de ordenamiento descendente para cada columna
            buttons = [
                dict(
                    args=[{"y": [heatmap_data.sort_values(by=col, ascending=False).index],
                          "x": [heatmap_data.columns],
                          "z": [heatmap_data.sort_values(by=col, ascending=False).values],
                          "text": [heatmap_data.sort_values(by=col, ascending=False).values.round(2)]}],
                    label=f"↓ {col}",
                    method="update"
                )
                for col in heatmap_data.columns
            ]

            # Crear el heatmap compacto
            fig = px.imshow(
                heatmap_data.sort_values(by=st.session_state.sort_column, ascending=False),
                height=300 + 15 * len(heatmap_data),  # Altura más compacta
                text_auto='.2f',
                aspect='auto',
                color_continuous_scale='Viridis',
                labels=dict(x="Variable", y="Pozo", color="Importancia"),
            )
            
            # Añadir botones de ordenamiento compactos
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        buttons=buttons,
                        pad={"r": 5, "t": 5, "b": 5},
                        showactive=True,
                        x=0.05,
                        xanchor="left",
                        y=1.05,  # Posición más ajustada
                        yanchor="bottom"
                    )
                ],
                font=dict(size=9),  # Fuente más pequeña
                xaxis=dict(
                    tickangle=45,
                    side="top",
                    title_standoff=10
                ),
                yaxis=dict(
                    title_standoff=10
                ),
                margin=dict(l=0, r=0, b=20, t=80),  # Márgenes reducidos
                title_x=0.05  # Alineación del título
            )
            
            # Añadir tooltips
            fig.update_traces(
                hovertemplate="<b>Pozo:</b> %{y}<br>" +
                              "<b>Variable:</b> %{x}<br>" +
                              "<b>Importancia:</b> %{z:.3f}<extra></extra>"
            )
            
            # Mostrar instrucciones compactas
            st.caption("Haz clic en los botones ↓ para ordenar por columna (mayor a menor)")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay suficientes datos para generar el heatmap.")