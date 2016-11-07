#!/usr/bin/python


# example of program that detects suspicious transactions
# fraud detection algorithm
import sys
from datetime import datetime, time


def buildBatchGraph(batchFilePath):
    """
    Builds graph to from batch_payment.csv file,
    which contains past user payment data
    """
    batchGraph = {} # key: value --> lower_id: higher_id

    with open(batchFilePath) as batchFile:
        # Graph is undirected: as long as the 2 have made a transaction 
        # Thus we can order it by id number
        next(batchFile) # Skip header: 'time, id1, id2, amount, message'
        for line in batchFile:
            try:
                #time, id1, id2, amt, msg = line.split(', ') # FIXME: this will cause problems if ',' in msg
                values = line.split(', ')
                time, id1, id2, amt = values[:4]
                msg = values[4:] #FIXME if msg is important (it's currently a list)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue

            id1 = int(id1)
            id2 = int(id2)
            batchGraph.setdefault(id1, []).append(id2) if id1 < id2 else batchGraph.setdefault(id2, []).append(id1)

    return batchGraph


def feature1(batchFilePath, streamFilePath, output1FilePath):
    """
    When anyone makes a payment to another user, 
    they'll be notified if they've never made a 
    transaction with that user before.
    """
    print datetime.now()#FIXME
    batchGraph = buildBatchGraph(batchFilePath)
    print datetime.now()#FIXME

    with open(streamFilePath) as streamFile, open(output1FilePath, "w") as outFile1:
        next(streamFile) # Skip header: 'time, id1, id2, amount, message'
        for line in streamFile:
            try:
                #time, id1, id2, amt, msg = line.split(', ') # FIXME: this will cause problems if ',' in msg
                values = line.split(', ')
                time, id1, id2, amt = values[:4]
                msg = values[4:] #FIXME if msg is important (it's currently a list)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            
            #lower = id1 if id1 < id2 else id2
            id1 = int(id1)
            id2 = int(id2)
            lower = min(id1, id2)
            higher = max(id1, id2)

            #if lower in batchGraph and batchGraph[lower] == higher:#FIXME THIS IS WRONG
            if lower in batchGraph and higher in batchGraph[lower]:
                outFile1.write("trusted\n")
                #print "trusted"
            else:
                outFile1.write("unverified\n")
                #print "unverified"


    print datetime.now()#FIXME
    


def usage():
    #FIXME add feature 2 and 3
    if sys.argv[0].startswith('./'):
        print "Usage: %s <path_to_batch> <path_to_streaming> <path_to_output1>" % sys.argv[0]
    else:
        print "Usage: python %s <path_to_batch> <path_to_streaming> <path_to_output1>" % sys.argv[0]
    sys.exit(1)


if __name__ == '__main__':

    try:
        batchFilePath = sys.argv[1]
        streamFilePath = sys.argv[2]
        output1FilePath = sys.argv[3]
        #output2FilePath = sys.argv[4]
        #output3FilePath = sys.argv[5]
    except IndexError as e:
        usage()

    try:
        feature1(batchFilePath, streamFilePath, output1FilePath)
    except IOError as e:
        print e
        usage()
