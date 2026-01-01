
from flask import jsonify, Blueprint, request
from typing                                 import List

from ..config                                import Config, logger
from ..models.dataClasses_EventDay           import EventDay
from ..services.service_events_day           import service_events_day
from ..libs.src.json.myJsonResponce          import myJsonResponce, RESULT_EVENTS, RESULT_STATUS

international_day_v100 = Blueprint('international_day_V100', __name__,)

@international_day_v100.route("/international_day", methods=["GET"])
def getInfo():
    logger.info("GET /international_day - called")
    payload = request.args.to_dict() or {}
    
    date = payload.get("date", None)
    type = payload.get("type", None)

    response = myJsonResponce( RESULT_STATUS.SUCCESS, "International events", data=[] )

    try:
        ## Load JSON DATA FROM FILE OR DATABASE HERE ##
        jsonDB = Config.DATABASE_JSON_EVENTS
        logger.info( f"Load - {jsonDB}" )
        service = service_events_day( jsonDB )
        events:List[EventDay] = []

        ## Extraction by TYPE
        if type is not None and date is None:
            logger.info(f"Filter by type: {type}")
            if (type.upper() == 'MONTH'):
                events = service.get_events_current_month()

            if (type.upper() == 'TODAY'):
                events = service.get_events_today()

        ## Extraction by DATE
        if type is None and date is not None:
            logger.info(f"Filter by date: {date}")
            events = service.get_events_by_date(date)

        ## Extraction by DEFAULT
        if len(events) == 0:
            logger.info("No filter, get ALL events")
            events = service.jsonDB


        # Convert `InternationalDay` objects to generic  dicts and add to response
        events_list = [ { "name": ev.getName, "date": ev.getDate } for ev in events ]
        response.event = RESULT_EVENTS.FETCHED
        response.add_datas(events_list)

    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.message = "Failed to load international events"
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))

    finally:
        return jsonify( response.to_dict() )

@international_day_v100.route("/dayOff", methods=["GET"])
def getDayOff():
    logger.info("GET /dayOff - called")
    response = myJsonResponce( RESULT_STATUS.SUCCESS, "International events", data=[] )
    try:
        ## Load JSON DATA FROM FILE OR DATABASE HERE ##
        jsonDB = Config.DATABASE_JSON_DAYOFF
        logger.info( f"Load - {jsonDB}" )

        logger.debug("Need to CODE this PART ...")


    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.message = "Failed to load international events"
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))

    finally:
        return jsonify( response.to_dict())


@international_day_v100.route("/international_day", methods=["POST"])
def updateInfo():
    logger.info("POST /international_day - called")
    
    
    
    return jsonify({"status": "ok", "version": "v1"})