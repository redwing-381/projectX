"""API client for ProjectX server."""

from typing import Any, Dict, Optional

import httpx


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ConnectionError(Exception):
    """Exception raised for connection errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProjectXClient:
    """API client for ProjectX server."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """Initialize the client.

        Args:
            base_url: Server base URL.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP request to the server.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path.
            data: Optional form data for POST requests.

        Returns:
            Response JSON as dictionary.

        Raises:
            ConnectionError: If server is unreachable.
            APIError: If server returns an error response.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = client.get(url)
                elif method.upper() == "POST":
                    if data:
                        response = client.post(url, data=data)
                    else:
                        response = client.post(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                if response.status_code >= 400:
                    # Try to get error detail from response
                    try:
                        data = response.json()
                        detail = data.get("detail", response.text)
                    except Exception:
                        detail = response.text or f"HTTP {response.status_code}"

                    raise APIError(detail, response.status_code)

                return response.json()

        except httpx.ConnectError:
            raise ConnectionError("Server unreachable - check URL and network")
        except httpx.TimeoutException:
            raise ConnectionError("Request timed out")
        except httpx.RequestError as e:
            raise ConnectionError(f"Request failed: {str(e)}")

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint)

    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, data)

    def health(self) -> Dict[str, Any]:
        """Check server health.

        Returns:
            Health response with status and app_name.
        """
        return self._request("GET", "/health")

    def status(self) -> Dict[str, Any]:
        """Get detailed server status.

        Returns:
            Status response with pipeline_ready and startup_error.
        """
        return self._request("GET", "/status")

    def check(self) -> Dict[str, Any]:
        """Trigger email check pipeline.

        Returns:
            Check response with success, message, and data.
        """
        return self._request("POST", "/check")

    def test_urgent(self) -> Dict[str, Any]:
        """Test urgency classification with sample email.

        Returns:
            Test response with classification and SMS status.
        """
        return self._request("POST", "/test-urgent")
