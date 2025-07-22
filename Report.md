# HealthKart Influencer Campaign Dashboard

## Overview

This is a Streamlit-based dashboard application for tracking and analyzing influencer campaign performance for HealthKart. The application provides comprehensive analytics for ROI, ROAS, and campaign metrics across multiple social media platforms including Instagram, YouTube, Twitter, Facebook, TikTok, and LinkedIn.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with expandable sidebar navigation
- **Visualization**: Plotly for interactive charts and graphs
- **Navigation**: Multi-page structure with sidebar menu for Dashboard, Data Upload, Insights, Payouts, and Export Data

### Backend Architecture
- **Data Processing**: Pandas for data manipulation and analysis
- **Analytics Engine**: Custom AnalyticsEngine class for ROI/ROAS calculations
- **Data Management**: DataManager class handling all data operations
- **Session State**: Streamlit session state for maintaining data across page interactions

### Data Storage Solutions
- **PostgreSQL Database**: Persistent data storage using PostgreSQL with SQLAlchemy ORM
- **Database Models**: Four main tables (influencers, posts, tracking_data, payouts) with proper relationships
- **Session Integration**: Data automatically loaded from database on session start
- **CSV Import/Export**: File-based data persistence through CSV uploads and exports with database sync

## Key Components

### 1. DataManager (data_models.py)
- Manages four core datasets: influencers, posts, tracking_data, payouts
- Integrates with PostgreSQL database for persistent storage
- Provides data validation for uploaded CSV files
- Handles schema validation and data type checking
- Supports platform validation (Instagram, YouTube, Twitter, Facebook, TikTok, LinkedIn)
- Automatic database synchronization on data upload

### 2. AnalyticsEngine (analytics.py)
- Calculates ROI and ROAS metrics with benchmarks (200% ROI, 4:1 ROAS)
- Applies filtering across multiple dimensions (platform, brand, category, date range)
- Provides advanced analytics for campaign performance
- Cross-references data between influencers, posts, and tracking data

### 3. Utility Functions (utils.py)
- CSV export functionality with comprehensive reporting
- PDF export using ReportLab for formatted reports
- Data aggregation and summary statistics
- Report generation with timestamps

### 4. Main Application (app.py)
- Streamlit configuration and page setup
- Session state management with database integration
- Navigation between different dashboard sections including Database Management
- Real-time data status display in sidebar
- Database operations interface for data management

### 5. Database Layer (database.py)
- SQLAlchemy ORM models for all data entities
- PostgreSQL connection management
- Bulk data operations for CSV uploads
- Database status monitoring and management tools
- Data integrity and transaction handling

## Data Flow

1. **Data Upload**: Users upload CSV files for influencers, posts, tracking data, and payouts
2. **Validation**: DataManager validates uploaded data against required schemas
3. **Database Storage**: Validated data automatically saved to PostgreSQL database
4. **Session Sync**: Data loaded from database into session state as Pandas DataFrames
5. **Analytics**: AnalyticsEngine processes data with filters and calculations
6. **Visualization**: Plotly generates interactive charts and metrics
7. **Export**: Users can export processed data as CSV or PDF reports
8. **Persistence**: All data persists across sessions via database storage

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualization library

### Database Libraries
- **sqlalchemy**: ORM and database toolkit
- **psycopg2-binary**: PostgreSQL adapter for Python

### Export Functionality
- **reportlab**: PDF generation and formatting
- **io**: String and byte stream handling
- **base64**: Data encoding for downloads

### Utility Libraries
- **datetime**: Date and time handling
- **uuid**: Unique identifier generation
- **os**: Operating system interface

## Deployment Strategy

### Current Setup
- **Platform**: Designed for Replit deployment
- **Dependencies**: All requirements managed through Python package imports
- **Configuration**: Streamlit configuration set for wide layout and custom page settings
- **File Structure**: Modular design with separate files for different functionalities

### Scalability Considerations
- **Database-Backed**: Now uses PostgreSQL for persistent data storage
- **Session Management**: Data automatically synced between database and session state
- **File Upload**: Limited by Streamlit's file upload constraints
- **Single-User**: Open access dashboard without user authentication

### Current Enhancements
- **PostgreSQL Integration**: Implemented with SQLAlchemy ORM
- **Persistent Storage**: All data survives session restarts
- **Database Management**: Admin interface for data operations
- **Sample Data Loading**: Built-in test data functionality

### Future Enhancements
- **Authentication**: User management and role-based access
- **API Integration**: Direct connections to social media platforms
- **Scheduled Updates**: Automated data refresh capabilities
- **Multi-tenant**: Support for multiple HealthKart campaigns or clients