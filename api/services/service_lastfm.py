import time
import requests
from typing import Optional
from urllib.parse import urlencode

from ..config import logger


class LastFMError(Exception):
    pass


class LastFMRateLimitError(LastFMError):
    pass


class LastFMServerError(LastFMError):
    pass


class LastFMAPI:
    BASE_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key: str, user: str, rate_limit: float = 0.2, max_retries: int = 3):
        self.api_key = api_key
        self.user = user
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._last_request_time = 0.0

    def _rate_limit_wait(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def _make_request(self, params: dict) -> dict:
        self._rate_limit_wait()
        params["api_key"] = self.api_key
        params["format"] = "json"

        url = f"{self.BASE_URL}?{urlencode(params)}"
        logger.debug(f"Last.fm request: {url}")

        last_exception = None
        for attempt in range(self.max_retries + 1):
            self._last_request_time = time.time()
            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 429:
                    raise LastFMRateLimitError("Rate limit exceeded")

                if 500 <= response.status_code < 600:
                    raise LastFMServerError(f"HTTP {response.status_code}: {response.text}")

                if response.status_code != 200:
                    raise LastFMError(f"HTTP {response.status_code}: {response.text}")

                data = response.json()

                if "error" in data:
                    error_code = data["error"]
                    error_msg = data.get("message", "Unknown error")
                    if error_code == 29:
                        raise LastFMRateLimitError(f"Rate limit: {error_msg}")
                    raise LastFMError(f"Last.fm error {error_code}: {error_msg}")

                return data

            except LastFMServerError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 1.0
                    logger.warning(f"Server error (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for server error: {e}")
                    raise

            except (LastFMRateLimitError, LastFMError):
                raise

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 1.0
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded: {e}")
                    raise LastFMError(f"Request failed after {self.max_retries + 1} attempts: {e}")

        raise last_exception

    def get_recent_tracks(
        self,
        page: int = 1,
        limit: int = 200,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        extended: int = 1,
    ) -> dict:
        params = {
            "method": "user.getrecenttracks",
            "user": self.user,
            "page": page,
            "limit": limit,
            "extended": extended,
        }
        if from_ts:
            params["from"] = from_ts
        if to_ts:
            params["to"] = to_ts

        return self._make_request(params)

    def get_all_tracks(
        self,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        max_tracks: Optional[int] = None,
        progress_callback=None,
    ) -> list[dict]:
        all_tracks = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            logger.info(f"Fetching page {page}/{total_pages}...")
            data = self.get_recent_tracks(page=page, from_ts=from_ts, to_ts=to_ts)

            recenttracks = data.get("recenttracks", {})
            tracks = recenttracks.get("track", [])
            total_pages = int(recenttracks.get("@attr", {}).get("totalPages", 1))

            if not tracks:
                break

            for track in tracks:
                if track.get("@attr", {}).get("nowplaying") == "true":
                    continue
                all_tracks.append(track)
                if max_tracks and len(all_tracks) >= max_tracks:
                    return all_tracks

            if progress_callback:
                progress_callback(page, total_pages, len(all_tracks))

            page += 1

        return all_tracks