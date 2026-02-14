import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Set page config for rich aesthetics
st.set_page_config(
    page_title="Ethiopian Medical Warehouse Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for glassmorphism and premium feel
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #ffffff;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        color: #00d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

BASE_URL = "http://localhost:8000"

def fetch_data(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return None
    return None

st.title("🏥 Ethiopian Medical Data Warehouse")
st.markdown("### End-to-End Medical Business Intelligence Pipeline")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Market Overview", "Visual Intelligence", "Predictive Analytics & SHAP"])

if page == "Market Overview":
    st.header("📈 Market Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Mentioned Medical Keywords")
        keywords = fetch_data("/api/reports/top-products?limit=15")
        if keywords:
            df_kw = pd.DataFrame(keywords)
            fig = px.bar(df_kw, x='frequency', y='keyword', orientation='h', 
                         color='frequency', color_continuous_scale='Viridis',
                         template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("API not reachable. Ensure FastAPI is running on port 8000.")

    with col2:
        st.subheader("Recent Message Samples")
        search = fetch_data("/api/search/messages?query=tablet&limit=5")
        if search:
            for msg in search:
                with st.expander(f"Message ID: {msg['id']} | Channel: {msg['channel']}"):
                    st.write(msg['text'])
                    st.caption(f"Views: {msg['views']} | Date: {msg['date']}")

if page == "Visual Intelligence":
    st.header("👁️ YOLOv8 Content Intelligence")
    
    stats = fetch_data("/api/reports/visual-content")
    if stats:
        df_stats = pd.DataFrame(stats)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Content Category Distribution")
            fig = px.pie(df_stats, values='count', names='category', 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Engagement (Avg Views) by Category")
            fig = px.bar(df_stats, x='category', y='avg_views', color='category',
                         template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No visual content data available. Run the YOLO detection pipeline first.")

if page == "Predictive Analytics & SHAP":
    st.header("🧠 Model Explainability (SHAP)")
    st.markdown("Explaning how **Image Categories** and **Channels** influence reach (Views).")

    # Mocking a dataset for SHAP since we are offline or need quick visualization
    # In a real scenario, this would fit a model on the actual DB data
    channels = ["CheMed123", "lobelia4cosmetics", "tikvahpharma", "yenehealth", "LiyuPharma"]
    categories = ["Promotional", "Product Display", "Lifestyle", "Other"]
    
    # Generate mock data consistent with our problem for SHAP demo
    data = []
    for _ in range(500):
        ch = np.random.choice(channels)
        cat = np.random.choice(categories)
        # Base views + effects
        views = 100 
        if ch == "yenehealth": views += 150
        if cat == "Promotional": views += 200
        if cat == "Lifestyle": views += 80
        views += np.random.normal(0, 30)
        data.append({"channel": ch, "category": cat, "views": max(0, int(views))})
    
    df = pd.DataFrame(data)
    
    # Preprocessing
    le_ch = LabelEncoder()
    le_cat = LabelEncoder()
    df['channel_enc'] = le_ch.fit_transform(df['channel'])
    df['category_enc'] = le_cat.fit_transform(df['category'])
    
    X = df[['channel_enc', 'category_enc']]
    y = df['views']
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    # SHAP Explanations
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Global Feature Importance")
        fig, ax = plt.subplots()
        shap.summary_plot(shap_values, X, plot_type="bar", show=False)
        st.pyplot(fig)
        st.caption("Which factors contribute most to message reach?")

    with col2:
        st.subheader("Feature Impact (Summary Plot)")
        fig, ax = plt.subplots()
        shap.summary_plot(shap_values, X, show=False)
        st.pyplot(fig)
        st.caption("How specific categories influence views positively or negatively.")

    st.markdown("---")
    st.subheader("Individual Prediction Explanation")
    test_ch = st.selectbox("Select Channel", channels)
    test_cat = st.selectbox("Select Content Type", categories)
    
    input_df = pd.DataFrame([[le_ch.transform([test_ch])[0], le_cat.transform([test_cat])[0]]], 
                            columns=['channel_enc', 'category_enc'])
    pred = model.predict(input_df)[0]
    
    st.metric("Predicted Views", f"{int(pred)}")
    
    # Force plot for the specific prediction
    st.markdown("**Why this prediction?** (Force Plot representation)")
    shap_val_single = explainer.shap_values(input_df)
    
    # Streamlit doesn't render SHAP force plots easily without JS, using a simple bar instead
    # But let's use the standard summary plot for the single point as a workaround or text
    st.write(f"- Channel impact ({test_ch})")
    st.write(f"- Content category impact ({test_cat})")
