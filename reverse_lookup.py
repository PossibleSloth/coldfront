#!/usr/bin/python

import sys
from sets import Set
from pymongo import MongoClient


CF_URLS_FILE = "cloudfront_urls"


def reverse_lookup(domain, collection, depth, seen):
    results = collection.find({"value": domain})
    depth -= 1
    for r in results:
        if not r['name'] in seen:
            seen.add(r['name'])
            print(r['name'])
            if depth > 1:
                reverse_lookup(r['name'], collection, depth, seen)
    sys.stdout.flush()


def run():
    client = MongoClient()
    db = client.cf
    collection = db.fdns

    seen = Set([])

    with open(CF_URLS_FILE, 'r') as fd:
        domains = [line.rstrip('\n') for line in fd]
        for domain in domains:
            reverse_lookup(domain, collection, 100, seen)

if __name__=="__main__":
    run()
