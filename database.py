import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not found")

# Create engine with SSL configuration for Replit
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "sslmode": "prefer"
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Influencer(Base):
    __tablename__ = "influencers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=False)
    follower_count = Column(Integer, nullable=False)
    platform = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, nullable=False)
    platform = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    url = Column(Text, nullable=False)
    caption = Column(Text)
    reach = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)
    comments = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrackingData(Base):
    __tablename__ = "tracking_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    campaign = Column(String(255), nullable=False)
    influencer_id = Column(Integer, nullable=False)
    user_id = Column(String(100), nullable=False)
    product = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    orders = Column(Integer, nullable=False, default=0)
    revenue = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payout(Base):
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, nullable=False)
    basis = Column(String(20), nullable=False)  # 'post' or 'order'
    rate = Column(Float, nullable=False)
    orders = Column(Integer, nullable=False, default=0)
    total_payout = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Manages database operations for the influencer campaign dashboard"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def bulk_insert_influencers(self, df: pd.DataFrame) -> bool:
        """Insert influencers data from DataFrame"""
        session = self.get_session()
        try:
            # Clear existing data
            session.query(Influencer).delete()
            
            # Insert new data
            for _, row in df.iterrows():
                influencer = Influencer(
                    id=int(row['ID']),
                    name=str(row['name']),
                    category=str(row['category']),
                    gender=str(row['gender']),
                    follower_count=int(row['follower_count']),
                    platform=str(row['platform'])
                )
                session.add(influencer)
            
            session.commit()
            logger.info(f"Inserted {len(df)} influencers")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting influencers: {e}")
            return False
        finally:
            session.close()
    
    def bulk_insert_posts(self, df: pd.DataFrame) -> bool:
        """Insert posts data from DataFrame"""
        session = self.get_session()
        try:
            # Clear existing data
            session.query(Post).delete()
            
            # Insert new data
            for _, row in df.iterrows():
                post = Post(
                    influencer_id=int(row['influencer_id']),
                    platform=str(row['platform']),
                    date=pd.to_datetime(row['date']),
                    url=str(row['URL']),
                    caption=str(row['caption']),
                    reach=int(row['reach']),
                    likes=int(row['likes']),
                    comments=int(row['comments'])
                )
                session.add(post)
            
            session.commit()
            logger.info(f"Inserted {len(df)} posts")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting posts: {e}")
            return False
        finally:
            session.close()
    
    def bulk_insert_tracking_data(self, df: pd.DataFrame) -> bool:
        """Insert tracking data from DataFrame"""
        session = self.get_session()
        try:
            # Clear existing data
            session.query(TrackingData).delete()
            
            # Insert new data
            for _, row in df.iterrows():
                tracking = TrackingData(
                    source=str(row['source']),
                    campaign=str(row['campaign']),
                    influencer_id=int(row['influencer_id']),
                    user_id=str(row['user_id']),
                    product=str(row['product']),
                    date=pd.to_datetime(row['date']),
                    orders=int(row['orders']),
                    revenue=float(row['revenue'])
                )
                session.add(tracking)
            
            session.commit()
            logger.info(f"Inserted {len(df)} tracking records")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting tracking data: {e}")
            return False
        finally:
            session.close()
    
    def bulk_insert_payouts(self, df: pd.DataFrame) -> bool:
        """Insert payouts data from DataFrame"""
        session = self.get_session()
        try:
            # Clear existing data
            session.query(Payout).delete()
            
            # Insert new data
            for _, row in df.iterrows():
                payout = Payout(
                    influencer_id=int(row['influencer_id']),
                    basis=str(row['basis']),
                    rate=float(row['rate']),
                    orders=int(row['orders']),
                    total_payout=float(row['total_payout'])
                )
                session.add(payout)
            
            session.commit()
            logger.info(f"Inserted {len(df)} payout records")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting payouts: {e}")
            return False
        finally:
            session.close()
    
    def get_influencers_df(self) -> pd.DataFrame:
        """Get influencers data as DataFrame"""
        session = self.get_session()
        try:
            result = session.query(Influencer).all()
            data = []
            for row in result:
                data.append({
                    'ID': row.id,
                    'name': row.name,
                    'category': row.category,
                    'gender': row.gender,
                    'follower_count': row.follower_count,
                    'platform': row.platform
                })
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def get_posts_df(self) -> pd.DataFrame:
        """Get posts data as DataFrame"""
        session = self.get_session()
        try:
            result = session.query(Post).all()
            data = []
            for row in result:
                data.append({
                    'influencer_id': row.influencer_id,
                    'platform': row.platform,
                    'date': row.date,
                    'URL': row.url,
                    'caption': row.caption,
                    'reach': row.reach,
                    'likes': row.likes,
                    'comments': row.comments
                })
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def get_tracking_data_df(self) -> pd.DataFrame:
        """Get tracking data as DataFrame"""
        session = self.get_session()
        try:
            result = session.query(TrackingData).all()
            data = []
            for row in result:
                data.append({
                    'source': row.source,
                    'campaign': row.campaign,
                    'influencer_id': row.influencer_id,
                    'user_id': row.user_id,
                    'product': row.product,
                    'date': row.date,
                    'orders': row.orders,
                    'revenue': row.revenue
                })
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def get_payouts_df(self) -> pd.DataFrame:
        """Get payouts data as DataFrame"""
        session = self.get_session()
        try:
            result = session.query(Payout).all()
            data = []
            for row in result:
                data.append({
                    'influencer_id': row.influencer_id,
                    'basis': row.basis,
                    'rate': row.rate,
                    'orders': row.orders,
                    'total_payout': row.total_payout
                })
            return pd.DataFrame(data)
        finally:
            session.close()
    
    def get_data_summary(self) -> dict:
        """Get summary statistics from database"""
        session = self.get_session()
        try:
            summary = {
                'influencers_count': session.query(Influencer).count(),
                'posts_count': session.query(Post).count(),
                'tracking_count': session.query(TrackingData).count(),
                'payouts_count': session.query(Payout).count(),
            }
            
            # Get total revenue if tracking data exists
            if summary['tracking_count'] > 0:
                total_revenue = session.query(TrackingData).with_entities(
                    session.query(TrackingData.revenue).subquery().c.revenue
                ).all()
                summary['total_revenue'] = sum([r[0] for r in total_revenue]) if total_revenue else 0
            else:
                summary['total_revenue'] = 0
                
            return summary
        finally:
            session.close()
    
    def clear_all_data(self):
        """Clear all data from database"""
        session = self.get_session()
        try:
            session.query(Payout).delete()
            session.query(TrackingData).delete()
            session.query(Post).delete()
            session.query(Influencer).delete()
            session.commit()
            logger.info("All data cleared from database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing data: {e}")
            raise
        finally:
            session.close()

# Initialize database manager
db_manager = DatabaseManager()