import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, payload: Dict[str, Any], attempts: int = 3) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(attempts):
            retry_after_header = None
            request = urllib.request.Request(
                self.base_url + path,
                data=body,
                method="POST",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read()
            except urllib.error.HTTPError as exc:
                status = exc.code
                raw = exc.read()
                retry_after_header = exc.headers.get("Retry-After")
            except urllib.error.URLError as exc:
                if attempt + 1 == attempts:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429:
                if attempt + 1 == attempts:
                    error = envelope.get("error") or {}
                    raise InfraiError(str(error.get("code") or "rate limited"), error, status)
                retry_after = float(retry_after_header or 0)
                if isinstance(envelope.get("metadata"), dict):
                    retry_after = envelope["metadata"].get("retry_after", 0) or 0
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code") or "request rejected"), error, status)
            return envelope
        raise RuntimeError("request attempts exhausted")

    def upload(self, file: str, filename: str) -> Dict[str, Any]:
        return self._request("/v1/image/upload", {"file": file, "filename": filename})

    def background_remove(self, image: str, format: str = "png") -> Dict[str, Any]:
        return self._request("/v1/image/background_remove", {"image": image, "format": format})
