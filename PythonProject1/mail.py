import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError

def send_email(to_email, admin_name, request_details, subject, body):
    from_email = 'Ruturajnavale1406@gmail.com'  # Replace with your email
    password = 'dgfy rkwj efij xcbb'  # Replace with your app password

    # Validate recipient's email address
    try:
        validate_email(to_email)
    except EmailNotValidError as e:
        print(f"Invalid email address: {e}")
        return

    # Check request details for missing keys and provide safe defaults
    name = request_details.get('name', 'User')
    email = request_details.get('email', 'N/A')
    description = request_details.get('description', 'N/A')

    # Build the HTML content based on the subject
    if "approved" in subject.lower():
        html_content = f"""
        <html>
            <body>
                <h3>Hello {name},</h3>
                <p>We are pleased to inform you that your request has been approved.</p>
                <p>Details of the approved request are as follows:</p>
                <table border="1" cellpadding="5">
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>{name}</td>
                        <td>{email}</td>
                        <td>{description}</td>
                    </tr>
                </table>
                <p><strong>Approved by:</strong> {admin_name}</p>
                <p>We will process your request and notify you once the items are ready for pickup.</p>
            </body>
        </html>
        """
    elif "rejected" in subject.lower():
        html_content = f"""
        <html>
            <body>
                <h3>Hello {name},</h3>
                <p>We regret to inform you that your request has been rejected.</p>
                <p>Details of the rejected request are as follows:</p>
                <table border="1" cellpadding="5">
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>{name}</td>
                        <td>{email}</td>
                        <td>{description}</td>
                    </tr>
                </table>
                <p><strong>Rejected by:</strong> {admin_name}</p>
                <p>If you have any questions or need further clarification, please feel free to reach out to the support team.</p>
            </body>
        </html>
        """
    else:
        html_content = f"""
        <html>
            <body>
                <h3>Hello {name},</h3>
                <p>{body}</p>
                <p>Details of your request:</p>
                <table border="1" cellpadding="5">
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>{name}</td>
                        <td>{email}</td>
                        <td>{description}</td>
                    </tr>
                </table>
                <p><strong>Processed by:</strong> {admin_name}</p>
                <p>You will be notified once the request has been approved or rejected.</p>
            </body>
        </html>
        """

    # Prepare the email
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html'))

    # Send the email using SMTP
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email successfully sent to {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")
