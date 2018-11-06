#!/usr/bin/env python2.7

import boto3
import json
import re
import datetime
from decimal import Decimal
import argparse

parser = argparse.ArgumentParser(description='Compare the Instance\'s actual price and spot price.',
                                 usage='''\n\
                                 $ spot-price.py -h \n\
                                 $ spot-price.py --region us-east-1 --instance-type m5.xlarge --product-type Linux/UNIX --output text --price-type all --mode compare \n\
                                 $ python spot-price.py --region us-east-1 --instance-type m5.xlarge c5.xlarge --product-type Linux/UNIX --output json --price-type all --mode show''')
parser.add_argument('--region', type=str, help='Region\'s code, like us-east-1', required=True)
parser.add_argument('--product-type', type=str, default='Linux/UNIX', help='(default: %(default)s)', choices=['Linux/UNIX', 'SUSE Linux', 'Windows', 'Linux/UNIX (Amazon VPC)', 'SUSE Linux (Amazon VPC)', 'Windows (Amazon VPC)'])
parser.add_argument('--mode', type=str, default='show', help='(default: %(default)s)', choices=['show', 'compare'])
parser.add_argument('--output', type=str, default='text', help='(default: %(default)s)', choices=['text', 'json'])
parser.add_argument('--price-type', type=str, default='all', help='(default: %(default)s)', choices=['all', 'ecu', 'memory', 'economy'])
parser.add_argument('--instance-type', nargs='+', help='(t1.micro or t1.micro t2.micro ...)', default=[], required=True)
args = parser.parse_args()

price = boto3.client('pricing')

priceList = {}
betterPrice = {}
betterPrice['economy'] = 0
betterECUPrice = {}
betterECUPrice['pricePerEcu'] = 100
betterMemoryPrice = {}
betterMemoryPrice['pricePerMemory'] = 100

productTypes = {
  'Linux/UNIX': {
    'os': 'LINUX'
  },
  'SUSE Linux': {
    'os': 'SUSE'
  },
  'Windows': {
    'os': 'Windows'
  },
  'Linux/UNIX (Amazon VPC)': {
    'os': 'LINUX'
  },
  'SUSE Linux (Amazon VPC)': {
    'os': 'SUSE'
  },
  'Windows (Amazon VPC)': {
    'os': 'Windows'
  }
}

regions = {
  'us-east-1': {
    'location': 'US East (N. Virginia)'
  },
  'us-east-2': {
    'location': 'US East (Ohio)' 
  },
  'us-west-1': {
    'location': 'US West (N. California)'
  },
  'us-west-2': {
    'location': 'US West (Oregon)'
  },
  'ap-south-1': {
    'location': 'Asia Pacific (Mumbai)'
  },
  'ap-northeast-3': {
    'location': 'Asia Pacific (Osaka-Local)'
  },
  'ap-northeast-2': {
    'location': 'Asia Pacific (Seoul)'
  },
  'ap-southeast-1': {
    'location': 'Asia Pacific (Singapore)'
  },
  'ap-southeast-2': {
    'location': 'Asia Pacific (Sydney)'
  },
  'ap-northeast-1': {
    'location': 'Asia Pacific (Tokyo)'
  },
  'ca-central-1': {
    'location': 'Canada (Central)'
  },
  'eu-central-1': {
    'location': 'EU (Frankfurt)'
  },
  'eu-west-1': {
    'location': 'EU (Ireland)'
  },
  'eu-west-2': {
    'location': 'EU (London)'
  },
  'eu-west-3': {
    'location': 'EU (Paris)'
  },
  'sa-east-1': {
    'location': 'South America (Sao Paulo)'
  }
}

for instanceType in args.instance_type:

  responseActualPrice = price.get_products(
      ServiceCode="AmazonEC2",
      Filters=[
        {
          'Field': 'ServiceCode',
          'Type': 'TERM_MATCH', 
          'Value': 'AmazonEC2'
        },
        {
          'Field': 'instanceType', 
          'Type': 'TERM_MATCH', 
          'Value': instanceType
        }, 
        {
          'Field': 'location', 
          'Type': 'TERM_MATCH', 
          'Value': regions[args.region]['location']
        },
        {
          'Field': 'operatingSystem', 
          'Type': 'TERM_MATCH', 
          'Value': productTypes[args.product_type]['os']
        },
        {
          'Field': 'preInstalledSw',
          'Type': 'TERM_MATCH',
          'Value': 'NA'
        },
        {
          'Field': 'tenancy',
          'Type': 'TERM_MATCH',
          'Value': 'Shared'
        }
    ], 
    FormatVersion="aws_v1", 
    MaxResults=1
  )

  if responseActualPrice['PriceList'] != []:

    priceList[instanceType] = {}

    data = json.loads(responseActualPrice['PriceList'][0])

    terms = data['terms']['OnDemand'].items()[0][1]['priceDimensions'].items()[0][1]
    attributes = data['product']['attributes']

    if ("On Demand" in terms['description'] and "BYOL" not in terms['description']) or ("Unused Reservation" in terms['description']):
            
      actualPrice = Decimal(terms['pricePerUnit']['USD'])

      memory = float(re.sub(r' GiB', '', attributes['memory']))
      cpu = int(attributes['vcpu'])
      if (instanceType.split(".")[0] != 't1') and (instanceType.split(".")[0] != 't2') and (instanceType.split(".")[0] != 't3'):
        ecu = int(attributes['ecu'])
      else:
        ecu = 0

      spot = boto3.client('ec2', region_name=args.region)

      responseSpotPrice = spot.describe_spot_price_history(
          EndTime=datetime.datetime.now(),
          InstanceTypes=[instanceType],
          ProductDescriptions=[args.product_type],
          StartTime=datetime.datetime.now() - datetime.timedelta(minutes=5)
      )

      for spotPrice in responseSpotPrice['SpotPriceHistory']:
        payload = {
          'type': instanceType,
          'actualPrice': float(actualPrice),
          'os': productTypes[args.product_type]['os'],
          'productDescription': args.product_type,
          'memory': memory,
          'cpu': cpu,
          'ecu': ecu,
          'spotPrice': float(spotPrice['SpotPrice']),
          'AvailabilityZone': spotPrice['AvailabilityZone'],
          'pricePerMemory': float(spotPrice['SpotPrice'])/memory,
          'pricePerEcu': float(0) if ecu == 0 else float(spotPrice['SpotPrice'])/ecu,
          'economy': "{0:.2f}".format(float(0) if actualPrice == 0 else 100-((float(spotPrice['SpotPrice']) * 100)/float(actualPrice))),
          'timestamp': spotPrice['Timestamp'].replace(microsecond=0).isoformat()
        }

        if args.mode == 'compare':
          if payload['economy'] > betterPrice['economy']:
            betterPrice = payload
          if payload['pricePerMemory'] < betterMemoryPrice['pricePerMemory']:
            betterMemoryPrice = payload
          if payload['pricePerEcu'] < betterECUPrice['pricePerEcu']:
            betterECUPrice = payload
        else:
          if args.output == 'text':
            print('--- %s price --- \ninstance type: %s \nregion: %s \nzone: %s \nvCPU: %s \necu: %s \nmemory: %s \nOnDemand price: %s \nSpot price: %s \neconomy: %s %%'
            % (instanceType, payload['type'], regions[args.region]['location'], payload['AvailabilityZone'], payload['cpu'], payload['ecu'], payload['memory'], payload['actualPrice'], payload['spotPrice'], payload['economy']))
            print('')
          else:
            priceList[instanceType][spotPrice['AvailabilityZone']] = payload

if args.mode == 'compare' and args.output == 'text':
  print('')
  if args.price_type == 'economy' or args.price_type == 'all':
    print('--- best economy price --- \ninstance type: %s \nregion: %s \nzone: %s \nvCPU: %s \necu: %s \nmemory: %s \nOnDemand price: %s \nSpot price: %s \neconomy: %s %%'
          % (betterPrice['type'], regions[args.region]['location'], betterPrice['AvailabilityZone'], betterPrice['cpu'], betterPrice['ecu'], betterPrice['memory'], betterPrice['actualPrice'], betterPrice['spotPrice'], betterPrice['economy']))
    print('')
  if args.price_type == 'memory' or args.price_type == 'all':
    print('--- best memory price --- \ninstance type: %s \nregion: %s \nzone: %s \nvCPU: %s \necu: %s \nmemory: %s \nOnDemand price: %s \nSpot price: %s \neconomy: %s %%'
          % (betterMemoryPrice['type'], regions[args.region]['location'], betterMemoryPrice['AvailabilityZone'], betterMemoryPrice['cpu'], betterMemoryPrice['ecu'], betterMemoryPrice['memory'], betterMemoryPrice['actualPrice'], betterMemoryPrice['spotPrice'], betterMemoryPrice['economy']))
    print('')
  if args.price_type == 'ecu' or args.price_type == 'all':
    print('--- best ecu price --- \ninstance type: %s \nregion: %s \nzone: %s \nvCPU: %s \necu: %s \nmemory: %s \nOnDemand price: %s \nSpot price: %s \neconomy: %s %%'
          % (betterECUPrice['type'], regions[args.region]['location'], betterECUPrice['AvailabilityZone'], betterECUPrice['cpu'], betterECUPrice['ecu'], betterECUPrice['memory'], betterECUPrice['actualPrice'], betterECUPrice['spotPrice'], betterECUPrice['economy']))
    print('')
elif args.mode == 'compare' and args.output == 'json':
  json_output = {}
  if args.mode == 'compare':
    if args.price_type == 'economy' or args.price_type == 'all':
      json_output['economy'] = betterPrice
    if args.price_type == 'memory' or args.price_type == 'all':
      json_output['memory'] = betterMemoryPrice
    if args.price_type == 'ecu' or args.price_type == 'all':
      json_output['ecu'] = betterECUPrice
    print(json.dumps(json_output,sort_keys=True))
elif args.mode == 'show' and args.output == 'json':
  print(json.dumps(priceList,sort_keys=True))