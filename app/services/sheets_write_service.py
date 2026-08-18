"""Service for writing data to Google Sheets via the Google Sheets API v4."""

import json
from typing import Any

import httpx

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


async def _get_access_token() -> str | None:
    """
    Obtain an OAuth2 access token from a Google Service Account JWT.

    The service account credentials are loaded from:
      - env var GOOGLE_SERVICE_ACCOUNT_JSON  (full JSON string)
    """
    cred_json = settings.google_service_account_json
    if not cred_json:
        logger.warning("GOOGLE_SERVICE_ACCOUNT_JSON not set — cannot write to Sheets")
        return None

    try:
        creds = json.loads(cred_json)
    except json.JSONDecodeError:
        logger.error("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON")
        return None

    import base64
    import time
    import uuid

    # Build JWT
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iss": creds["client_email"],
        "scope": "https://www.googleapis.com/auth/spreadsheets",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }

    def _b64(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()

    signing_input = f"{_b64(header)}.{_b64(payload)}"
    private_key = creds["private_key"]
    if "-----BEGIN" not in private_key:
        # If stored as escaped string, fix newlines
        private_key = private_key.replace("\\n", "\n")

    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes, serialization
    key = serialization.load_pem_private_key(private_key.encode(), password=None)
    signature = key.sign(signing_input.encode(), padding.PKCS1v15(), hashes.SHA256())
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    jwt_str = f"{signing_input}.{sig_b64}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": jwt_str,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
    except (httpx.HTTPError, KeyError, ValueError) as error:
        logger.error(f"Failed to authenticate Google service account: {error}")
        return None


async def append_row(
    spreadsheet_id: str,
    sheet_name: str,
    row: list[str],
) -> bool:
    """
    Append a single row to the first empty row of a sheet.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        sheet_name: Tab/sheet name to write to
        row: List of cell values (strings)
    Returns:
        True if successful, False otherwise.
    """
    token = await _get_access_token()
    if not token:
        return False

    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
        f"/values/{sheet_name}!A:Z:append"
        f"?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    )
    body = {"values": [row]}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=body,
                headers={"Authorization": f"Bearer {token}"},
                timeout=15.0,
            )
            resp.raise_for_status()
            logger.info(f"Appended row to {sheet_name}", extra={"spreadsheet_id": spreadsheet_id})
            return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to write to sheet {sheet_name}: {e}")
        return False
