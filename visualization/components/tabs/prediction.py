import streamlit as st
import plotly.express as px
import pandas as pd
from utils.ml_models import train_range_prediction_model


def render_prediction_tab(df):
    """Render the range prediction model tab"""
    st.subheader("Electric Range Prediction Model")

    # Filter data with valid range
    range_data = df[df["electric_range"] > 0].copy()

    if not range_data.empty and len(range_data) > 10:
        # Train model button
        if st.button("Train Prediction Model", type="primary"):
            with st.spinner("Training model..."):
                trained_model = train_range_prediction_model(range_data)
                st.session_state.range_model = trained_model
                st.success("✅ Model trained successfully!")

        if "range_model" in st.session_state:
            model_data = st.session_state.range_model
            metrics = model_data["metrics"]

            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Mean Absolute Error", f"{metrics['mae']:.2f} miles")
            col2.metric("Root Mean Squared Error", f"{metrics['rmse']:.2f} miles")
            col3.metric("R² Score", f"{metrics['r2']:.4f}")

            st.markdown("---")

            # Prediction interface
            st.subheader("Make a Prediction")

            expanded_range = []
            for _, row in range_data.iterrows():
                expanded_range.append(row.to_dict())
            df_range_expanded = pd.DataFrame(expanded_range)

            col1, col2, col3 = st.columns(3)

            with col1:
                pred_year = st.number_input(
                    "Model Year", min_value=2010, max_value=2030, value=2024
                )
                pred_make = st.selectbox(
                    "Make",
                    sorted(df_range_expanded["make"].unique()),
                    key="pred_make",
                )

            with col2:
                available_models = df_range_expanded[
                    df_range_expanded["make"] == pred_make
                ]["model"].unique()
                pred_model = st.selectbox(
                    "Model", sorted(available_models), key="pred_model"
                )
                pred_ev_type = st.selectbox(
                    "EV Type",
                    sorted(df_range_expanded["ev_type"].unique()),
                    key="pred_ev_type",
                )

            with col3:
                pred_cafv = st.selectbox(
                    "CAFV Eligibility",
                    sorted(df_range_expanded["cafv_eligibility"].unique()),
                    key="pred_cafv",
                )
                pred_state = st.selectbox(
                    "State",
                    sorted(df_range_expanded["state"].unique()),
                    key="pred_state",
                )

            if st.button("Predict Range"):
                try:
                    encoders = model_data["encoders"]
                    input_data = pd.DataFrame(
                        {
                            "model_year": [pred_year],
                            "make_encoded": [
                                encoders["make"].transform([pred_make])[0]
                            ],
                            "model_encoded": [
                                encoders["model"].transform([pred_model])[0]
                            ],
                            "ev_type_encoded": [
                                encoders["ev_type"].transform([pred_ev_type])[0]
                            ],
                            "cafv_encoded": [
                                encoders["cafv"].transform([pred_cafv])[0]
                            ],
                            "state_encoded": [
                                encoders["state"].transform([pred_state])[0]
                            ],
                        }
                    )

                    prediction = model_data["model"].predict(input_data)[0]
                    st.success(
                        f"### Predicted Electric Range: **{prediction:.1f} miles**"
                    )

                    actual_range = df_range_expanded[
                        (df_range_expanded["make"] == pred_make)
                        & (df_range_expanded["model"] == pred_model)
                        & (df_range_expanded["model_year"] == pred_year)
                    ]["electric_range"]

                    if not actual_range.empty:
                        avg_actual = actual_range.mean()
                        st.info(
                            f"ℹ️ Actual average range for this vehicle: **{avg_actual:.1f} miles**"
                        )
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("This combination might not exist in training data.")

            # Feature importance chart
            st.markdown("---")
            st.subheader("Feature Importance")
            fig_imp = px.bar(
                model_data["feature_importance"],
                x="importance",
                y="feature",
                orientation="h",
                title="Which factors matter most for predicting range?",
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info("👆 Click 'Train Prediction Model' to get started")
    else:
        st.warning("Not enough data with valid electric range for predictions")