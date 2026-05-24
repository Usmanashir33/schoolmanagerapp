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

def generate_registration_email(email:str ,name: str, ) -> str:
    content = f"""
        <p>Hello <strong>{name}</strong>,</p>
        <p>🎉 Your registration on <strong>EduPortal</strong> was successfull!</p>
        <p>Kindly note: </p>
        <p style="text-align:center;">
            you can access your dashbord using your Director email {email[:5]}****{email[-8:-1]} and password you provided during registration 
        </p>
    """
    return base_email_template(content, title="Welcome to eduportal services !")
def generate_staff_role_assignment_email(
    name: str,
    role_name: str,
    school_name: str,
    assigned_by: str,
) -> str:

    content = f"""
        <div style="padding:10px 0;">
            
            <p style="font-size:16px;">
                Hello <strong>{name}</strong>,
            </p>

            <p style="font-size:15px; line-height:1.7;">
                🎉 We are pleased to inform you that you have been assigned a new role on 
                <strong>{school_name}</strong>.
            </p>

            <div style="
                background:#f4f7ff;
                border-left:5px solid #4f46e5;
                padding:18px;
                border-radius:8px;
                margin:25px 0;
            ">
                <p style="margin:0; font-size:15px;">
                    <strong>Assigned Role:</strong> {role_name}
                </p>

                <p style="margin-top:10px; font-size:15px;">
                    <strong>Assigned By:</strong> {assigned_by}
                </p>
            </div>

            <p style="font-size:15px; line-height:1.7;">
                Your access permissions and responsibilities within the platform have now been updated based on this role.
            </p>

            <p style="font-size:15px; line-height:1.7;">
                Kindly log in to your dashboard to view and manage your newly assigned privileges.
            </p>

            <div style="text-align:center; margin:35px 0;">
                <a href="#"
                    style="
                        background:#4f46e5;
                        color:white;
                        padding:14px 28px;
                        text-decoration:none;
                        border-radius:8px;
                        font-weight:bold;
                        display:inline-block;
                    "
                >
                    Access Dashboard
                </a>
            </div>

            <p style="font-size:14px; color:#666;">
                If you believe this assignment was made in error, please contact your school administrator.
            </p>

        </div>
    """

    return base_email_template(
        content,
        title="New Role Assignment Notification"
    )

def generate_login_email(user_name: str, dashboard_url: str) -> str:
    content = f"""
        <p>Dear <strong>{user_name}</strong>,</p>
        <p>🎉 Your login request <strong>EduPortal</strong> is successfull!</p>
        <p>if you dont initiate it  contact support!</p>
        <p style="text-align:center;">
            <a href="{dashboard_url} class="button">Go to Dashboard</a>
        </p>
    """
    return base_email_template(content, title="Welcome to Fentech!")

def generate_school_update_email(director_name: str, school_name: str) -> str:
    content = f"""
        <p>Dear <strong>{director_name}</strong>,</p>
        <p>🎉 Your School <strong>{school_name}</strong> is successfully updated!</p>
        <p>if you dont initiate it  contact support!</p>
        
    """
    return base_email_template(content, title="School Update Alert!")
def generate_teacher_update_email(director_name: str, school_name: str) -> str:
    content = f"""
        <p>Dear <strong>{director_name}</strong>,</p>
        <p>🎉 Your School <strong>{school_name}</strong> profile has been  successfully updated!</p>
        <p>if you dont initiate it  contact support!</p>
        
    """
    return base_email_template(content, title="School Update Alert!")

def generate_school_delete_email(director_name: str, school_name: str) -> str:
    content = f"""
        <p>Dear <strong>{director_name}</strong>,</p>
        <p>🎉 Your School <strong>{school_name}</strong> deleting request is being received!</p>
            <p style="text-align:center; color:red;">
                ⚠️ Your school data will be permanently <strong>deleted</strong> in the next 30 days.
                this includes all associated user accounts, records, and files.
                during this period, you can contact support to halt the deletion process.
                we will alert you when the deletion is completed,
                we recommend you to back up any important information before the deadline.
                This action cannot be undone after the deadline. ⚠️
            </p>
    """
    return base_email_template(content, title="School Alert!")