from enum import StrEnum
from datetime import datetime, timezone

####
class RESULT_STATUS(StrEnum):
        SUCCESS = 'success'
        ERROR   = 'error'
        WARNING = 'warning'
        INFO    = 'info'
        UNKNOWN = 'unknown'

class RESULT_EVENTS(StrEnum):
        CREATED = 'created'
        UPDATED = 'updated'
        DELETED = 'deleted'
        FETCHED = 'fetched'
        PAYMENT = 'payment'
        WEBHOOK = 'webhook'
        CUSTOM  = 'custom'
        INFO    = 'info'
        UNKNOWN = 'unknown'

class myJsonResponce:

    def __init__(self, status: RESULT_STATUS, message: str, data: list ):
        self.status = status
        self.event = RESULT_EVENTS.UNKNOWN
        self.message = message

        self.data = data if data is not None else []
        self.errors = []
        self.meta = { 'len':0 , 'requestDate':None }


    def refresfh_meta(self):
        self.meta['len'] = len( self.data ) if self.data is not None else 0
        # Set current date/time in UTC as YYYYMMDDThhmmss
        self.meta['requestDate'] = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')

### ADD ERRORS
    def add_error(self, key: str, value: str):
        tmpValue = { key: value }
        self.errors.append( tmpValue )
        return
    
    def add_errors(self, errors: list[dict]):
       self.errors.extend( errors )
       return

### ADD DATA
    def add_data(self, key: str, value: str):
        #self.data[key] = value
        tmpValue = { key: value }
        self.data.append( tmpValue )
        return

    def add_datas(self, data: list[dict] ):
        self.data.extend( data )
        return

### TO DICT
    def to_dict(self) -> dict:
        self.refresfh_meta()

        return {
            "status": self.status
            ,"event": self.event
            ,"message": self.message
            ,"data": self.data
            ,"errors": self.errors
            ,"meta": self.meta
        }