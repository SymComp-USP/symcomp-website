from __future__ import annotations

import asyncio
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

from app.core.config import get_settings


class EmailService(ABC):
    @abstractmethod
    async def send_verification_email(
        self, email: str, name: str, token: str
    ) -> None: ...

    @abstractmethod
    async def send_password_reset_email(
        self, email: str, name: str, token: str
    ) -> None: ...


class SMTPEmailService(EmailService):
    async def send_verification_email(self, email: str, name: str, token: str) -> None:
        settings = get_settings()
        url = f"{str(settings.frontend_base_url).rstrip('/')}/semana/verify-email?token={token}"
        await self._send(
            email,
            "Verify your SymComp email",
            f"Hello {name},\n\nVerify your email: {url}\n\nThis link expires in 24 hours.",
        )

    async def send_password_reset_email(
        self, email: str, name: str, token: str
    ) -> None:
        settings = get_settings()
        url = f"{str(settings.frontend_base_url).rstrip('/')}/semana/reset-password?token={token}"
        await self._send(
            email,
            "Reset your SymComp password",
            f"Hello {name},\n\nReset your password: {url}\n\nThis link expires in 1 hour.",
        )

    async def _send(self, recipient: str, subject: str, body: str) -> None:
        settings = get_settings()
        if not settings.smtp_host or not settings.smtp_from:
            raise RuntimeError("SMTP_HOST and SMTP_FROM must be configured")

        message = EmailMessage()
        message["From"] = settings.smtp_from
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        await asyncio.to_thread(self._send_sync, message)

    @staticmethod
    def _send_sync(message: EmailMessage) -> None:
        settings = get_settings()
        password = (
            settings.smtp_password.get_secret_value()
            if settings.smtp_password is not None
            else None
        )
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, password or "")
            smtp.send_message(message)


def get_email_service() -> EmailService:
    return SMTPEmailService()
