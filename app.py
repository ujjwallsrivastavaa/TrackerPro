import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Import custom modules
from data_models import DataManager
from analytics import AnalyticsEngine
from utils import export_to_csv, export_to_pdf

# Configure page
st.set_page_config(
    page_title="HealthKart Influencer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsEngine()
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def main():
    # Sidebar navigation
    st.sidebar.title("🎯 HealthKart Analytics")
    st.sidebar.markdown("---")
    
    # Navigation menu with radio buttons
    st.sidebar.markdown("### 📋 Navigation")
    
    # Page options with icons
    page_options = [
        "📊 Dashboard", 
        "📁 Data Upload", 
        "🔍 Insights", 
        "💸 Payouts", 
        "📤 Export Data", 
        "🗄️ Database Management"
    ]
    
    # Map display names to internal names
    page_mapping = {
        "📊 Dashboard": "Dashboard",
        "📁 Data Upload": "Data Upload", 
        "🔍 Insights": "Insights",
        "💸 Payouts": "Payouts",
        "📤 Export Data": "Export Data",
        "🗄️ Database Management": "Database Management"
    }
    
    # Find current display option
    current_display = None
    for display, internal in page_mapping.items():
        if internal == st.session_state.current_page:
            current_display = display
            break
    
    # Use radio buttons for explicit navigation
    selected_display = st.sidebar.radio(
        "Choose a page:",
        page_options,
        index=page_options.index(current_display) if current_display else 0,
        label_visibility="collapsed"
    )
    
    selected_page = page_mapping[selected_display]
    
    # Update session state if page changed
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    page = st.session_state.current_page
    
    st.sidebar.markdown("---")
    
    # Display current data status
    st.sidebar.markdown("### 📊 Data Status")
    data_manager = st.session_state.data_manager
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Influencers", len(data_manager.influencers))
        st.metric("Posts", len(data_manager.posts))
    with col2:
        st.metric("Tracking Records", len(data_manager.tracking_data))
        st.metric("Payouts", len(data_manager.payouts))
    
    st.sidebar.markdown("---")
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Data Upload":
        show_upload_page()
    elif page == "Insights":
        show_insights_page()
    elif page == "Payouts":
        show_payouts_page()
    elif page == "Export Data":
        show_export_page()
    elif page == "Database Management":
        show_database_management_page()

def show_dashboard():
    st.title("📊 Campaign Performance Dashboard")
    
    data_manager = st.session_state.data_manager
    analytics = st.session_state.analytics
    
    if len(data_manager.tracking_data) == 0:
        st.warning("⚠️ No campaign data available. Please upload data first.")
        if st.button("Go to Data Upload"):
            st.rerun()
        return
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        platforms = ['All'] + list(data_manager.influencers['platform'].unique())
        selected_platform = st.selectbox("Platform", platforms)
    
    with col2:
        brands = ['All'] + list(data_manager.tracking_data['campaign'].unique())
        selected_brand = st.selectbox("Brand/Campaign", brands)
    
    with col3:
        categories = ['All'] + list(data_manager.influencers['category'].unique())
        selected_category = st.selectbox("Category", categories)
    
    with col4:
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now() - timedelta(days=30), datetime.now()],
            max_value=datetime.now()
        )
    
    # Apply filters
    filtered_data = analytics.apply_filters(
        data_manager, selected_platform, selected_brand, 
        selected_category, date_range
    )
    
    if len(filtered_data['tracking']) == 0:
        st.warning("No data matches the selected filters.")
        return
    
    # KPI Metrics
    st.subheader("📈 Key Performance Indicators")
    
    total_revenue = filtered_data['tracking']['revenue'].sum()
    total_orders = filtered_data['tracking']['orders'].sum()
    total_reach = filtered_data['posts']['reach'].sum()
    total_engagement = filtered_data['posts']['likes'].sum() + filtered_data['posts']['comments'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    with col2:
        st.metric("Total Orders", f"{total_orders:,.0f}")
    with col3:
        st.metric("Total Reach", f"{total_reach:,.0f}")
    with col4:
        st.metric("Total Engagement", f"{total_engagement:,.0f}")
    
    # ROI and ROAS Calculations
    st.subheader("💰 ROI & ROAS Analysis")
    roi_data = analytics.calculate_roi_roas(filtered_data)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average ROI", f"{roi_data['avg_roi']:.1f}%", f"{roi_data['roi_change']:+.1f}%")
    with col2:
        st.metric("Average ROAS", f"{roi_data['avg_roas']:.2f}x", f"{roi_data['roas_change']:+.2f}x")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Platform
        platform_revenue = filtered_data['tracking'].groupby(
            filtered_data['tracking']['influencer_id'].map(
                dict(zip(data_manager.influencers['ID'], data_manager.influencers['platform']))
            )
        )['revenue'].sum().reset_index()
        platform_revenue.columns = ['Platform', 'Revenue']
        
        fig_platform = px.bar(
            platform_revenue, 
            x='Platform', 
            y='Revenue',
            title="Revenue by Platform",
            color='Revenue',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_platform, use_container_width=True)
    
    with col2:
        # Performance Trend
        trend_data = filtered_data['tracking'].groupby('date').agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        fig_trend = px.line(
            trend_data, 
            x='date', 
            y='revenue',
            title="Revenue Trend Over Time",
            labels={'revenue': 'Revenue (₹)', 'date': 'Date'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Top Performers Table
    st.subheader("🏆 Top Performing Influencers")
    top_performers = analytics.get_top_performers(filtered_data, limit=10)
    st.dataframe(top_performers, use_container_width=True)

def show_upload_page():
    st.title("📁 Data Upload")
    
    st.markdown("""
    Upload your influencer campaign data using the CSV templates below. 
    Ensure your data follows the required format for accurate analysis.
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Influencers", "Posts", "Tracking Data", "Payouts"])
    
    data_manager = st.session_state.data_manager
    
    with tab1:
        st.subheader("Influencers Data")
        st.markdown("**Required columns:** ID, name, category, gender, follower_count, platform")
        
        uploaded_file = st.file_uploader("Upload Influencers CSV", type="csv", key="influencers")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                required_cols = ['ID', 'name', 'category', 'gender', 'follower_count', 'platform']
                
                if all(col in df.columns for col in required_cols):
                    success = data_manager.save_influencers_to_db(df)
                    if success:
                        st.success(f"✅ Saved {len(df)} influencers to database successfully!")
                        st.dataframe(df.head())
                    else:
                        st.error("❌ Failed to save influencers to database")
                else:
                    st.error(f"❌ Missing required columns: {set(required_cols) - set(df.columns)}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with tab2:
        st.subheader("Posts Data")
        st.markdown("**Required columns:** influencer_id, platform, date, URL, caption, reach, likes, comments")
        
        uploaded_file = st.file_uploader("Upload Posts CSV", type="csv", key="posts")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                required_cols = ['influencer_id', 'platform', 'date', 'URL', 'caption', 'reach', 'likes', 'comments']
                
                if all(col in df.columns for col in required_cols):
                    df['date'] = pd.to_datetime(df['date'])
                    success = data_manager.save_posts_to_db(df)
                    if success:
                        st.success(f"Saved {len(df)} posts to database successfully!")
                        st.dataframe(df.head())
                    else:
                        st.error("Failed to save posts to database")
                else:
                    st.error(f"Missing required columns: {set(required_cols) - set(df.columns)}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with tab3:
        st.subheader("Tracking Data")
        st.markdown("**Required columns:** source, campaign, influencer_id, user_id, product, date, orders, revenue")
        
        uploaded_file = st.file_uploader("Upload Tracking CSV", type="csv", key="tracking")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                required_cols = ['source', 'campaign', 'influencer_id', 'user_id', 'product', 'date', 'orders', 'revenue']
                
                if all(col in df.columns for col in required_cols):
                    df['date'] = pd.to_datetime(df['date'])
                    success = data_manager.save_tracking_data_to_db(df)
                    if success:
                        st.success(f"✅ Saved {len(df)} tracking records to database successfully!")
                        st.dataframe(df.head())
                    else:
                        st.error("❌ Failed to save tracking data to database")
                else:
                    st.error(f"❌ Missing required columns: {set(required_cols) - set(df.columns)}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with tab4:
        st.subheader("Payouts Data")
        st.markdown("**Required columns:** influencer_id, basis, rate, orders, total_payout")
        
        uploaded_file = st.file_uploader("Upload Payouts CSV", type="csv", key="payouts")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                required_cols = ['influencer_id', 'basis', 'rate', 'orders', 'total_payout']
                
                if all(col in df.columns for col in required_cols):
                    success = data_manager.save_payouts_to_db(df)
                    if success:
                        st.success(f"✅ Saved {len(df)} payout records to database successfully!")
                        st.dataframe(df.head())
                    else:
                        st.error("❌ Failed to save payouts to database")
                else:
                    st.error(f"❌ Missing required columns: {set(required_cols) - set(df.columns)}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")

def show_insights_page():
    st.title("🔍 Advanced Insights")
    
    data_manager = st.session_state.data_manager
    analytics = st.session_state.analytics
    
    if len(data_manager.tracking_data) == 0:
        st.warning("⚠️ No data available for insights. Please upload data first.")
        st.info("💡 Try loading sample data from the Database Management page to test the insights features.")
        return
    
    # Generate insights with error handling
    try:
        insights = analytics.generate_insights(data_manager)
    except Exception as e:
        st.error(f"❌ Error generating insights: {str(e)}")
        st.info("This might be due to missing data columns. Please check your uploaded data format.")
        return
    
    # Top Influencers
    st.subheader("🏆 Top Performing Influencers")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**By Revenue**")
        top_revenue = insights['top_influencers']['by_revenue']
        fig_revenue = px.bar(
            top_revenue.head(10), 
            x='revenue', 
            y='name',
            orientation='h',
            title="Top 10 by Revenue Generated"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.markdown("**By ROI**")
        top_roi = insights['top_influencers']['by_roi']
        fig_roi = px.bar(
            top_roi.head(10), 
            x='roi', 
            y='name',
            orientation='h',
            title="Top 10 by ROI"
        )
        st.plotly_chart(fig_roi, use_container_width=True)
    
    # Platform Analysis
    st.subheader("📱 Platform Performance")
    platform_stats = insights['platform_analysis']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_platform_revenue = px.pie(
            platform_stats, 
            values='total_revenue', 
            names='platform',
            title="Revenue Distribution by Platform"
        )
        st.plotly_chart(fig_platform_revenue, use_container_width=True)
    
    with col2:
        fig_platform_engagement = px.bar(
            platform_stats, 
            x='platform', 
            y='avg_engagement_rate',
            title="Average Engagement Rate by Platform"
        )
        st.plotly_chart(fig_platform_engagement, use_container_width=True)
    
    with col3:
        fig_platform_roi = px.bar(
            platform_stats, 
            x='platform', 
            y='avg_roi',
            title="Average ROI by Platform"
        )
        st.plotly_chart(fig_platform_roi, use_container_width=True)
    
    # Poor Performing Campaigns
    st.subheader("⚠️ Underperforming Analysis")
    poor_performers = insights['poor_performers']
    
    if len(poor_performers) > 0:
        st.dataframe(
            poor_performers[['name', 'platform', 'total_revenue', 'roi', 'reason']],
            use_container_width=True
        )
    else:
        st.success("🎉 No significantly underperforming influencers found!")
    
    # Category Insights
    st.subheader("🎯 Category Performance")
    category_stats = insights['category_analysis']
    
    fig_category = px.scatter(
        category_stats,
        x='avg_follower_count',
        y='avg_revenue_per_post',
        size='total_posts',
        color='category',
        title="Category Performance: Followers vs Revenue per Post",
        hover_data=['avg_roi']
    )
    st.plotly_chart(fig_category, use_container_width=True)

def show_payouts_page():
    st.title("💸 Payout Management")
    
    data_manager = st.session_state.data_manager
    
    if len(data_manager.payouts) == 0:
        st.warning("⚠️ No payout data available. Please upload payout data first.")
        return
    
    # Summary metrics
    total_payouts = data_manager.payouts['total_payout'].sum()
    pending_payouts = len(data_manager.payouts[data_manager.payouts['total_payout'] > 0])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Payouts", f"₹{total_payouts:,.0f}")
    with col2:
        st.metric("Active Influencers", pending_payouts)
    with col3:
        avg_payout = data_manager.payouts['total_payout'].mean()
        st.metric("Average Payout", f"₹{avg_payout:,.0f}")
    
    # Payout basis analysis
    st.subheader("📊 Payout Structure Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Payout by basis
        basis_summary = data_manager.payouts.groupby('basis').agg({
            'total_payout': 'sum',
            'influencer_id': 'count'
        }).reset_index()
        basis_summary.columns = ['Basis', 'Total_Payout', 'Count']
        
        fig_basis = px.pie(
            basis_summary,
            values='Total_Payout',
            names='Basis',
            title="Payout Distribution by Basis"
        )
        st.plotly_chart(fig_basis, use_container_width=True)
    
    with col2:
        # Rate distribution
        fig_rates = px.histogram(
            data_manager.payouts,
            x='rate',
            color='basis',
            title="Rate Distribution by Payout Basis",
            nbins=20
        )
        st.plotly_chart(fig_rates, use_container_width=True)
    
    # Detailed payout table
    st.subheader("📋 Detailed Payout Records")
    
    # Add influencer names to payout data
    payout_details = data_manager.payouts.merge(
        data_manager.influencers[['ID', 'name', 'platform', 'category']],
        left_on='influencer_id',
        right_on='ID',
        how='left'
    )
    
    # Search and filter
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search by influencer name")
    with col2:
        basis_filter = st.selectbox("Filter by basis", ['All'] + list(data_manager.payouts['basis'].unique()))
    
    # Apply filters
    filtered_payouts = payout_details.copy()
    if search_term:
        filtered_payouts = filtered_payouts[
            filtered_payouts['name'].str.contains(search_term, case=False, na=False)
        ]
    if basis_filter != 'All':
        filtered_payouts = filtered_payouts[filtered_payouts['basis'] == basis_filter]
    
    # Display table
    display_cols = ['name', 'platform', 'category', 'basis', 'rate', 'orders', 'total_payout']
    st.dataframe(
        filtered_payouts[display_cols].sort_values('total_payout', ascending=False),
        use_container_width=True
    )

def show_export_page():
    st.title("📤 Export Data")
    
    data_manager = st.session_state.data_manager
    analytics = st.session_state.analytics
    
    st.markdown("Export your campaign data and insights in various formats.")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Export")
        
        if st.button("Export to CSV", key="csv_export"):
            if len(data_manager.tracking_data) > 0:
                csv_data = export_to_csv(data_manager)
                st.download_button(
                    label="Download CSV Report",
                    data=csv_data,
                    file_name=f"healthkart_campaign_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.success("✅ CSV report generated successfully!")
            else:
                st.error("❌ No data available to export.")
    
    with col2:
        st.subheader("PDF Report")
        
        if st.button("Generate PDF Report", key="pdf_export"):
            if len(data_manager.tracking_data) > 0:
                pdf_data = export_to_pdf(data_manager, analytics)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"healthkart_insights_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF report generated successfully!")
            else:
                st.error("No data available to export.")
    
        # Data summary
    st.subheader("Current Data Summary")

    if len(data_manager.tracking_data) > 0:
        # Ensure 'date' column is in datetime format
        data_manager.tracking_data['date'] = pd.to_datetime(data_manager.tracking_data['date'], errors='coerce')

        # Compute min and max dates
        min_date = data_manager.tracking_data['date'].min()
        max_date = data_manager.tracking_data['date'].max()

        # Format date range safely
        if pd.notnull(min_date) and pd.notnull(max_date):
            date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        else:
            date_range = "Invalid or missing dates"

        summary_data = {
            "Metric": [
                "Total Influencers",
                "Total Posts",
                "Total Tracking Records",
                "Total Revenue",
                "Date Range"
            ],
            "Value": [
                len(data_manager.influencers),
                len(data_manager.posts),
                len(data_manager.tracking_data),
                f"₹{data_manager.tracking_data['revenue'].sum():,.0f}",
                date_range
            ]
        }

        
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
    else:
        st.info("ℹ️ No data loaded. Upload data to see summary.")

def show_database_management_page():
    st.title("🗄️ Database Management")
    
    data_manager = st.session_state.data_manager
    
    st.markdown("""
    Manage your database and view current data status. All uploaded data is 
    automatically saved to PostgreSQL for persistence across sessions.
    """)
    
    # Database Status
    st.subheader("📊 Database Status")
    
    try:
        if data_manager.db_manager:
            summary = data_manager.db_manager.get_data_summary()
        else:
            # Fallback summary if no database
            summary = {
                'influencers_count': len(data_manager.influencers),
                'posts_count': len(data_manager.posts),
                'tracking_count': len(data_manager.tracking_data),
                'payouts_count': len(data_manager.payouts),
                'total_revenue': data_manager.tracking_data['revenue'].sum() if len(data_manager.tracking_data) > 0 else 0
            }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Influencers", summary["influencers_count"])
        with col2:
            st.metric("Posts", summary["posts_count"])
        with col3:
            st.metric("Tracking Records", summary["tracking_count"])
        with col4:
            st.metric("Payouts", summary["payouts_count"])
        
        if summary["total_revenue"] > 0:
            revenue_value = summary["total_revenue"]
            st.metric("Total Revenue", f"₹{revenue_value:,.0f}")
            
        if data_manager.db_manager:
            st.success("✅ Database connection is working properly")
        else:
            st.warning("⚠️ Using in-memory storage (database not available)")
        
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
    
    st.markdown("---")
    
    # Database Actions
    st.subheader("🔧 Database Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Refresh Data**")
        st.markdown("Reload data from database to sync any external changes.")
        if st.button("🔄 Refresh Data from Database"):
            try:
                data_manager.refresh_data_from_db()
                st.success("✅ Data refreshed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error refreshing data: {str(e)}")
    
    with col2:
        st.markdown("**Load Sample Data**")
        st.markdown("Load pre-created sample data for testing the dashboard.")
        if st.button("📊 Load Sample Data"):
            try:
                # Load sample CSV files we created
                
                influencers_df = pd.read_csv("sample data/sample_influencers.csv")
                posts_df = pd.read_csv("sample data/sample_posts.csv") 
                tracking_df = pd.read_csv("sample data/sample_tracking.csv")
                payouts_df = pd.read_csv("sample data/sample_payouts.csv")
                
                # Save to database
                success1 = data_manager.save_influencers_to_db(influencers_df)
                success2 = data_manager.save_posts_to_db(posts_df)
                success3 = data_manager.save_tracking_data_to_db(tracking_df)
                success4 = data_manager.save_payouts_to_db(payouts_df)
                
                if all([success1, success2, success3, success4]):
                    st.success("✅ Sample data loaded successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to load some sample data")
                    
            except FileNotFoundError:
                st.error("❌ Sample data files not found. Please create them first.")
            except Exception as e:
                st.error(f"❌ Error loading sample data: {str(e)}")
    
    st.markdown("---")
    
    # Danger Zone
    st.subheader("⚠️ Danger Zone")
    st.warning("The following actions cannot be undone!")
    
    if st.button("🗑️ Clear All Database Data", type="secondary"):
        if st.checkbox("I understand this will delete all data permanently"):
            try:
                if data_manager.db_manager:
                    data_manager.db_manager.clear_all_data()
                    data_manager.refresh_data_from_db()
                    st.success("✅ All data cleared from database")
                else:
                    # Clear in-memory data
                    data_manager.influencers = pd.DataFrame()
                    data_manager.posts = pd.DataFrame()
                    data_manager.tracking_data = pd.DataFrame()
                    data_manager.payouts = pd.DataFrame()
                    st.success("✅ All data cleared from memory")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error clearing data: {str(e)}")
    
    # Current Data Preview
    st.markdown("---")
    st.subheader("👀 Current Data Preview")
    
    preview_type = st.selectbox("Select data to preview:", 
                               ["Influencers", "Posts", "Tracking Data", "Payouts"])
    
    if preview_type == "Influencers" and len(data_manager.influencers) > 0:
        st.dataframe(data_manager.influencers.head(10), use_container_width=True)
    elif preview_type == "Posts" and len(data_manager.posts) > 0:
        st.dataframe(data_manager.posts.head(10), use_container_width=True)
    elif preview_type == "Tracking Data" and len(data_manager.tracking_data) > 0:
        st.dataframe(data_manager.tracking_data.head(10), use_container_width=True)
    elif preview_type == "Payouts" and len(data_manager.payouts) > 0:
        st.dataframe(data_manager.payouts.head(10), use_container_width=True)
    else:
        st.info(f"No {preview_type.lower()} data available")

if __name__ == "__main__":
    main()
