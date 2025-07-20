from src.lib.logger import logger
from src.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr


class EmailService:
    def __init__(self):
        self.support_email = "support@modaic.dev"
        self.personal_email = "farouk@modaic.dev"
        self.sender_email = "hey@modaic.dev"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(
        self, recipient_email: str, recipient_name: str, subject: str, body: str
    ):
        """
        Sends an email using the configured SMTP server. Defaults to the personal email of the sender.
        """

        msg = MIMEMultipart()
        msg["From"] = formataddr(("Modaic", self.sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = subject

        body = body.format(name=recipient_name.split()[0])
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, settings.gmail_app_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())

        logger.info(f"Email sent to {recipient_name} <{recipient_email}>")

    def send_email_html(self, recipient_email: str, subject: str, html_body: str):
        """
        Sends an HTML email using the configured SMTP server.
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr(("Modaic", self.sender_email))
        msg["To"] = recipient_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, settings.gmail_app_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())

        logger.info(f"HTML email sent to <{recipient_email}>")

    def account_creation(self, recipient_email: str, recipient_name: str):
        """
        Sends an account creation email to the user.
        """

        subject = "Welcome to Modaic!"
        body = f"""\
Hey {recipient_name.split()[0]},

Thanks for signing up for Modaic! We're excited to have you on board.

If you have any questions or need assistance, feel free to reach out to us at {self.support_email}.

Best,
The Modaic Team"""

        self.send_email(recipient_email, recipient_name, subject, body)

    def user_upgraded_to_pro(self, recipient_email: str, recipient_name: str):
        """
        Sends an email to the user when they upgrade to Pro.
        """
        subject = "You've Upgraded to Modaic Pro!"
        body = f"""\
Hey {recipient_name.split()[0]},

Congratulations! Your account has been upgraded to Modaic Pro. Enjoy all the new features and enhanced capabilities.

If you have any questions, reach out to us at {self.support_email}.

Best,
The Modaic Team"""

        self.send_email(recipient_email, recipient_name, subject, body)

    def user_invited_to_repo(
        self,
        recipient_email: str,
        recipient_name: str,
        repo_name: str,
        repo_link: str,
        sender_name: str,
    ):
        """
        Sends an HTML email to the user when they are invited to a repo, including the invitation link.
        """
        subject = f"You've Been Invited to Join '{repo_name}' on Modaic!"
        html_body = f"""\
        <html>
          <body>
            <p>Hey {recipient_name.split()[0]},</p>
            <p>You've been invited to join the repository '<b>{repo_name}</b>' on Modaic by <b>{sender_name}</b>! Start syncing memories with ease.<br>
            Click the invitation link below to get started:</p>
            <p><a href="{repo_link}?src=invite">Accept the Invite.</a></p>
            <p>If you have any questions, let us know at {self.support_email}.</p>
            <p>Cheers,<br>The Modaic Team</p>
          </body>
        </html>
        """
        self.send_email_html(recipient_email, subject, html_body)

    def non_existing_user_invited_to_repo(
        self,
        recipient_email: str,
        repo_name: str,
        repo_link: str,
        sender_name: str,
    ):
        """
        Sends an HTML email to the user when they are invited to a repo, including the invitation link.
        """
        subject = f"You've Been Invited to Join '{repo_name}' on Modaic!"
        html_body = f"""\
        <html>
          <body>
            <p>Hey there,</p>
            <p>You've been invited to join the repo '<b>{repo_name}</b>' on Modaic by <b>{sender_name}</b>! Start syncing memories with ease.<br>
            Click the invitation link below to get started:</p>
            <p>Create an account <a href="{settings.next_url}/auth">here</a></p>
            <p>Accept the invite <a href="{repo_link}?src=newuserinvite">here</a></p>
            <p>If you have any questions, let us know at {self.support_email}.</p>
            <p>Cheers,<br>The Modaic Team</p>
          </body>
        </html>
        """
        self.send_email_html(recipient_email, subject, html_body)

    def onboarding_message(self, recipient_email: str, recipient_name: str):
        """
        Sends a personalized onboarding message.
        """
        subject = "Welcome to Modaic!"
        body = f"""\
Welcome to Modaic, {recipient_name.split()[0]}!

We're excited to have you on board. Let us know if you need any help getting started.

Best,
The Modaic Team"""

        self.send_email(recipient_email, recipient_name, subject, body)

    def weekly_update(self, recipient_email: str, recipient_name: str):
        """
        Sends a weekly update email with bug fixes and improvements.
        """
        subject = "Modaic Weekly Update"
        body = f"""\
Hey {recipient_name.split()[0]},

Here’s what’s new this week:
- Bug fixes
- Performance improvements
- New features coming soon!

Thank you for being part of Modaic.

Cheers,
The Modaic Team"""

        self.send_email(recipient_email, recipient_name, subject, body)


email_service = EmailService()
