import pandas as pd
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64

def export_to_csv(data_manager):
    """Export campaign data to CSV format"""
    
    # Create a comprehensive report combining all data
    output = io.StringIO()
    
    # Summary statistics
    summary_data = []
    summary_data.append(['Metric', 'Value'])
    summary_data.append(['Total Influencers', len(data_manager.influencers)])
    summary_data.append(['Total Posts', len(data_manager.posts)])
    summary_data.append(['Total Tracking Records', len(data_manager.tracking_data)])
    summary_data.append(['Total Revenue', f"₹{data_manager.tracking_data['revenue'].sum():,.2f}" if len(data_manager.tracking_data) > 0 else "₹0"])
    summary_data.append(['Total Orders', data_manager.tracking_data['orders'].sum() if len(data_manager.tracking_data) > 0 else 0])
    summary_data.append(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    
    # Write summary
    output.write("HEALTHKART INFLUENCER CAMPAIGN REPORT\n")
    output.write("="*50 + "\n\n")
    output.write("SUMMARY STATISTICS\n")
    output.write("-"*20 + "\n")
    
    for row in summary_data:
        output.write(f"{row[0]}: {row[1]}\n")
    
    output.write("\n" + "="*50 + "\n\n")
    
    # Detailed performance data
    if len(data_manager.tracking_data) > 0 and len(data_manager.influencers) > 0:
        # Merge tracking data with influencer info
        detailed_data = data_manager.tracking_data.merge(
            data_manager.influencers,
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        # Add posts data if available
        if len(data_manager.posts) > 0:
            posts_agg = data_manager.posts.groupby('influencer_id').agg({
                'reach': 'sum',
                'likes': 'sum',
                'comments': 'sum'
            }).reset_index()
            
            detailed_data = detailed_data.merge(posts_agg, on='influencer_id', how='left')
        
        # Add payout data if available
        if len(data_manager.payouts) > 0:
            detailed_data = detailed_data.merge(
                data_manager.payouts[['influencer_id', 'basis', 'rate', 'total_payout']],
                on='influencer_id',
                how='left'
            )
        
        output.write("DETAILED PERFORMANCE DATA\n")
        output.write("-"*25 + "\n")
        detailed_data.to_csv(output, index=False)
        
        output.write("\n" + "="*50 + "\n\n")
    
    # Platform summary
    if len(data_manager.influencers) > 0:
        platform_summary = data_manager.influencers.groupby('platform').agg({
            'ID': 'count',
            'follower_count': ['sum', 'mean']
        }).round(2)
        
        output.write("PLATFORM SUMMARY\n")
        output.write("-"*16 + "\n")
        platform_summary.to_csv(output)
        
        output.write("\n" + "="*50 + "\n\n")
    
    # Campaign performance
    if len(data_manager.tracking_data) > 0:
        campaign_summary = data_manager.tracking_data.groupby('campaign').agg({
            'revenue': 'sum',
            'orders': 'sum',
            'influencer_id': 'nunique'
        }).round(2)
        
        output.write("CAMPAIGN PERFORMANCE\n")
        output.write("-"*19 + "\n")
        campaign_summary.to_csv(output)
    
    csv_string = output.getvalue()
    output.close()
    
    return csv_string

def export_to_pdf(data_manager, analytics):
    """Export insights and summary to PDF format"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#FF6B35')
    )
    
    # Title
    story.append(Paragraph("HealthKart Influencer Campaign Report", title_style))
    story.append(Spacer(1, 20))
    
    # Report metadata
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    summary_text = f"""
    This report provides a comprehensive analysis of HealthKart's influencer campaign performance. 
    The data encompasses {len(data_manager.influencers)} influencers across {len(data_manager.influencers['platform'].unique()) if len(data_manager.influencers) > 0 else 0} platforms, 
    generating a total revenue of ₹{data_manager.tracking_data['revenue'].sum():,.0f if len(data_manager.tracking_data) > 0 else 0} 
    from {data_manager.tracking_data['orders'].sum() if len(data_manager.tracking_data) > 0 else 0} orders.
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Key Metrics Table
    story.append(Paragraph("Key Performance Indicators", heading_style))
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Total Influencers', str(len(data_manager.influencers))],
        ['Total Posts', str(len(data_manager.posts))],
        ['Total Revenue', f"₹{data_manager.tracking_data['revenue'].sum():,.0f}" if len(data_manager.tracking_data) > 0 else "₹0"],
        ['Total Orders', str(data_manager.tracking_data['orders'].sum() if len(data_manager.tracking_data) > 0 else 0)],
        ['Average Order Value', f"₹{(data_manager.tracking_data['revenue'].sum() / max(data_manager.tracking_data['orders'].sum(), 1)):,.0f}" if len(data_manager.tracking_data) > 0 else "₹0"],
    ]
    
    metrics_table = Table(metrics_data)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Platform Analysis
    if len(data_manager.influencers) > 0:
        story.append(Paragraph("Platform Performance Analysis", heading_style))
        
        platform_stats = data_manager.influencers.groupby('platform').agg({
            'ID': 'count',
            'follower_count': ['sum', 'mean']
        }).round(0)
        
        platform_data = [['Platform', 'Influencers', 'Total Followers', 'Avg Followers']]
        for platform, row in platform_stats.iterrows():
            platform_data.append([
                platform,
                str(int(row[('ID', 'count')])),
                f"{int(row[('follower_count', 'sum')]):,}",
                f"{int(row[('follower_count', 'mean')]):,}"
            ])
        
        platform_table = Table(platform_data)
        platform_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(platform_table)
        story.append(Spacer(1, 20))
    
    # Top Performers
    if len(data_manager.tracking_data) > 0 and len(data_manager.influencers) > 0:
        story.append(Paragraph("Top Performing Influencers", heading_style))
        
        # Get top performers
        filtered_data = {
            'tracking': data_manager.tracking_data,
            'influencers': data_manager.influencers,
            'posts': data_manager.posts,
            'payouts': data_manager.payouts
        }
        
        top_performers = analytics.get_top_performers(filtered_data, limit=5)
        
        if len(top_performers) > 0:
            performer_data = [['Name', 'Platform', 'Revenue', 'Orders', 'Revenue per Follower']]
            for _, row in top_performers.iterrows():
                performer_data.append([
                    row['name'][:20] + "..." if len(str(row['name'])) > 20 else str(row['name']),
                    str(row['platform']),
                    f"₹{row['revenue']:,.0f}",
                    str(int(row['orders'])),
                    f"₹{row['revenue_per_follower']:.2f}" if pd.notna(row['revenue_per_follower']) else "N/A"
                ])
            
            performer_table = Table(performer_data)
            performer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(performer_table)
            story.append(Spacer(1, 20))
    
    # ROI Analysis
    if len(data_manager.tracking_data) > 0:
        story.append(Paragraph("ROI & ROAS Analysis", heading_style))
        
        filtered_data = {
            'tracking': data_manager.tracking_data,
            'influencers': data_manager.influencers,
            'posts': data_manager.posts,
            'payouts': data_manager.payouts
        }
        
        roi_data = analytics.calculate_roi_roas(filtered_data)
        
        roi_text = f"""
        <b>Return on Investment (ROI):</b> {roi_data['avg_roi']:.1f}%<br/>
        <b>Return on Ad Spend (ROAS):</b> {roi_data['avg_roas']:.2f}:1<br/>
        <b>Total Revenue:</b> ₹{roi_data['total_revenue']:,.0f}<br/>
        <b>Estimated Investment:</b> ₹{roi_data['total_cost']:,.0f}<br/><br/>
        
        The campaign demonstrates {'strong' if roi_data['avg_roi'] > 200 else 'moderate' if roi_data['avg_roi'] > 100 else 'weak'} 
        performance with an ROI of {roi_data['avg_roi']:.1f}%. Industry benchmarks suggest targeting 
        ROI above 200% for influencer campaigns.
        """
        
        story.append(Paragraph(roi_text, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    
    recommendations = get_recommendations(data_manager, analytics)
    for i, rec in enumerate(recommendations, 1):
        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        story.append(Spacer(1, 8))
    
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("Report generated by HealthKart Analytics Dashboard", styles['Italic']))
    
    # Build PDF
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def get_recommendations(data_manager, analytics):
    """Generate actionable recommendations based on data analysis"""
    recommendations = []
    
    if len(data_manager.tracking_data) == 0:
        return ["Upload campaign data to generate personalized recommendations."]
    
    # Analyze platform performance
    if len(data_manager.influencers) > 0:
        platform_revenue = data_manager.tracking_data.merge(
            data_manager.influencers,
            left_on='influencer_id',
            right_on='ID',
            how='left'
        ).groupby('platform')['revenue'].sum().sort_values(ascending=False)
        
        if len(platform_revenue) > 0:
            top_platform = platform_revenue.index[0]
            recommendations.append(f"Focus investment on {top_platform} as it generates the highest revenue (₹{platform_revenue.iloc[0]:,.0f})")
    
    # Analyze ROI
    filtered_data = {
        'tracking': data_manager.tracking_data,
        'influencers': data_manager.influencers,
        'posts': data_manager.posts,
        'payouts': data_manager.payouts
    }
    
    roi_data = analytics.calculate_roi_roas(filtered_data)
    
    if roi_data['avg_roi'] < 150:
        recommendations.append("Consider optimizing campaign costs as ROI is below industry standards (target: >200%)")
    elif roi_data['avg_roi'] > 300:
        recommendations.append("Excellent ROI performance! Consider scaling successful campaigns")
    
    # Analyze engagement if posts data available
    if len(data_manager.posts) > 0:
        avg_engagement = ((data_manager.posts['likes'] + data_manager.posts['comments']) / 
                         data_manager.posts['reach'] * 100).mean()
        
        if avg_engagement < 2:
            recommendations.append("Work on content strategy to improve engagement rates (currently below 2%)")
        elif avg_engagement > 5:
            recommendations.append("High engagement rates detected! Leverage successful content formats")
    
    # Order conversion analysis
    total_orders = data_manager.tracking_data['orders'].sum()
    total_revenue = data_manager.tracking_data['revenue'].sum()
    
    if total_orders > 0:
        avg_order_value = total_revenue / total_orders
        if avg_order_value < 500:
            recommendations.append("Focus on promoting higher-value products to increase average order value")
        elif avg_order_value > 2000:
            recommendations.append("Strong average order value! Consider expanding premium product campaigns")
    
    # Seasonal analysis
    if len(data_manager.tracking_data) > 30:  # If we have enough data
        data_manager.tracking_data['month'] = pd.to_datetime(data_manager.tracking_data['date']).dt.month
        monthly_performance = data_manager.tracking_data.groupby('month')['revenue'].sum()
        
        if len(monthly_performance) > 1:
            best_month = monthly_performance.idxmax()
            recommendations.append(f"Month {best_month} shows peak performance - plan major campaigns during similar periods")
    
    # Diversification recommendation
    unique_campaigns = data_manager.tracking_data['campaign'].nunique()
    if unique_campaigns < 3:
        recommendations.append("Consider diversifying campaigns across more brands/products to reduce risk")
    
    # Default recommendations if none generated
    if not recommendations:
        recommendations = [
            "Continue monitoring campaign performance regularly",
            "Experiment with different content formats and posting schedules",
            "Consider A/B testing different influencer categories",
            "Set up automated alerts for significant performance changes"
        ]
    
    return recommendations[:6]  # Limit to top 6 recommendations

def format_currency(amount):
    """Format currency in Indian Rupees"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.1f}L"
    elif amount >= 1000:  # 1 thousand
        return f"₹{amount/1000:.1f}K"
    else:
        return f"₹{amount:.0f}"

def format_number(number):
    """Format large numbers with appropriate suffixes"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(int(number))

def validate_date_range(start_date, end_date):
    """Validate date range inputs"""
    if start_date > end_date:
        return False, "Start date cannot be after end date"
    
    if (end_date - start_date).days > 365:
        return False, "Date range cannot exceed 365 days"
    
    if end_date > datetime.now().date():
        return False, "End date cannot be in the future"
    
    return True, "Valid date range"

def calculate_growth_rate(current_value, previous_value):
    """Calculate growth rate between two values"""
    if previous_value == 0:
        return 100 if current_value > 0 else 0
    
    return ((current_value - previous_value) / previous_value) * 100
