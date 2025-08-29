import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailNotifier:
    def __init__(self):
        """Initialize email notifier with environment variables"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SMTP_EMAIL', '')
        self.sender_password = os.getenv('SMTP_PASSWORD', '')
        
    def send_notification(self, recipient_email, subject, body):
        """
        Send email notification
        Returns dict with success status and error message if any
        """
        try:
            # Validate configuration
            if not self.sender_email or not self.sender_password:
                return {
                    'success': False,
                    'error': 'Email credentials not configured. Set SMTP_EMAIL and SMTP_PASSWORD environment variables.'
                }
            
            if not recipient_email:
                return {
                    'success': False,
                    'error': 'Recipient email not provided.'
                }
            
            # Create message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Add body to email
            message.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.sender_email, self.sender_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            return {
                'success': True,
                'error': None
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': 'Authentication failed. Check email credentials and enable "Less secure app access" or use app-specific password.'
            }
        except smtplib.SMTPRecipientsRefused:
            return {
                'success': False,
                'error': 'Recipient email address was refused by the server.'
            }
        except smtplib.SMTPServerDisconnected:
            return {
                'success': False,
                'error': 'SMTP server disconnected unexpectedly.'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'error': f'SMTP error occurred: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def test_connection(self):
        """
        Test SMTP connection and authentication
        Returns dict with success status and message
        """
        try:
            if not self.sender_email or not self.sender_password:
                return {
                    'success': False,
                    'message': 'Email credentials not configured.'
                }
            
            # Test connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email configuration is working correctly.'
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Authentication failed. Check credentials.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }
