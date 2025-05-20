import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_noreply_email(email: str, subject: str, body: str, config: Config) -> bool:
    """
    Send an email from the no-reply account to the specified recipient.
    
    Args:
        email (str): Recipient email address
        subject (str): Email subject line
        body (str): Email body content (can be HTML)
        config (Config): Application configuration object containing email settings
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    
    Raises:
        ValueError: If required email configuration is missing
    """
    # Get email configuration from config
    sender_email = config.email_noreply_address
    sender_password = config.email_noreply_password
    smtp_server = config.email_smtp_server
    smtp_port = config.email_smtp_port
    
    # Validate configuration
    if not all([sender_email, sender_password, smtp_server, smtp_port]):
        error_msg = "Missing email configuration. Check your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    
    # Attach body
    message.attach(MIMEText(body, "html"))
    
    try:
        # Connect to server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        
        # Login
        server.login(sender_email, sender_password)
        
        # Send email
        server.sendmail(sender_email, email, message.as_string())
        
        # Close connection
        server.quit()
        
        logger.info(f"Email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
