# donation-analytics

This solution was developed with python 3.6

Required python modules:
 * sys
 * datetime
 * math
 * numpy

My approach is to use hash table lookups in order to efficiently select transactions that meet the criteria describing repeat donations within a particular zip code.

First, I assign each donation a unique id, roughly corresponding to its line number within the file itcont.txt. Each id is used as a key in a 'master' dictionary, whose values are dictionaries containing all the relevant information from itcont.txt, as well as a key,value pair that signals whether or not this transaction constitutes a repeat donation.

Additionally, I populate two more dictionaries:
 * The first indexes the transaction ids by the donor identification tuple (donor_name, donor_zip). This dictionary can be queried in order to determine whether a given donation constitutes a repeat donation.
 * The second indexes the transaction ids by the following tuple: (recipient_id, transaction_date, zip_code, is_repeat). This dictionary is used to efficiently select all the transaction ids from the past calendar year with the same recipient and zip code that are repeat donations.

During development, I noticed that the computation of the percentile was the most significant bottleneck. It turned out that I was sorting all the repeat donation amounts, which scaled poorly and was unnecessary. A little research showed that the numpy.partition() function was sufficient to compute the percentile information, and scaled more favorably.

I could have saved on system memory by using an integer to represent the date, rather than datetime.date objects. However, I enjoyed the convenience of the datetime module, and the memory requirement would scale linearly in the length of the input file, either way. I think this scaling is optimal since I need to keep track of the entire history of the donations. If I needed to be more careful about memory usage, I could design a similar algorithm around tables in a database rather than dictionaries in memory.

I noticed that some of the contributions are negative, which I presume to mean they were returned by the election candidate. Since this is meaningful information, I decided not to ignore these cases. However, since we only are performing this analysis on a partial history of the election data, this means that some of the lines in the output file could have a negative donation percentile and/or total donation amount.