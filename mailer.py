import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes
import os
from jinja2 import Environment, FileSystemLoader

class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.server = None
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader('templates'))

    def __enter__(self):
        self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.server.starttls()
        self.server.login(self.sender_email, self.sender_password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            self.server.quit()

    def create_message(self, recipient_email, subject, template_data, chart_image_path):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        
        # Render HTML body
        template = self.env.get_template('report_email.html')
        html_content = template.render(**template_data)
        
        # Set email content
        msg.set_content("Please enable HTML to view this email.")
        msg.add_alternative(html_content, subtype='html')
        
        # Embed the image
        with open(chart_image_path, 'rb') as img:
            image_data = img.read()
            maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
            
            # The Content-ID must match the 'cid:' reference in HTML
            msg.get_payload()[1].add_related(
                image_data, 
                maintype=maintype, 
                subtype=subtype, 
                cid="<chart_image>"
            )
            
        return msg

    def send_email(self, msg):
        try:
            if not self.server:
                raise Exception("SMTP server connection is not open. Use 'with' statement.")
            self.server.send_message(msg)
            print(f"Successfully sent email to {msg['To']}")
            return True
        except Exception as e:
            print(f"Failed to send email to {msg['To']}. Error: {e}")
            return False
