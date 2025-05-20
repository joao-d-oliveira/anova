import os
import boto3

from app.config import Config


def send_noreply_email(email: str, subject: str, body: str, config: Config):
    # key = config.noreply_access_key_id
    # secret = config.noreply_secret_access_key
    # ses_client = boto3.client(
    #     "ses",
    #     region_name="us-east-1",
    #     aws_access_key_id=key,
    #     aws_secret_access_key=secret,
    # )

    # ses_client.send_email(
    #     Source="no-reply@anovasports.com",
    #     Destination={"ToAddresses": [email]},
    #     Message={"Subject": {"Data": subject, 'Charset': 'UTF-8'}, "Body": {"Html": {"Data": body, 'Charset': 'UTF-8'}}},
    # )
    print(f"""Would've sent following email
        To: {email}
        Subject: {subject}
        Body: {body}
    """)


def send_verify_email(email: str, unique_token: str, config: Config):
    """
    Send an email to a single email with a unique token
    """
    send_noreply_email(
        email,
        "Verify your email",
        f"""
        <p>Welcome to Anova,</p>
        <p>This is your unique temporary code to verify your email: {unique_token}</p>
        <p>If you did not request this email, please ignore it</p>
        <p>Best regards,</p>
        <p>The Anova Team</p>
        """,
        config,
    )


def send_reset_password_email(email: str, unique_token: str, config: Config):
    """
    Send an email to a single email with a unique token
    """
    send_noreply_email(
        email,
        "Reset your password",
        f"""
        <p>Hi,</p>
        <p>We received a request to reset your password. This is your unique temporary code: {unique_token}</p>
        <p>If you did not request this email, please ignore it</p>
        <p>Best regards,</p>
        <p>The Anova Team</p>
        """,
        config,
    )
