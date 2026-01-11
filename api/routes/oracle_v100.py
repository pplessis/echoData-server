from flask                                  import jsonify, Blueprint, request
from typing                                 import List

from ..config                               import Config, logger
from ..models.dataClasses_Horoscope         import Horoscope20, Sign

from ..services.service_oracle              import Service_Oracle
from ..libs.src.json.myJsonResponce         import myJsonResponce, RESULT_EVENTS, RESULT_STATUS

oracle = Blueprint('oracle', __name__,)

# #################################################################
@oracle.route("/oracle", methods=["GET"])
def getInfoFutues():
    logger.info("GET /oracle - called")
    payload = request.args.to_dict() or {}

    signText = payload.get("sign", None)
    signEnum = None

    response = myJsonResponce( RESULT_STATUS.SUCCESS, f"Oracle for {signText}", data=[] )

    try:
        ## Check Sign
        if signText is None:
            raise ValueError( f"PARAM Sign={signText}")
        else:
            signEnum = Sign(signText)

        ## Load ORACLE service ##
        service = Service_Oracle( Sign(signText) )

        my_horoscope = service.loadData ( Sign(signText), Horoscope20 )
        service.Horoscope =  my_horoscope 

        result_list = [ { "sign": ev.sign, "date": ev.date.strftime('%Y-%m-%d'), "sections":ev.sections  } for ev in [ service.Horoscope ] ]
        response.add_datas(result_list)

        response.event = RESULT_EVENTS.INFO


    except Exception as e:
        logger.error( f"Error loading ORACLE: {str(e)}" )
        response.status = RESULT_STATUS.ERROR
        response.event = RESULT_EVENTS.UNKNOWN
        response.add_error( "exception", str(e) )

    finally:
        return jsonify( response.to_dict() )