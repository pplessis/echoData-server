import csv
from inspect import getmembers
from os import path

class CsvFile:
    """ Represent a CSV File in memory
    """

    HEAD_PK_NAME = 'TECH_EXTERNAL_ID'
    DELIMITER = ';'
    ENDLINE = '\n'
    QUOTECHAR = '"'
    DEFAULT_ENCODING = 'utf-8'

    def __init__( self, Data:list, WithHeader:bool = True, NamespaceHeader:str ='' , Filename:str='' ,PkName = None ) -> None:
        """_summary_

        Args:
            data (_type_): _description_
            withHeader (bool, optional): _description_. Defaults to True.
            namespaceHeader (str, optional): _description_. Defaults to ''.
            filename (str, optional): _description_. Defaults to ''.
            pkName (_type_, optional): _description_. Defaults to None.
        """

        self.index = -1
        self.pkIndex = -1

        self.namespaceHeader =  NamespaceHeader
        self.filename = Filename

        self.withHeader = WithHeader
        self.rawData = Data
        self.headerLine = list()

        self.pkName = CsvFile.HEAD_PK_NAME
        if (PkName != None): self.pkName = PkName


        if (self.withHeader):
           if (self.pkName in self.rawData[0] ):
               self.pkIndex = self.rawData[0].index (self.pkName)

           self.headerLine = self.rawData[0]
           self.rawData.pop(0)

        pass

    def replaceData (self, Data:list, WithHeader:bool = True) -> None:
        self.rawData = Data
        """Replace the DATA rows in this object.
        """

        if (WithHeader):
           if (self.pkName in self.rawData[0] ):
               self.pkIndex = self.rawData[0].index (self.pkName)

           self.headerLine = self.rawData[0]
           self.rawData.pop(0)
        pass

    def calculateHeader(self, WithHeader:bool = True) -> None:
        """_summary_

        Args:
            WithHeader (bool, optional): _description_. Defaults to True.
        """

        if (WithHeader):
           if (self.pkName in self.rawData[0] ):
               self.pkIndex = self.rawData[0].index (self.pkName)

           if(len(self.headerLine) == 0):
                self.headerLine = self.rawData[0]
                self.rawData.pop(0)

           self.withHeader = WithHeader

        pass

    @property
    def countData(self) -> int:
        returnValue = len (self.rawData)
        if (self.withHeader): returnValue -= 1
        return returnValue

    @property
    def getHeader(self) -> list:
        returnValue =  []

        if (self.withHeader and len(self.rawData) >= 1) :
            # Add NameSpace on each header name as pre-fixe.
            if (len( self.namespaceHeader ) > 0 ):
                returnValue = [self.namespaceHeader + '.' + sub for sub in self.headerLine ] 
            else:
                returnValue = self.headerLine

        return returnValue



    def extractCol (self, ColIndex)-> list:
        """Extract all data in a colum.

        Args:
            ColIndex (int): Index of the col will be extracted.

        Returns:
            list: All Rows extracted.
        """
        returnValue =  []
        
        for row in self.rawData:
            returnValue.append( row[ColIndex] )
        
        return returnValue


    def findLine (self, Value, ColIndex = -1) -> list:
        """Return the first value in the Rows.
        Args:
            Value (string): Value searched
            ColIndex (int, optional): _description_. Defaults to -1.

        Returns:
            list: Values with the value Searched.
        """
        returnValue = []
        if (self.withHeader == False): return returnValue
        if (ColIndex == -1): ColIndex = self.pkIndex
        
        for row in self.rawData:
            if (Value == row[ColIndex]):
                returnValue = row
                break
        
        return returnValue
    
    def findLines (self, Value, ColIndex = -1, AddHeader = False) -> list:
        """Return all values in the Rows.

        Args:
            Value (string): Value searched
            ColIndex (int, optional): Force the index for the PK. Defaults to -1.
            AddHeader (bool, optional): Add Header name in a tuple on each values returned.

        Returns:
            list: Values with the values Searched.
        """
        returnValue = []
        if (self.withHeader == False): return returnValue
        if (ColIndex == -1): ColIndex = self.pkIndex

        for row in self.rawData:
            if (Value == row[ColIndex]):
                if (AddHeader and self.withHeader):
                    returnValue.append( tuple( zip( self.getHeader, row  ) ) )
                else:
                    returnValue.append( row )

        return returnValue

    def cloneEmptyRows (self) -> list:
        returnValues = [''] * len(self.rawData[0])
        return returnValues

    def findIndexCol (self, Value) -> int:
        """Return ColIndex from an colum Name in the Header.

        Args:
            Value (str): colum Name

        Returns:
            int: colum index for this name or 0.
        """
        returnValue = 0

        if (self.withHeader==False): return returnValue
        if (Value==None or len(Value)==0): return returnValue

        returnValue = self.headerLine.index (Value)

        return returnValue

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1

        if self.index == len(self.rawData):
            raise StopIteration

        return self.rawData [self.index]
    def saveCsv (self, FilePath:str) -> str:
        """Save the CSV File in a file.

        Args:
            FilePath (str): Path of the file
            Filename (str): Name of the file

        Returns:
            str: Path of the file
        """
        newFile = path.join ( FilePath , self.filename )

        with open(newFile, 'w', newline=CsvFile.ENDLINE, encoding=CsvFile.DEFAULT_ENCODING ) as csvfile:
            fieldnames = self.headerLine
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Écrire l'en-tête du fichier CSV
            writer.writeheader()

            # Écrire les données des objets dans le fichier CSV
            for obj in self.rawData:
                #writer.writerow({'Name': obj.name, 'Age': obj.age, 'Profession': obj.profession})

                # Create Dicionary from DATA
                currentRow = dict()
                for index in range(len(self.headerLine)):
                    currentRow.update( {self.headerLine[index]: obj[index] } )

                ## Save Data in CSV
                writer.writerow(currentRow)

        return newFile

# ######################
    @staticmethod
    def getClassMembers(object) -> list:
        """
        Retrieves all non-private members of a class object.

        This method uses the inspect.getmembers function to get all members of the provided
        object and filters out any members whose names contain '__' (dunder methods).

        Args:
            object: The class object to inspect for members.

        Returns:
            list: A list of tuples containing (name, value) pairs for all non-private 
                  members of the class.

        Example:
            >>> class MyClass:
            ...     def method1(self): pass
            ...     def __private(self): pass
            >>> members = getClassMembers(MyClass)
            >>> # Returns [('method1', <function MyClass.method1 at 0x...>)]
        """
        returnList = []
        list = getmembers(object)
        for item in list:
            if (not ('__' in item[0])):
                returnList.append(item)

        return returnList

    # ######################
    @staticmethod
    def csvHead (object) -> list[str] :
        forceUpperCase = False
        returnHead = []
        attributes =  CsvFile.getClassMembers (object)
        for name, value in attributes:
            returnHead.append( name.upper() if forceUpperCase else name  )

        return returnHead

    @staticmethod
    def objects_to_csv( Objects:list, FilePath:str, Filename:str, Func = None) -> str :
        """Fonction pour convertir les objets en fichier CSV  - POC -

        Args:
            objects (any): _description_
            file_path (str): _description_
        """
        newFile = path.join ( FilePath , Filename )

        # Check parameters
        if ( len(Objects) == 0 ):
            raise ValueError (Objects)

        # Build CSV Head
        csvHeads = CsvFile.csvHead( Objects[0] )

        with open(newFile, 'w', newline=CsvFile.ENDLINE, encoding='utf8' ) as csvfile:
            fieldnames = csvHeads
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Écrire l'en-tête du fichier CSV
            writer.writeheader()

            # Écrire les données des objets dans le fichier CSV
            for obj in Objects:
                #writer.writerow({'Name': obj.name, 'Age': obj.age, 'Profession': obj.profession})

                # Create Dicionary from DATA
                currentRawData = CsvFile.getClassMembers(obj)
                currentRow = dict()

                for name,value in currentRawData:
                    if ( not( isinstance(value, dict) )  ):
                        currentRow.update( {name: str(value) } )
                    else:
                        if (Func!=None):
                            valueTmp = Func (value)
                            currentRow.update( {name: valueTmp } )

                ## Save Data in CSV
                writer.writerow(currentRow)


        return newFile