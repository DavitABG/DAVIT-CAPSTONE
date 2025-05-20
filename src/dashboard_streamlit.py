import numpy as np
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ========== CONFIG ==========
BACKEND = "http://localhost:8000"

# ========== THEME & STYLING ==========
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    div[data-testid="stVerticalBlock"] > div {
        padding: 10px;
    }
    .plot-container {
        border-radius: 10px;
        background-color: white;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


# ========== UTILITY FUNCTIONS ==========
def fetch_json(endpoint, params=None):
    if not endpoint.endswith('/') and not endpoint.endswith('fit'):
        endpoint += '/'

    try:
        resp = requests.get(f"{BACKEND}{endpoint}", params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Error fetching data from {endpoint}: Status {resp.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def train_model():
    try:
        resp = requests.post(f"{BACKEND}/models/pnbd/fit")
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Error training model: {resp.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def create_gauge_chart(value, title, min_val=0, max_val=1):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_val / 3], 'color': "lightgray"},
                {'range': [max_val / 3, 2 * max_val / 3], 'color': "gray"},
                {'range': [2 * max_val / 3, max_val], 'color': "darkgray"}
            ],
        }
    ))
    fig.update_layout(height=200)
    return fig


# ========== PAGE SETUP ==========
st.title("🎯 Customer Analytics Dashboard")

# Navigation with emojis
PAGES = {
    "📊 Data Overview": "Data Overview",
    "💰 Customer Lifetime Value": "Customer Lifetime Value",
    "👥 Customer Analysis": "Customer Analysis"
}
page = st.sidebar.radio("Navigation", list(PAGES.keys()))

if "📊 Data Overview" in page:
    st.header("📊 Database Overview")


    tables = ["customers", "products", "sales"]
    selected_table = st.selectbox("Select table to preview", tables)

    data = fetch_json(f"/{selected_table}")
    if data:
        df = pd.DataFrame(data)

        # Corrected metrics calculations
        # Add an expander to show table information
        with st.expander("📋 Table Structure"):
            st.write("Columns in the table:")
            for col in df.columns:
                st.write(f"- {col} (type: {df[col].dtype})")

            st.write("\nSample data:")
            st.dataframe(df.head(2))

        col1, col2, col3 = st.columns(3)

        # Column 1: Total Records
        with col1:
            st.metric("Total Records", len(df))

        # Column 2: Unique Values based on table type
        with col2:
            if selected_table == "customers":
                id_col = next((col for col in df.columns if col.lower() in ['id', 'customer_id']), None)
                if id_col:
                    st.metric("Unique Customers", df[id_col].nunique())
            elif selected_table == "products":
                id_col = next((col for col in df.columns if col.lower() in ['id', 'product_id']), None)
                if id_col:
                    st.metric("Unique Products", df[id_col].nunique())
            elif selected_table == "sales":
                id_col = next((col for col in df.columns if col.lower() in ['id', 'sale_id', 'sales_id']), None)
                if id_col:
                    st.metric("Unique Sales", df[id_col].nunique())

        # Column 3: Date Range or other metrics
        with col3:
            date_col = next((col for col in df.columns if col.lower() in ['date', 'created_at', 'timestamp']), None)
            if date_col:
                st.metric("Date Range", f"{df[date_col].min()} to {df[date_col].max()}")
            elif selected_table == "products" and 'price' in df.columns:
                st.metric("Average Price", f"${df['price'].mean():.2f}")
            else:
                st.metric("Column Count", len(df.columns))

        # Display the data
        st.dataframe(df)

        # Additional visualizations based on table type
        if selected_table == "sales":
            col1, col2 = st.columns(2)
            with col1:
                daily_sales = df.groupby('date').size().reset_index(name='count')
                fig = px.line(daily_sales, x='date', y='count',
                              title="Daily Sales Volume",
                              template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                if 'qty' in df.columns and 'price' in df.columns:
                    df['revenue'] = df['qty'] * df['price']
                    fig = px.box(df, y='revenue',
                                 title="Revenue Distribution",
                                 template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
elif "💰 Customer Lifetime Value" in page:
    st.header("💰 Customer Lifetime Value Analysis")

    # Model Training Section with better styling
    with st.expander("🔄 Model Training", expanded=True):
        col1, col2 = st.columns([2, 3])
        with col1:
            if st.button("Train PNBD & Gamma-Gamma Models", use_container_width=True):
                with st.spinner("Training models..."):
                    result = train_model()
                    if result:
                        st.success("✅ Models trained successfully!")
                        st.json(result)

    # Customer Analysis Section
    st.subheader("📈 Customer Analysis")

    customers_data = fetch_json("/customers")
    if customers_data:
        customer_ids = [c["id"] for c in customers_data]
        customer_id = st.selectbox("Select Customer ID", customer_ids)

        if customer_id:
            # Create tabs for different analyses
            tab1, tab2, tab3 = st.tabs(["📊 Summary", "💵 CLV Analysis", "🔮 Predictions"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    summary = fetch_json(f"/models/pnbd/summary/{customer_id}")
                    if summary:
                        st.write("### Customer Metrics")
                        metrics_df = pd.DataFrame([summary])
                        fig = px.bar(metrics_df.melt(),
                                     x='variable', y='value',
                                     title="Customer RFM Metrics",
                                     template="plotly_white")
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    prob = fetch_json(f"/models/pnbd/prob_alive/{customer_id}")
                    if prob:
                        fig = create_gauge_chart(
                            prob['prob_alive'],
                            "Probability Customer is Active"
                        )
                        st.plotly_chart(fig, use_container_width=True)

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    time_horizon = st.slider("Time Horizon (days)", 30, 365, 90)
                    clv_data = fetch_json(f"/models/pnbd/clv/{customer_id}",
                                          params={"time": time_horizon})
                    if clv_data:
                        st.metric("Predicted CLV",
                                  f"${clv_data['clv']:,.2f}",
                                  delta=f"{time_horizon} days")

                with col2:
                    avg_value = fetch_json(f"/models/pnbd/avg_value/{customer_id}")
                    if avg_value:
                        st.metric("Expected Transaction Value",
                                  f"${avg_value['expected_avg_value']:,.2f}")

            with tab3:
                cumulative = fetch_json(f"/models/pnbd/cumulative/{customer_id}",
                                        params={"periods": time_horizon})
                if cumulative:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=list(range(1, len(cumulative['cumulative']) + 1)),
                        y=cumulative['cumulative'],
                        mode='lines',
                        fill='tozeroy',
                        line=dict(color='rgb(49, 130, 189)'),
                        name='Expected Transactions'
                    ))
                    fig.update_layout(
                        title="Predicted Cumulative Transactions",
                        xaxis_title="Days",
                        yaxis_title="Number of Transactions",
                        template="plotly_white",
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # Customer Analysis Section
elif page == "👥 Customer Analysis":
    st.header("👥 Customer Analysis")

    # Create tabs for different types of analysis
    tab1, tab2, tab3 = st.tabs(["📈 Segment Analysis", "🎯 RFM Details", "🔮 Predictive Insights"])

    customers_data = fetch_json("/customers")
    sales_data = fetch_json("/sales")
    products_data = fetch_json("/products")

    if customers_data and sales_data and products_data:
        df_customers = pd.DataFrame(customers_data)
        df_sales = pd.DataFrame(sales_data)
        df_products = pd.DataFrame(products_data)

        # Prepare data
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        today = df_sales['date'].max()

        # Calculate RFM metrics
        customer_metrics = df_sales.groupby('customer_id').agg({
            'date': lambda x: (today - x.max()).days,  # Recency
            'id': 'count',  # Frequency
            'qty': 'sum'  # Quantity
        }).reset_index()

        # Calculate monetary value
        sales_value = df_sales.merge(df_products[['product_id', 'price']],
                                     left_on='product_id',
                                     right_on='product_id')
        sales_value['Value'] = sales_value['qty'] * sales_value['price']
        monetary = sales_value.groupby('customer_id')['Value'].sum().reset_index()

        # Combine metrics
        rfm_df = customer_metrics.merge(monetary, on='customer_id')
        rfm_df.columns = ['customer_id', 'recency', 'frequency', 'quantity', 'monetary']

        # Calculate RFM scores
        rfm = pd.DataFrame()
        rfm['customer_id'] = rfm_df['customer_id']
        rfm["recency_score"] = pd.qcut(rfm_df['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm["frequency_score"] = pd.qcut(rfm_df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        rfm["monetary_score"] = pd.qcut(rfm_df["monetary"], 5, labels=[1, 2, 3, 4, 5])

        # Calculate RFM_SCORE
        rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                            rfm["frequency_score"].astype(str))

        # Segment mapping
        seg_map = {
            r'[1-2][1-2]': 'HIBERNATING',
            r'[1-2][3-4]': 'AT RISK',
            r'[1-2]5': 'CANT LOSE',
            r'3[1-2]': 'ABOUT TO SLEEP',
            r'33': 'NEED ATTENTION',
            r'[3-4][4-5]': 'LOYAL CUSTOMER',
            r'41': 'PROMISING',
            r'51': 'NEW CUSTOMERS',
            r'[4-5][2-3]': 'POTENTIAL LOYALIST',
            r'5[4-5]': 'CHAMPIONS'
        }

        # Create segments
        rfm['Customer_Segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

        # Merge with original metrics for analysis
        analysis_df = rfm.merge(rfm_df, on='customer_id')

        # Display KPI metrics at the top
        st.subheader("📊 Customer Segments Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Customers", len(analysis_df))
        with col2:
            st.metric("Average Customer Value", f"${analysis_df['monetary'].mean():.2f}")
        with col3:
            champions_count = len(analysis_df[analysis_df['Customer_Segment'] == 'CHAMPIONS'])
            st.metric("Champions", champions_count)

        # Tab 1: Segment Analysis
        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                # Customer Segments Distribution
                segment_dist = rfm['Customer_Segment'].value_counts()
                fig = px.pie(values=segment_dist.values,
                             names=segment_dist.index,
                             title="Customer Segments Distribution",
                             template="plotly_white",
                             color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Average Monetary Value by Segment
                avg_monetary = analysis_df.groupby('Customer_Segment')['monetary'].mean().reset_index()
                fig = px.bar(avg_monetary,
                             x='Customer_Segment',
                             y='monetary',
                             title="Average Customer Value by Segment",
                             labels={'monetary': 'Average Value ($)',
                                     'Customer_Segment': 'Segment'},
                             template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

        # Tab 2: RFM Details
        with tab2:
            col1, col2 = st.columns(2)

            with col1:
                # RFM Score Distribution
                fig = px.scatter(analysis_df,
                                 x='recency',
                                 y='frequency',
                                 color='Customer_Segment',
                                 size='monetary',
                                 title="RFM Segmentation Map",
                                 labels={'recency': 'Recency (days)',
                                         'frequency': 'Frequency',
                                         'monetary': 'Monetary Value ($)'},
                                 template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Segment Metrics Table
                segment_metrics = analysis_df.groupby('Customer_Segment').agg({
                    'customer_id': 'count',
                    'recency': 'mean',
                    'frequency': 'mean',
                    'monetary': 'mean'
                }).round(2).reset_index()

                segment_metrics.columns = ['Segment', 'Count', 'Avg Recency', 'Avg Frequency', 'Avg Value']
                segment_metrics = segment_metrics.sort_values('Count', ascending=False)

                fig = go.Figure(data=[go.Table(
                    header=dict(values=list(segment_metrics.columns),
                                fill_color='paleturquoise',
                                align='left'),
                    cells=dict(values=[segment_metrics[col] for col in segment_metrics.columns],
                               fill_color='lavender',
                               align='left'))
                ])
                fig.update_layout(title="Segment Metrics Summary")
                st.plotly_chart(fig, use_container_width=True)

        # Tab 3: Predictive Insights
        with tab3:
            st.subheader("🔮 Purchase Predictions")

            # Calculate expected purchases for next 30 and 90 days
            # Using simple frequency-based prediction for demonstration
            analysis_df['Expected_Purchases_30'] = (analysis_df['frequency'] /
                                                    (analysis_df['recency'] + 1)) * 30
            analysis_df['Expected_Purchases_90'] = (analysis_df['frequency'] /
                                                    (analysis_df['recency'] + 1)) * 90

            # Calculate probability of being alive (simple version)
            analysis_df['Probability_of_being_Alive'] = 1 / (1 + np.exp(analysis_df['recency'] / 365))

            col1, col2 = st.columns(2)

            with col1:
                # Top customers - 30 days prediction
                top_30_days = analysis_df.nlargest(10, 'Expected_Purchases_30')
                fig = go.Figure(data=[go.Bar(
                    x=top_30_days['customer_id'].astype(str),
                    y=top_30_days['Expected_Purchases_30'],
                    text=top_30_days['Expected_Purchases_30'].round(2),
                    textposition='auto'
                )])
                fig.update_layout(
                    title="Top 10 Customers (30-Day Prediction)",
                    xaxis_title="Customer ID",
                    yaxis_title="Expected Purchases",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Top customers - 90 days prediction
                top_90_days = analysis_df.nlargest(10, 'Expected_Purchases_90')
                fig = go.Figure(data=[go.Bar(
                    x=top_90_days['customer_id'].astype(str),
                    y=top_90_days['Expected_Purchases_90'],
                    text=top_90_days['Expected_Purchases_90'].round(2),
                    textposition='auto'
                )])
                fig.update_layout(
                    title="Top 10 Customers (90-Day Prediction)",
                    xaxis_title="Customer ID",
                    yaxis_title="Expected Purchases",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            # At-Risk Customers Section
            st.subheader("⚠️ At-Risk Customers")

            col1, col2 = st.columns(2)

            with col1:
                # Lowest expected purchases - 90 days
                bottom_90_days = analysis_df.nsmallest(10, 'Expected_Purchases_90')
                fig = go.Figure(data=[go.Bar(
                    x=bottom_90_days['customer_id'].astype(str),
                    y=bottom_90_days['Expected_Purchases_90'],
                    text=bottom_90_days['Expected_Purchases_90'].round(2),
                    textposition='auto',
                    marker_color='salmon'
                )])
                fig.update_layout(
                    title="Customers with Lowest Expected Purchases (90 Days)",
                    xaxis_title="Customer ID",
                    yaxis_title="Expected Purchases",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Customer Aliveness Distribution
                fig = go.Figure(data=[go.Histogram(
                    x=analysis_df['Probability_of_being_Alive'],
                    nbinsx=50,
                    marker_color='lightblue'
                )])
                fig.update_layout(
                    title='Distribution of Customer Aliveness Probability',
                    xaxis_title='Probability of Being Active',
                    yaxis_title='Number of Customers',
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Predictive Insights Summary
            st.subheader("💡 Key Predictive Insights")

            col1, col2, col3 = st.columns(3)

            with col1:
                avg_30day = analysis_df['Expected_Purchases_30'].mean()
                st.metric(
                    "Avg. Expected Purchases (30 Days)",
                    f"{avg_30day:.2f}"
                )

            with col2:
                avg_90day = analysis_df['Expected_Purchases_90'].mean()
                st.metric(
                    "Avg. Expected Purchases (90 Days)",
                    f"{avg_90day:.2f}"
                )

            with col3:
                active_customers = len(analysis_df[analysis_df['Probability_of_being_Alive'] > 0.5])
                st.metric(
                    "Likely Active Customers",
                    f"{active_customers}"
                )

            # Recommendations
            st.warning(f"""
            **Priority Actions Required:**
            - {len(analysis_df[analysis_df['Probability_of_being_Alive'] < 0.2])} customers are at high risk of churn
            - {len(analysis_df[analysis_df['Expected_Purchases_90'] < 1])} customers expected to make less than 1 purchase in next 90 days
            - Focus on re-engagement strategies for these segments
            """)

        # Overall Key Insights (below all tabs)
        st.subheader("💡 Overall Key Insights")

        # Calculate key metrics
        top_segment = segment_metrics.iloc[0]['Segment']
        top_segment_count = segment_metrics.iloc[0]['Count']
        top_value_segment = segment_metrics.sort_values('Avg Value', ascending=False).iloc[0]['Segment']

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"""
            **Largest Segment**: {top_segment}
            - Contains {top_segment_count} customers
            - Represents {(top_segment_count / len(analysis_df) * 100):.1f}% of customer base
            """)

        with col2:
            st.info(f"""
            **Highest Value Segment**: {top_value_segment}
            - Average value: ${segment_metrics[segment_metrics['Segment'] == top_value_segment]['Avg Value'].values[0]:,.2f}
            - Focus on retention strategies for this segment
            """)


def check_model_status():
    """Check the complete status of the PNBD model and data."""
    status = {
        "model_trained": False,
        "data_available": False,
        "customers_count": 0,
        "transactions_count": 0,
        "last_training": None,
        "errors": []
    }

    try:
        # Check if data is available
        customers = fetch_json("/customers")
        sales = fetch_json("/sales")

        if customers:
            status["data_available"] = True
            status["customers_count"] = len(customers)

        if sales:
            status["transactions_count"] = len(sales)

        # Check if model is trained by attempting to get predictions
        if customers and len(customers) > 0:
            test_customer = customers[0]["id"]

            # Try to get model predictions
            prob_alive = fetch_json(f"/models/pnbd/prob_alive/{test_customer}")
            if prob_alive and "prob_alive" in prob_alive:
                status["model_trained"] = True

    except Exception as e:
        status["errors"].append(str(e))

    return status


# In the sidebar:
st.sidebar.markdown("### 🔍 Model Status")
if st.sidebar.button("Check Model Status"):
    with st.sidebar:
        with st.spinner("Checking model status..."):
            status = check_model_status()

            st.write("### System Status")

            # Model Status
            if status["model_trained"]:
                st.success("✅ Model is trained and operational")
            else:
                st.warning("⚠️ Model needs training")

            # Data Status
            st.write("### Data Overview")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Customers", status["customers_count"])
            with col2:
                st.metric("Transactions", status["transactions_count"])

            if not status["data_available"]:
                st.warning("⚠️ No data available")

            # Errors if any
            if status["errors"]:
                st.error("Errors found:")
                for error in status["errors"]:
                    st.write(f"- {error}")

            # Recommendations
            st.write("### Recommendations")
            if not status["model_trained"]:
                st.info("💡 Click 'Train PNBD & Gamma-Gamma Models' to train the model")
            if status["customers_count"] == 0:
                st.info("💡 Import customer data")
            if status["transactions_count"] == 0:
                st.info("💡 Import transaction data")
# Add timestamp
st.sidebar.markdown("---")
st.sidebar.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
