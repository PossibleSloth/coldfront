#!/usr/bin/python

import sys
import requests
import boto3
import argparse
from Queue import Queue
from threading import Thread

DOMAIN_CHECKERS = 10

def check_domain_worker(q1, q2):
    while True:
        domain = q1.get()
        if check_domain(domain):
            q2.put(domain)
        q1.task_done()


def check_cf_worker(q2, distribution_id):
    while True:
        domain = q2.get()
        if is_url_available(domain, distribution_id):
            print(domain)
            sys.stdout.flush()
        q2.task_done()


def check_domain(domain):
    try:
        result = requests.get("http://" + domain)
        return "The request could not be satisfied" in result.content
    except:
        return False


def is_url_available(url, distribution_id):
    cf = boto3.client('cloudfront')
    get_config = cf.get_distribution_config(Id=distribution_id)
    get_config['DistributionConfig']['Aliases']['Items'] = [url]
    get_config['DistributionConfig']['Aliases']['Quantity'] = 1
    try:
        update_request = cf.update_distribution(DistributionConfig=get_config['DistributionConfig'],
                                                Id=distribution_id,
                                                IfMatch=get_config['ETag'])
    except Exception as e:
        if type(e).__name__ == 'CNAMEAlreadyExists':
            return False
        else:
            sys.stderr.write("Error for CNAME %s: %s" % (url, e))
            return False

    return True


def run():
    parser = argparse.ArgumentParser(description='Scan that shit')
    parser.add_argument('-f', '--filename')
    parser.add_argument('-d', '--domain')
    args = parser.parse_args()

    distributions = ['EQ1DEE6GRXPPF']

    if args.domain:
        if is_url_available(args.domain, distributions[0]):
            print("that domain can be H4X0R3D")
        else:
            print("someone owns that domain")

    else:
        q1 = Queue()
        q2 = Queue()

        for i in range(0, DOMAIN_CHECKERS):
            worker = Thread(target=check_domain_worker, args=(q1, q2))
            worker.setDaemon(True)
            worker.start()

        for d in distributions:
            worker = Thread(target=check_cf_worker, args=(q2, d))
            worker.setDaemon(True)
            worker.start()

        if args.filename:
            with open(args.filename, 'r') as fd:
                domains = [line.rstrip('\n') for line in fd]
                for d in domains:
                    q1.put(d)

        else:
            for line in sys.stdin:
                q1.put(line.strip('.\n'))

        q1.join()
        q2.join()



if __name__=="__main__":
    run()
