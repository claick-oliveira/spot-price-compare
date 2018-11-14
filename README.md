# Spot Price Compare

This script was developed to help you to compare the Spot Price between instances types and which the actual saving percentage (more information about spot [click here](https://aws.amazon.com/ec2/spot/)).

## Prerequisites

You need this things to run the script:

* [AWS Account](https://aws.amazon.com/)
* [aws-cli](https://aws.amazon.com/cli/)
* [AWS Credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
* [Python](https://www.python.org/)
* [Pip](https://pypi.org/project/pip/)
* [Git](https://git-scm.com/)

And install the modules with pip:

```
pip install -r requirements.txt
```

## Usage

To use this script you need to pass some information, example:

```
python spot-price.py --region us-east-1 --instance-type m5.xlarge --product-type Linux/UNIX --output text --price-type all --mode compare
```

The outputs can be:

### Text

```
--- best economy price ---
instance type: m5.xlarge
region: US East (N. Virginia)
zone: us-east-1f
vCPU: 4
ecu: 16
memory: 16.0
OnDemand price: 0.192
Spot price: 0.0734
economy: 61.77 %

--- best memory price ---
instance type: m5.xlarge
region: US East (N. Virginia)
zone: us-east-1f
vCPU: 4
ecu: 16
memory: 16.0
OnDemand price: 0.192
Spot price: 0.0734
economy: 61.77 %

--- best ecu price ---
instance type: m5.xlarge
region: US East (N. Virginia)
zone: us-east-1f
vCPU: 4
ecu: 16
memory: 16.0
OnDemand price: 0.192
Spot price: 0.0734
economy: 61.77 %
```

### Json

```json
{
  "economy": {
    "AvailabilityZone": "us-east-1f",
    "actualPrice": 0.192,
    "cpu": 4,
    "economy": "61.46",
    "ecu": 16,
    "memory": 16.0,
    "os": "LINUX",
    "pricePerEcu": 0.004625,
    "pricePerMemory": 0.004625,
    "productDescription": "Linux/UNIX",
    "spotPrice": 0.074,
    "timestamp": "2018-11-06T15:54:20+00:00",
    "type": "m5.xlarge"
  },
  "ecu": {
    "AvailabilityZone": "us-east-1f",
    "actualPrice": 0.192,
    "cpu": 4,
    "economy": "61.46",
    "ecu": 16,
    "memory": 16.0,
    "os": "LINUX",
    "pricePerEcu": 0.004625,
    "pricePerMemory": 0.004625,
    "productDescription": "Linux/UNIX",
    "spotPrice": 0.074,
    "timestamp": "2018-11-06T15:54:20+00:00",
    "type": "m5.xlarge"
  },
  "memory": {
    "AvailabilityZone": "us-east-1f",
    "actualPrice": 0.192,
    "cpu": 4,
    "economy": "61.46",
    "ecu": 16,
    "memory": 16.0,
    "os": "LINUX",
    "pricePerEcu": 0.004625,
    "pricePerMemory": 0.004625,
    "productDescription": "Linux/UNIX",
    "spotPrice": 0.074,
    "timestamp": "2018-11-06T15:54:20+00:00",
    "type": "m5.xlarge"
  }
}
```

### Table

```
+---------------+-------------------+----------------+------------+--------------------+------------------+---------------+
| instance type | Availability Zone | OnDemand Price | Spot Price | Percentage Economy | Price per Memory | Price per ECU |
+---------------+-------------------+----------------+------------+--------------------+------------------+---------------+
|   m5.xlarge   |     us-east-1f    |     0.192      |   0.0734   |       61.77        |    0.0045875     |   0.0045875   |
|   m5.xlarge   |     us-east-1f    |     0.192      |   0.0734   |       61.77        |    0.0045875     |   0.0045875   |
|   m5.xlarge   |     us-east-1f    |     0.192      |   0.0734   |       61.77        |    0.0045875     |   0.0045875   |
+---------------+-------------------+----------------+------------+--------------------+------------------+---------------+
```

## Interface

```
usage:
  $ spot-price.py -h
  $ spot-price.py --region us-east-1 --instance-type m5.xlarge --product-type Linux/UNIX --output text --price-type all --mode compare
  $ python spot-price.py --region us-east-1 --instance-type m5.xlarge c5.xlarge --product-type Linux/UNIX --output json --price-type all --mode show

Compare the Instance's actual price and spot price.

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       Region's code, like us-east-1
  --product-type {Linux/UNIX,SUSE Linux,Windows,Linux/UNIX (Amazon VPC),SUSE Linux (Amazon VPC),Windows (Amazon VPC)}
                        (default: Linux/UNIX)
  --mode {show,compare}
                        (default: show)
  --output {text,json,table}
                        (default: text)
  --price-type {all,ecu,memory,economy}
                        (default: all)
  --instance-type INSTANCE_TYPE [INSTANCE_TYPE ...]
                        (t1.micro or t1.micro t2.micro ...)
```

## Authors

* **Claick Oliveira** - *Initial work* - [claick-oliveira](https://github.com/claick-oliveira)