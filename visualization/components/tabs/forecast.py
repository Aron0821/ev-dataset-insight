import streamlit as st
import plotly.graph_objects as go
from utils.ml_models import forecast_adoption


def render_forecast_tab(df):
    """Render the EV adoption forecasting tab"""
    st.subheader("EV Adoption Forecasting")

    years_ahead = st.slider("Years to forecast", 1, 10, 5, key="forecast_years")
    poly_degree = st.slider("Model complexity", 1, 4, 2, key="poly_degree")

    if st.button("Generate Forecast", type="primary"):
        with st.spinner("Generating forecast..."):
            forecast_results = forecast_adoption(df, years_ahead, poly_degree)

            # Metrics
            col1, col2, col3 = st.columns(3)

            current_year = int(forecast_results["historical"]["model_year"].max())
            current_count = int(
                forecast_results["historical"]["vehicle_count"].iloc[-1]
            )

            with col1:
                st.metric("Current Year", current_year)
                st.metric("Vehicles in Latest Year", f"{current_count:,}")

            with col2:
                st.metric(
                    "Model R² Score", f"{forecast_results['model_fit']['r2']:.4f}"
                )
                st.metric(
                    "Mean Absolute Error",
                    f"{forecast_results['model_fit']['mae']:,.0f}",
                )

            with col3:
                future_year = int(forecast_results["predictions"]["year"].iloc[-1])
                future_count = int(
                    forecast_results["predictions"]["predicted_vehicles"].iloc[-1]
                )
                st.metric(f"Forecast for {future_year}", f"{future_count:,}")
                growth_rate = ((future_count - current_count) / current_count) * 100
                st.metric("Projected Growth", f"{growth_rate:.1f}%")

            # Visualization
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=forecast_results["historical"]["model_year"],
                    y=forecast_results["historical"]["vehicle_count"],
                    mode="markers+lines",
                    name="Historical Data",
                    marker=dict(size=8, color="blue"),
                    line=dict(color="blue", width=2),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=forecast_results["historical"]["model_year"],
                    y=forecast_results["fitted_values"],
                    mode="lines",
                    name="Model Fit",
                    line=dict(color="green", dash="dot", width=2),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=forecast_results["predictions"]["year"],
                    y=forecast_results["predictions"]["predicted_vehicles"],
                    mode="markers+lines",
                    name="Forecast",
                    marker=dict(size=8, color="red", symbol="diamond"),
                    line=dict(color="red", width=2, dash="dash"),
                )
            )

            fig.update_layout(
                title="EV Adoption Trend and Forecast",
                xaxis_title="Year",
                yaxis_title="Number of Vehicles",
                hovermode="x unified",
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Forecast table
            st.subheader("Detailed Forecast")
            forecast_table = forecast_results["predictions"].copy()
            forecast_table["predicted_vehicles"] = forecast_table[
                "predicted_vehicles"
            ].astype(int)
            st.dataframe(
                forecast_table.style.format({"predicted_vehicles": "{:,}"}),
                use_container_width=True,
            )