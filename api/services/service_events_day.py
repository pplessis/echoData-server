from pathlib                                import Path
from datetime                               import datetime, date
import calendar
import json
from typing                                 import List

from ..models.dataClasses_EventDay          import EventDay
from ..config                               import logger

class service_events_day:
    def __init__(self, fileJson: str | Path ) -> None:

        self.jsonDB:List[EventDay] = self._load_events_from_file(fileJson)

        # store loaded events on the instance for reuse in other methods
        self.events:List[EventDay] = []

# #######################################################
    def _load_events_from_file(self, fileJson: str | Path) -> list [EventDay]:
        path = Path(fileJson)
        allEvents = service_events_day.loadJsonEvents(path)
        return allEvents

# #######################################################
    def _filter_events_by_date(self,  startDate: datetime|None , endDate: datetime) -> list:
        """ This method filter events between two dates and exclude Others events.

        Args:
            startDate (datetime | None): _description_
            endDate (datetime): _description_

        Returns:
            list[EventDay]: _description_
        """
        events = self.jsonDB or []

        # normalize start/end
        if startDate is not None and startDate > endDate:
            startDate, endDate = endDate, startDate

        filtered: list[EventDay] = []

        # normalize start/end and compare only date portion (year, month, day)
        if startDate is not None and isinstance(startDate, datetime):
            start_date_only = startDate.date()
        else:
            start_date_only = None

        end_date_only = endDate.date() if isinstance(endDate, datetime) else endDate

        for evt in events:
            evt_dt = getattr(evt, "date", None)
            if not evt_dt:
                continue

            # support both datetime and date on stored events
            if isinstance(evt_dt, datetime):
                evt_date_only = evt_dt.date()
            else:
                evt_date_only = evt_dt

            # if start is provided, require evt_date between start and end inclusive
            if start_date_only is not None:
                if evt_date_only < start_date_only or evt_date_only > end_date_only:
                    continue
            else:
                # only end bound provided: include events on or before end_date_only
                if evt_date_only > end_date_only:
                    continue

            filtered.append(evt)

        # sort by date ascending
        filtered.sort(key=lambda e: e.date or datetime.max)

        return filtered

# #######################################################
    def get_events_by_date(self, date: str) -> list[EventDay]:

        dateNeeded = datetime.strptime(date, "%Y-%m-%d")
        self.events = self._filter_events_by_date(dateNeeded, dateNeeded)

        return self.events

# #######################################################
    def get_events_current_month(self) -> list[EventDay] :
        today = datetime.today()

        # Month START
        start_month = today.replace(day=1)

        # Month END
        last_day_num = calendar.monthrange(today.year, today.month)[1]
        end_month = today.replace(day=last_day_num)

        self.events = self._filter_events_by_date(start_month, end_month)

        logger.info( f"Events Filtered: {len(self.events)}" )

        return self.events

# #######################################################
    def get_events_today(self) -> list:
        #dateTmp = datetime( dateTmp.year, dateTmp.month, dateTmp.day, 0, 0 )
        today = datetime.today()

        logger.info( f"Date: {today}" )
        self.events = self._filter_events_by_date(today, today)
        logger.info( f"Events Filtered: {len(self.events)}" )

        return self.events

# #######################################################
    def get_is_day_off_today(self) -> bool:
        return False

# #######################################################
    def get_events_Off(self) -> list[EventDay]:
        return []


# #######################################################
    @staticmethod
    def loadJsonEvents (jsonFile: str | Path) -> List[EventDay]:
        path = Path(jsonFile)

        if not path.exists():
            logger.error (f"❌ File {jsonFile} not found.")
            raise FileNotFoundError(f"File not found.")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data_list = json.load(f)

            days = [EventDay.fromDict(data) for data in data_list]

            logger.info (f"✅ {len(days)} EVENTS Loaded")

            return days

        except json.JSONDecodeError as e:
            logger.error (f"❌ Error JSON: {e}")
            raise e

        except Exception as e:
            logger.error (f"❌ Error: {e}")
            raise e
