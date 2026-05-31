import boto3
import os


def send_reset_email(to_email: str, reset_link: str):
    client = boto3.client(
        "ses",
        region_name=os.getenv("AWS_REGION", "us-east-2"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    client.send_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "Reset your password"},
            "Body": {
                "Text": {
                    "Data": (
                        "Click the link below to reset your password "
                        f"(expires in 30 minutes):\n\n{reset_link}"
                    )
                },
                "Html": {
                    "Data": f"""
                    <p>Click the link below to reset your password.
                    This link expires in <strong>30 minutes</strong>.</p>
                    <p><a href="{reset_link}">Reset Password</a></p>
                    <p>If you did not request this, you can ignore this email.</p>
                    """
                },
            },
        },
    )
