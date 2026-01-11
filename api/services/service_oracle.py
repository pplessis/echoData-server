from ..models.dataClasses_Horoscope         import Sign, Horoscope, Horoscope20
from ..config                               import logger
from requests                               import get, RequestException
from typing                                 import List

# #####################################################################
class Service_Oracle:

    def __init__ (self, sign:Sign ):
        self.Sign:      Sign = sign
        self.Horoscope: Horoscope|None

# ---------------------------------------------------------------------
    @staticmethod
    def loadData ( sign:Sign, type ) -> Horoscope :
        retrun_dic = {}
        htmlText = ''
        url = type.urls[sign]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        try:
            # Envoi de la requête GET
            logger.info(f"GET Url: {url}")
            response = get(url, headers=headers, timeout=10) # timeout de 10s pour éviter de bloquer indéfiniment

            # Vérifie si la requête a réussi (code 200-299)
            response.raise_for_status()

            # Retourne le contenu textuel (HTML)
            htmlText = response.text
            logger.info( f"RESPONSE: #{response.status_code}| SIZE: {len(htmlText)} Bytes" )
            sections =  type.extractData(htmlText)
            logger.info( f"SECTIONS: #{len(sections)}" )

        except RequestException as e:
           raise e

        finally:
            #CREATE OBJECT
            return Horoscope.fromData( {'sign':sign, 'sections': sections })

