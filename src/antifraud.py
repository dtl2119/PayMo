#!/usr/bin/python

import sys
from datetime import datetime


def buildBatchGraph(batchFilePath):
    """
    Builds a graph from a batch payment.csv file,
    which contains previous user payment transactions.
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
            batchGraph.setdefault(id1, set()).add(id2)
            batchGraph.setdefault(id2, set()).add(id1)

    return batchGraph


def feature1(batchGraph, streamFilePath, output1FilePath):
    """
    When anyone makes a payment to another user, 
    they'll be notified if they've never made a 
    transaction with that user before.
    """

    with open(streamFilePath) as streamFile, open(output1FilePath, "w") as outFile1:
        next(streamFile) # Skip header: 'time, id1, id2, amount, message'
        for line in streamFile:
            try:
                time, id1, id2, amt, msg = line.split(', ', 4)
            except ValueError as e:
                print "Unable to parse line: %s" % line
                continue
            
            id1 = int(id1)
            id2 = int(id2)

            # Unverified if either user hasn't made a previous transaction
            if id1 not in batchGraph or id2 not in batchGraph:
                outFile1.write("unverified\n")
                continue

            if id1 in batchGraph[id2]:
                outFile1.write("trusted\n")
            else:
                outFile1.write("unverified\n")


def feature2(batchGraph, streamFilePath, output2FilePath):
    """
    Trusted if the two users have mutual friends (i.e. have
    previously made a transaction with the same person)
    """

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
            id1Friends = batchGraph[id1] if id1 in batchGraph else set()
            id2Friends = batchGraph[id2] if id2 in batchGraph else set()

            # unverified if one of them has never made a transaction
            if not id1Friends or not id2Friends:
                outFile2.write("unverified\n")
                continue

            # Trusted if they're immediate friends too
            if id2 in id1Friends or id1 in id2Friends:
                outFile2.write("trusted\n")
                continue

            # Check the set intersection
            if id1Friends.isdisjoint(id2Friends):
                outFile2.write("unverified\n")
                continue
                
            outFile2.write("trusted\n")



def isWithinFour(graph, id1, id2):
    """
    Helper function for feature3.  This returns True if id1
    and id2 are within 4 degrees, else it returns False
    """

    # If neither have made a previous transaction, unverified
    if id1 not in graph or id2 not in graph:
        return False

    id1Network = graph[id1] # Friend set of user id1
    id2Network = graph[id2] # Friend set of user id2
   
    # Immediate Friends
    if id2 in id1Network:
        return True

    # Mutual Friends (1 degree)
    if not id1Network.isdisjoint(id2Network):
        return True

    # Next loops: for both of the users, keep expanding
    # their friend's networks (union: O(n+m) for sets), 
    # but keep checking if the other user is in it along
    # the way.
    for user in id1Network:
        id1Network = id1Network | graph[user]
        if id2 in id1Network:
            return True

    for user in id2Network:
        id2Network = id2Network | graph[user]
        if id1 in id2Network:
            return True


    # At this point, we have two sets of users, two degrees
    # out from both id1 and id2.  If the intersection is
    # the empty set, isdisjoint returns true, and id1 and id2
    # are not within 4 degrees; thus unverified
    if id1Network.isdisjoint(id2Network):
        return False

    # Return True if the intersection is not empty
    return True
        
    

def feature3(batchGraph, streamFilePath, output3FilePath):
    """
    Trusted if the two users have mutual friends (i.e. have
    previously made a transaction with the same person)
    """
    
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

            if isWithinFour(batchGraph, id1, id2):
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
        batchGraph = buildBatchGraph(batchFilePath)
        
        feature1(batchGraph, streamFilePath, output1FilePath)
        feature2(batchGraph, streamFilePath, output2FilePath)
        feature3(batchGraph, streamFilePath, output3FilePath)
    except IOError as e:
        print e
        usage()

