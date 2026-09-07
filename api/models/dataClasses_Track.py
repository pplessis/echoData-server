from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional
import json


@dataclass(slots=True)
class Track:
    name: str

    artist: str
    #artist_mbid: Optional[str] = None

    album: Optional[str] = None
    #album_mbid: Optional[str] = None
    #album_artist: Optional[str] = None

    date_uts: int = 0
    date_iso: str = ""
    lastfm_url: str = ""
    track_mbid: Optional[str] = None
    songlink_url: Optional[str] = None
    #songlink_page_url: Optional[str] = None

    #platforms: dict = field(default_factory=dict)

    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        return cls(**data)

    @classmethod
    def from_lastfm_track(cls, track: dict, fetched_at: str) -> "Track":
        date_uts = int(track.get("date", {}).get("uts", 0)) if track.get("date") else 0
        date_iso = datetime.fromtimestamp(date_uts, tz=timezone.utc).isoformat() if date_uts else ""

        artist = track.get("artist", {})
        artist_name = artist.get("name", "") if isinstance(artist, dict) else str(artist)
        #artist_mbid = artist.get("mbid") if isinstance(artist, dict) else None

        album = track.get("album", {})
        album_name = album.get("#text", "") if isinstance(album, dict) else str(album)
        #album_mbid = album.get("mbid") if isinstance(album, dict) else None

        return cls(
            name=track.get("name", ""),

            artist=artist_name,
            #artist_mbid=artist_mbid or None,

            album=album_name or None,
            #album_mbid=album_mbid or None,

            #album_artist=None,

            date_uts=date_uts,
            date_iso=date_iso,
            lastfm_url=track.get("url", ""),
            track_mbid=track.get("mbid") or None,
            fetched_at=fetched_at,
        )


@dataclass(slots=True)
class MusicDatabase:
    meta: dict
    tracks: list[Track]

    def to_dict(self) -> dict:
        return {
            "meta": self.meta,
            "tracks": [t.to_dict() for t in self.tracks],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "MusicDatabase":
        return cls(
            meta=data.get("meta", {}),
            tracks=[Track.from_dict(t) for t in data.get("tracks", [])],
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MusicDatabase":
        return cls.from_dict(json.loads(json_str))