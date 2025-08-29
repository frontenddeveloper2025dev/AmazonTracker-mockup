import streamlit as st
import threading
import time
import os
from datetime import datetime
from amazon_tracker import AmazonTracker
from email_notifier import EmailNotifier

# Configure page
st.set_page_config(
    page_title="Amazon Product Tracker",
    page_icon="📦",
    layout="centered"
)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = None
if 'tracking_thread' not in st.session_state:
    st.session_state.tracking_thread = None
if 'is_tracking' not in st.session_state:
    st.session_state.is_tracking = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'product_info' not in st.session_state:
    st.session_state.product_info = {}

def add_log(message):
    """Add a timestamped log entry"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    # Keep only last 50 logs
    if len(st.session_state.logs) > 50:
        st.session_state.logs = st.session_state.logs[-50:]

def tracking_worker(asin, email_recipient, check_interval):
    """Background worker function for tracking"""
    tracker = AmazonTracker()
    notifier = EmailNotifier()
    
    previous_availability = None
    
    while st.session_state.is_tracking:
        try:
            add_log(f"Checking availability for ASIN: {asin}")
            
            # Get product information
            product_info = tracker.get_product_info(asin)
            
            if product_info['error']:
                add_log(f"Error: {product_info['error']}")
                time.sleep(check_interval)
                continue
            
            # Update session state with product info
            st.session_state.product_info = product_info
            
            current_availability = product_info['availability']
            
            add_log(f"Product: {product_info['title']}")
            add_log(f"Price: {product_info['price']}")
            add_log(f"Availability: {current_availability}")
            
            # Check if availability changed
            if previous_availability is not None and previous_availability != current_availability:
                add_log("Availability changed! Sending notification...")
                
                # Send email notification
                subject = f"Amazon Product Availability Changed - {product_info['title']}"
                body = f"""
Product: {product_info['title']}
ASIN: {asin}
Price: {product_info['price']}
Previous Status: {previous_availability}
Current Status: {current_availability}
URL: https://www.amazon.com/dp/{asin}

Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
                
                email_result = notifier.send_notification(email_recipient, subject, body)
                if email_result['success']:
                    add_log("Email notification sent successfully!")
                else:
                    add_log(f"Failed to send email: {email_result['error']}")
            
            previous_availability = current_availability
            
        except Exception as e:
            add_log(f"Tracking error: {str(e)}")
        
        # Wait before next check
        time.sleep(check_interval)

# Main UI
st.title("📦 Amazon Product Tracker")
st.markdown("Track Amazon product availability and get notified when stock status changes.")

# Input section
with st.container():
    st.subheader("Product Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        asin = st.text_input(
            "Amazon ASIN ID",
            placeholder="e.g., B077PWK5BT",
            help="Enter the ASIN ID from the Amazon product URL"
        )
    
    with col2:
        check_interval = st.selectbox(
            "Check Interval",
            options=[60, 300, 900, 1800, 3600],
            format_func=lambda x: f"{x//60} minutes" if x < 3600 else f"{x//3600} hour(s)",
            index=1,
            help="How often to check for availability"
        )

# Email configuration
with st.expander("Email Notification Settings", expanded=not st.session_state.is_tracking):
    email_recipient = st.text_input(
        "Recipient Email",
        placeholder="your-email@example.com",
        help="Email address to receive notifications"
    )
    
    st.info("📧 Email settings are configured via environment variables (SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT)")

# Control buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🚀 Start Tracking", disabled=st.session_state.is_tracking or not asin or not email_recipient):
        if asin and email_recipient:
            st.session_state.is_tracking = True
            st.session_state.logs = []
            st.session_state.product_info = {}
            
            # Start tracking thread
            st.session_state.tracking_thread = threading.Thread(
                target=tracking_worker,
                args=(asin, email_recipient, check_interval),
                daemon=True
            )
            st.session_state.tracking_thread.start()
            
            add_log("Tracking started!")
            st.rerun()

with col2:
    if st.button("⏹️ Stop Tracking", disabled=not st.session_state.is_tracking):
        st.session_state.is_tracking = False
        add_log("Tracking stopped!")
        st.rerun()

with col3:
    if st.button("🗑️ Clear Logs"):
        st.session_state.logs = []
        st.session_state.product_info = {}
        st.rerun()

# Status indicator
if st.session_state.is_tracking:
    st.success("🔄 Currently tracking...")
else:
    st.info("⏸️ Tracking stopped")

# Product information display
if st.session_state.product_info and not st.session_state.product_info.get('error'):
    st.subheader("📋 Current Product Information")
    
    info = st.session_state.product_info
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Title:** {info.get('title', 'N/A')}")
        st.write(f"**ASIN:** {info.get('asin', 'N/A')}")
        st.write(f"**Availability:** {info.get('availability', 'N/A')}")
    
    with col2:
        st.write(f"**Price:** {info.get('price', 'N/A')}")
        if info.get('asin'):
            st.markdown(f"[View on Amazon](https://www.amazon.com/dp/{info['asin']})")

# Logs section
st.subheader("📜 Tracking Logs")

if st.session_state.logs:
    # Display logs in reverse order (newest first)
    log_container = st.container()
    with log_container:
        for log in reversed(st.session_state.logs[-20:]):  # Show last 20 logs
            st.text(log)
else:
    st.info("No logs yet. Start tracking to see activity.")

# Auto-refresh when tracking
if st.session_state.is_tracking:
    time.sleep(2)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("💡 **Tips:**")
st.markdown("- Find ASIN in Amazon product URL: amazon.com/dp/ASIN")
st.markdown("- Configure email settings via environment variables")
st.markdown("- Logs are automatically cleared after 50 entries")
