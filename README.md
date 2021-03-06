#PayMo
Digital-Wallet program with fraud detection

###Project:
Create a digital wallet system, that allows users to make transactions (i.e.
make or accept payments to others).  For this project, we will implement 3
features.
* Feature 1: A transaction is marked unverified if the 2 users have never
made a transaction with each other previously.  If they have, it should
be marked trusted.
* Feature 2: A transaction is marked trusted if the 2 users have a mutual
friend.
* Feature 3: A transaction is marked trusted as long as the 2 users are
within 4 degrees (trusted if no more than 3 people between them).

Instead of using an API to stream data, the focus is more on the data
engineering side.  Thus, batch_payment.csv will be used to build the
initial graph (representing previous transactions), and we'll read
stream_payment.csv line by line, as if they are incoming transactions.


###Pre-built modules:
I imported very few modules for my program in order to focus on using the
best data structures, and writing fundamental search algorithms on my own
with some modifications.  I did import some though:

* sys: used for command line args, and to exit on incorrect arguments
* time: used for testing, in order to improve algorithm speed and efficiency

###Executing my program:
I used **Python 2.7** to write my program, and I was able to run it on 
OS X El Capitan (v10.11.3) as well as Ubuntu 12.04.  After cloning and
cd'ing into my PayMo repo, my antifraud.py script can be executed via:

> ./run.sh

This runs my program with 5 parameters: batch_payment.txt, stream_payment.txt,
output1.txt, output2.txt, and output3.txt  (one output file for each feature).


###NOTES:
* I created a separate method for feature 1 to build the batch graph because
for that feature, you can always have the lower user id as the key

* For feature 2, I decided to get immediate friends for id1 and id2, and 
then find the intersection using isdisjoint().  All you need is one mutual
friend and it will be 'trusted'.  Otherwise, it's 'unverified'.

* Feature 3 is definitely the most time costly.  I tried really hard to do
it without using any other tools, frameworks, modules, databases, and on a
single machine.  In general, up to 4th degree friends in a dense graph 
will be difficult.  The way I implemented it was somewhat like a breadth
first search, but stopping after k iterations (where k == 4 in our case).
The algorithm as it is, sometimes takes a long time depending on the user.
However, I thought of some different ways you could implement feature 3,
and I would have loved to try it if given more time:
    * After a streaming payment, add to the batch graph.  A person is
much more likely to make a transaction with a friend or someone they have
in the past already.
    * After a transaction, definitely CACHE!  Perhaps you could use a 
dictionary to help remember user's who have made transactions after using
my feature 3 algorithm.
    * I was considering doing a breadth-first or depth-first search, but
keep track of paths and hash them.  Then lookup times could be much faster
    * AND MY FAVORITE SOLUTION: take the time building the batch graph
or setting up your data structure BEFORE you start processing the streaming
file.  Perhaps you can use a cluster or distribute the workload for setting
everything up.  But once everything is set up, then you can process the 
streaming file, where lookups can be linear (possibly even constant if the
graph isn't too big).  For example, you could create a dictionary where the
key is the user id, and the value is a list of all user ids that are within
4 degrees.  This way, the time complexity is linear, and most importantly,
the user experience is much better!

###FEATURE3 UPDATE:
* I still believe all that I mentioned above will help  (i.e. continuously
adding to the build graph w/ incoming streaming payments, building a graph 
and caching before streaming so that the user experience is smooth, etc)

* However, I dramatically improved processing time for feature 3!  I got 
my result to an average of less than 0.0001s per streaming payment.

* The idea was, for each streaming payment take the 2 user ids and expand
each network out 2 degrees.  If you take the intersection of these 2 
network sets, an empty set would indicate the 2 users are not within
4 degrees.  In addition, along this process, continuously checking if 
one user is within the other's network saved time as well.


###RESULTS
I was able to scale the full batch_payment.csv and stream_payment.csv files
from dropbox!  In both files, each line represented a payment transaction.
Excluding the headers, each file had:
batch_payment.csv -->  3938360L
stream_payment.csv --> 3000000L

* Building the batch graph
    * On average, this took about 11s
* Feature1
    * The streaming file took approximately 7.9s
    * This is about 2.6 microseconds per transaction
    * output1: 1456949 trusted, 1543051 unverified
* Feature2
    * The streaming file took approximately 9.4s
    * This is about 3.1 microseconds per transaction
    * output2: 2347130 trusted, 652870 unverified
* Feature3
    * The streaming file took approximately 40m 06s
    * This is about 0.8 milliseconds per transaction
    * output3: 2775426 trusted, 224574 unverified

Pretty impressive, the algorithm takes less than a millisecond to verify 
if two users are within 4 degrees of separation!
