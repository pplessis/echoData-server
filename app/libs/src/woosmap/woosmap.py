## See More : https://developers.woosmap.com/products/address-api/geocode/#woosmap_http_address_geocode_collection-txt

import requests
import datetime
import json
from enum import Enum
from datetime import date

# ##################################
class GEO_QUALITY (int, Enum):
    ROOFTOP             = 0	    #result is a precise geocode for which we have location information accurate down to street address precision.
    RANGE_INTERPOLATED  = 20	#result reflects an approximation (usually on a road) interpolated between two precise points (such as intersections). Interpolated results are generally returned when rooftop geo codes are unavailable for a street address.
    GEOMETRIC_CENTER    = 50	#result is the geometric center of a result such as a polyline (for example, a street) or polygon (city, region, …).
    APPROXIMATE         = 80	#result is approximate (usually when no other above value applies)
    NONE                = 100
# ##################################
class GEO_STATUS (int, Enum):
    OK	              = 0  #indicates the response contains a valid result.
    INVALID_REQUEST	  = 2  #indicates that the provided request was invalid (e.g. wrong URL syntax).
    REQUEST_DENIED	  = 3  #indicates that the service denied use of the Address API (e.g. wrong API Key, wrong/no referer, …).
    UNKNOWN_ERROR	  = 5  #indicates an Address API request could not be processed due to a server error. The request may succeed if you try again.
    NONE              = 10

# ##################################
class WoosmapMetaData:
    def __init__(self) -> None:
        self.initAddress = None
        self.resultDate = date.today()

        pass

    @property
    def convertJson(self) -> str:
        return json.dumps(self)


class Woosmap:

    ADDRESS_FORMAT_WITH_STATE = '{0}, {1} {2}, {3} {4}'
    ADDRESS_FORMAT_WITHOUT_STATE = '{0}, {1} {2}, {4}'

    WOOSMAP_KEY = 'woos-3917e89c-7e41-37d5-829a-6710bfedfb61'
    WOOSMAP_REF = 'http://dev.preprod.stanhome.com'

    WOOSMAP_URL = 'https://api.woosmap.com/address/geocode/json?'
    WOOSMAP_GET_PARAMETES = {
         "address": None
        ,"components": None
        ,"limit": 1
        ,"key": WOOSMAP_KEY
    }

    MAP_URL_LAT_LOG = 'https://maps.google.com/?q={0},{1}'

    def __init__ (self):

        self.sfId = None
        self.sthId = None
        self.name = None
        self.comment = None

        self.street = ''
        self.postalCode = ''
        self.city = ''
        self.province = ''
        self.country = ''

        self.metadata = None
        self.geoStatus = 0
        self.geoCodingDone = False
        self.geoType = None
        
        # Formated Addeds
        self.geoFormattedAddress = None
        
        #Geo
        # {'location_type': 'GEOMETRIC_CENTER', 'location': {'lat': 47.82019, 'lng': -2.93714}, 'viewport': {'northeast': {...}, 'southwest': {...}}}
        self.geoGeometry = None
        
        #Components
        # #[{'types': [...], 'long_name': 'France', 'short_name': 'FRA'}, {'types': [...], 'long_name': 'Brittany', 'short_name': 'BRE'}, {'types': [...], 'long_name': 'Morbihan', 'short_name': 'Morbihan'}, {'long_name': 'Pluvigner', 'short_name': 'Pluvigner', 'types': [...]}, {'long_name': 'Kerlagadec', 'short_name': 'Kerlagadec', 'types': [...]}, {'long_name': '56330', 'short_name': '56330', 'types': [...]}]
        self.geoAddressComponents = []

        self.checkCertificate = False
        
        self.components = 'country:FRA'

    def __iter__(self):
        returnValues = []
        
        if (self.geoCodingDone == True):
            if (self.geoGeometry != None):
                # Geo Coding with Response
                returnValues = [
              self.sthId
            , self.sfId
            , self.name
            , self.completeAddress
            , self.postalCode
            , self.geoFormattedAddress
            , self.geoPostalCode
            , self.geoQuality
            , self.geoGeometry
            , self.geoAddressComponents
            , self.geoError
            , ''
            , self.geoUrl
            , self.lat
            , self.lng]
            
            else:
                # Geo Coding without Response
                returnValues = [
              self.sthId
            , self.sfId
            , self.name
            , self.completeAddress
            , self.postalCode
            , ''
            , ''
            , self.geoQuality
            , ''
            , ''
            , self.geoError
            , 'N/A'
            , 'N/A'
            , 'N/A'
            , 'N/A']
        else:
            # Geo Coding Not DONE
            returnValues = [
              self.sthId
            , self.sfId
            , self.name
            , self.completeAddress
            , self.postalCode
            , ''
            , ''
            , ''
            , ''
            , ''
            , self.geoError
            , 'N/A'
            , 'N/A'
            , 'N/A'
            , 'N/A']
        
        return iter(returnValues)

    def __str__(self) -> str:
        
        formatSth = 'STH_ID: {0}' + '|ID: {1}'  +'|NAME: {2}' +'|ADDRESS: {3}'  +'|POSTAL_CODE: {4}' + '\n###\n'  +'GEO_ADDRESS: {5}'  +'|GEO_POSTAL_CODE: {6}'  +'|GEO_QUALITY: {7}' + '\n###\n' +'CHECK_ERROR: {8}' +'|CHECK_POSTAL_CODE: {9}'  +'|CHECK_MAP_URL: {10}'

        return formatSth.format(
              self.sthId
            , self.sfId
            , self.name
            , self.completeAddress
            , self.postalCode
            , self.geoFormattedAddress
            , self.geoPostalCode
            , self.geoQuality
            , self.geoError
            , ''
            , self.geoUrl)

    @property
    def csvHeader (self):
        return ([
             'STH_ID'
            ,'ID'
            ,'NAME'
            ,'ADDRESS'
            ,'POSTAL_CODE'
            ,'GEO_ADDRESS'
            ,'GEO_POSTAL_CODE'
            ,'GEO_QUALITY'
            ,'GEO_JSON_CORDONATES'
            ,'GEO_JSON_ADDRESS'
            ,'CHECK_ERROR'
            ,'CHECK_POSTAL_CODE'
            ,'CHECK_MAP_URL'
            ,'LAT'
            ,'LNG'
        ])


    @property
    def geoQuality(self):
        returnValue = GEO_QUALITY.NONE
        if (self.geoCodingDone==True and self.geoGeometry != None ):
            if (self.geoGeometry['location_type'] == 'ROOFTOP'): returnValue = GEO_QUALITY.ROOFTOP
            if (self.geoGeometry['location_type'] == 'RANGE_INTERPOLATED'): returnValue = GEO_QUALITY.RANGE_INTERPOLATED
            if (self.geoGeometry['location_type'] == 'GEOMETRIC_CENTER'): returnValue = GEO_QUALITY.GEOMETRIC_CENTER
            if (self.geoGeometry['location_type'] == 'APPROXIMATE'): returnValue = GEO_QUALITY.APPROXIMATE

        return returnValue

    @property
    def geoError(self):
        returnValue = 100
        geoLevel = self.geoQuality
        
        if (geoLevel == GEO_QUALITY.ROOFTOP): returnValue = 0
        if (geoLevel == GEO_QUALITY.RANGE_INTERPOLATED): returnValue = 20
        if (geoLevel == GEO_QUALITY.GEOMETRIC_CENTER): returnValue = 50
        if (geoLevel == GEO_QUALITY.APPROXIMATE): returnValue = 80
        
        return returnValue

    @property
    def geoPostalCode(self) -> str:
        returnValue = ''
        
        jsonComplement =  self.geoAddressComponents
        
        for value in jsonComplement:
           if ( value['types'][0] == 'postal_code'): 
                returnValue = value.get('long_name')
                break
        
        return returnValue

    @property
    def geoUrl(self):
        lat = 0.0
        lng = 0.0

        if (self.geoCodingDone==True and self.geoGeometry != None ):
            lat = self.geoGeometry['location']['lat']
            lng = self.geoGeometry['location']['lng']
        
        return Woosmap.MAP_URL_LAT_LOG.format(lat, lng)

    @property
    def completeAddress(self):
        currentFormat = Woosmap.ADDRESS_FORMAT_WITHOUT_STATE
        if (self.province != None): currentFormat = Woosmap.ADDRESS_FORMAT_WITH_STATE

        returnValue = currentFormat.format(  self.street
                                            ,self.postalCode
                                            ,self.city
                                            ,self.province
                                            ,self.country)

        return returnValue
    @property
    def lat(self) -> float:
        returnValue = -0.00
        if (self.geoCodingDone==True and self.geoGeometry != None ):
            returnValue = self.geoGeometry['location']['lat']

        return returnValue

    @property
    def lng(self) -> float:
        returnValue = -0.00
        if (self.geoCodingDone==True and self.geoGeometry != None ):
            returnValue = self.geoGeometry['location']['lng']

        return returnValue

    def launchGeoCoding(self) -> int:
        headers = {
            'Referer' : Woosmap.WOOSMAP_REF
        }
        payload = {}

        params = Woosmap.WOOSMAP_GET_PARAMETES
        
        params['address'] = self.completeAddress
        params['components'] = self.components
        
        try:
            # Create and Push HTTP Request for Woosmap API
            woosmapResponse = requests.request( "GET"
                                            , Woosmap.WOOSMAP_URL
                                            , params=params
                                            , headers=headers
                                            , data=payload
                                            , verify=self.checkCertificate)

            # Saved Results
            self.geoStatus = woosmapResponse.status_code
            self.geoCodingDone = True

            if (self.geoStatus == 200):
                jsonWoosmapResults = woosmapResponse.json()['results']
                if ( len ( jsonWoosmapResults ) != 1 ): return 0

                jsonWoosmapResult = jsonWoosmapResults[0]

                self.geoType = jsonWoosmapResult['types']
                self.geoFormattedAddress  = jsonWoosmapResult['formatted_address']
                self.geoGeometry = jsonWoosmapResult['geometry']
                self.geoAddressComponents = jsonWoosmapResult['address_components']

                currentMetadata = WoosmapMetaData()
                currentMetadata.initAddress = self.completeAddress
                
                self.metadata = currentMetadata
        
        except requests.exceptions.ConnectionError:
            self.geoCodingDone = False

