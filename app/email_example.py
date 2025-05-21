#!/usr/bin/env python3
"""
Example script demonstrating how to use the send_noreply_email function.
"""

from config import Config
from email_sender import send_noreply_email

def main():
    """
    Example of sending an email using the no-reply account.
    """
    # Initialize configuration
    config = Config()
    
    # Email details
    recipient_email = "recipient@example.com"  # Replace with actual recipient
    subject = "Test Email from Anova Sports"
    
    # HTML body
    body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #4a86e8; color: white; padding: 10px; text-align: center; }
            .content { padding: 20px; }
            .footer { font-size: 12px; text-align: center; color: #777; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Anova Sports</h1>
            </div>
            <div class="content">
                <h2>Hello from Anova Sports!</h2>
                <p>This is a test email sent from our application.</p>
                <p>You can customize this template with your own content.</p>
                <p>Thank you for using our service!</p>
            </div>
            <div class="footer">
                <p>© 2025 Anova Sports. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send the email
    success = send_noreply_email(recipient_email, subject, body, config)
    
    if success:
        print(f"Email successfully sent to {recipient_email}")
    else:
        print("Failed to send email. Check the logs for details.")

if __name__ == "__main__":
    main()
