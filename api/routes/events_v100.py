import random
from datetime import datetime

from flask                                  import jsonify, Blueprint, request, Response
from typing                                 import List

from ..libs.src.json.myJsonResponce          import myJsonResponce, RESULT_EVENTS, RESULT_STATUS
from ..config                                import Config, logger

from ..models.dataClasses_EventDay           import EventDay
from ..services.service_events_day           import service_events_day


events = Blueprint('events', __name__)

# #################################################################

@events.route("/random", methods=["GET"])
def getRandomEvents() -> Response:
    data = { 'title': "None", 'details': "None" }

    try:
        ## Load JSON DATA FROM FILE OR DATABASE HERE ##
        jsonDB = Config.DATABASE_JSON_EVENTS
        logger.info( f"Load - {jsonDB}" )

        # GET TODAY ENENT
        service = service_events_day( jsonDB )
        events = service.get_events_today()

        # GET RANDOM EVENT
        if ( len (events) == 0 ):
            events = service.get_events_random()

        # FILL DATA for RESULT
        if len(events) > 0:
            ## Select a EVENT in LIST
            indexRnd = random.randint(0, len(events) - 1) 
            data["title"]   = events[indexRnd].getDateFormated('long')
            data["details"] = events[indexRnd].getName
        else:
            logger.warning("Aucun événement trouvé")
            data["title"] = "📅 Pas d'événement"
            data["details"] = "Aucun événement disponible"


    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        data["title"] = '❌ ERROR'
        data["details"]= str(e)  # Plus d'infos debug

    finally:
        return jsonify( data )


# #################################################################
@events.route("/international_day", methods=["GET"])
def getInfoEvents():
    logger.info("GET /international_day - called")
    payload = request.args.to_dict() or {}

    date = payload.get("date", None)
    type = payload.get("type", None)

    response = myJsonResponce( RESULT_STATUS.SUCCESS, "International events", data=[] )
    responseStatus = 200

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
        responseStatus = 500

    finally:
        return jsonify( response.to_dict() ), responseStatus


# ------------------------------------------------------------------
@events.route("/international_day", methods=["POST"])
def updateInfo():
    logger.info("POST /international_day - called")
    response = myJsonResponce( RESULT_STATUS.SUCCESS, "International events: Method POST not implemented.", data=[] )
    responseStatus = 500

    return jsonify( response.to_dict() ), responseStatus


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

        # Determine if today is weekend (Saturday=5, Sunday=6)
        today = datetime.today()
        today_is_weekend = today.weekday() >= 5  # 5=Saturday, 6=Sunday

        ## Extraction by TYPE
        if type is not None and date is None:
            logger.info(f"Filter by type: {type}")
            if (type.upper() == 'MONTH'):
                events = service.get_events_current_month()
                logger.info(f"Filtered MONTH events to weekends: {len(events)}")

            if (type.upper() == 'TODAY'):
                # Check if today is weekend before the service
                if today_is_weekend:
                    #events = service.get_events_today()

                    # Ensure today is included as a day off if not already present
                    today_str = today.strftime('%Y-%m-%d')
                    if not any(ev.date and ev.date.strftime('%Y-%m-%d') == today_str for ev in events):
                        events.append(EventDay(name="Weekend Day (Off by DEFAULT)", date=today, format="MM-DD"))
                else:
                    events = service.get_events_today()

            if (type.upper() == 'STATUS'):
                # Apply same rule as TODAY
                if today_is_weekend:
                    events = service.get_events_today()

                    # Ensure today is included as a day off if not already present
                    today_str = today.strftime('%Y-%m-%d')
                    if not any(ev.date and ev.date.strftime('%Y-%m-%d') == today_str for ev in events):
                        events.append(EventDay(name="Weekend Day Off", date=today, format="MM-DD"))

                    if (len(events) > 0):
                        response.status = RESULT_STATUS.SUCCESS
                        response.event  = RESULT_EVENTS.INFO
                        responseStatus = 200
                    else:
                        response.status = RESULT_STATUS.ERROR
                        response.event  = RESULT_EVENTS.INFO
                        responseStatus = 500
                else:
                    events = service.get_events_today()
                    if (len(events) > 0):
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

            # TODO : Add A format Check for the date (HTTP Params)

            events = service.get_events_by_date(date)

        ## Extraction by DEFAULT
        if (type is None and date is None) and len(events) == 0:
            logger.info("No filter, get ALL events")
            events = service.jsonDB

            # Add all Weekends days on current year to the list
            year = today.year
            import calendar

            for month in range(1, 13):
                last_day = calendar.monthrange(year, month)[1]
                for day in range(1, last_day + 1):
                    d = datetime(year, month, day)
                    if d.weekday() >= 5:  # Saturday or Sunday
                        # Check if already in events
                        if not any(ev.date and ev.date == d for ev in events):
                            events.append(EventDay(name="Weekend", date=d, format="MM-DD"))

        # Convert `InternationalDay` objects to generic  dicts and add to response
        response.event = RESULT_EVENTS.FETCHED

        events_list = [ { "name": ev.getName, "date": ev.getDate } for ev in events ]
        response.add_datas(events_list)

    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))
        responseStatus = 500

    finally:
        return jsonify( response.to_dict()), responseStatus

# ------------------------------------------------------------------

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

        # Convert `SAINTS` objects to generic  dicts and add to response
        response.event = RESULT_EVENTS.FETCHED

        events_list = [ { "name": ev.getName, "date": ev.getDate } for ev in events ]
        response.add_datas(events_list)

    except Exception as e:
        logger.error( f"Error loading events: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error("exception", str(e))
        responseStatus=500

    finally:
        return jsonify( response.to_dict() ) , responseStatus
