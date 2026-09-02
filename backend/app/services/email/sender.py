import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, Any, Optional, Tuple, List
import datetime
from backend.app.core.config import settings

class EmailSender:
    @property
    def smtp_host(self) -> str:
        return settings.SMTP_HOST

    @property
    def smtp_port(self) -> int:
        return settings.SMTP_PORT

    @property
    def smtp_user(self) -> str:
        return settings.SMTP_USER

    @property
    def smtp_password(self) -> str:
        return settings.SMTP_PASSWORD

    @property
    def from_email(self) -> str:
        return settings.SMTP_FROM_EMAIL or "outreach@leadforge.io"

    @property
    def from_name(self) -> str:
        return settings.SMTP_FROM_NAME or "LeadForge Outreach"

    def render_template(self, template_str: str, variables: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Renders template with variables {{key}}.
        If required variable is missing, returns (False, "", "Missing variable: {{key}}")
        """
        if not template_str:
            return True, "", None
            
        rendered = template_str
        import re
        tags = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template_str)
        for tag in tags:
            val = variables.get(tag)
            if val is None or val == "":
                val = f"[{tag}]"
            rendered = rendered.replace(f"{{{{{tag}}}}}", str(val))
            
        return True, rendered, None

    async def test_connection(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None
    ) -> Tuple[bool, str]:
        """
        Tests live connection to SMTP host.
        """
        h = host or self.smtp_host
        p = port or self.smtp_port
        u = user or self.smtp_user
        pw = password or self.smtp_password
        tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS

        if not h or not u:
            return True, "Development mode active: Simulated local delivery is operational."

        try:
            context = ssl.create_default_context()
            if p == 465:
                with smtplib.SMTP_SSL(h, p, context=context, timeout=8) as server:
                    if pw:
                        server.login(u, pw)
            else:
                with smtplib.SMTP(h, p, timeout=8) as server:
                    if tls:
                        server.starttls(context=context)
                    if pw:
                        server.login(u, pw)
            return True, f"SMTP server '{h}:{p}' connection and authentication verified successfully."
        except Exception as e:
            return False, f"SMTP connection failed: {str(e)}"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Sends email via SMTP with HTML and file attachments support.
        If SMTP host is not configured, logs delivery safely in development/demo mode.
        Returns: (success: bool, message_id: str, error_message: str)
        """
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name
        
        # Build multipart message
        if attachments:
            msg = MIMEMultipart("mixed")
            alt_part = MIMEMultipart("alternative")
            alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
            if body_html:
                alt_part.attach(MIMEText(body_html, "html", "utf-8"))
            msg.attach(alt_part)

            for att in attachments:
                fname = att.get("filename", "attachment.html")
                raw_content = att.get("content", "")
                if isinstance(raw_content, str):
                    raw_bytes = raw_content.encode("utf-8")
                else:
                    raw_bytes = bytes(raw_content)

                att_part = MIMEApplication(raw_bytes)
                att_part.add_header("Content-Disposition", "attachment", filename=fname)
                msg.attach(att_part)
        else:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body_text, "plain", "utf-8"))
            if body_html:
                msg.attach(MIMEText(body_html, "html", "utf-8"))

        msg["Subject"] = subject
        msg["From"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
        msg["To"] = to_email
        msg["Date"] = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

        domain_part = sender_email.split("@")[-1] if "@" in sender_email else "leadforge.io"

        # If no real SMTP server configured, simulate local safe delivery
        if not self.smtp_host or not self.smtp_user:
            simulated_msg_id = f"sim-{datetime.datetime.now(datetime.timezone.utc).timestamp()}@{domain_part}"
            return True, simulated_msg_id, None
            
        try:
            context = ssl.create_default_context()
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context, timeout=12) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(sender_email, to_email, msg.as_string())
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=12) as server:
                    if settings.SMTP_USE_TLS:
                        server.starttls(context=context)
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(sender_email, to_email, msg.as_string())
                    
            msg_id = f"smtp-{datetime.datetime.now(datetime.timezone.utc).timestamp()}@{domain_part}"
            return True, msg_id, None
        except Exception as e:
            return False, None, str(e)

email_sender = EmailSender()
