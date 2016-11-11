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

This runs my program with 5 parameters: batch_payment.csv, stream_payment.csv,
output1.txt, output2.txt, and output3.txt  (one output file for each feature).


