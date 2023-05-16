# Change AWS Security Group

This repo helps you to automate the change of a security group for an instance in AWS using Fortigate automation stitches https://docs.fortinet.com/document/fortigate/7.4.0/administration-guide/139441/automation-stitches. 

## Use case

Imagine you want to isolate an EC2 from comunicating with other EC2s in the same subnet or with some host on internet after it downloads (or try to) a malware. It could help you to prevent other critical problems and isolating the EC2 you can investigate the event further.

## Disclaimer

This is a work in progress. There are many things to improve, as error handling, not EC2 instances, better ways to do, etc. Feel free to send your PRs.

## Overview

This consists of:
- Creating a Lambda
- Creating an API gateway
- Changing it for private endpoint
- Configuring automation stitch on FortiGate

## Create new Lambda

- Go to your AWS Console
- Search for Lambda
- Click "Create function"
- Choose a function name (eg: ChangeSG)
- Runtime: Python 3.10
- Architecture: X86_64
- Click "Create function"
- It will redirect you to function page. Click menu "Configuration" then the submenu "Permissions"
- Click in the role name. It will open a new page with the IAM role created by default.
- In the IAM page, under "Permissions" click on the policy to open it
- Click "Edit" button
- Add the code below
```
		{
			"Effect": "Allow",
			"Action": [
				"ec2:DescribeInstances",
				"ec2:ModifyInstanceAttribute",
				"ec2:DescribeSecurityGroups"
			],
			"Resource": "*"
		}
```
- Your policy should be like the policy-file.json
- Click "Next" and "Save changes"


