import pandas as pd
import datetime as dt
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Set up the Streamlit app
st.title("RFM Analysis Dashboard")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    # Load the data
    retail_df = pd.read_csv(uploaded_file)

    # Data preprocessing
    retail_df.drop_duplicates(inplace=True)
    retail_df.dropna(subset=['CustomerID'], inplace=True)
    retail_df['Total'] = retail_df['Quantity'] * retail_df['UnitPrice']

    # Convert 'InvoiceDate' column to datetime
    retail_df['InvoiceDate'] = pd.to_datetime(retail_df['InvoiceDate'])

    # Recency
    latest_date = retail_df['InvoiceDate'].max() + dt.timedelta(days=1)

    rfm = retail_df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (latest_date - x.max()).days,
        'InvoiceNo': 'count',
        'Total': 'sum'
    }).reset_index()

    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'Total': 'MonetaryValue'
    }, inplace=True)

    # Recency score based on quantiles
    rfm["Recency_score"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])

    # Frequency score
    rfm["Frequency_score"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

    # Combine Recency and Frequency scores to create RFM Segment
    rfm["rfm_segment"] = rfm['Recency_score'].astype(str) + rfm['Frequency_score'].astype(str)

    # Mapping segments to their corresponding customer segments
    segment_map = {
        r'[1-2][1-2]': 'Hibernating',
        r'[1-2][3-4]': 'At-Risk',
        r'[1-2]5': "Can't Lose",
        r'3[1-2]': 'About to Slip',
        r'33': 'Need Attention',
        r'[3-4][4-5]': 'Loyal Customers',
        r'41': 'Promising',
        r'51': 'New Customers',
        r'[4-5][2-3]': 'Potential Loyalists',
        r'5[4-5]': 'Champions',
    }

    # Mapping RFM segments to corresponding customer segments
    rfm['rfm_segment'] = rfm['rfm_segment'].replace(segment_map, regex=True)

    new_rfm = rfm[["Recency", "Frequency", "MonetaryValue", "rfm_segment"]]

    # Display RFM data
    st.subheader("RFM Segmentation Results")
    st.write(new_rfm)

    # Create a plot for Customer Cluster based on Recency and Frequency
    st.subheader("Customer Cluster based on Recency and Frequency")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Recency', y='Frequency', hue='rfm_segment', data=new_rfm, palette='viridis')
    plt.title('Customer Cluster based on Recency and Frequency')
    st.pyplot(plt)

    # Top 10 most preferred products
    segments = new_rfm['rfm_segment'].value_counts()
    
    # Bar chart for RFM segments
    st.subheader("RFM Segments Bar Chart")
    fig = px.bar(
        x=segments.index,
        y=segments.values,
        color=segments.index,
        text=segments.values,
        title="RFM Segments"
    )
    fig.update_layout(
        xaxis_title="Segment",
        yaxis_title="Count",
        font=dict(size=15, family="Arial"),
        title_font=dict(size=20, family="Arial")
    )
    st.plotly_chart(fig)

    # Pie chart for segments
    st.subheader("RFM Segments Pie Chart")
    plt.figure(figsize=(10, 8))
    explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    segments.plot(
        kind='pie',
        explode=explode,
        autopct='%1.2f%%'
    )
    plt.axis('equal')
    plt.title("RFM Segment Distribution")
    st.pyplot(plt)

    # Customer Segments by Frequency
    st.subheader("Customer Segments by Frequency")
    plt.figure(figsize=(15, 7))
    sns.barplot(x="rfm_segment", y="Frequency", data=new_rfm, palette="dark")
    plt.title("Customer Segments by Frequency")
    plt.xlabel("Segment")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    st.pyplot(plt)

else:
    st.info("Please upload a CSV file to proceed.")


