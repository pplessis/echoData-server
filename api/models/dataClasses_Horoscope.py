from enum import StrEnum
from requests import get, RequestException
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass

# ########################################################
class Sign(StrEnum):
    BELIER      = 'BELIER'
    TAUREAU     = 'TAUREAU'
    GEMEAUX     = 'GEMEAUX'
    CANCER      = 'CANCER'
    LION        = 'LION'
    VIERGE      = 'VIERGE'
    BALANCE     = 'BALANCE'
    SCORPION    = 'SCORPION'
    SAGITTAIRE  = 'SAGITTAIRE'
    CAPRICORNE  = 'CAPRICORNE'
    VERSEAU     = 'VERSEAU'
    POISSONS    = 'POISSONS'

# ########################################################
class Section(StrEnum):
    LOVE        = 'Love'
    MONEY       = 'Money'
    CARE        = 'Care'
    MOOD        = 'Mood'
    ADVICE      = 'Advice'

# ########################################################
@dataclass(slots=True)
class Horoscope:
    sign:       Sign|None
    date:       datetime
    sections:   dict|None

# -----------------------------------------------------
    @classmethod
    def fromData(cls, data: dict) -> "Horoscope":
        return cls(  sign=data.get('sign', None)
                   , date=datetime.today()
                   , sections=data.get('sections', None) )

# ------------------------------------------------------


# ########################################################
@dataclass(slots=True)
class Horoscope20(Horoscope):

    urls = {
     'BELIER'       :   'https://www.20minutes.fr/horoscope/horoscope-belier'
    ,'TAUREAU'      :   'https://www.20minutes.fr/horoscope/horoscope-taureau'
    ,'GEMEAUX'      :   'https://www.20minutes.fr/horoscope/horoscope-gemeaux'
    ,'CANCER'       :   'https://www.20minutes.fr/horoscope/horoscope-cancer'
    ,'LION'         :   'https://www.20minutes.fr/horoscope/horoscope-lion'
    ,'VIERGE'       :   'https://www.20minutes.fr/horoscope/horoscope-vierge'
    ,'BALANCE'      :   'https://www.20minutes.fr/horoscope/horoscope-balance'
    ,'SCORPION'     :   'https://www.20minutes.fr/horoscope/horoscope-scorpion'
    ,'SAGITTAIRE'   :   'https://www.20minutes.fr/horoscope/horoscope-sagittaire'
    ,'CAPRICORNE'   :   'https://www.20minutes.fr/horoscope/horoscope-capricorne'
    ,'VERSEAU'      :   'https://www.20minutes.fr/horoscope/horoscope-verseau'
    ,'POISSONS'     :   'https://www.20minutes.fr/horoscope/horoscope-poissons'
    }


# -----------------------------------------------------
    @staticmethod
    def extract_section(soup, mot_cle:str) -> str:
        # On cherche tous les h3 (ou h2) qui contiennent le mot clé
        titles = soup.find_all( ['h3', 'h2'], string=lambda text: text and mot_cle.lower() in text.lower() )

        for titre in titles:
            # METHODE 1 (Classique) : The paragraph follow the TITLE.
            paragraph = titre.find_next_sibling('p')
            if paragraph:
                return paragraph.get_text(strip=True)

            # METHODE 2 (Robuste) : Parfois le texte est dans le parent ou plus loin
            # On cherche le premier <p> qui suit l'élément titre dans tout le document
            paragraph_Next = titre.find_next('p')

            # Sécurité : on vérifie que ce paragraphe n'est pas trop loin (ex: footer)
            # On peut par exemple vérifier s'il contient beaucoup de texte
            if paragraph_Next and len(paragraph_Next.get_text(strip=True)) > 20:
                return paragraph_Next.get_text(strip=True)

        return '#N/A'
# -----------------------------------------------------
    @staticmethod
    def extractData (inputHTML:str) -> dict:
        # Dictionnaire pour stocker les résultats
        results = {}

        html_sections = {
                Section.LOVE      :   "Amour",
                Section.MONEY     :   "Argent",
                Section.CARE      :   "Santé",
                Section.MOOD      :   "Humeur",
                Section.ADVICE    :   "Conseil"
        }

        try:
            soup = BeautifulSoup(inputHTML, 'html.parser')

            # 1. Main TITLE (H1)
            main_title = soup.find('h1')
            if main_title:
                results['title'] = main_title.get_text(strip=True)

            # Récupération et affichage
            #print(f"--- {results.get('TITLE', 'Horoscope')} ---\n")

            for nom_section, key_world in html_sections.items():
                section = Horoscope20.extract_section( soup, key_world )

                #print(f"[{key_world}]")
                #print(f"{section}\n")

                results[nom_section] = {'title':key_world, 'value': section}

        except Exception as e:
            raise e

        finally:
            return results
