import streamlit as st
import pandas as pd
import plotly.express as px 
import altair as alt

st.title("Ecommerce Sales Dashboard")

df = pd.read_csv('sales.csv')
#st.subheader("Data Preview")
#st.dataframe(df.head())

#st.subheader("Summary Statistics")
#st.write(df.describe())

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"${df['Sales_Amount'].sum():,.2f}")

with col2:
    st.metric("Total Products", df['Product_Category'].nunique())

with col3:
    st.metric("Total Regions", df['Region'].nunique())


tab1, tab2, tab3 = st.tabs(["Sales by Product & Region", "Sales Trends", "Customer Insights"])

#Sidebar 

#Product Category Filter
st.sidebar.subheader("Filter by Product Category")
product_categories = df['Product_Category'].unique()
selected_category = st.sidebar.multiselect("Select a Product Category", product_categories,
                                         default=product_categories)

#Region Filter
st.sidebar.subheader("Filter by Region")
sales_region = df['Region'].unique()
selected_region = st.sidebar.multiselect('Select a region', sales_region, default=sales_region)

#Time Filter 
st.sidebar.subheader("Filter by Date")

df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])

min_date = df['Sale_Date'].min().date()
max_date = df['Sale_Date'].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

mask = (df['Sale_Date'].dt.date >= start_date) & (df['Sale_Date'].dt.date <= end_date)
filtered_df = df.loc[mask]

with tab1:
    col5, col6 = st.columns(2)

    #Show Product Sales by type
    with col5:
        st.subheader("Total Sales by Product")
        sales_by_product = filtered_df.groupby('Product_Category')['Sales_Amount'].sum().reset_index()
        sales_by_product = sales_by_product[sales_by_product['Product_Category'].isin(selected_category)]
        st.bar_chart(sales_by_product.set_index('Product_Category'), horizontal=False)


    #Show Sales by Region
    with col6:
        st.subheader("Total Sales by Region")
        sales_by_region = filtered_df.groupby('Region')['Sales_Amount'].sum().reset_index()
        sales_by_region = sales_by_region[sales_by_region['Region'].isin(selected_region)]
        st.bar_chart(sales_by_region.set_index('Region'), horizontal=False)

    #Show Sales by Product and Region
    st.subheader("Sales by Product and Region")
    sales_by_product_region = filtered_df.groupby(['Product_Category', 'Region'])['Sales_Amount'].sum().reset_index()
    sales_by_product_region = sales_by_product_region[sales_by_product_region['Product_Category'].isin(selected_category) & sales_by_product_region['Region'].isin(selected_region)]
    sales_by_product_region_pivot = sales_by_product_region.pivot(index='Product_Category', columns='Region', values='Sales_Amount')
    st.bar_chart(sales_by_product_region_pivot, horizontal=True)

with tab2:
    st.subheader("Sales Trends Over Time")
    filtered_df['Month'] = filtered_df['Sale_Date'].dt.to_period('M')
    sales_trends = filtered_df.groupby('Month')['Sales_Amount'].sum().reset_index()
    sales_trends['Month'] = sales_trends['Month'].astype(str)
    st.line_chart(sales_trends.set_index('Month'))

    #Product Sales Trends by Product Category
    st.subheader("Product Sales Trends Overtime")
    df['Month'] = df['Sale_Date'].dt.to_period('M')
    sales_trends_product = df.groupby(['Month', 'Product_Category'])['Sales_Amount'].sum().reset_index()
    sales_trends_product['Month'] = sales_trends_product['Month'].astype(str)
    sales_trends_product_pivot = sales_trends_product.pivot(index='Month', columns='Product_Category', values='Sales_Amount')
    st.line_chart(sales_trends_product_pivot)

    #Sales Trends by Region
    st.subheader("Sales Trends by Region")
    sales_trends_region = df.groupby(['Month', 'Region'])['Sales_Amount'].sum().reset_index()
    sales_trends_region['Month'] = sales_trends_region['Month'].astype(str)
    sales_trends_region_pivot = sales_trends_region.pivot(index='Month', columns='Region', values='Sales_Amount')
    st.line_chart(sales_trends_region_pivot)

    
with tab3:
    #Show Top Customers
    st.subheader("Customer Insights")
    top_customers = df.groupby('Sales_Rep')['Sales_Amount'].sum().reset_index().sort_values(by='Sales_Amount', ascending=False).head(10)
    st.bar_chart(top_customers.set_index('Sales_Rep'), horizontal=False)

    #Returning Customers vs New Customers
    st.subheader("Returning Customers")
    r_vs_new = df['Customer_Type'].value_counts().reset_index()
    r_vs_new.columns = ['Customer_Type', 'Count']
    fig1 = px.pie(r_vs_new, values='Count', names='Customer_Type', title='Returning vs New Customers')
    st.plotly_chart(fig1)

    #Payment Types Chart
    st.subheader("Payment Types")
    payments = df["Payment_Method"].value_counts().reset_index()
    payments.columns = ['Payment_Method', 'Count']
    fig2 = px.pie(payments, values='Count', names = 'Payment_Method', title='Payment Methods' )
    st.plotly_chart(fig2)
