from dataclasses import dataclass
from datetime import datetime

from typing import List, ClassVar

# #######################################################
@dataclass(slots=True)
class EventDay:
    name:str
    date:datetime|None
    format:str              = "MM-DD"

    # New Fields
    description:str|None    = ''
    importance:int          = 0
    category:str|None       = ''

    CONVERT_DATE_FORMAT: ClassVar[dict] = { "MM-DD": "%m-%d", "YYYY-MM-DD": "%Y-%m-%d" }

# #######################################################

    @property
    def getDate (self) -> str:

        if self.date is not None:
            fmt = self.CONVERT_DATE_FORMAT.get(self.format, "%m-%d")
            return self.date.strftime(fmt)

        return ""
    
    def getDateFormated(self, format_type: str = "long") -> str:
        """
        Formate self.date en français sans dépendre de locale système.
        
        Args:
            format_type: "long", "short", "date-only"
        """
        if self.date is None:
            return ""
        
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        mois = ["janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        
        jour = jours[self.date.weekday()]
        mois_nom = mois[self.date.month - 1]
        
        if format_type == "long":
            return f"{jour} {self.date.day} {mois_nom} {self.date.year}"
        elif format_type == "short":
            return f"{self.date.day} {mois_nom} {self.date.year}"
        else:
            return self.date.strftime("%d/%m/%Y")


    @property
    def getName (self) -> str:
        return self.name


# #######################################################

    @classmethod
    def fromDict(cls, data: dict) -> "EventDay":
        """Convert a dictionary from JSON file to an InternationalDay instance.

        Args:
            data (dict): JSON data representing an day.

        Returns:
            InternationalDay: _description_
        """
        date_str = ''
        try:
            if len(data["date"]) < 6:
                currentYear = datetime.today().year.__str__()
                date_str = currentYear + '-' + data["date"]
                date_format = "%Y-%m-%d"
            else:
                date_str = data["date"]
                date_format = cls.dateFormat(data)

            date_obj = datetime.strptime(date_str, date_format)
            return cls( name=data["name"], date=date_obj, format=data.get("format", "MM-DD") )

        except ValueError as eValue :
            raise ValueError( eValue, f"DATA: {date_str}")

    @classmethod
    def dateFormat(cls, data: dict) -> str:
        fmt_key = data.get("format", None)
        if fmt_key in cls.CONVERT_DATE_FORMAT:
            return cls.CONVERT_DATE_FORMAT.get(fmt_key, "%Y-%m-%d")
        return "%Y-%m-%d"

    @classmethod
    def todayEvent(cls, jours: List["EventDay"], jour: str) -> List["EventDay"]:
        """ Trouve tous les événements du jour donné (format 'MM-DD')."""
        return [evt for evt in jours if evt.getDate == jour]

# #######################################################
