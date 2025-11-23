from .base_email import base_email_template

def generate_otp_email(user_name: str, otp: str) -> str:
    content = f"""
        <p>Hello <strong>{user_name}</strong>,</p>
        <p>Your one-time password (OTP) is:</p>
        <p style='text-align:center'>
            <span class="otp" onclick="copyOTP('{otp}')">{otp}</span>
        </p>
        <p>This OTP will expire in 10 minutes. Do not share it with anyone.</p>
    """
    return base_email_template(content, title="Your OTP Code")

def generate_registration_email(user_name: str, dashboard_url: str) -> str:
    content = f"""
        <p>Hello <strong>{user_name}</strong>,</p>
        <p>🎉 Your registration on <strong>Fentech</strong> was successful!</p>
        <p>Click the button below to log into your dashboard.</p>
        <p style="text-align:center;">
            <a href="{dashboard_url}" class="button">Go to Dashboard</a>
        </p>
    """
    return base_email_template(content, title="Welcome to Fentech!")
def generate_login_email(user_name: str, dashboard_url: str) -> str:
    content = f"""
        <p>Dear <strong>{user_name}</strong>,</p>
        <p>🎉 Your login request <strong>Fentech</strong> is successful!</p>
        <p>if you dont initiate it  contact support!</p>
        <p style="text-align:center;">
            <a href="{dashboard_url}" class="button">Go to Dashboard</a>
        </p>
    """
    return base_email_template(content, title="Welcome to Fentech!")