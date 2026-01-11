
from flask                                  import jsonify, Blueprint, request
from typing                                 import List

from ..config                                import Config, logger
from ..models.dataClasses_EventDay           import EventDay
from ..services.service_events_day           import service_events_day
from ..libs.src.json.myJsonResponce          import myJsonResponce, RESULT_EVENTS, RESULT_STATUS

events = Blueprint('events', __name__,)

# #################################################################
@events.route("/international_day", methods=["GET"])
def getInfoEvents():
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
        if (type is None and date is None) and len(events) == 0:
            logger.info("No filter, get ALL events")
            events = service.jsonDB

        # Convert `InternationalDay` objects to generic  dicts and add to response
        response.event = RESULT_EVENTS.FETCHED

        events_list = [ { "name": ev.getName, "date": ev.getDate } for ev in events ]
        response.add_datas(events_list)

    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))

    finally:
        return jsonify( response.to_dict() )

# ------------------------------------------------------------------
@events.route("/international_day", methods=["POST"])
def updateInfo():
    logger.info("POST /international_day - called")

    return jsonify({"status": "ok", "version": "v1"})


# #################################################################

@events.route("/daysOff", methods=["GET"])
def getDayOff():
    logger.info("GET /dayOff - called")
    payload = request.args.to_dict() or {}

    date = payload.get("date", None)
    type = payload.get("type", None)

    response = myJsonResponce( RESULT_STATUS.SUCCESS, "Days Off", data=[] )
    responseStatus = 200

    try:
        ## Load JSON DATA FROM FILE OR DATABASE HERE ##
        jsonDB = Config.DATABASE_JSON_DAYOFF
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

            if (type.upper() == 'STATUS'):
                events = service.get_events_today()

                if (len(events)>0):
                    response.status = RESULT_STATUS.SUCCESS
                    response.event  = RESULT_EVENTS.INFO
                    responseStatus = 200

                else:
                    response.status = RESULT_STATUS.ERROR
                    response.event  = RESULT_EVENTS.INFO
                    responseStatus = 500

        ## Extraction by DATE
        if type is None and date is not None:
            logger.info(f"Filter by date: {date}")
            events = service.get_events_by_date(date)

        ## Extraction by DEFAULT
        if (type is None and date is None) and len(events) == 0:
            logger.info("No filter, get ALL events")
            events = service.jsonDB

        # Convert `InternationalDay` objects to generic  dicts and add to response
        response.event = RESULT_EVENTS.FETCHED

        events_list = [ { "name": ev.getName, "date": ev.getDate } for ev in events ]
        response.add_datas(events_list)

    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))

    finally:
        return jsonify( response.to_dict()), responseStatus
# ------------------------------------------------------------------

# ##################################################################
@events.route("/saints", methods=["GET"])
def getInfoSaints():
    logger.info("GET /saints - called")
    payload = request.args.to_dict() or {}

    date = payload.get("date", None)
    type = payload.get("type", None)

    response = myJsonResponce( RESULT_STATUS.SUCCESS, "Saints List", data=[] )
    responseStatus = 200

    try:
        ## Load JSON DATA FROM FILE OR DATABASE HERE ##
        jsonDB = Config.DATABASE_JSON_SAINTS
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
        if (type is None and date is None) and len(events) == 0:
            logger.info("No filter, get ALL events")
            events = service.jsonDB

        # Convert `InternationalDay` objects to generic  dicts and add to response
        response.event = RESULT_EVENTS.FETCHED

        events_list = [ { "name": ev.getName, "date": ev.getDate } for ev in events ]
        response.add_datas(events_list)

    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))

    finally:
        return jsonify( response.to_dict() ) , responseStatus
