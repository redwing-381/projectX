"""Gmail API integration service."""

import base64
import json
import logging
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models.schemas import Email

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ):
        """Initialize Gmail service with OAuth credentials.

        Args:
            credentials_path: Path to OAuth client credentials JSON file.
            token_path: Path to store/load user token.
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self._service = None
        self._creds = None

    def _authenticate(self) -> Credentials:
        """Authenticate with Gmail API using OAuth 2.0."""
        creds = None

        # First, try to load token from environment variable (for Railway deployment)
        token_json = os.environ.get("GMAIL_TOKEN_JSON")
        if token_json:
            logger.info("Loading Gmail token from environment variable")
            try:
                token_data = json.loads(token_json)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            except Exception as e:
                logger.error(f"Failed to load token from env: {e}")

        # Fall back to token file
        if not creds and self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
                # Update env var if we refreshed (for Railway)
                if token_json:
                    logger.info("Token refreshed - update GMAIL_TOKEN_JSON env var")
            else:
                # Only try OAuth flow if not in production (Railway)
                if os.environ.get("RAILWAY_ENVIRONMENT"):
                    raise RuntimeError(
                        "Gmail token expired or missing. "
                        "Re-authenticate locally and update GMAIL_TOKEN_JSON env var."
                    )
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}. "
                        "Download it from Google Cloud Console."
                    )
                logger.info("Starting OAuth flow for new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run (local only)
            if not os.environ.get("RAILWAY_ENVIRONMENT"):
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())
                    logger.info(f"Saved credentials to {self.token_path}")

        return creds

    def _get_service(self):
        """Get or create Gmail API service."""
        if self._service is None:
            self._creds = self._authenticate()
            self._service = build("gmail", "v1", credentials=self._creds)
        return self._service

    async def get_unread_emails(self, max_results: int = 10) -> list[Email]:
        """Fetch unread emails from inbox.

        Args:
            max_results: Maximum number of emails to fetch.

        Returns:
            List of Email objects.
        """
        try:
            service = self._get_service()

            # Search for unread emails in inbox
            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q="is:unread in:inbox",
                    maxResults=max_results,
                )
                .execute()
            )

            messages = results.get("messages", [])
            if not messages:
                logger.info("No unread emails found")
                return []

            emails = []
            for msg in messages:
                full_msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )
                email = self.extract_email_data(full_msg)
                emails.append(email)

            logger.info(f"Fetched {len(emails)} unread emails")
            return emails

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise

    def extract_email_data(self, raw_message: dict) -> Email:
        """Extract sender, subject, and snippet from raw Gmail message.

        Args:
            raw_message: Raw message from Gmail API.

        Returns:
            Email object with extracted data.
        """
        msg_id = raw_message.get("id", "")
        snippet = raw_message.get("snippet", "")

        # Extract headers
        headers = raw_message.get("payload", {}).get("headers", [])
        sender = ""
        subject = ""

        for header in headers:
            name = header.get("name", "").lower()
            if name == "from":
                sender = header.get("value", "")
            elif name == "subject":
                subject = header.get("value", "")

        return Email(
            id=msg_id,
            sender=sender or "Unknown",
            subject=subject or "(No Subject)",
            snippet=snippet or "",
        )
