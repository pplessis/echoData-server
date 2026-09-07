from pathlib                                import Path
import json
import random
from typing                                 import List
from os                                     import environ

from ..config                               import Config, logger
from .service_songlink                      import SonglinkAPI


class service_music:
    """Service utilitaire pour la sélection aléatoire d'un fichier / track music."""

    # -------------------------------------------------------------
    @staticmethod
    def listTrackFiles() -> List[Path]:
        """Liste tous les fichiers du dossier music correspondant au pattern configuré."""
        folder = Path(Config.DATABASE_JSON_FOLDER_MUSIC)
        files  = sorted(folder.glob(Config.JSON_FILES_MUSIC_PATERN))
        logger.info(f"🎵 {len(files)} music file(s) found in {folder}")
        return files

    # -------------------------------------------------------------
    @staticmethod
    def selectRandomTrackFile() -> Path:
        """Retourne un fichier JSON music choisi aléatoirement."""
        files = service_music.listTrackFiles()

        if not files:
            logger.error(
                f"❌ No music files matching '{Config.JSON_FILES_MUSIC_PATERN}' in "
                f"{Config.DATABASE_JSON_FOLDER_MUSIC}"
            )
            raise FileNotFoundError("No music files found.")

        chosen = random.choice(files)
        logger.info(f"🎲 Selected music file: {chosen.name}")
        return chosen

    # -------------------------------------------------------------
    @staticmethod
    def _enrich_songlink(track: dict) -> None:
        """
        Si songlink_url est manquant (None ou ''), appelle le service songlink pour le compléter.
        Met aussi à jour songlink_page_url et platforms si disponibles.
        N'altère pas le track si l'enrichissement échoue.
        """
        if track.get("songlink_url"):
            return

        name   = track.get("name", "")
        artist = track.get("artist", "")

        if not name or not artist:
            logger.warning("⚠️ Cannot enrich: missing name or artist")
            return

        try:
            api_key = environ.get("SONGLINK_API_KEY")
            client  = SonglinkAPI(api_key=api_key, rate_limit=0.1, max_retries=0)
            data    = client.enrich_track(name, artist)
        except Exception as e:
            logger.warning(f"⚠️ songlink enrichment error for {artist} - {name}: {e}")
            return

        if not data:
            logger.info(f"ℹ️ No songlink data for {artist} - {name}")
            return

        new_url = data.get("songlink_url")
        if new_url:
            track["songlink_url"]      = new_url
            track["songlink_page_url"] = data.get("songlink_page_url") or track.get("songlink_page_url")
            platforms                 = data.get("platforms")
            if platforms:
                track["platforms"]    = platforms
            track["_songlink_enriched"] = True
            logger.info(f"🔗 songlink enriched: {artist} - {name} -> {new_url}")
        else:
            logger.info(f"ℹ️ songlink returned no URL for {artist} - {name}")

    # -------------------------------------------------------------
    @staticmethod
    def loadRandomTrack(enrich: bool = True) -> dict:
        """Sélectionne un fichier music aléatoire puis un track aléatoire à l'intérieur.

        Si ``enrich`` est True (défaut) et que ``songlink_url`` est manquant,
        appelle le service songlink pour compléter l'URL.
        """
        path = service_music.selectRandomTrackFile()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in {path.name}: {e}")
            raise

        tracks = data.get("tracks", [])
        if not tracks:
            logger.error(f"❌ No tracks in {path.name}")
            raise ValueError(f"No tracks in {path.name}")

        track = random.choice(tracks)
        track["_source_file"] = path.name
        logger.info(
            f"🎶 Random track: {track.get('artist','?')} - {track.get('name','?')}"
        )

        if enrich:
            service_music._enrich_songlink(track)

        return track
