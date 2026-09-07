#!/usr/bin/env python3
"""
Build Music Database from Last.fm Scrobbles

Fetches all historical scrobbles from Last.fm, enriches with song.link (Odesli) universal URLs,
and saves compiled JSON to api/static/data/music/

Usage:
    python scripts/build_music_db.py --user <LASTFM_USER> --api-key <KEY> [options]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.config import logger
from api.models.dataClasses_Track import Track, MusicDatabase
from api.services.service_lastfm import LastFMAPI, LastFMRateLimitError
from api.services.service_songlink import SonglinkAPI


CHECKPOINT_FILE = ".checkpoint.json"
OUTPUT_FILENAME = "tracks_{date}.json"
LATEST_SYMLINK = "tracks_latest.json"


def parse_date_arg(value: str) -> int:
    """Parse date string (YYYY-MM-DD or UNIX timestamp) to UNIX timestamp."""
    try:
        return int(value)
    except ValueError:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return int(dt.replace(tzinfo=timezone.utc).timestamp())


def load_checkpoint(output_dir: Path) -> dict:
    checkpoint_path = output_dir / CHECKPOINT_FILE
    if checkpoint_path.exists():
        try:
            with open(checkpoint_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
    return {}


def save_checkpoint(output_dir: Path, checkpoint: dict):
    checkpoint_path = output_dir / CHECKPOINT_FILE
    checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save checkpoint: {e}")


def load_existing_tracks(output_dir: Path) -> list[Track]:
    latest_path = output_dir / LATEST_SYMLINK
    if latest_path.exists():
        try:
            with open(latest_path, "r") as f:
                data = json.load(f)
                return [Track.from_dict(t) for t in data.get("tracks", [])]
        except Exception as e:
            logger.warning(f"Failed to load existing tracks: {e}")
    return []


def get_existing_track_keys(tracks: list[Track]) -> set[str]:
    """Return a set of unique track identifiers (artist - name) for deduplication."""
    keys = set()
    for t in tracks:
        key = f"{t.artist.strip().lower()}|{t.name.strip().lower()}"
        keys.add(key)
    return keys


def save_database(db: MusicDatabase, output_dir: Path, date_str: str):
    output_dir.mkdir(parents=True, exist_ok=True)

    dated_file = output_dir / OUTPUT_FILENAME.format(date=date_str)
    latest_file = output_dir / LATEST_SYMLINK

    json_str = db.to_json(indent=2)

    with open(dated_file, "w") as f:
        f.write(json_str)

    try:
        # Create a symlink
        if latest_file.exists() or latest_file.is_symlink():
            latest_file.unlink()
        #latest_file.symlink_to(dated_file.name)

    except Exception:
        with open(latest_file, "w") as f:
            f.write(json_str)

    logger.info(f"Saved {len(db.tracks)} tracks to {dated_file}")


def progress_callback(page: int, total: int, count: int):
    pct = (page / total * 100) if total > 0 else 0
    logger.info(f"Progress: page {page}/{total} ({pct:.1f}%) - {count} tracks fetched")


def main():
    parser = argparse.ArgumentParser(
        description="Build Music Database from Last.fm Scrobbles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full backfill
    python scripts/build_music_db.py --user myuser --api-key $LASTFM_API_KEY

    # Test with 50 tracks
    python scripts/build_music_db.py --user myuser --api-key $LASTFM_API_KEY --max-tracks 50

    # Since specific date
    python scripts/build_music_db.py --user myuser --api-key $LASTFM_API_KEY --since 2024-01-01

    # Resume interrupted run
    python scripts/build_music_db.py --user myuser --api-key $LASTFM_API_KEY --resume
        """,
    )

    parser.add_argument("--user", required=True, help="Last.fm username")
    parser.add_argument("--api-key", help="Last.fm API key (or env LASTFM_API_KEY)")
    parser.add_argument("--songlink-key", help="song.link/Odesli API key (or env SONGLINK_API_KEY)")
    parser.add_argument("--output-dir", default="api/static/data/music", help="Output directory")
    parser.add_argument("--since", type=parse_date_arg, help="Start date (YYYY-MM-DD or UNIX timestamp)")
    parser.add_argument("--until", type=parse_date_arg, help="End date (YYYY-MM-DD or UNIX timestamp)")
    parser.add_argument("--max-tracks", type=int, help="Maximum tracks to fetch (for testing)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--no-songlink", action="store_true", help="Skip song.link enrichment")
    parser.add_argument("--checkpoint-interval", type=int, default=10, help="Save checkpoint every N pages")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("LASTFM_API_KEY")
    if not api_key:
        parser.error("Last.fm API key required (--api-key or LASTFM_API_KEY env var)")

    songlink_key = args.songlink_key or os.getenv("SONGLINK_API_KEY")
    output_dir = Path(args.output_dir)

    logger.info(f"Starting music database build for user: {args.user}")
    logger.info(f"Output directory: {output_dir}")

    lastfm = LastFMAPI(api_key, args.user)
    songlink = SonglinkAPI(songlink_key) if not args.no_songlink else None

    checkpoint = load_checkpoint(output_dir) if args.resume else {}
    start_page = checkpoint.get("last_page", 0) + 1
    all_tracks = []
    existing_keys = set()

    if args.resume and checkpoint.get("tracks_fetched", 0) > 0:
        existing = load_existing_tracks(output_dir)
        all_tracks = existing
        existing_keys = get_existing_track_keys(existing)
        logger.info(f"Resuming from page {start_page}, loaded {len(existing)} existing tracks")

    fetched_at = datetime.now(timezone.utc).isoformat()
    date_range = {"from": None, "to": None}

    try:
        if args.resume and start_page > 1:
            raw_tracks = lastfm.get_all_tracks(
                from_ts=args.since,
                to_ts=args.until,
                max_tracks=args.max_tracks,
            )
            if raw_tracks:
                last_uts = int(raw_tracks[-1].get("date", {}).get("uts", 0))
                first_uts = int(raw_tracks[0].get("date", {}).get("uts", 0))
                date_range["from"] = datetime.fromtimestamp(last_uts, tz=timezone.utc).isoformat()
                date_range["to"] = datetime.fromtimestamp(first_uts, tz=timezone.utc).isoformat()
        else:
            raw_tracks = lastfm.get_all_tracks(
                from_ts=args.since,
                to_ts=args.until,
                max_tracks=args.max_tracks,
                progress_callback=progress_callback,
            )
            if raw_tracks:
                last_uts = int(raw_tracks[-1].get("date", {}).get("uts", 0))
                first_uts = int(raw_tracks[0].get("date", {}).get("uts", 0))
                date_range["from"] = datetime.fromtimestamp(last_uts, tz=timezone.utc).isoformat()
                date_range["to"] = datetime.fromtimestamp(first_uts, tz=timezone.utc).isoformat()

        logger.info(f"Fetched {len(raw_tracks)} raw tracks from Last.fm")

        skipped_duplicates = 0
        maxTrack = len( list(raw_tracks) )
        for i, raw_track in enumerate(raw_tracks):
            track = Track.from_lastfm_track(raw_track, fetched_at)

            logger.info(f"Processed {i+1}/{maxTrack} tracks... {round(((i+1)/maxTrack)*100,2)}% ")

            # Check for duplicates by track_mbid + name
            track_key = f"{track.track_mbid}|{track.name.strip().lower()}"
            if track_key in existing_keys:
                skipped_duplicates += 1
                continue
            existing_keys.add(track_key)

            if songlink:
                enrichment = songlink.enrich_track_with_apple_music(track.name, track.artist, 'FR')

                #enrichment = songlink.get_song_links_from_odesli( enrichment_appleM ["apple_music_url"])

                track.songlink_url = enrichment.get("songlink_url")
                #track.songlink_page_url = enrichment.get("songlink_page_url")
                #track.platforms = enrichment.get("platforms", {})

            all_tracks.append(track)

            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(raw_tracks)} tracks... (skipped {skipped_duplicates} duplicates)")

    except LastFMRateLimitError:
        logger.error("Rate limited by Last.fm. Wait before retrying.")
        save_checkpoint(output_dir, {
            "last_page": start_page - 1,
            "tracks_fetched": len(all_tracks),
        })
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        save_checkpoint(output_dir, {
            "last_page": start_page - 1,
            "tracks_fetched": len(all_tracks),
        })
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fetching tracks: {e}")
        sys.exit(1)

    all_tracks.sort(key=lambda t: t.date_uts, reverse=True)

    meta = {
        "lastfm_user": args.user,
        "total_tracks": len(all_tracks),
        "date_range": date_range,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "songlink_enriched": songlink is not None,
        "version": 1,
    }

    db = MusicDatabase(meta=meta, tracks=all_tracks)
    date_str = datetime.now().strftime("%Y%m%d")
    save_database(db, output_dir, date_str)

    if (output_dir / CHECKPOINT_FILE).exists():
        (output_dir / CHECKPOINT_FILE).unlink()

    logger.info(f"Done! Total tracks: {len(all_tracks)}")


if __name__ == "__main__":
    main()