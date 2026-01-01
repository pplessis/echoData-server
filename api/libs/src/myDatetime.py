import datetime
from datetime import timedelta
from enum import Enum

###############################################################################
class TIMEZONE(int, Enum):
    UTC = 0
    CET = 2
###############################################################################

class MyDatetime:
    """DateTime based on ISO 8601 and UTC convert
       See: https://en.wikipedia.org/wiki/ISO_8601
    """

    def __init__(self, strIsoDatetime=None) -> None:
        myDateUTCtmp = datetime.datetime.now( tz=datetime.UTC )
        self.myDateUTC = datetime.datetime(myDateUTCtmp.year, myDateUTCtmp.month, myDateUTCtmp.day, myDateUTCtmp.hour, myDateUTCtmp.minute, myDateUTCtmp.second,myDateUTCtmp.microsecond, tzinfo=datetime.timezone.utc)

        if (strIsoDatetime != None):
            year =      int(strIsoDatetime[0:4])
            month =     int(strIsoDatetime[5:7])
            day =       int(strIsoDatetime[8:10])
            hour =      int(strIsoDatetime[11:13])
            min =       int(strIsoDatetime[14:16])
            sec =       int(strIsoDatetime[17:19])

            if (len(strIsoDatetime)>20):
                microSec =  int(strIsoDatetime[20:23])
            else:
                microSec = 0

            self.myDateUTC = datetime.datetime(year, month, day, hour, min, sec, microSec, tzinfo=datetime.timezone.utc)

        start_dst = datetime.datetime(self.myDateUTC.year,3,31,2, tzinfo=datetime.timezone.utc)
        end_dst = datetime.datetime(self.myDateUTC.year,10,31,3, tzinfo=datetime.timezone.utc)

        if (start_dst <= self.myDateUTC  < end_dst):
            difference_cet_utc = timedelta(hours=2)
        else:
            difference_cet_utc = timedelta(hours=1)

        self.myDateCET = self.myDateUTC + difference_cet_utc
        pass

    def get_hoursCET(self) -> int:
        return self.myDateCET.hour

    def get_minutesCET(self) -> int:
        return self.myDateCET.minute

    def IsAfterThanOrEqual(self, otherTime )-> bool:
        """ Test if the date proposed is after Than (more modern than)

        Args:
            otherTime (MyDatetime): _description_

        Returns:
            bool: _description_
        """

        return self.myDateUTC >= otherTime.myDateUTC

    def IsOlderThan(self, otherTime )-> bool:
        """ Test if the date proposed is before Than (more older than)

        Args:
            otherTime (MyDatetime): _description_

        Returns:
            bool: _description_
        """

        return self.myDateUTC < otherTime.myDateUTC

    @property
    def get_IsoFormatUTC(self) -> str:
        return self.myDateUTC.strftime('%Y-%m-%dT%H:%M:%S.000+0000')
    @property
    def get_IsoFormatCET(self) -> str:
        return self.myDateCET.strftime('%Y-%m-%dT%H:%M:%S.000+0200')

    def __str__(self) -> str:
        """Convert Object to STRING
        Returns:
            str: Object Values in String.
        """
        return  self.myDateUTC.strftime('%Y-%m-%d %H:%M:%S') + '(UTC)'

    def getDate(self, timezone = TIMEZONE.UTC) -> datetime.datetime:
        """_summary_

        Args:
            timezone (TIMEZONE, optional): _description_. Defaults to TIMEZONE.UTC.

        Returns:
            _type_: _description_
        """
        returnDate = self.myDateUTC

        if ( timezone == TIMEZONE.CET ): returnDate = self.myDateCET

        return returnDate