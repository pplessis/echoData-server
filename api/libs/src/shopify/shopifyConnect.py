import requests
import json
import urllib3
import ssl
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from enum import Enum

from ..utils import Print
from .shopifyDB import ShopifyInfoId, ShopifyID, SH_ENTITY

from .shopifyInfo import SHOPIFY_API_VERSION

####
class SH_REST_URL (str, Enum):
   products         = 'https://{0}.myshopify.com/admin/api/{1}/products.json?limit=50'
   delProduct       = 'https://{0}.myshopify.com/admin/api/{1}/products/{2}.json'
   order            = 'https://{0}.myshopify.com/admin/api/{1}/orders.json?limit=50'

####
class ShopifyConnect:
    SHOPIFY_ADMIN_TOKEN_DEFAULT = 'NONE'
    SHOPIFY_CHECK_CERTIFICATE_DEFAULT = False
    #SHOPIFY_API_VERSION_DEFAULT  = '2024-07'#'2025-01'
    SHOPIFY_SHOP_NAME_DEFAULT = 'NONE'
    HTTP_TIMEOUT = 20
    SHOPIFY_GET_ALL_PRODUCTS = 'https://{0}.myshopify.com/admin/api/{1}/products.json?limit=50'
    SHOPIFY_CREATE_PRODUCTS = 'https://{0}.myshopify.com/admin/api/{1}/products.json'

    SHOPIFY_GET_HEADER = {
         "User-Agent": 'PostmanRuntime/7.36.0'
        , "Accept": '*/*'
        , "Accept-Encoding": 'gzip, deflate' #br =  Brotli library
        ,"Content-Type": 'application/json'
        ,"X-Shopify-Access-Token": '{0}'
    }

    def __init__(self, ShopName, AdminToken) -> None:
        self.shIds = list()
        self.sslVersion = ssl.PROTOCOL_TLSv1

        self.requestCertificate = self.SHOPIFY_CHECK_CERTIFICATE_DEFAULT
        self.apiVersion = SHOPIFY_API_VERSION

        self.shopName = ShopName
        if (len(ShopName)==0): self.shopName = self.SHOPIFY_SHOP_NAME_DEFAULT

        self.securityToken = AdminToken
        if (len(AdminToken)==0): self.AdminToken = self.SHOPIFY_ADMIN_TOKEN_DEFAULT

        ## Create a copy in the current object
        self.httpHeader = ShopifyConnect.SHOPIFY_GET_HEADER.copy()

        pass


    @property
    def getRequestHeader(self):
        returnValue = self.httpHeader
        # Apply current token
        returnValue['X-Shopify-Access-Token'] = returnValue['X-Shopify-Access-Token'].format(self.securityToken)

        return  returnValue

    @property
    def getUrlAllProduct(self):
        return  self.SHOPIFY_GET_ALL_PRODUCTS.format(self.shopName, self.apiVersion)

    @property
    def getUrlCreateProduct(self):
        return  self.SHOPIFY_CREATE_PRODUCTS.format(self.shopName, self.apiVersion)

    @property
    def getConnectionInfo (self) -> str:
        #TODO: Need to be implemented
        return ''

    ## get Product count
    def getProductCount (self) -> int:
        #  REST : https://{{ShopName}}.myshopify.com/admin/products/count.json
        countProducts = -1

        try:
            print ('Pierre')

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

        return countProducts
        pass

    ## get All Product
    def getAllProduct (self) -> ShopifyInfoId:
        """The code block is a REST request using Python's `requests` library to get all products from the Shopify API. The code starts by defining two constants: `SH_ENTITY` and `STATUS`. SH_ENTITY is used to determine which entity type we are fetching (e.g., product, variant). STATUS is used to indicate the status of a product in the Shopify platform.
Next, the function `getAllProduct()` is defined with a comment indicating that it is meant to extract all products from Shopify's boutique. The function takes no parameters and returns an instance of `ShopifyInfoId`, which contains the list of Shopify product IDs.
The function then opens a connection to the Shopify API using the `getUrlAllProduct` method, which returns a list of products from the given handle (e.g., 'shop'). The function then sets the headers to send with the request, including the `Authorization` header and the `requestCertificate` parameter if needed.
Next, the function checks whether the response status code is 200 (`result.status_code == 200`) to indicate that the request was successful. If so, the function extracts the list of products from the JSON response using `resultJson['products']`, then loops through each product and adds it to a global list called `resultProducts`.
The loop continues until all products are fetched or there is no more next link available (indicated by checking if `'next'` exists in the result links). If no more links are found, the function returns an instance of `ShopifyInfoId` with the updated list of product IDs. 
Finally, the function closes the connection to the Shopify API using the `close()` method and returns the instance of `ShopifyInfoId`.
See: https://shopify.dev/docs/api/admin-rest/2023-07/resources/product#resource-object

        Returns:
            ShopifyInfoId: _description_
        """
        resultProducts = []
        returnValues = ShopifyInfoId()

        try :
            # Open a connection to API Shopify
            result = requests.request('GET'
            , self.getUrlAllProduct
            , params=None
            , headers= self.getRequestHeader
            , data = None
            , verify= self.requestCertificate

            )
            # Check Result
            if (result.status_code == 200):
                resultJson = result.json()
                ## Add Items in global List
                for product in resultJson['products']:
                    resultProducts.append(product)

                # Loops on results
                while ( 'next' in result.links ):
                    linkUrl = result.links['next']['url']

                    result = requests.request('GET'
                        , linkUrl
                        , params=None
                        , headers= self.getRequestHeader
                        , data = None
                        , verify= self.requestCertificate
                        )

                    resultJson = result.json()

                    ## Add Items in global List
                    for product in resultJson['products']:
                        resultProducts.append(product)


        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

        finally:

            for resultProduct in resultProducts:
                #print(resultProduct)
                prdHandle = resultProduct['handle']

                for variant in resultProduct['variants']:
                    tmpValue = ShopifyID.from_product (
                                  resultProduct['id']
                                , variant ['sku']
                                , variant ['id']
                                , SH_ENTITY.PRODUCT
                                , Status = resultProduct['status']
                                , PriceWithTaxes = variant['price']
                    )

                    #TODO: Split TAGS
                    tmpTags = resultProduct['tags']
                    #tmpValue.tags = resultProduct['tags']
                    tags = tmpTags.split( ShopifyID.SHOPIFY_TAGS_SEPARATOR )
                    stripped_tags = [j.strip() for j in tags]
                    tmpValue.tags = stripped_tags

                    tmpValue.createDate = variant['created_at']
                    tmpValue.modificationDate = variant['updated_at']
                    if (len(prdHandle)> 0): tmpValue.handle = prdHandle

                    # define variant['compare_at_price']
                    if (variant['compare_at_price']!=None):
                        tmpValue.priceStandard = variant['compare_at_price']

                    returnValues.addValue(tmpValue)

            return returnValues

    def confirmSiteConnection (self, Env:str = 'test') -> bool:
        """This function can be used when connecting to a site where you want to confirm whether the 
        correct sandbox or test environment is being used before proceeding with the connection in 
        non-production environments.

        Args:
            Env (str, optional): _description_. Defaults to 'test'.

        Returns:
            bool: _description_
        """

        if Env.lower() != 'prod':
            Continue = Print.confirmExecution('Please check the sandbox is correct or/and Input file "' + self.shopName + '" ')

        else:
            print("/!\\ Is PROD Env")
            Continue = True

        return Continue

    def createProduct (self, JsonProduct) -> list:
        """Create a new PRODUCT in Shopify POST request (REST)
            See: https://shopify.dev/docs/api/admin-rest/2023-07/resources/product#post-products

        Args:
            JsonProduct (str): _description_

        Returns:
            str: _description_
        """
        returnValue = list()

        jsonTmp = '{"product": '+ JsonProduct  + '}'
        try :
            result = requests.request('POST'
            , self.getUrlCreateProduct
            , params=None
            , headers= self.getRequestHeader
            , data = jsonTmp
            , verify= self.requestCertificate
            )

                #print ('result.status_code : ', result.status_code )
            if(result.status_code == 201):

                tmpProductId = json.loads(result.text)['product']['id']
                tmpProductStatus = json.loads(result.text)['product']['status']
                tmpProductVariants = json.loads(result.text)['product']['variants']

                for tmpVariant in tmpProductVariants:
                    tmpItem = ShopifyID.from_product(
                            int(tmpProductId)
                        ,   tmpVariant ['sku']
                        ,   int(tmpVariant ['id'])
                        ,   SH_ENTITY.PRODUCT
                        ,   tmpProductStatus
                        ,   0.00)
                    returnValue.append(tmpItem)
            else:
                Print.error( '#{0}-{1}'.format( result.status_code, result.content ) )

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

        return returnValue

    def cleanProduct(self, ShIdProd:str)->int:
        """ Delete a PRODUCT
            SEE: https://shopify.dev/docs/api/admin-rest/2023-07/resources/product#delete-products-product-id
            curl -X DELETE "https://your-development-store.myshopify.com/admin/api/2023-07/products/632910392.json" \
            -H "X-Shopify-Access-Token: {access_token}"

        Returns:
            _type_: _description_
        """
        returnResult = -1
        requestHTTP = None
        endpoint = SH_REST_URL.delProduct.value
        urlEndpoint =  endpoint.format(self.shopName,
                                       self.apiVersion,
                                       ShIdProd)

        try :

            requestHTTP = requests.request('DELETE'
            , urlEndpoint
            , params=None
            , headers= self.getRequestHeader
            , data = None
            , verify= self.requestCertificate
            , timeout= ShopifyConnect.HTTP_TIMEOUT
            )

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

        if (requestHTTP!=None): returnResult = requestHTTP.status_code

        return returnResult


    def __extractInfoShopify (self, EndPoint: str) -> list:
        returnList = list()
        return returnList

        try :

            # Open a connexion to API Shopify
            result = requests.request('GET'
            , EndPoint
            , params=None
            , headers= self.getRequestHeader
            , data = None
            , verify= self.requestCertificate
            )

            # Check Result
            if (result.status_code == 200):
                resultJson = result.json()

                ## Add Items in global List
                for product in resultJson['products']:
                    resultProducts.append(product)

                # Loops on results
                while ( 'next' in result.links ):
                    linkUrl = result.links['next']['url']

                    result = requests.request('GET'
                        , linkUrl
                        , params=None
                        , headers= self.getRequestHeader
                        , data = None
                        , verify= self.requestCertificate
                        )

                    resultJson = result.json()

                    ## Add Items in global List
                    for product in resultJson['products']:
                        resultProducts.append(product)

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)

