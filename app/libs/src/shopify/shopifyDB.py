import datetime
import hashlib
import json
from enum import Enum

from ..utils import Io
from ..csv.csvFile import CsvFile

####
class SH_ENTITY (str, Enum):
    NONE        = 'UNKNOWN'
    PRODUCT     = 'PRODUCT'
    CUSTOMER    = 'CUSTOMER'
    METAOBJ     = 'METAOBJ'

####
class ShopifyID:
    DELIMITER = CsvFile.DELIMITER
    CSV_HEADER = 'MD5' + DELIMITER + 'SH_PRODUCT_ID' + DELIMITER + 'SH_VARIANT_ID' +  DELIMITER + 'STH_EXT_ID' + DELIMITER + 'STATUS' + DELIMITER + 'TYPE' + 'CREATED_DATE' + DELIMITER + 'MODIFICATION_DATE'
    SHOPIFY_TAGS_SEPARATOR = ','

    def __init__( self ) -> None:
        #Shopify HANDLE (URL)
        self.handle           = '#N/A'
        self.shId             = '000'

        self.shMd5              = ''
        self.entity             = SH_ENTITY.NONE
        self.status             = '#N/A'

        self.tags               = list()

        self.createDate         = '#N/A'
        self.modificationDate   = '#N/A'

        self.extendedValues     = object()

        # Info on SHOPIFY PRODUCT
        self.shIdProd       = -1
        self.shIdVariant    = -1
        self.priceWithTaxes = 0.00
        self.priceStandard  = None

        # Info STANHOME
        self.sthId          = ''

        # Info METAOBJECT
        self.type = ''

        pass

    @classmethod
    def from_entity(cls, Entity:SH_ENTITY):
        objReturn = cls()
        objReturn.entity          = Entity

        return objReturn

    @classmethod
    def from_product(cls, ShIdProd:int, SthId:str, ShIdVariant:int, Entity:SH_ENTITY, Status: str, PriceWithTaxes:float ):
        objReturn = cls()

        objReturn.entity           = Entity      # = SH_ENTITY.NONE
        objReturn.status           = Status      # = ''

        # Info on SHOPIFY PRODUCT
        objReturn.shId           = str(ShIdProd)
        objReturn.shIdProd       = ShIdProd
        objReturn.shIdVariant    = ShIdVariant       #  = -1
        objReturn.priceWithTaxes = PriceWithTaxes    # = 0.00

        # Info STANHOME
        objReturn.sthId          = SthId

        return objReturn

    def __str__(self) -> str:
        returnValue = 'SthId: {0} | ProductID {1} | VariantID: {2}'.format(self.sthId, self.shIdProd, self.shIdVariant)
        return returnValue

    @property
    def isDiscounted(self)->bool:
        returnValue = False

        if (self.priceStandard!=None
            and self.priceStandard > 0.00
            and self.priceStandard > self.priceWithTaxes ):
            returnValue = True

        return returnValue

    @property
    def getKey(self):
        return self.sthId

    @property
    def getValueProduct(self):
        return self.shIdProd

    @property
    def getValueVariant(self):
        return self.shIdVariant

    @property
    def md5(self)->str:
        returnValue = str( self.shIdProd ) + str( self.shIdVariant )
        returnValue =  hashlib.md5( returnValue.encode() ).hexdigest()
        return returnValue

    @property
    def getLowerTags (self) -> list:
        returnValues = list()
        for tag in self.tags:
            returnValues.append( tag.lower() )
        return returnValues

    @property
    def getGID (self) -> str:
        """Get the GID for the element

        Returns:
            str: GID
        """
        returnValue = ''
        prefix = 'gid://shopify/'

        if (self.entity == SH_ENTITY.NONE):
            returnValue = '{0}'.format(self.shId)

        if (self.entity == SH_ENTITY.METAOBJ):
            returnValue = '{0}'.format(self.shId)

        if (self.entity == SH_ENTITY.CUSTOMER):
            returnValue = prefix + 'Customer/{0}'.format(self.shId)

        if (self.entity == SH_ENTITY.PRODUCT):
            returnValue = prefix + 'Product/{0}'.format(self.shId)

        return returnValue

    def toJSON(self) -> str:
        returnValue = ''

        returnValue += json.dumps(self.shIdProd)
        returnValue += json.dumps(self.shIdVariant)
        returnValue += json.dumps(self.sthId)
        returnValue += json.dumps(self.entity)

        return  returnValue

    def toCsv (self) -> str:
        returnValue = ''

        # Build the CSV Line
        returnValue += str(self.md5)         + self.DELIMITER
        returnValue += str(self.shIdProd)    + self.DELIMITER
        returnValue += str(self.shIdVariant) + self.DELIMITER
        returnValue += self.sthId            + self.DELIMITER

        returnValue += self.status           + self.DELIMITER

        if (self.entity == SH_ENTITY.NONE ): returnValue        +=  'UNKNOWN'   + self.DELIMITER
        if (self.entity == SH_ENTITY.PRODUCT): returnValue      +=  'PRODUCT'   + self.DELIMITER
        if (self.entity == SH_ENTITY.CUSTOMER ): returnValue    +=  'CUSTOMER'  + self.DELIMITER
        if (self.entity == SH_ENTITY.METAOBJ): returnValue      +=  'METAOBJ'   + self.DELIMITER

        returnValue += self.createDate
        returnValue += self.modificationDate

        return returnValue

###
def ShopifyIDToStr (AShopifyIDList:list) -> str:
    """_summary_

    Args:
        AShopifyIDList (list): _description_

    Returns:
        str: _description_
    """
    productID  = ''
    variants = ''
    status = ''

    for item in AShopifyIDList:
        productID = item.shIdProd
        status = item.status
        variants += '[{0}|{1}]'.format(item.sthId, item.shIdVariant)

    return '{0} ({1}) - {2}'.format(productID, status, variants)

####
class ShopifyInfoId ():
    def __init__(self) -> None:
        self.index = -1
        self.listDataFromShopify = list()

        pass

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if (self.index == len(self.listDataFromShopify)):
            raise StopIteration
        return self.listDataFromShopify [self.index]

    def __str__(self) -> str:

        returnValue = '# All: {0}'.format(self.countData)
        returnValue += '\n# NONE: {0}'.format(self.countDataType (SH_ENTITY.NONE) )
        returnValue += '\n# PRODUCT: {0}'.format(self.countDataType (SH_ENTITY.PRODUCT) )
        returnValue += '\n# CUSTOMER: {0}'.format(self.countDataType (SH_ENTITY.CUSTOMER) )
        returnValue += '\n# META_OBJECT: {0}'.format(self.countDataType (SH_ENTITY.METAOBJ) )

        return returnValue

    @property
    def getAllTags (self) -> list:
        returnList = list()

        for item in self.listDataFromShopify:
            tags = item.tags
            for tag in tags:
                # Add a Check is already exist in the list.
                if (not(tag in returnList)):
                    returnList.append(tag)

        return returnList


    @property
    def countData(self) -> int:
        returnValue = len (self.listDataFromShopify)
        return returnValue

    def addItem (self, newItem:ShopifyID) -> bool:
        self.listDataFromShopify.append(newItem)
        return True


    def exist(self, SthId:str, Type = SH_ENTITY.NONE) -> bool:
        """_summary_

        Args:
            Value (str): _description_
            Type (SH_ENTITY, optional): Type RECORD TYPE in the search. Defaults to SH_ENTITY.NONE.

        Returns:
            bool: If the value Exist return TRUE
        """
        returnValue = False

        for item in self.listDataFromShopify:
            if ( item.sthId == SthId
                and item.entity == Type ):
                returnValue = True

                break

        return returnValue

    def getListInfo ( self, Entity:SH_ENTITY ) -> list :
        returnValues = list ()

        for item in self.listDataFromShopify:
            if (item.entity == Entity):
                returnValues.append(item)

        return returnValues

    def getShopifyInfo (self, SthId:str , Type = SH_ENTITY.NONE):
        returnValue = None

        for item in self.listDataFromShopify:
            if ( item.sthId == SthId
                and item.entity == Type ):
                returnValue = item
                break

        return returnValue

    def getShopifyProductId (self, Value, Type = SH_ENTITY.NONE) -> int:
        """Return Shopify Product ID

        Args:
            Value (_type_): _description_
            Type (_type_, optional): _description_. Defaults to SH_ENTITY.NONE.

        Returns:
            int: _description_
        """
        returnValue = -1

        for item in self.listDataFromShopify:
            if ( item.sthId == Value
                and item.entity == Type ):
                returnValue = item.shIdProd

                break

        return returnValue

    def countDataType(self, Type = SH_ENTITY.NONE):
        index = 0
        for element in self.listDataFromShopify:
            if (element.entity == Type ):
                index += 1

        return index

    def addValue (self, newValue:ShopifyID) -> None:
        """_summary_

        Args:
            newValue (ShopifyID): _description_

        Returns:
            None: _description_
        """
        self.listDataFromShopify.append(newValue)
        return None

    def toJSON(self, BackupToFile:bool = False, SiteName:str = 'None' , BackupFolder:str = 'json'):
        jsonText  =  ''

    #    #for item in self.listDataFromShopify:
    #    #    jsonText += item.toJSON()

        #TODO: Correct BUG "AttributeError: 'object' object has no attribute '__dict__'. Did you mean: '__dir__'?"
        #jsonText  = json.dumps(self, default = lambda o: o.__dict__, sort_keys=True)
        jsonText  = json.dumps(self.listDataFromShopify)

        if ( BackupToFile and len(jsonText)>0 ):
            # Save the JSON to a file
            now = datetime.datetime.now()
            nowStr = now.strftime('%Y%m%d%H%M%S')
            filename = '{0}_{1}_{2}.json'.format( nowStr, 'shopifyDB', SiteName )
            Io.saveTxtFile( BackupFolder , filename, jsonText)

        return jsonText


    @classmethod
    def fromJSON(cls, Json_string):
        data = json.loads (Json_string)

        instance = cls()
        instance.index = data.get('index', -1)
        #instance.listDataFromShopify = data.get('listDataFromShopify', [])
        listShopifyEntities = data.get('listDataFromShopify', [])
        for item in listShopifyEntities:
            newItem = ShopifyID()

            # Info on SHOPIFY for ALL
            newItem.handle           = item.get( 'handle'           ,'#N/A')
            newItem.shId             = item.get( 'shId'             ,'')
            newItem.shMd5            = item.get( 'shMd5'            ,'')
            newItem.entity           = item.get( 'entity'           , SH_ENTITY.NONE)
            newItem.status           = item.get( 'status'           ,'#N/A')
            newItem.tags             = item.get( 'tags'             , [])
            newItem.createDate       = item.get( 'createDate'       ,'#N/A')
            newItem.modificationDate = item.get( 'modificationDate' ,'#N/A')

            # Info on SHOPIFY PRODUCTS & VARIANTS
            newItem.shIdProd       = item.get( 'modificationDate' ,-1)
            newItem.shIdVariant    = item.get( 'modificationDate' ,-1)
            newItem.priceWithTaxes = item.get( 'modificationDate' , 0.00)
            newItem.priceStandard  = item.get( 'modificationDate' , None )

            # Info STANHOME
            newItem.sthId          = item.get( 'sthId'           ,'')

            # Info METAOBJECT
            newItem.type           = item.get( 'type'           ,'')

            instance.listDataFromShopify.append(newItem)

        return instance


    def toCSV (self, outputFile:str)-> None:
        return None
