# Amazon Product Tracker

## Overview

A web-based Amazon product availability tracker that monitors specific products by ASIN and sends email notifications when availability changes. The application uses web scraping to check product status and provides a Streamlit-based user interface for configuration and monitoring.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Application**: Single-page web interface built with Streamlit for user interaction
- **Session State Management**: Uses Streamlit's session state to maintain application state across user interactions
- **Real-time Logging**: Live log display showing tracking activity and status updates

### Backend Architecture
- **Modular Design**: Three main components separated into dedicated modules:
  - `AmazonTracker`: Handles web scraping and product data extraction
  - `EmailNotifier`: Manages SMTP email notifications
  - `app.py`: Main application orchestrating the user interface and background tracking

### Data Extraction Strategy
- **Web Scraping Approach**: Uses BeautifulSoup and requests to parse Amazon product pages
- **Anti-Detection Measures**: Implements browser-like headers, random delays, and session management to avoid blocking
- **ASIN-based Tracking**: Leverages Amazon's unique product identifiers for reliable product monitoring

### Background Processing
- **Threading Architecture**: Uses Python threading to run tracking operations in the background while maintaining responsive UI
- **Periodic Monitoring**: Configurable check intervals for continuous product availability monitoring
- **State Synchronization**: Thread-safe communication between background workers and UI using session state

### Notification System
- **SMTP Integration**: Email notifications sent via configurable SMTP servers (default: Gmail)
- **Environment-based Configuration**: Email credentials managed through environment variables for security
- **Change Detection**: Triggers notifications only when product availability status changes

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **BeautifulSoup4**: HTML parsing for web scraping Amazon product pages
- **Requests**: HTTP client for making web requests to Amazon

### Email Infrastructure
- **SMTP Protocol**: Uses standard SMTP for email delivery
- **Gmail SMTP**: Default configuration for Gmail SMTP servers
- **Environment Variables**: Requires `SMTP_EMAIL`, `SMTP_PASSWORD`, `SMTP_SERVER`, and `SMTP_PORT` configuration

### Target Platform
- **Amazon.com**: Primary target for product tracking and data extraction
- **ASIN System**: Relies on Amazon's Standard Identification Number system for product identification

### Runtime Dependencies
- **Python Threading**: Built-in threading module for background task execution
- **Environment Management**: Uses `os.getenv()` for configuration management
- **Time Management**: Built-in `time` and `datetime` modules for scheduling and logging