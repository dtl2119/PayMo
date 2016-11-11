#!/usr/bin/python

import sys

def buildBatchGraph1(batchFilePath):
    """
    BUILDS BATCH GRAPH FOR FEATURE 1
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
                time, id1, id2, amt, msg = line.split(', ', 4)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            id1 = int(id1)
            id2 = int(id2)
            # Always have the lower user id be the key (only for feature1)
            batchGraph.setdefault(id1, []).append(id2) if id1 < id2 else batchGraph.setdefault(id2, []).append(id1)

    return batchGraph


def feature1(batchFilePath, streamFilePath, output1FilePath):
    """
    When anyone makes a payment to another user, 
    they'll be notified if they've never made a 
    transaction with that user before.
    """
    batchGraph = buildBatchGraph1(batchFilePath)

    with open(streamFilePath) as streamFile, open(output1FilePath, "w") as outFile1:
        next(streamFile) # Skip header: 'time, id1, id2, amount, message'
        for line in streamFile:
            try:
                time, id1, id2, amt, msg = line.split(', ', 4)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            
            # lower = id1 if id1 < id2 else id2
            id1 = int(id1)
            id2 = int(id2)
            lower = min(id1, id2)
            higher = max(id1, id2)

            if lower in batchGraph and higher in batchGraph[lower]:
                outFile1.write("trusted\n")
            else:
                outFile1.write("unverified\n")


def buildBatchGraph(batchFilePath):
    """
    BUILDS BATCH GRAPH FOR BOTH FEATURE 2 AND 3
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
                time, id1, id2, amt, msg = line.split(', ', 4)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            id1 = int(id1)
            id2 = int(id2)
            batchGraph.setdefault(id1, []).append(id2)
            batchGraph.setdefault(id2, []).append(id1)

    return batchGraph


def feature2(batchFilePath, streamFilePath, output2FilePath):
    """
    Trusted if the two users have mutual friends (i.e. have
    previously made a transaction with the same person)
    """
    batchGraph = buildBatchGraph(batchFilePath)

    with open(streamFilePath) as streamFile, open(output2FilePath, "w") as outFile2:
        next(streamFile) # Skip header: 'time, id1, id2, amount, message'
        for line in streamFile:
            try:
                time, id1, id2, amt, msg = line.split(', ', 4)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            
            # lower = id1 if id1 < id2 else id2
            id1 = int(id1)
            id2 = int(id2)

            # Get transaction list for each user
            id1Friends = batchGraph[id1] if id1 in batchGraph else []
            id2Friends = batchGraph[id2] if id2 in batchGraph else []

            # unverified if one of them has never made a transaction
            if not id1Friends or not id2Friends:
                outFile2.write("unverified\n")
                continue

            # Trusted if they're immediate friends too
            if id2 in id1Friends or id1 in id2Friends:
                outFile2.write("trusted\n")
                continue

            # Check the set intersection
            if set(id1Friends).isdisjoint(id2Friends):
                outFile2.write("unverified\n")
                continue
                
            outFile2.write("trusted\n")



def isWithin(graph, k, id1, id2):
    """
    Returns True if id1 and id2 are within 4 degrees, else
    it returns False.  In our case, k == 4
    """
    visited = set([id1]) # Keep track of users already visited

    if id1 not in graph or id2 not in graph:
        return False

    # Start with 1st degree users (immediate friends)
    network = set(graph[id1])
    for i in range(k):
        if id2 in network: # O(1)
            return True
        else:
            visited = visited | network
       
        # Add all adjacent users to the network set
        for user in network:
            network = network | set(graph[user])
        
        # To avoid cycles, remove all users already visited
        network = network - visited

    return False

def feature3(batchFilePath, streamFilePath, output3FilePath):
    """
    Trusted if the two users have mutual friends (i.e. have
    previously made a transaction with the same person)
    """
    batchGraph = buildBatchGraph(batchFilePath)
    
    with open(streamFilePath) as streamFile, open(output3FilePath, "w") as outFile3:
        next(streamFile) # Skip header: 'time, id1, id2, amount, message'
        for line in streamFile:
            try:
                time, id1, id2, amt, msg = line.split(', ', 4)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            
            #lower = id1 if id1 < id2 else id2
            id1 = int(id1)
            id2 = int(id2)

            if isWithin(batchGraph, 4, id1, id2):
                outFile3.write("trusted\n")
                continue

            outFile3.write("unverified\n")
            

def usage():
    if sys.argv[0].startswith('./'):
        print "Usage: %s <path_to_batch> <path_to_streaming> <path_to_output1> <path_to_output2> <path_to_output3>" % sys.argv[0]
    else:
        print "Usage: python %s <path_to_batch> <path_to_streaming> <path_to_output1> <path_to_output2> <path_to_output3>" % sys.argv[0]
    sys.exit(1)


if __name__ == '__main__':

    try:
        batchFilePath = sys.argv[1]
        streamFilePath = sys.argv[2]
        output1FilePath = sys.argv[3]
        output2FilePath = sys.argv[4]
        output3FilePath = sys.argv[5]
    except IndexError as e:
        usage()

    try:
        feature1(batchFilePath, streamFilePath, output1FilePath)
        feature2(batchFilePath, streamFilePath, output2FilePath)
        feature3(batchFilePath, streamFilePath, output3FilePath)
    except IOError as e:
        print e
        usage()

