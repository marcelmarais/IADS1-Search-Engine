# Inf2-IADS Coursework 1, October 2020

# Python source file: search_queries.py
# Author: John Longley

# TEMPLATE FILE
# Please add your code at the point marked: # TODO


# PART B: PROCESSING SEARCH QUERIES

import index_build
import copy
# We find hits for queries using the index entries for the search terms.
# Since index entries for common words may be large, we don't want to
# process the entire index entry before commencing a search.
# Instead, we process the index entry as a stream of items, each of which
# references an occurrence of the search term.

# For example, the (short) index entry

#    'ABC01,23,DEF004,056,789\n'

# generates a stream which successively yields the items

#    ('ABC',1), ('ABC',23), ('DEF',4), ('DEF',56), ('DEF',789), None, None, ...

# Item streams also support peeking at the next item without advancing.

class ItemStream:
    def __init__(self,entryString):
        self.entryString = entryString
        self.pos = 0
        self.doc = 0
        self.comma = 0
    def updateDoc(self):
        if self.entryString[self.pos].isalpha():
            self.doc = self.entryString[self.pos:self.pos+3]
            self.pos += 3
    def peek(self):
        if self.pos < len(self.entryString):
            self.updateDoc()
            self.comma = self.entryString.find(',',self.pos)
                    # yields -1 if no more commas after pos
            line = int(self.entryString[self.pos:self.comma])
                    # magically works even when comma == -1, thanks to \n
            return (self.doc,line)
        # else will return None
    def pop(self):
        e = self.peek()
        if self.comma == -1:
            self.pos = len(self.entryString)
        else:
            self.pos = self.comma + 1
        return e

# TODO
# Add your code here.

# Building index
index_build.buildIndex()
test = index_build.generateMetaIndex('sample_index.txt')

class HitStream:
    def __init__(self, itemStreams: [ItemStream], lineWindow: int, minRequired: int):
        self.itemStreams = itemStreams
        self.numSearchTerms = len(itemStreams)
        self.lineWindow = lineWindow if lineWindow >= 1 \
                                     else Exception("Line Window is less than 1")
        self.minRequired = minRequired if self.numSearchTerms >= minRequired \
                                       else Exception("More search terms than min")

    def next(self):
        for item in self.itemStreams:
            self.current_item = item
            try:
                entries = item.pop()
            except:
                return None
            entry = copy.deepcopy(entries)
            #print(entry)
            while entry != None:
                search = self.checkOccurances(*entry, item)
                if search: return entry#,search)
                entry = item.pop()
    
    def checkOccurances(self, code, lineNum, item: ItemStream):
        lines_to_check = list(range(lineNum, lineNum + self.lineWindow - 1)) # Need to check for distinct
        numUniqueOccurances = 0
        for i in self.itemStreams:
            if self.findUnique(i, code, lines_to_check): numUniqueOccurances += 1
            if numUniqueOccurances >= self.minRequired - 1: return True # Since first item is implicitly counted
        return False
    
    def findUnique(self, item, code, lines_to_check):
        # Checks if next search term is found
        entries = copy.deepcopy(item) 
        try:
            entry = entries.pop()
        except:
            return False

        while entry != None:
            if entry[0] == code and entry[1] in lines_to_check: 
                return True
            entry = entries.pop()
        return False

def create_query(words_to_find):
    query = []
    for i in words_to_find:
        a = index_build.indexEntryFor(i)
        query.append(ItemStream(a))
    return query
    
test_words  = ['woke','where']

query = create_query(test_words)
lineWindow = 1
minRequired = 1
numHits = 3

H = HitStream(query, lineWindow, minRequired)
print(test_words)
for i in range(0,numHits):
    print(H.next())

# Displaying hits as corpus quotations:

import linecache

def displayLines(startref,lineWindow):
    # global CorpusFiles
    if startref is not None:
        doc = startref[0]
        docfile = index_build.CorpusFiles[doc]
        line = startref[1]
        print ((doc + ' ' + str(line)).ljust(16) +
               linecache.getline(docfile,line).strip())
        for i in range(1,lineWindow):
            print (' '*16 + linecache.getline(docfile,line+i).strip())
        print ('')

def displayHits(hitStream,numberOfHits,lineWindow):
    for i in range(0,numberOfHits):
        startref = hitStream.next()
        if startref is None:
            print('-'*16)
            break
        displayLines(startref,lineWindow)
    linecache.clearcache()
    return hitStream


# Putting it all together:

currHitStream = None

currLineWindow = 0

def advancedSearch(keys,lineWindow,minRequired,numberOfHits=5):
    indexEntries = [index_build.indexEntryFor(k) for k in keys]
    if not all(indexEntries):
        message = "Words absent from index:  "
        for i in range(0,len(keys)):
            if indexEntries[i] is None:
                message += (keys[i] + " ")
        print(message + '\n')
    itemStreams = [ItemStream(e) for e in indexEntries if e is not None]
    if len(itemStreams) >= minRequired:
        global currHitStream, currLineWindow
        currHitStream = HitStream (itemStreams,lineWindow,minRequired)
        currLineWindow = lineWindow
        displayHits(currHitStream,numberOfHits,lineWindow)

def easySearch(keys,numberOfHits=5):
    global currHitStream, currLineWindow
    advancedSearch(keys,1,len(keys),numberOfHits)

def more(numberOfHits=5):
    global currHitStream, currLineWindow
    displayHits(currHitStream,numberOfHits,currLineWindow)

# End of file
print(advancedSearch(test_words,lineWindow,minRequired,numberOfHits = numHits))