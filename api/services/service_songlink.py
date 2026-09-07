import time
import requests
from typing import Optional
from urllib.parse import urlencode

from ..config import logger


class SonglinkError(Exception):
    pass


class SonglinkRateLimitError(SonglinkError):
    pass


class SonglinkServerError(SonglinkError):
    pass


ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


class SonglinkAPI:
    BASE_URL = "https://api.odesli.co/v1-alpha.1/links"

    PLATFORM_MAP = {
        "spotify": "spotify",
        "appleMusic": "appleMusic",
        "youtube": "youtube",
        "youtubeMusic": "youtubeMusic",
        "amazonMusic": "amazonMusic",
        "tidal": "tidal",
        "deezer": "deezer",
        "soundcloud": "soundcloud",
        "pandora": "pandora",
        "napster": "napster",
        "yandexMusic": "yandexMusic",
        "anghami": "anghami",
        "boomplay": "boomplay",
        "joox": "joox",
        "kkbox": "kkbox",
        "qobuz": "qobuz",
    }

    def __init__(self, api_key: Optional[str] = None, rate_limit: float = 0.1, max_retries: int = 0):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._last_request_time = 0.0

    def _rate_limit_wait(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def search_apple_music(
        self, song_name: str, artist_name: str, entity_type: str = "song", country: str = "FR"
    ) -> Optional[dict]:
        """
        Recherche une chanson sur Apple Music via l'iTunes Search API
        et retourne les infos normalisées (titre, artiste, URL Apple Music).
        """
        params = {
            "term": f"{song_name} {artist_name}",
            "entity": entity_type,
            "country": country,
            "limit": 1,
        }

        try:
            response = requests.get(ITUNES_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                logger.warning(f"Aucun résultat iTunes pour: {song_name} - {artist_name}")
                return None

            track = results[0]
            return {
                "title": track.get("trackName"),
                "artist": track.get("artistName"),
                "apple_music_url": track.get("trackViewUrl"),
                "artwork": track.get("artworkUrl100"),
            }
        except Exception as e:
            logger.warning(f"Échec recherche iTunes pour {song_name} - {artist_name}: {e}")
            return None

    def _make_request(self, params: dict) -> dict:
        self._rate_limit_wait()

        if self.api_key:
            params["key"] = self.api_key

        url = f"{self.BASE_URL}?{urlencode(params)}"
        logger.debug(f"song.link request: {url}")

        last_exception = None
        for attempt in range(self.max_retries + 1):
            self._last_request_time = time.time()
            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 429:
                    raise SonglinkRateLimitError("Rate limit exceeded (Too many request for today)")

                if 500 <= response.status_code < 600:
                    raise SonglinkServerError(f"HTTP {response.status_code}: {response.text}")

                if response.status_code != 200:
                    logger.warning(f"song.link HTTP {response.status_code}: {response.text[:200]}")
                    return {}

                data = response.json()
                return data

            except SonglinkRateLimitError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 2.0

                    logger.warning(f"Rate limited (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for rate limit: {e}")
                    raise

            except SonglinkServerError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 1.0
                    logger.warning(f"Server error (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for server error: {e}")
                    raise

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 1.0
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded: {e}")
                    raise SonglinkError(f"Request failed after {self.max_retries + 1} attempts: {e}")

        raise last_exception

    def get_links_by_song_artist(
        self, song_name: str, artist_name: str, entity_type: str = "song"
    ) -> dict:
        params = {
            "songName": song_name,
            "artistName": artist_name,
            "entityType": entity_type,
        }
        return self._make_request(params)

    def extract_platform_urls(self, data: dict) -> dict:
        platforms = {}

        entities = data.get("entitiesByUniqueId", {})
        for entity_id, entity in entities.items():
            entity_platforms = entity.get("platforms")
            if not isinstance(entity_platforms, dict):
                continue
            for platform_key, platform_name in self.PLATFORM_MAP.items():
                platform_data = entity_platforms.get(platform_key)
                if isinstance(platform_data, dict) and "url" in platform_data:
                    platforms[platform_name] = platform_data["url"]

        page_url = data.get("pageUrl")
        if page_url:
            platforms["songlink_page"] = page_url

        return platforms

    def get_songlink_url(self, data: dict) -> Optional[str]:
        return data.get("pageUrl")

    def get_song_links_from_odesli(self, apple_url: str, country: str = "FR") -> dict:
        """
        Envoie l'URL Apple Music à Odesli (song.link) pour récupérer les liens multi-plateformes.
        Retourne le JSON brut de l'API.
        """
        return self._make_request({"url": apple_url, "userCountry": country})

    def enrich_track(self, track_name: str, artist_name: str) -> dict:
        try:
            data = self.get_links_by_song_artist(track_name, artist_name)
            if not data:
                return {}

            platforms = self.extract_platform_urls(data)
            songlink_url = self.get_songlink_url(data)

            return {
                "songlink_url": songlink_url,
                "songlink_page_url": platforms.get("songlink_page"),
                "platforms": {k: v for k, v in platforms.items() if k != "songlink_page"},
            }
        except SonglinkRateLimitError:
            logger.warning(f"song.link rate limit exceeded for {artist_name} - {track_name}, skipping enrichment")
            return {}
        except Exception as e:
            logger.warning(f"song.link enrichment failed for {artist_name} - {track_name}: {e}")
            return {}

    def enrich_track_with_apple_music(
        self, track_name: str, artist_name: str, country: str = "FR"
    ) -> dict:
        """
        Enrichit un track en cherchant d'abord sur Apple Music (iTunes Search API),
        puis en utilisant l'URL Apple Music pour interroger song.link (Odesli).
        """
        apple_result = self.search_apple_music(track_name, artist_name, country=country)

        if not apple_result or not apple_result.get("apple_music_url"):
            logger.warning(f"Impossible de trouver sur Apple Music: {track_name} - {artist_name}")
            return self.enrich_track(track_name, artist_name)

        apple_url = apple_result["apple_music_url"]

        try:
            data = self._make_request({"url": apple_url})
            if not data:
                return {}

            platforms = self.extract_platform_urls(data)
            songlink_url = self.get_songlink_url(data)

            return {
                "songlink_url": songlink_url,
                "songlink_page_url": platforms.get("songlink_page"),
                "platforms": {k: v for k, v in platforms.items() if k != "songlink_page"},
                "apple_music_info": apple_result,
            }
        except SonglinkRateLimitError:
            logger.warning(f"song.link rate limit exceeded for {apple_url}, skipping enrichment")
            return {}
        except Exception as e:
            logger.warning(f"song.link enrichment failed for {apple_url}: {e}")
            return {}