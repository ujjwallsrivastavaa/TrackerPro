import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

# Try to import database manager, but make it optional
db_manager = None
try:
    from database import db_manager
    logger.info("Database connection available")
except Exception as e:
    logger.warning(f"Database not available: {e}")

class DataManager:
    """Manages all data operations for the influencer campaign dashboard"""
    
    def __init__(self):
        # Initialize with empty dataframes
        self.influencers = pd.DataFrame()
        self.posts = pd.DataFrame()
        self.tracking_data = pd.DataFrame()
        self.payouts = pd.DataFrame()
        
        # Set up database manager if available
        self.db_manager = db_manager
        
        # Try to load data from database, but don't fail if connection issues
        if self.db_manager:
            try:
                self.refresh_data_from_db()
            except Exception as e:
                logger.warning(f"Could not load data from database on initialization: {e}")
                # Continue with empty dataframes
    
    def refresh_data_from_db(self):
        """Load all data from database"""
        if not self.db_manager:
            logger.warning("Database not available, keeping current data")
            return
        
        try:
            self.influencers = self.db_manager.get_influencers_df()
            self.posts = self.db_manager.get_posts_df()
            self.tracking_data = self.db_manager.get_tracking_data_df()
            self.payouts = self.db_manager.get_payouts_df()
            logger.info("Data successfully loaded from database")
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            # Keep existing data if refresh fails
    
    def save_influencers_to_db(self, df: pd.DataFrame) -> bool:
        """Save influencers data to database"""
        if not self.db_manager:
            # Fallback to in-memory storage if no database
            self.influencers = df
            return True
        
        try:
            success = self.db_manager.bulk_insert_influencers(df)
            if success:
                self.influencers = df
            return success
        except Exception as e:
            logger.error(f"Database save failed, using in-memory storage: {e}")
            self.influencers = df
            return True
    
    def save_posts_to_db(self, df: pd.DataFrame) -> bool:
        """Save posts data to database"""
        if not self.db_manager:
            self.posts = df
            return True
        
        try:
            success = self.db_manager.bulk_insert_posts(df)
            if success:
                self.posts = df
            return success
        except Exception as e:
            logger.error(f"Database save failed, using in-memory storage: {e}")
            self.posts = df
            return True
    
    def save_tracking_data_to_db(self, df: pd.DataFrame) -> bool:
        """Save tracking data to database"""
        if not self.db_manager:
            self.tracking_data = df
            return True
        
        try:
            success = self.db_manager.bulk_insert_tracking_data(df)
            if success:
                self.tracking_data = df
            return success
        except Exception as e:
            logger.error(f"Database save failed, using in-memory storage: {e}")
            self.tracking_data = df
            return True
    
    def save_payouts_to_db(self, df: pd.DataFrame) -> bool:
        """Save payouts data to database"""
        if not self.db_manager:
            self.payouts = df
            return True
        
        try:
            success = self.db_manager.bulk_insert_payouts(df)
            if success:
                self.payouts = df
            return success
        except Exception as e:
            logger.error(f"Database save failed, using in-memory storage: {e}")
            self.payouts = df
            return True
        
    def validate_data(self, df, required_columns, data_type):
        """Validate uploaded data against required schema"""
        errors = []
        
        # Check for required columns
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
            
        # Data type specific validations
        if data_type == "influencers":
            errors.extend(self._validate_influencers(df))
        elif data_type == "posts":
            errors.extend(self._validate_posts(df))
        elif data_type == "tracking":
            errors.extend(self._validate_tracking(df))
        elif data_type == "payouts":
            errors.extend(self._validate_payouts(df))
            
        return errors
    
    def _validate_influencers(self, df):
        """Validate influencers data"""
        errors = []
        
        if 'follower_count' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['follower_count']):
                errors.append("follower_count must be numeric")
        
        valid_platforms = ['Instagram', 'YouTube', 'Twitter', 'Facebook', 'TikTok', 'LinkedIn']
        if 'platform' in df.columns:
            invalid_platforms = set(df['platform'].unique()) - set(valid_platforms)
            if invalid_platforms:
                errors.append(f"Invalid platforms: {invalid_platforms}. Valid platforms: {valid_platforms}")
        
        return errors
    
    def _validate_posts(self, df):
        """Validate posts data"""
        errors = []
        
        numeric_cols = ['reach', 'likes', 'comments']
        for col in numeric_cols:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"{col} must be numeric")
        
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except:
                errors.append("date column contains invalid dates")
        
        return errors
    
    def _validate_tracking(self, df):
        """Validate tracking data"""
        errors = []
        
        numeric_cols = ['orders', 'revenue']
        for col in numeric_cols:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"{col} must be numeric")
        
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except:
                errors.append("date column contains invalid dates")
        
        return errors
    
    def _validate_payouts(self, df):
        """Validate payouts data"""
        errors = []
        
        numeric_cols = ['rate', 'orders', 'total_payout']
        for col in numeric_cols:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"{col} must be numeric")
        
        valid_basis = ['post', 'order']
        if 'basis' in df.columns:
            invalid_basis = set(df['basis'].unique()) - set(valid_basis)
            if invalid_basis:
                errors.append(f"Invalid basis values: {invalid_basis}. Valid values: {valid_basis}")
        
        return errors
    
    def get_data_summary(self):
        """Get summary statistics of loaded data"""
        summary = {
            'influencers': {
                'count': len(self.influencers),
                'platforms': list(self.influencers['platform'].unique()) if len(self.influencers) > 0 else [],
                'categories': list(self.influencers['category'].unique()) if len(self.influencers) > 0 else []
            },
            'posts': {
                'count': len(self.posts),
                'date_range': f"{self.posts['date'].min()} to {self.posts['date'].max()}" if len(self.posts) > 0 else "No data",
                'total_reach': self.posts['reach'].sum() if len(self.posts) > 0 else 0
            },
            'tracking': {
                'count': len(self.tracking_data),
                'total_revenue': self.tracking_data['revenue'].sum() if len(self.tracking_data) > 0 else 0,
                'total_orders': self.tracking_data['orders'].sum() if len(self.tracking_data) > 0 else 0
            },
            'payouts': {
                'count': len(self.payouts),
                'total_amount': self.payouts['total_payout'].sum() if len(self.payouts) > 0 else 0
            }
        }
        
        return summary
    
    def merge_data_for_analysis(self):
        """Merge all datasets for comprehensive analysis"""
        if len(self.tracking_data) == 0 or len(self.influencers) == 0:
            return pd.DataFrame()
        
        # Start with tracking data
        merged_df = self.tracking_data.copy()
        
        # Add influencer information
        merged_df = merged_df.merge(
            self.influencers,
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        # Add post information if available
        if len(self.posts) > 0:
            # Group posts by influencer and date to get aggregated metrics
            post_agg = self.posts.groupby(['influencer_id', 'date']).agg({
                'reach': 'sum',
                'likes': 'sum',
                'comments': 'sum'
            }).reset_index()
            
            merged_df = merged_df.merge(
                post_agg,
                on=['influencer_id', 'date'],
                how='left'
            )
        
        # Add payout information if available
        if len(self.payouts) > 0:
            merged_df = merged_df.merge(
                self.payouts,
                on='influencer_id',
                how='left'
            )
        
        return merged_df
    
    def get_influencer_performance(self, influencer_id):
        """Get detailed performance metrics for a specific influencer"""
        if len(self.tracking_data) == 0:
            return {}
        
        # Filter data for the specific influencer
        influencer_data = self.tracking_data[
            self.tracking_data['influencer_id'] == influencer_id
        ]
        
        if len(influencer_data) == 0:
            return {}
        
        # Calculate performance metrics
        performance = {
            'total_revenue': influencer_data['revenue'].sum(),
            'total_orders': influencer_data['orders'].sum(),
            'avg_order_value': influencer_data['revenue'].sum() / max(influencer_data['orders'].sum(), 1),
            'active_days': influencer_data['date'].nunique(),
            'campaigns': influencer_data['campaign'].unique().tolist(),
            'products': influencer_data['product'].unique().tolist()
        }
        
        # Add post metrics if available
        if len(self.posts) > 0:
            influencer_posts = self.posts[
                self.posts['influencer_id'] == influencer_id
            ]
            
            if len(influencer_posts) > 0:
                performance.update({
                    'total_posts': len(influencer_posts),
                    'total_reach': influencer_posts['reach'].sum(),
                    'total_engagement': influencer_posts['likes'].sum() + influencer_posts['comments'].sum(),
                    'avg_engagement_rate': ((influencer_posts['likes'].sum() + influencer_posts['comments'].sum()) / 
                                          max(influencer_posts['reach'].sum(), 1)) * 100
                })
        
        # Add payout information if available
        if len(self.payouts) > 0:
            influencer_payout = self.payouts[
                self.payouts['influencer_id'] == influencer_id
            ]
            
            if len(influencer_payout) > 0:
                performance.update({
                    'payout_basis': influencer_payout['basis'].iloc[0],
                    'payout_rate': influencer_payout['rate'].iloc[0],
                    'total_payout': influencer_payout['total_payout'].iloc[0]
                })
        
        return performance
    
    def export_summary_data(self):
        """Export summary data for reporting"""
        summary = {}
        
        if len(self.influencers) > 0:
            summary['influencer_summary'] = self.influencers.groupby(['platform', 'category']).agg({
                'follower_count': ['count', 'mean', 'sum']
            }).round(2)
        
        if len(self.tracking_data) > 0:
            summary['campaign_summary'] = self.tracking_data.groupby('campaign').agg({
                'revenue': 'sum',
                'orders': 'sum',
                'influencer_id': 'nunique'
            }).round(2)
            
            summary['daily_performance'] = self.tracking_data.groupby('date').agg({
                'revenue': 'sum',
                'orders': 'sum'
            }).round(2)
        
        return summary
