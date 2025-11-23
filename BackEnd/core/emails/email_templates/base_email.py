# base email folder 

def base_email_template(content: str, title: str = "Fentech Notification") -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: #fff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                color: #999;
                font-size: 14px;
            }}
            .button {{
                display: inline-block;
                background-color: #007bff;
                color: #fff;
                padding: 12px 20px;
                border-radius: 5px;
                text-decoration: none;
                margin-top: 20px;
            }}
            .otp {{
                font-size: 28px;
                font-weight: bold;
                letter-spacing: 6px;
                background: blue;
                padding: 10px 20px;
                display: inline-block;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 20px;
            }}
            .popup {{
                visibility: hidden;
                background-color: #4BB543;
                color: white;
                text-align: center;
                border-radius: 5px;
                padding: 10px;
                position: fixed;
                z-index: 1;
                right: 20px;
                top: 20px;
                min-width: 200px;
                font-weight: bold;
            }}
            .popup.show {{
                visibility: visible;
                animation: fadein 0.5s, fadeout 0.5s 2.5s;
            }}
            @keyframes fadein {{
                from {{ top: 0; opacity: 0; }}
                to {{ top: 20px; opacity: 1; }}
            }}
            @keyframes fadeout {{
                from {{ top: 20px; opacity: 1; }}
                to {{ top: 0; opacity: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{title}</h2>
            </div>
            {content}
            <div class="footer">
                &copy; 2025 Fentech. All rights reserved.
            </div>
        </div>
        <div id="popup" class="popup">OTP Copied!</div>
        <script>
            function copyOTP(otpText) {{
                navigator.clipboard.writeText(otpText).then(() => {{
                    const popup = document.getElementById("popup");
                    popup.classList.add("show");
                    setTimeout(() => popup.classList.remove("show"), 3000);
                }});
            }}
        </script>
    </body>
    </html>
    """