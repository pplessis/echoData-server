# importing os module for environment variables
import os
from dotenv import load_dotenv, dotenv_values
from enum import Enum, StrEnum

# LOAD ".env" File
values = dotenv_values()
#load_dotenv()

class CONNECTION_COUNTRY (StrEnum):
    ESP = 'ESP'
    FRA = 'FRA'

class CONNECTION_ENV (StrEnum):
    TEST = 'TEST'
    PROD = 'PROD'

# Centralized API version
SHOPIFY_API_VERSION = '2025-01'

# ###########################p
CONNECTION_INFO = {
    #SPAIN
        "ESP"  : {
    "TEST": {
                "SHOPIFY_SHOP_NAME"   :   values['TEST_ES_SHOPIFY_SHOP_NAME']
                ,"SHOPIFY_ADMIN_TOKEN" :  values['TEST_ES_SHOPIFY_ADMIN_TOKEN']
            }
    ,
    "PROD": {
                "SHOPIFY_SHOP_NAME"   :    values['PROD_ES_SHOPIFY_SHOP_NAME']
                ,"SHOPIFY_ADMIN_TOKEN" :   values['PROD_ES_SHOPIFY_ADMIN_TOKEN']
            }
    }

    # FRANCE
    ,   "FRA" : {
    "TEST": {
                "SHOPIFY_SHOP_NAME"   :     values['TEST_FR_SHOPIFY_SHOP_NAME']
                ,"SHOPIFY_ADMIN_TOKEN" :    values['TEST_FR_SHOPIFY_ADMIN_TOKEN']
            }
    ,
    "PROD": {
                "SHOPIFY_SHOP_NAME"   :     values['PROD_FR_SHOPIFY_SHOP_NAME']
                ,"SHOPIFY_ADMIN_TOKEN" :    values['PROD_FR_SHOPIFY_ADMIN_TOKEN']
            }
    }

    # ITALY
    ,   "ITA" : {
    "TEST": {
                "SHOPIFY_SHOP_NAME"   :     values['TEST_IT_SHOPIFY_SHOP_NAME']
                ,"SHOPIFY_ADMIN_TOKEN" :    values['TEST_IT_SHOPIFY_ADMIN_TOKEN']
            }
    ,
    "PROD": {
                "SHOPIFY_SHOP_NAME"   :     values['PROD_IT_SHOPIFY_SHOP_NAME']
                ,"SHOPIFY_ADMIN_TOKEN" :    values['PROD_IT_SHOPIFY_ADMIN_TOKEN']
            }
    }
}
# ################################

