import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class AnalyticsEngine:
    """Advanced analytics engine for influencer campaign analysis"""
    
    def __init__(self):
        self.benchmark_roi = 200  # 200% ROI benchmark
        self.benchmark_roas = 4.0  # 4:1 ROAS benchmark
        
    def apply_filters(self, data_manager, platform, brand, category, date_range):
        
        filtered_data = {
            'influencers': data_manager.influencers.copy(),
            'posts': data_manager.posts.copy(),
            'tracking': data_manager.tracking_data.copy(),
            'payouts': data_manager.payouts.copy()
        }

        # Ensure date columns are datetime
        if 'date' in filtered_data['posts'].columns:
            filtered_data['posts']['date'] = pd.to_datetime(filtered_data['posts']['date'], errors='coerce')
        if 'date' in filtered_data['tracking'].columns:
            filtered_data['tracking']['date'] = pd.to_datetime(filtered_data['tracking']['date'], errors='coerce')

        # Apply platform filter
        if platform != 'All':
            influencer_ids = filtered_data['influencers'][
                filtered_data['influencers']['platform'] == platform
            ]['ID'].tolist()

            filtered_data['posts'] = filtered_data['posts'][
                filtered_data['posts']['influencer_id'].isin(influencer_ids)
            ]
            filtered_data['tracking'] = filtered_data['tracking'][
                filtered_data['tracking']['influencer_id'].isin(influencer_ids)
            ]
            filtered_data['payouts'] = filtered_data['payouts'][
                filtered_data['payouts']['influencer_id'].isin(influencer_ids)
            ]
            filtered_data['influencers'] = filtered_data['influencers'][
                filtered_data['influencers']['ID'].isin(influencer_ids)
            ]

        # Apply category filter
        if category != 'All':
            influencer_ids = filtered_data['influencers'][
                filtered_data['influencers']['category'] == category
            ]['ID'].tolist()

            filtered_data['posts'] = filtered_data['posts'][
                filtered_data['posts']['influencer_id'].isin(influencer_ids)
            ]
            filtered_data['tracking'] = filtered_data['tracking'][
                filtered_data['tracking']['influencer_id'].isin(influencer_ids)
            ]
            filtered_data['payouts'] = filtered_data['payouts'][
                filtered_data['payouts']['influencer_id'].isin(influencer_ids)
            ]
            filtered_data['influencers'] = filtered_data['influencers'][
                filtered_data['influencers']['ID'].isin(influencer_ids)
            ]

        # Apply brand/campaign filter
        if brand != 'All':
            filtered_data['tracking'] = filtered_data['tracking'][
                filtered_data['tracking']['campaign'] == brand
            ]

        # Apply date filter
        if len(date_range) == 2:
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])

            if not filtered_data['posts'].empty:
                filtered_data['posts'] = filtered_data['posts'][
                    (filtered_data['posts']['date'] >= start_date) &
                    (filtered_data['posts']['date'] <= end_date)
                ]

            if not filtered_data['tracking'].empty:
                filtered_data['tracking'] = filtered_data['tracking'][
                    (filtered_data['tracking']['date'] >= start_date) &
                    (filtered_data['tracking']['date'] <= end_date)
                ]

        return filtered_data

    
    def calculate_roi_roas(self, filtered_data):
        """Calculate ROI and ROAS metrics"""
        tracking_data = filtered_data['tracking']
        payouts_data = filtered_data['payouts']
        
        if len(tracking_data) == 0:
            return {
                'avg_roi': 0,
                'avg_roas': 0,
                'roi_change': 0,
                'roas_change': 0
            }
        
        # Calculate total revenue and costs
        total_revenue = tracking_data['revenue'].sum()
        
        # Estimate costs from payouts
        if len(payouts_data) > 0:
            # Get influencers in tracking data
            influencer_ids = tracking_data['influencer_id'].unique()
            relevant_payouts = payouts_data[payouts_data['influencer_id'].isin(influencer_ids)]
            total_cost = relevant_payouts['total_payout'].sum()
        else:
            # Estimate cost as 25% of revenue if no payout data
            total_cost = total_revenue * 0.25
        
        # Calculate metrics
        roi = ((total_revenue - total_cost) / max(total_cost, 1)) * 100 if total_cost > 0 else 0
        roas = total_revenue / max(total_cost, 1) if total_cost > 0 else 0
        
        # Calculate period-over-period changes (mock calculation)
        roi_change = roi - self.benchmark_roi
        roas_change = roas - self.benchmark_roas
        
        return {
            'avg_roi': roi,
            'avg_roas': roas,
            'roi_change': roi_change,
            'roas_change': roas_change,
            'total_revenue': total_revenue,
            'total_cost': total_cost
        }
    
    def get_top_performers(self, filtered_data, limit=10):
        """Get top performing influencers"""
        tracking_data = filtered_data['tracking']
        influencers_data = filtered_data['influencers']
        posts_data = filtered_data['posts']
        
        if len(tracking_data) == 0 or len(influencers_data) == 0:
            return pd.DataFrame()
        
        # Aggregate performance by influencer
        performance = tracking_data.groupby('influencer_id').agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        # Add influencer details
        performance = performance.merge(
            influencers_data[['ID', 'name', 'platform', 'category', 'follower_count']],
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        # Add engagement metrics if posts data is available
        if len(posts_data) > 0:
            engagement_metrics = posts_data.groupby('influencer_id').agg({
                'reach': 'sum',
                'likes': 'sum',
                'comments': 'sum'
            }).reset_index()
            
            engagement_metrics['engagement_rate'] = (
                (engagement_metrics['likes'] + engagement_metrics['comments']) / 
                engagement_metrics['reach'] * 100
            ).fillna(0)
            
            performance = performance.merge(
                engagement_metrics,
                on='influencer_id',
                how='left'
            )
        
        # Calculate additional metrics
        performance['revenue_per_follower'] = performance['revenue'] / performance['follower_count']
        performance['orders_per_post'] = performance['orders'] / performance.get('reach', 1).fillna(1)
        
        # Sort by revenue and return top performers
        return performance.sort_values('revenue', ascending=False).head(limit)
    
    def generate_insights(self, data_manager):
        """Generate comprehensive insights from all data"""
        insights = {}
        
        # Top influencers analysis
        insights['top_influencers'] = self._analyze_top_influencers(data_manager)
        
        # Platform analysis
        insights['platform_analysis'] = self._analyze_platforms(data_manager)
        
        # Category analysis
        insights['category_analysis'] = self._analyze_categories(data_manager)
        
        # Poor performers
        insights['poor_performers'] = self._identify_poor_performers(data_manager)
        
        # Trend analysis
        insights['trends'] = self._analyze_trends(data_manager)
        
        return insights
    
    def _analyze_top_influencers(self, data_manager):
        """Analyze top performing influencers"""
        if len(data_manager.tracking_data) == 0:
            return {'by_revenue': pd.DataFrame(), 'by_roi': pd.DataFrame()}
        
        # Merge tracking data with influencer info
        merged_df = data_manager.tracking_data.merge(
            data_manager.influencers,
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        # Group by influencer
        influencer_performance = merged_df.groupby(['influencer_id', 'name', 'platform']).agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        # Calculate ROI (assuming 25% cost of revenue)
        influencer_performance['cost'] = influencer_performance['revenue'] * 0.25
        influencer_performance['roi'] = ((influencer_performance['revenue'] - influencer_performance['cost']) / 
                                       influencer_performance['cost'] * 100).fillna(0)
        
        # Top by revenue
        top_by_revenue = influencer_performance.sort_values('revenue', ascending=False).head(10)
        
        # Top by ROI
        top_by_roi = influencer_performance.sort_values('roi', ascending=False).head(10)
        
        return {
            'by_revenue': top_by_revenue,
            'by_roi': top_by_roi
        }
    
    def _analyze_platforms(self, data_manager):
        """Analyze performance by platform"""
        if len(data_manager.tracking_data) == 0 or len(data_manager.influencers) == 0:
            return pd.DataFrame()
        
        # Merge data
        merged_df = data_manager.tracking_data.merge(
            data_manager.influencers,
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        # Platform analysis
        platform_stats = merged_df.groupby('platform').agg({
            'revenue': 'sum',
            'orders': 'sum',
            'influencer_id': 'nunique'
        }).reset_index()
        
        platform_stats.columns = ['platform', 'total_revenue', 'total_orders', 'influencer_count']
        
        # Calculate averages
        platform_stats['avg_revenue_per_influencer'] = (
            platform_stats['total_revenue'] / platform_stats['influencer_count']
        ).round(2)
        
        # Add engagement rate if posts data is available
        if len(data_manager.posts) > 0 and 'platform' in data_manager.posts.columns:
            engagement_by_platform = data_manager.posts.groupby('platform').apply(
                lambda x: ((x['likes'].sum() + x['comments'].sum()) / x['reach'].sum() * 100) if x['reach'].sum() > 0 else 0
            ).reset_index()
            engagement_by_platform.columns = ['platform', 'avg_engagement_rate']
            
            platform_stats = platform_stats.merge(engagement_by_platform, on='platform', how='left')
        else:
            platform_stats['avg_engagement_rate'] = 0
        
        # Calculate ROI
        platform_stats['estimated_cost'] = platform_stats['total_revenue'] * 0.25
        platform_stats['avg_roi'] = ((platform_stats['total_revenue'] - platform_stats['estimated_cost']) / 
                                    platform_stats['estimated_cost'] * 100).fillna(0)
        
        return platform_stats
    
    def _analyze_categories(self, data_manager):
        """Analyze performance by influencer category"""
        if len(data_manager.influencers) == 0:
            return pd.DataFrame()
        
        category_stats = data_manager.influencers.groupby('category').agg({
            'follower_count': ['count', 'mean', 'sum'],
            'ID': 'count'
        }).round(2)
        
        category_stats.columns = ['total_posts', 'avg_follower_count', 'total_followers', 'influencer_count']
        category_stats = category_stats.reset_index()
        
        # Add revenue data if available
        if len(data_manager.tracking_data) > 0:
            merged_df = data_manager.tracking_data.merge(
                data_manager.influencers,
                left_on='influencer_id',
                right_on='ID',
                how='left'
            )
            
            revenue_by_category = merged_df.groupby('category').agg({
                'revenue': 'sum',
                'orders': 'sum'
            }).reset_index()
            
            category_stats = category_stats.merge(revenue_by_category, on='category', how='left')
            category_stats['avg_revenue_per_post'] = (
                category_stats['revenue'] / category_stats['total_posts']
            ).fillna(0)
            
            # Calculate ROI
            category_stats['estimated_cost'] = category_stats['revenue'] * 0.25
            category_stats['avg_roi'] = ((category_stats['revenue'] - category_stats['estimated_cost']) / 
                                        category_stats['estimated_cost'] * 100).fillna(0)
        
        return category_stats
    
    def _identify_poor_performers(self, data_manager):
        """Identify underperforming influencers"""
        if len(data_manager.tracking_data) == 0 or len(data_manager.influencers) == 0:
            return pd.DataFrame()
        
        # Get performance data
        merged_df = data_manager.tracking_data.merge(
            data_manager.influencers,
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        performance = merged_df.groupby(['influencer_id', 'name', 'platform']).agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        # Calculate ROI
        performance['cost'] = performance['revenue'] * 0.25
        performance['roi'] = ((performance['revenue'] - performance['cost']) / 
                             performance['cost'] * 100).fillna(0)
        
        # Identify poor performers (ROI < benchmark)
        poor_performers = performance[performance['roi'] < self.benchmark_roi].copy()
        
        # Add reasons
        poor_performers['reason'] = poor_performers.apply(
            lambda row: self._get_poor_performance_reason(row), axis=1
        )
        
        return poor_performers.sort_values('roi')
    
    def _get_poor_performance_reason(self, row):
        """Determine reason for poor performance"""
        if row['revenue'] < 1000:
            return "Low revenue generation"
        elif row['orders'] < 10:
            return "Low order conversion"
        elif row['roi'] < 50:
            return "Very low ROI"
        else:
            return "Below benchmark ROI"
    
    def _analyze_trends(self, data_manager):
        """Analyze trends over time"""
        if len(data_manager.tracking_data) == 0:
            return {}
        
        # Daily trends
        daily_trends = data_manager.tracking_data.groupby('date').agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        # Weekly trends
        data_manager.tracking_data['week'] = pd.to_datetime(data_manager.tracking_data['date']).dt.isocalendar().week
        weekly_trends = data_manager.tracking_data.groupby('week').agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        return {
            'daily': daily_trends,
            'weekly': weekly_trends
        }
    
    def calculate_incremental_roas(self, data_manager, baseline_period_days=30):
        """Calculate incremental ROAS by comparing to baseline"""
        if len(data_manager.tracking_data) == 0:
            return 0
        
        # Get recent data
        recent_date = data_manager.tracking_data['date'].max()
        baseline_start = recent_date - timedelta(days=baseline_period_days)
        
        baseline_data = data_manager.tracking_data[
            data_manager.tracking_data['date'] < baseline_start
        ]
        recent_data = data_manager.tracking_data[
            data_manager.tracking_data['date'] >= baseline_start
        ]
        
        if len(baseline_data) == 0 or len(recent_data) == 0:
            return 0
        
        # Calculate baseline metrics
        baseline_revenue = baseline_data['revenue'].mean()
        recent_revenue = recent_data['revenue'].mean()
        
        # Incremental revenue
        incremental_revenue = recent_revenue - baseline_revenue
        
        # Estimate cost (25% of revenue)
        estimated_cost = recent_revenue * 0.25
        
        # Incremental ROAS
        incremental_roas = incremental_revenue / max(estimated_cost, 1) if estimated_cost > 0 else 0
        
        return max(incremental_roas, 0)
