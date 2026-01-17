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

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth if configured."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an HTTP request to the server."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=headers)
                elif method.upper() == "POST":
                    if data:
                        response = client.post(url, headers=headers, data=data)
                    else:
                        response = client.post(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                if response.status_code >= 400:
                    try:
                        resp_data = response.json()
                        detail = resp_data.get("detail", response.text)
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

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, data)

    def health(self) -> Dict[str, Any]:
        """Check server health."""
        return self._get("/health")

    def status(self) -> Dict[str, Any]:
        """Get detailed server status."""
        return self._get("/status")

    def check(self) -> Dict[str, Any]:
        """Trigger email check pipeline."""
        return self._post("/check")

    def test_urgent(self) -> Dict[str, Any]:
        """Test urgency classification with sample email."""
        return self._post("/test-urgent")
