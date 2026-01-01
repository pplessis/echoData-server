import time

from enum       import Enum
from io         import open
from datetime   import datetime
from re         import error, fullmatch, match
from os         import environ, system, path, listdir
from platform   import system                           as getSystem

DEBUG       = True
MINI_LEVEL  = 3
MAX_LEVEL   = 12

LOG_FOLDER = '../logs'

# #############################################
class PColors:
    HEADER = '\033[95m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    DARK_CYAN = '\033[36m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# #############################################
class Tools:
    @staticmethod
    def handelReplacementArray () -> dict:
        replacements = {
             '/': '-' ,' ': '-'
            ,'?': '-' ,'!': '-'
            ,':': '-' ,';': '-'
            ,'.': '-' ,'&': '-'
            ,'é': 'e' ,'è': 'e'
            ,'à': 'e' ,'ç': 'c'
            ,'ù': 'u' ,'@': '-'
            ,'$': '-' ,'€': '-'
            ,'£': '-' ,'%': '-'
            ,'`': '-' ,'"':  ''
            ,'\'': '' ,'#': '-'
            ,'*': '-' ,'=': '-'
            ,'+': '-' ,'~': '-'
            ,'^': '-' ,'\\': '-'
            ,'{': '-' ,'}': '-'
            ,'[': '-' ,']': '-'
            ,'(': '-' ,')': '-'
            ,'<': '-' ,'>': '-'
            ,'|': '-'
        }

        return replacements

    # ######################
    @staticmethod
    def searchInList(List:list, Pattern:str, FullMatch:bool=False) -> list:
        returnList = list()

        try:
            for value in List:
                if (FullMatch == False):
                    if (match(Pattern, value)):
                        returnList.append(value)
                else:
                    if (fullmatch(Pattern, value)):
                        returnList.append(value)

        except error as e:
            print(f"Invalid regular expression pattern: {e}")
            return list()

        return returnList

    # ######################
    @staticmethod
    def get_size_format(n:float, suffix="B"):
        # converts bytes to scaled format (e.g KB, MB, etc.)
        for unit in ["", "K", "M", "G", "T", "P"]:
            if (n < 1024):
                return f"{n:.2f}{unit}{suffix}"
            n /= int(1024)

    # ######################
    @staticmethod
    def get_datetime_format( Current_dateTime:datetime ):
        # convert to datetime object
        Current_dateTime = datetime.strptime( str(Current_dateTime), "%Y%m%d%H%M%S")
        # convert to human readable date time string
        return Current_dateTime.strftime("%Y/%m/%d %H:%M:%S")

    # ######################
    @staticmethod
    def replaceValueInHTMLTemplate(HtmlText:str, MaskAndValues:dict={}) -> str:
        """Replaces placeholders in an HTML template with actual values.

        Args:
            HtmlText (str): Html Template with values like %VALUE%.
            MaskAndValues (dict, optional): _description_. Defaults to {}.

        Returns:
            str: Html completed with MaskValues.
        """
        returnHTMLCompleted = HtmlText

        if (len( MaskAndValues) > 0 ):
            for key, replacement in MaskAndValues.items():
                returnHTMLCompleted = returnHTMLCompleted.replace( key, (str)(replacement) )

        return returnHTMLCompleted

# #############################################
class Print:
    
    def __init__(self, Variable, Level=0, Title=None) -> None:
        """Print a message on the screen base on alert LEVEL.
        00 : DEBUG (default)
        05 : INFO
        10 : PROGRAM MESSAGE

        Args:
            Variable (str): Message
            Level (int, optional): Message level. Defaults to 0.
            Title (str, optional): Title put in suffix. Defaults to None.
        """
        Print.log(Variable, Level, Title)
        pass
    
    @staticmethod
    def hr (WithDate:bool):
        """ Create a line in the shell with date or not.
        Args:
            WithDate (Bool): Add date in the line

        Returns:
            datetime: Current DateTime
        """

        CAR_LINE = '#'*20
        NOW = datetime.now()

        if (WithDate == False):
            print ( "{0}".format(CAR_LINE ) )
        else:
            print ( "{0}|{1}".format(CAR_LINE, NOW.strftime("%Y-%m-%d %H:%M:%S")))

        return NOW

    # ##########################################
    @staticmethod
    def h1 (Title):
        """Create a TITLE level 1 (H1)
        Args:
            Title (str): Title
        """
        now = datetime.now()
        automatic = False
        returnValue = None

        pattern = '\033[1;34m # {0} # \033[0;0m'
        if (automatic): pattern = ' # {0} #'

        print (pattern.format(Title.upper()))
        returnValue = '# {0} - {1}'.format(Title.upper(), now.strftime('%Y-%m-%d %H:%M:%S'))

        Print.logInFile( returnValue )

        return returnValue
    # ##########################################
    @staticmethod
    def h2 (Title):
        """Create a TITLE level 1 (H2)
        Args:
            Title (str): Title
        """
        automatic = False
        returnValue = None

        pattern = '\033[1;34m ## {0} \033[0;0m'
        if automatic: pattern = ' ## {0} '

        returnValue = pattern.format(Title)

        print (returnValue)

        return returnValue

    # ######################
    @staticmethod
    def h3 (Title:str):
        """Create a TITLE level 3 (H3)
        Args:
            Title (str): Title
        """
        automatic = False
        returnValue = None

        pattern = '\033[0;34m ### {0} \033[0;0m'
        if automatic: pattern = ' ### {0} '

        returnValue = pattern.format(Title) 

        print (returnValue)
        return returnValue

    # ######################
    @staticmethod
    def end():
        """Line to mark program end
        """
        CAR_LINE = '#'*20
        print ("{0}".format(CAR_LINE) )

        return

    # ######################
    @staticmethod
    def log (Variable, Level=0, Title=None):
        """Print a message on the screen base on alert LEVEL.
        00 : DEBUG (default)
        05 : INFO
        10 : PROGRAM MESSAGE

        Args:
            Variable (str): Message
            Level (int, optional): Message level. Defaults to 0.
            Title (str, optional): Title put in suffix. Defaults to None.
        """

        addTime = False
        currentDate = datetime.now()
        loginLine = ''
        preFixe = ''

        if (addTime) :
            preFixe = '{0} '.format( currentDate.strftime("%Y-%m-%d %H:%M:%S") )

        if (DEBUG and Level == 0):                                                      ## DEBUG LEVEL
            if (Title != None): loginLine = 'D>{0}> {1}'.format(Title, Variable)
            else : loginLine = 'D> {0}'.format(Variable)

        if (Level > 0 and Level <= 2):                                                  ## INFO LEVEL
            if (Title!=None): loginLine = 'I>{0}> {1}'.format(Title, Variable)
            else: loginLine = 'I> {0}'.format(Variable)

        if (Level > 2 and ( MINI_LEVEL <= Level and  Level <= MAX_LEVEL ) ):            ## OTHER LEVELS
            if (Title!=None): loginLine = '{0}> {1}'.format(Title, Variable)
            else: loginLine = '> {0}'.format(Variable)

        #loginLine = preFixe + loginLine
        if (len(loginLine) >0 ): print( loginLine )

        if (Level > 10 and ( MINI_LEVEL <= Level and  Level <= MAX_LEVEL )):                                                                ## LOG FILE
            Print.logInFile (loginLine)

        return loginLine

    # ######################
    @staticmethod
    def logCols ( Values:list, WithIndex:bool=False ) -> str:
        returnValues = ''
        nbItem = len (Values)
        for index in range(0, nbItem, 3):
            tag01 = Values[index]
            tag02 = ''
            tag03 = ''

            if (index+1 < nbItem): tag02 = Values[index+1]
            if (index+2 < nbItem): tag03 = Values[index+2]

            if (len(tag01)>0 and len(tag02)>0 and len(tag03)>0):
                if not(WithIndex):
                    returnValues += ( '|{0:>40s}|{1:>40s}|{2:>40s}|\n'.format( tag01, tag02, tag03 ) )
                else:
                    returnValues += ( '|{6}({3:2d}){7}{0:>36s}|{6}({4:2d}){7}{1:>36s}|{6}({5:2d}){7}{2:>36s}|\n'.format( tag01, tag02, tag03, index,index+1,index+2, PColors.BOLD, PColors.ENDC ) )

            elif ( len(tag01)>0 and len(tag02)>0 ):
                if not(WithIndex):
                    returnValues += ( '|{0:>40s}|{1:>40s}|\n'.format( tag01, tag02 ) )
                else:
                    returnValues += ( '|{5}({3:2d}){6}{0:>36s}|{5}({4:2d}){6}{1:>36s}|\n'.format( tag01, tag02, index, index+1, PColors.BOLD, PColors.ENDC ) )

            elif ( len(tag01)>0 ):
                if not(WithIndex):
                    returnValues += ( '|{0:>40s}|\n'.format( tag01 ) )
                else:
                    returnValues += ( '|{2}({1:2d}){3}{0:>36s}|\n'.format( tag01, index, PColors.BOLD, PColors.ENDC ) )

        return returnValues

    # ######################
    @staticmethod
    def cleanLogFile ():
        """Clean the LOG file.

        Returns:
            BOOLEAN: Result of the operation.
        """
        returnValue = True
        logFileName = '{0}.log'.format(__file__)
        logPath = LOG_FOLDER

        try:
            with open(logPath+'/'+logFileName, 'w') as f:
                f.truncate(4)
                f.close()

        except IOError as e:
            returnValue = False

        return returnValue

    # ######################
    @staticmethod
    def logInFile (newLine):
        """
        Add a new line in the LOG file.

        Args:
            newLine (Str): Append the line in the LOG file.

        Returns:
            BOOLEAN: Result of the operation.
        """
        returnValue = True
        logFileName = '{0}.log'.format(__file__)
        logPath = LOG_FOLDER

        if ( path.isdir(logPath ) == True ):
            try:
                with open(logPath + '/'+logFileName, 'a') as f:
                    f.write( newLine + '\n' )
                    f.close()

            except IOError as e:
                Print.error( e )
                returnValue = False

        return returnValue

    # ######################
    @staticmethod
    def error (Msg) -> str:
        """Print an error message on the screen.

        Args:
            Msg (str): Message
        """
        #pattern = f'{PColors.RED}!> {Msg}{PColors.ENDC}'
        pattern = '{0}!> {1}{2}'.format (PColors.RED, Msg, PColors.ENDC)
        print ( pattern )

        return pattern

    # ######################
    @staticmethod
    def cleanScreen():
        """
        Clean Screen (Compatible Windows and Linux). [Required import sys]
        """
        os_Name = getSystem()
        if (os_Name == 'Windows'):
            system('cls')
        else:
            system('clear')

    # ######################
    @staticmethod
    def confirmExecution ( Message:str ) -> bool:
        """
    Confirms whether to continue the execution based on user input.

    Args:
        Message (str): The message to display to the user.

    Returns:
        bool: True if the user confirms, False if they stop.
        """

        try:
            confirm = input( Message +'(y/n) [n] ? ').lower().strip()
            result = confirm in ('y', 'yes')
        except NameError:
                pass

        return result

    # ######################
    @staticmethod
    def convertToDict (enumClass) -> dict:
        """Convert a Enum class to a dict with a list with each values possible.

        Args:
            enumClass (Enum): Enum Type

        Returns:
            dict: List values
        """
        myDict = {value.name: value.value for value in enumClass}

        return myDict

    # ######################
    @staticmethod
    def selectAValue (EnumClass, DefaultValue = None) -> Enum:
        """
    Prompts the user to select a value from an enumeration class.

    Args:
        EnumClass: The enumeration class to select from.
        DefaultValue (Enum, optional): The default value to return if no input is provided. Defaults to None.

    Returns:
        Enum: The selected value.

    Raises:
        AttributeError: If the input cannot be converted to an attribute of the enum class.
        KeyError: If the user enters a value that does not exist in the enumeration class.
        NameError: If there is an error in naming conventions while selecting the value.
        """
        if (DefaultValue!=None):
            result = EnumClass[DefaultValue]
        else:
            result = EnumClass[0]

        prompt = 'Select a value between ({0})'
        if (DefaultValue!= None): prompt += ' [{1}]'
        prompt += ' ? '

        possibleValues = Print.convertToDict(EnumClass)
        message = prompt.format( ', '.join( possibleValues ), DefaultValue)

        try:
            confirm = input( message ).strip()

            if (len(confirm) ==0):
                confirm = DefaultValue

            result = EnumClass[confirm]

        except AttributeError as attributeError:
            Print.error (attributeError)
        except KeyError as keyError:
            Print.error ('Value ('+ str(keyError) +') not allowed.')
        except NameError as nameError:

            Print.error (nameError)

        return result

    # ######################
    @staticmethod
    def Environnement (Country:Enum, Environnement:Enum)-> None:
        """
    Prints the current environment details.

    Args:
        Country (Enum): The country of execution.
        Environnement (Enum): The execution environment.

    Returns:
        None
        """

        #pattern = f'{PColors.RED}!> {Msg}{PColors.ENDC}'
        Print.hr(False)
        pattern = 'Country: {0}{1}{2} | Execution Environnement: {3}{4}{5}'.format(  PColors.GREEN, Country.value, PColors.ENDC
                                                                                   , PColors.PURPLE, Environnement.value, PColors.ENDC)
        #print ( f'Country: {PColors.GREEN}{Country.value}{PColors.ENDC} | Execution Environnement: {PColors.PURPLE}{Environnement.value}{PColors.ENDC}')
        print (pattern)

    # ######################
    @staticmethod
    def selectAValueInList (Values:list[str], DefaultValue = None) -> list[str]:
        returnValue = list()
        prompt = 'Select a value between :\n'
        aListedValue = f'{PColors.YELLOW}({{0}}){PColors.ENDC} {{1}}\n'
        question = f'{PColors.BOLD}Select a value between{PColors.ENDC} ?'
        questionWithDefault = f'{PColors.BOLD}Select a value between [{0}]{PColors.ENDC} ?'
        
        #List options
        for index, value in enumerate(Values):
            prompt += aListedValue.format(index, value)
        
        prompt += questionWithDefault.format( '' )
        print(prompt, end = '')

        return returnValue
    # ##################### #
    @staticmethod
    def selectAFileInList (Values:list[str], DefaultValue = None) -> list[str]:
        returnValue = list()
        prompt = 'Select a value in list :\n'
        aListedValue = f'{PColors.YELLOW}({{0}}){PColors.ENDC} {{1}}\n'
        question = f'{PColors.BOLD}Select a value between{PColors.ENDC} ?'
        questionWithDefault = f'\r\n{PColors.BOLD}Select a value between [{0}]{PColors.ENDC}? '

        #List options
        #for index, value in enumerate(Values):
        #    prompt += aListedValue.format(index, value)

        prompt += Print.logCols(Values, WithIndex=True)
        prompt += questionWithDefault.format( '' )

        #Print Values and Question
        #print(prompt, end = '')

        try:
            confirmStr = input( prompt ).strip()

            # Check value and remplace to default 
            if (len(confirmStr) == 0):
                if (DefaultValue != None):
                    confirmStr = DefaultValue
                else:
                    confirmStr = '0'

            confirmIndex = int(confirmStr)
            if (confirmIndex < 0 or confirmIndex >= len(Values)):
                    raise ValueError('Index out of range')

            returnValue.append( Values[confirmIndex] )

        except KeyError as keyError:
            print ('Value ('+ str(keyError) +') not allowed.')
        except ValueError as valueError:
            print ('Value ('+ str(valueError) +') not allowed.')

        return returnValue


# #############################################
class Timer:
    @staticmethod
    def Start_timer():
        start_time = time.time()            # Set current time as timestamp.
        return start_time

    @staticmethod
    def stop_timer(start_time):
        end_time = time.time()              # Set current time as timestamp.
        total_time = end_time - start_time  # Calculate diff between START and END times.
        return total_time


# #############################################
class Io:

    NEWLINE = '\n'

    @staticmethod
    def saveTxtFile (Folder, FileName, Content) -> str:
        targetFile = Folder + '/' + FileName

        try:
            with open(targetFile, 'w') as f:
                f.write(Content)
                f.flush()
                f.close()
            return targetFile

        except IOError as e:
            Print.error('File ERROR :' + str(e) )

        return ''
    # ######################
    @staticmethod
    def appendTxtFile (Folder, FileName, Content) -> str:
        """
    Appends content to a text file.

    Args:
        folder (str): The path to the folder containing the file.
        file_name (str): The name of the file to be modified.
        content (str): The content to be appended to the file.

    Returns:
        str: The full path to the updated file.
        """

        targetFile = path.join( Folder , FileName )

        try:
            with open(targetFile, 'a+') as f:
                f.write( Io.NEWLINE + '######################' + Io.NEWLINE )
                f.write(Content)
                f.flush()

            return targetFile

        except IOError as e:
            Print.error('File ERROR: ' + str(e))
            return ''
        except Exception as e:
            Print.error('Unexpected error: ' + str(e))
            return ''

    # ######################
    @staticmethod
    def openTxtFile (Folder:str, Filename:str, Encoding:str='utf-8') -> list :
        """
    Opens a text file and returns its contents as a list of lines.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file to be opened.
        encoding (str, optional): The encoding type. Defaults to 'utf-8'.

    Returns:
        list: A list of strings representing the file's contents on each line.
        """
        returnValue = list()
        filename = Folder + '/' + Filename

        with open(filename, 'r', encoding=Encoding) as f:
                text = f.read()

        returnValue = text.split(Io.NEWLINE)

        return returnValue
    # ######################
    @staticmethod
    def loadListFromFile ( CompleteFilename:str, CleanEmpty:bool = False) -> list :
        """
        Load a list from a FILE (alias Io.openTxtFile() )

        Args:
            CompleteFilename (str): file complete path (Folder & Filename)
            CleanEmpty (bool): Remove all (None, Empty, 0 or False)

        Returns:
            list: File content
        """
        returnValue = list()
        folder = path.dirname   (CompleteFilename)
        file = path.basename    (CompleteFilename)

        content = Io.openTxtFile(folder, file)
        if (CleanEmpty):
            # Remove all (None, Empty, 0 or False)
            returnValue = [value for value in content if value]
        else:
            returnValue = content

        return content
    # ######################
    @staticmethod
    def openTxtFileStr (Folder:str, Filename:str, Encoding:str='utf-8') -> str :
        """
    Opens a text file and returns its contents.

    Args:
        folder (str): The path to the folder containing the file.
        filename (str): The name of the file to be opened.
        encoding (str): The encoding type. Defaults to 'utf-8'.

    Returns:
        str: The contents of the file.
        """
        returnValue = ''
        filename = Folder + '/' + Filename

        with open(filename, 'r', encoding=Encoding) as f:
                returnValue = f.read()

        return returnValue
    # ######################
    @staticmethod
    def listFilesInFolder (Folder:str, Extension=None) -> list:
        """
        List all files in a folder with a specific extension.
        Args:
            Folder (str):
            Extension (str, optional): _description_. Defaults to None.

        Returns:
            list: All Files in the folder with the extension.
        """

        files = []
        for filename in listdir(Folder):
            if filename.endswith( str(Extension) ) or Extension == None:
                files.append(filename)

        return files