import requests
from os import environ

class Sfdc :
    UPDATE_DATA = True
    DEBUG = False
    MAX_DATA_LINKED = 5

    SF_VERSION = 'v58.0'

    SF_URLs = {
        'tooling'               :       '/services/data/'+ SF_VERSION +'/tooling'
        ,'metadata'             :       '/services/data/'+ SF_VERSION +'/metadata'
        ,'eclair'               :       '/services/data/'+ SF_VERSION +'/eclair'
        ,'folders'              :       '/services/data/'+ SF_VERSION +'/folders'
        ,'prechatForms'         :       '/services/data/'+ SF_VERSION +'/prechatForms'
        ,'contact-tracing'      :       '/services/data/'+ SF_VERSION +'/contact-tracing'
        ,'jsonxform'            :       '/services/data/'+ SF_VERSION +'/jsonxform'
        ,'chatter'              :       '/services/data/'+ SF_VERSION +'/chatter'
        ,'payments'             :       '/services/data/'+ SF_VERSION +'/payments'
        ,'tabs'                 :       '/services/data/'+ SF_VERSION +'/tabs'
        ,'appMenu'              :       '/services/data/'+ SF_VERSION +'/appMenu'
        ,'quickActions'         :       '/services/data/'+ SF_VERSION +'/quickActions'
        ,'queryAll'             :       '/services/data/'+ SF_VERSION +'/queryAll'
        ,'commerce'             :       '/services/data/'+ SF_VERSION +'/commerce'
        ,'wave'                 :       '/services/data/'+ SF_VERSION +'/wave'
        ,'iot'                  :       '/services/data/'+ SF_VERSION +'/iot'
        ,'analytics'            :       '/services/data/'+ SF_VERSION +'/analytics'
        ,'search'               :       '/services/data/'+ SF_VERSION +'/search [SAMPLE]'
        ,'smartdatadiscovery'   :       '/services/data/'+ SF_VERSION +'/smartdatadiscovery'
        ,'identity'             :       '/id/00DD0000000rV9gMAE/005D00000027abaIAA'
        ,'composite'            :       '/services/data/'+ SF_VERSION +'/composite'
        ,'parameterizedSearch'  :       '/services/data/'+ SF_VERSION +'/parameterizedSearch'
        ,'fingerprint'          :       '/services/data/'+ SF_VERSION +'/fingerprint'
        ,'theme'                :       '/services/data/'+ SF_VERSION +'/theme'
        ,'nouns'                :       '/services/data/'+ SF_VERSION +'/nouns'
        ,'domino'               :       '/services/data/'+ SF_VERSION +'/domino'
        ,'event'                :       '/services/data/'+ SF_VERSION +'/event'
        ,'serviceTemplates'     :       '/services/data/'+ SF_VERSION +'/serviceTemplates'
        ,'recent'               :       '/services/data/'+ SF_VERSION +'/recent'
        ,'connect'              :       '/services/data/'+ SF_VERSION +'/connect'
        ,'licensing'            :       '/services/data/'+ SF_VERSION +'/licensing'
        ,'limits'               :       '/services/data/'+ SF_VERSION +'/limits'
        ,'process'              :       '/services/data/'+ SF_VERSION +'/process'
        ,'dedupe'               :       '/services/data/'+ SF_VERSION +'/dedupe'
        ,'async-queries'        :       '/services/data/'+ SF_VERSION +'/async-queries'
        ,'query'                :       '/services/data/'+ SF_VERSION +'/query'
        ,'jobs'                 :       '/services/data/'+ SF_VERSION +'/jobs'
        ,'ai'                   :       '/services/data/'+ SF_VERSION +'/ai'
        ,'localizedvalue'       :       '/services/data/'+ SF_VERSION +'/localizedvalue'
        ,'mobile'               :       '/services/data/'+ SF_VERSION +'/mobile'
        ,'emailConnect'         :       '/services/data/'+ SF_VERSION +'/emailConnect'
        ,'consent'              :       '/services/data/'+ SF_VERSION +'/consent'
        ,'tokenizer'            :       '/services/data/'+ SF_VERSION +'/tokenizer'
        ,'compactLayouts'       :       '/services/data/'+ SF_VERSION +'/compactLayouts'
        ,'knowledgeManagement'  :       '/services/data/'+ SF_VERSION +'/knowledgeManagement'
        ,'sobjects'             :       '/services/data/'+ SF_VERSION +'/sobjects'
        ,'actions'              :       '/services/data/'+ SF_VERSION +'/actions'
        ,'support'              :       '/services/data/'+ SF_VERSION +'/support'
    }

    def __init__(self, grant_type:str, client_id:str, client_secret:str, username:str, password:str, env:str='prod', byPassCertif:bool=True):
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.url = ''
        self.checkCertificate = byPassCertif

        #Check YRG domain
        if ('OS' in environ and environ['OS'] == 'Windows_NT'):
            if (environ['userdomain'] == 'YRG'):
                self.checkCertificate = False

        #print("------ENV------:", env)
        #print("------CERT------:", self.checkCertificate)

        if (env != 'prod'):
            self.url = 'https://{0}.salesforce.com/services/oauth2/token'.format ('test')
        else:
            self.url = 'https://{0}.salesforce.com/services/oauth2/token'.format ('login')

        params = {
        "grant_type": self.grant_type,
        "client_id": self.client_id, # Consumer Key
        "client_secret": self.client_secret, # Consumer Secret
        "username": self.username, # The email you use to login
        "password": self.password # Concat your password and your security token
        }

        #print("------URL------:", self.url)
        #print("------USERNAME------:", self.username)
        #print("------CLIENT-ID------:", self.client_id)

        r = requests.post(self.url, params=params, verify=self.checkCertificate)
        # if you connect to a Sandbox, use test.salesforce.com instead
        access_token = r.json().get("access_token")
        instance_url = r.json().get("instance_url")
        #print("------Access Token------:", access_token)
        #print("------Instance URL------:", instance_url)

        self.access_token = access_token
        self.instance_url = instance_url

    # ############################
    def sf_api_call(self, action, parameters = {}, method = 'get', data = {}, debug=False, timeout=30) -> dict:
        """Call A Salesforce API

        Args:
            action (_type_): _description_
            parameters (dict, optional): _description_. Defaults to {}.
            method (str, optional): _description_. Defaults to 'get'.
            data (dict, optional): _description_. Defaults to {}.
            debug (bool, optional): _description_. Defaults to False.
            timeout (int, optional): _description_. Defaults to 30.

        Raises:
            ValueError: _description_
            Exception: _description_

        Returns:
            dict: _description_
        """

        statusCode = 'false'
        r = requests.Response()

        access_token = self.access_token
        instance_url = self.instance_url

        headers = {
            'Content-type': 'application/json',
            'Accept-Encoding': 'gzip',
            'Authorization': 'Bearer %s' % access_token
        }

        if method == 'get':
            r = requests.request(method, instance_url+action, headers=headers, params=parameters, timeout=timeout, verify=self.checkCertificate)

        elif method in ['post', 'patch']:
            if (Sfdc.UPDATE_DATA):
                r = requests.request(method, instance_url+action, headers=headers, json=data, params=parameters, timeout=timeout, verify=self.checkCertificate)

        else:
            if method == 'delete':
                if (Sfdc.UPDATE_DATA):
                    r = requests.request(method, instance_url+action, headers=headers, params=parameters, timeout=timeout, verify=self.checkCertificate)

            else:
                # other methods not implemented in this example
                raise ValueError('Method should be get or post or patch.')

        if (r!=None and r.status_code < 300):
            if method=='patch':
                    if (r.status_code == 204): statusCode='True'
                    return {'result' : statusCode}
            else:
                if (method == 'delete'):
                    if (r.status_code == 204): statusCode='True'
                    return {'result' : statusCode}
                else:
                    return r.json()
        else:
            raise Exception('API error when calling %s : %s' % (r.url, r.content))

        return

    # ############################
    def getSfdcQuery (self,
         query):
        """_summary_

        Args:
            query (str): _description_

        Raises:
            ValueError: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        call = { }
        sfdcUrlSql = Sfdc.SF_URLs['query']

        call = self.sf_api_call(sfdcUrlSql, {'q': query}, timeout=500)

        # First Extract (Data part)
        rows = call.get('records', [])
        next = call.get('nextRecordsUrl', None)

        while next:
            call = self.sf_api_call(next, timeout=500)
            rows.extend(call.get('records', []))
            next = call.get('nextRecordsUrl', None)

        return rows

    # ############################
    def GetJobsToSF(self, action, debug=False):
        """
        Helper function to make calls to Salesforce REST API.
        Parameters: action (the URL), URL params, method (get, post or patch), data for POST/PATCH.
        """
        #print (self.access_token)

        next = None
        call = requests.Response()
        rows = []

        call = self.sf_api_call(action=action, debug=debug)
        rows = call.get('records', [])

        next = call.get('nextRecordsUrl', None)

        while (next):
            call = self.sf_api_call(next, timeout=500)
            rows.extend(call.get('records', []))
            next = call.get('nextRecordsUrl', None)

        return rows

    # ##########################################
    def getSfdcObjectDescription(self, sfdcObjectName: str, securityParams: dict) -> list:
        """Get the list of fields available for a Salesforce object.

        Args:
            sfdcObjectName (str): Name of the Salesforce object (e.g. 'Account', 'Contact')
            securityParams (dict, optional): Security parameters. Defaults to None.

        Raises:
            Exception: If the object is not queryable
            Exception: If the API call fails

        Returns:
            list: List of field names available for the object
        """
        if securityParams is None:
            securityParams = {}

        describe = self.sf_api_call(
            Sfdc.SF_URLs['sobjects'] + f'/{sfdcObjectName}/describe'
        )

        if not describe:
            raise Exception(f"Failed to get description for object {sfdcObjectName}")

        if not describe.get('queryable', False):
            raise Exception(f"This object ({sfdcObjectName}) is not queryable")

        fields = [f['name'] for f in describe.get('fields', [])]
        return fields
    # ##########################################
    def updateSfdcRecord (self,
            sfdcObjectName, sfdcRecordId, dataToUpdate,
            securityParams={} ):
        global UPDATE_DATA
        status = None

        #path = "test.png"
        #    with open(path, "rb") as f:
        #    encoded_string = base64.b64encode(f.read())

        #data={
        #    'Title': 'An image',
        #    'PathOnClient': path,
        #    'VersionData': encoded_string,

        if (Sfdc.UPDATE_DATA):
            status  = self.sf_api_call(Sfdc.SF_URLs['sobjects'] + '/{0}/{1}/'.format(sfdcObjectName, sfdcRecordId), method="patch", data=dataToUpdate, timeout=50 )
        else:
            print('[DATA] Update is disabled - ERROR')

        return status


    # ############################
    @staticmethod
    def getContextValue ( contextFile, key ):
        """Read the file .property and return a setup information

        Args:
            contextFile (Str): Path and Filename of the context file.
            key (Str): Name of the key

        Returns:
            Str: Value read in the config file
        """

        output = ''
        # ERRORS Management‹
        assert len(contextFile) > 0 , "ContextFile can't empty!"
        assert len(key) > 0 , "Key can't empty!"
        #Open Context File
        fileContext = open(contextFile, "r")
        try:
            searchLines = fileContext.readlines()
            for i, line in enumerate(searchLines):
                if not("#" in line):
                    if (key +'=') in line:
                        # NOTA: Add splint after the '=' ?
                        output = line.split('=',1)[1]
        finally:
            fileContext.close()

        return output.rstrip('\n')

    # ############################
    @staticmethod
    def query_creatorById (
        fieldsList, objectName,
        id=None, otherId={}, limit=1 ):
        # Create a query based on the SFDC Id (PK) or Others with OtherId (FK).

        #sqlFieldSeparator = ','
        sqlQuery = "SELECT {0} FROM {1} WHERE "
        sqlWhereId = " Id='{0}'"
        sqlLimit = " LIMIT {0}"

        sqlQueryReturn = sqlQuery.format(fieldsList, objectName)

        if (id != None):
            sqlQueryReturn = sqlQueryReturn+sqlWhereId.format(id)
        else:
            for value in otherId:
                sqlQueryReturn = sqlQueryReturn + '{0} '.format(value)

        sqlQueryReturn = sqlQueryReturn + sqlLimit.format(limit)
        return sqlQueryReturn

    # ##########################################
    @staticmethod
    def query_creator (
        fieldsList, objectName,
        countryCode='ITA', limit=5000, maxDate=None):

        #sqlFieldSeparator = ','
        sqlQuery = "SELECT {0} FROM {1} WHERE TECH_ExternalId__c like '{2}%'"
        sqlLimit = " LIMIT {0}"
        sqlDateLimit = ' and LastModifiedDate < {0}'
        # sqlFieldSeparator.join(fieldsList)

        sqlQueryReturn = sqlQuery.format(fieldsList, objectName, countryCode)
        if (maxDate != None): sqlQueryReturn = sqlQueryReturn + sqlDateLimit.format(maxDate)
        #sqlQueryReturn = sqlQueryReturn   ' ORDER BY LastModifiedDate ASC'
        sqlQueryReturn = sqlQueryReturn + sqlLimit.format(limit)

        return sqlQueryReturn
    # ##########################################
