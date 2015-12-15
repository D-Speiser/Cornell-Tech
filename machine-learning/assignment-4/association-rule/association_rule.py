import pandas as pd
import numpy as np
import apriori # adapted from Harrington 11.5
import random
import re

RAW_DATA = pd.read_csv("data/votesmart_20bill.txt", header=None, skiprows=1, skip_footer=1, engine='python')
RAW_MEANING = pd.read_csv("data/votesmart_20bill_meaning.txt", sep="\n", header=None, skiprows=range(0,100,2), skip_footer=1, engine='python')

# Parse raw data into transaction records
def map_transactions (raw_data):
    strip = re.compile('[^\d.p]+')
    transactions = {}
    k = 0
    
    for data in raw_data:
        parsed = strip.sub("", data)
        if parsed.isdigit() == False:
            k += 1
            transactions[k] = []
        else:
            transactions[k].append(int(parsed))
    return transactions

def map_meaning (raw_meaning):
    strip = re.compile("\'.*\'")
    parsed = []
    for i in raw_meaning:
        parsed.append(strip.search(i).group())
    return dict(zip(range(0,len(raw_meaning)), parsed))

def get_meaning (i, meaning):
    print meaning[i]

# Extract transactions and meanings
transactions = map_transactions(RAW_DATA[0])
meaning = map_meaning(RAW_MEANING[0])

for threshold in np.arange(0.5, 0.25, -0.05):
    itemsets, support = apriori.apriori(transactions.values(), minSupport=threshold)
    print "THRESHOLD: ", threshold
    print len(itemsets), "itemsets of length:"
    print [len(i) for i in itemsets]
    print "\n"

itemset, support = apriori.apriori(transactions.values(), minSupport=0.3)
for threshold in np.arange(0.7, 0.99, 0.05):
    print "THRESHOLD: ", threshold
    rules = apriori.generateRules(itemset, support, minConf=threshold)
    print "\n"

def get_meaning (rule, meaning):
    condition, result = [], []
    for c in rule[0]:
        condition.append(meaning[c])
    for r in rule[1]:
        result.append(meaning[r])
    
    print "IF:", " AND ".join(condition)
    print "THEN:", " AND ".join(result)
    print "CONFIDENCE: ", rule[2], "\n\n"

for i in range(6):
    get_meaning(random.choice(rules), meaning)
