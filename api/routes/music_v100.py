from pathlib                                import Path
from flask                                  import jsonify, Blueprint

from ..libs.src.json.myJsonResponce         import myJsonResponce, RESULT_STATUS, RESULT_EVENTS
from ..config                               import Config, logger
from ..services.service_music               import service_music


music_v100 = Blueprint('music_v100', __name__)


# #################################################################
def __selectDB() -> Path:
    """Sélectionne aléatoirement un fichier JSON music via le service dédié."""
    return service_music.selectRandomTrackFile()


# #################################################################
@music_v100.route("/music/random", methods=["GET"])
def getRandomTrack():
    response = myJsonResponce(
        RESULT_STATUS.SUCCESS,
        "Random track fetched",
        data=[]
    )
    response.event = RESULT_EVENTS.FETCHED

    try:
        jsonDB = __selectDB()
        logger.info(f"Load - {jsonDB}")

        track = service_music.loadRandomTrack()
        response.add_data("track", track)
        response.message = f"Random track from {track.get('_source_file','?')}"

    except FileNotFoundError as e:
        logger.error(f"Music file not found: {e}")
        response.status  = RESULT_STATUS.ERROR
        response.event   = RESULT_EVENTS.UNKNOWN
        response.message = "No music file available"
        response.add_error("file", str(e))

    except ValueError as e:
        logger.error(f"Empty music file: {e}")
        response.status  = RESULT_STATUS.WARNING
        response.event   = RESULT_EVENTS.UNKNOWN
        response.message = str(e)
        response.add_error("tracks", str(e))

    except Exception as e:
        logger.error(f"Error loading random track: {e}")
        response.status  = RESULT_STATUS.ERROR
        response.event   = RESULT_EVENTS.UNKNOWN
        response.message = "Internal error while fetching random track"
        response.add_error("exception", str(e))

    finally:
        return jsonify(response.to_dict())


# #################################################################
@music_v100.route("/music/random-file", methods=["GET"])
def getRandomMusicFile():
    """Retourne le nom du fichier music sélectionné aléatoirement (debug/info)."""
    response = myJsonResponce(
        RESULT_STATUS.SUCCESS,
        "Random music file selected",
        data=[]
    )
    response.event = RESULT_EVENTS.INFO

    try:
        chosen = __selectDB()
        response.add_data("file", chosen.name)
        response.add_data("path", str(chosen))

    except FileNotFoundError as e:
        logger.error(f"Music file not found: {e}")
        response.status  = RESULT_STATUS.ERROR
        response.event   = RESULT_EVENTS.UNKNOWN
        response.message = "No music file available"
        response.add_error("file", str(e))

    except Exception as e:
        logger.error(f"Error: {e}")
        response.status  = RESULT_STATUS.ERROR
        response.event   = RESULT_EVENTS.UNKNOWN
        response.message = "Internal error"
        response.add_error("exception", str(e))

    finally:
        return jsonify(response.to_dict())
