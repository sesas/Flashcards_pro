'''
flashcard program for studying.
'''

import os, sys, csv, pickle, collections, random, time, argparse
headers = []
terms = []

class GameOver(Exception):
    pass
class ChangeGame(Exception):
    pass

def getTermsFromInput(inp):
    global terms
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(inp)
    iterator = csv.reader(inp.split('\n'), dialect)
    terms = [ line for line in iterator ]
    pass

def getTermsFromCSV(file):
    global terms
    with open(file) as f:
        iterator = csv.reader(f)    
        
        terms = [ line for line in iterator ]

    pass

def getTermsFromFile(file):
    if os.path.splitext(file)[1] == '.csv':
        getTermsFromCSV(file)
    pass 

def askForHeaders():
    global terms, headers
    
    inp = input("does the file have a header?"+os.linesep)
    if not inp in ['no', 'n']:
        headers = terms.pop(0)
    for ind, head in enumerate(headers):
        print(ind, ":", head)
    
    inp = input("""which colums are relevant?
type the number of the colums you would like to keep,
or enter 'all' to keep all colums.
""")
    if inp in ['all', "'all'"]:
        pass
    else:
        filterTerms( [int(num) for num in inp.split(',')] )


def filterTerms(colNum):
    global terms, headers
    newH = []
    newT = []
    if headers:
        for n in colNum:
            newH.append(headers[n])
    for line in terms:
        newL = []
        for n in colNum:
            newL.append(line[n])
        newT.append(newL)
    headers = newH
    terms = newT
    
##    for num in reversed(range(len(headers))):
##        if not num in colNum:
####            print(num)
##            del headers[num]
##            for line in terms:
##                try:
##                    del line[num]
##                except (IndexError) as e:
##                    print(e)
##                    pass

def saveFlashCardData():
    global terms, headers
    inp = input("What name for the .flascard file do you want? ")
    if not inp:
        inp = "New flashcard - " + str(time.ctime().replace(':', '-'))
    pickle.dump( (headers, terms), open(str(inp)+'.flashcard', 'wb') )


def loadFlashCardData(fileName):
    global terms, headers
    headers, terms  = pickle.load( open(fileName, 'rb') )
    pass

def printAvailableFlashcards():
    fnames = os.listdir()
    fnames = [j for j in filter(lambda x: x.endswith('.flashcard'), fnames)]
    if fnames:
        for n, name in enumerate(fnames):
            print(n, ':', name)
        return fnames
##        inp = input("which file do you want? ")
##        return fnames[eval(inp)]

def main():
    global terms
##    loadFlashCardData()
    while(1):
        fnames = printAvailableFlashcards()
        if fnames:
            print("Enter the number corresponding to the flashcard you want to load, or")
        inp = input("""copy and paste the terms to add to the flashcards comma separated or
tab separated values (you can copy and paste from excel or google spreadsheet),
or alternatively enter a .csv file name.
""")
        if not inp:
            continue
        elif inp.isnumeric() and fnames:
            loadFlashCardData(fnames[int(inp)])
            return
        if os.path.isfile(inp) :
            # it's the name of the file
##            try:
                getTermsFromFile(inp)
                break
##            except e:
##                print(e)
##                print("Could not find file", inp, "try with using the full path")
##                pass
        else:
            try:
                getTermsFromInput(inp)
                break
            except:
                print("malformed input", repr(inp))
                pass
    assert terms, print(repr(terms))
    askForHeaders()
    saveFlashCardData()
    pass

def loadFlashcard(fileName=''):
    global g
    if not fileName:
        fnames = printAvailableFlashcards()
        if fnames:        
            inp = input("Enter the number corresponding to the flashcard you want to load:\n")
            if inp.isnumeric():
                fileName = fnames[int(inp)]
##                    loadFlashCardData(fnames[int(inp)])
    if fileName.endswith('.flashcard'):
        pass
    else:
        fileName += '.flashcard'
    try:
        g = pickle.load( open(fileName, 'rb') )
        raise ChangeGame
    except (IOError):
        print("Sorry, the file could not be loaded. Are you sure it exists?")
        
                    

def compare(str1, str2):
    """Returns a number in [0,1] describing how close str1 is to str2 (str2 is the correct answer)"""
    str1 = str1.lower()
    str2 = str2.lower()
        
    if str1 == str2:
        return 1
    else:
        set1 = set( str1.split() )
        set2 = set( str2.split() )
        diff = set2.difference(set1)
        return 1 - (len(diff)+1)/(len(set2)+1)

class Game:
    def __init__(self, headers, terms, histMaxLen=None):
        self.headers = headers
        self.terms = terms
        self.learning = collections.defaultdict(lambda: 0)
        self.colQuestion = [0]
        self.runNum = 0
        self.testHistory = collections.deque()
        if not histMaxLen:
            histMaxLen = int( len(terms)/2 )
        self.histMaxLen = histMaxLen
        self.init_optparse()

    def init_optparse(self):
        self.parser = argparse.ArgumentParser(description="Helps you study terms for your class.",
##                                              add_help=None,
##                                              prog = "flashcards.py"
                                              )
        class ChangeCols(argparse.Action):
            def __call__(me, parser, namespace, values, option_string=None):
##                print( '%r %r %r' % (namespace, values, option_string))
##                print(me.dest)
##                setattr(namespace, me.dest, values)
##                print(self)
                self.cmd_changeTestColumns(numList = values)
        class SaveGame(argparse.Action):
            def __call__(me, parser, namespace, values, option_string=None):
                self.saveFlashcard(' '.join(values))
        class LoadGame(argparse.Action):
            def __call__(me, parser, namespace, values, option_string=None):
                loadFlashcard(' '.join(values))
                
            
        self.parser.add_argument('-c', '--changeCols', nargs='*', type=int,
                                 action=ChangeCols, help="Change which columns to be tested on.")
        self.parser.add_argument('-v', '--view-settings', action='store_true', 
                                 help="View the current settings of these flashcards.")
##        self.parser.add_argument('-s', '--save', nargs='*', action=SaveGame, metavar='FILE_name_part',
##                                 help="Save the current flashcards to a file that can be loaded later. The file name can have spaces.")
##        self.parser.add_argument('-l', '--load', nargs='*', action=LoadGame, metavar='FILE_name_part',
##                                 help="Loads a file of flashcards that was saved previously. The file name can have spaces.")
        self.parser.add_argument('-q', '--quit', action='store_true', help="Quit the program and exit. You can also press Ctrl+C a second time.")

        
        pass

    def printHeaders(self):
        if self.headers:
            for ind, head in enumerate(self.headers):
                print(ind, ':', head)

    def cmd_changeTestColumns(self, numList = []):
##        print('numList =', numList)
        while 1:
            if not numList:
                self.printHeaders()
                numList = input("Select the columns you would like to be tested on (space separated):\n").strip().split()                
            if not numList:
                break
            try:
                newNum = [int(j) for j in numList]
                assert max(newNum) < len(self.terms[0]) and min(newNum) >= 0, print(newNum)
                self.colQuestion = newNum
                break
            except:
                print("\nCouldn't understand the numbers entered. Try again.\n", numList)
                numList = []
                pass
                

    def commandMode(self):
        print("\n ********** ENTERING COMMAND MODE ********* ")
##        self.parser.parse_args('-h'.split())
        self.parser.print_help()
        inp = input("Enter command (multiple commands can be used at one time):\n")
        try:
            commands = self.parser.parse_args(inp.split())
        except (SystemExit):
            return
        if commands.quit:
            raise GameOver()
        if commands.changeCols:
            self.cmd_changeTestColumns()

        
        print(" ********** EXITING COMMAND MODE ********* ")

    def run(self):
        while 1:
            try:
                self.run1test()
            except (KeyboardInterrupt):
                self.commandMode()
##                self.printMenu()
##                self.processInput()
####                continue

    def run1test(self):
        print(" ---------- NEW FLASHCARD ----------")
        while 1:
            curNum = random.randrange(0, len(self.terms))
            if not curNum in self.testHistory:
                self.testHistory.append(curNum)
                if len(self.testHistory) > self.histMaxLen:
                    self.testHistory.popleft()
                break
        self.runNum += 1
##        print(curNum, self.testHistory)
        curTest = self.terms[curNum]
##        curTest = self.terms[20]
        
##        curTest = random.sample(self.terms, 1)[0]
##        print(curTest)
        for ind, item in enumerate(curTest):
            if ind in self.colQuestion:
                continue
            else:
                if self.headers:
                    print()
                    print(self.headers[ind])
                print(curTest[ind])
        for qn in self.colQuestion:
            print("\nWhat is the corresponding:", end=' ')
            if self.headers:
                print(self.headers[qn], end=' ')
            else:
                print("column", qn, end=' ')
            inp = input('?\n')
            correctLevel = compare(inp, curTest[qn])
            print("correctness:", correctLevel)
            print('Answer:', curTest[qn])
        print()
##        if correctLevel

    def saveFlashcard(self, inp=''):
        if not inp:
            inp = input("What name for the .flascard file do you want? ")
        if not inp:
            inp = "New flashcard - " + str(time.ctime().replace(':', '-'))
        pickle.dump( self, open(str(inp)+'.flashcard', 'wb') )

            


if __name__ == "__main__":
    testFile = 'HIS111B-Final Prep - ID Terms.csv'
    main()
    g = Game(headers, terms)
    while 1:
        try:
            g.run()
        except(GameOver):
            break
        except(ChangeGame):
            continue
