# Change AWS Security Group

This repo helps you to automate the change of a security group for an instance in AWS using Fortigate automation stitches https://docs.fortinet.com/document/fortigate/7.4.0/administration-guide/139441/automation-stitches. 

## Use case

Imagine you want to isolate an EC2 from communicating with other EC2s in the same subnet or with some host on the internet after it downloads (or tries to) malware. It could help you to prevent other critical problems and by isolating the EC2 you can investigate the event further.

## Disclaimer

This is a work in progress. There are many things to improve, as error handling, not EC2 instances, better ways to do, etc. Feel free to send your PRs.

## Overview

This consists of:
- Creating a Lambda
- Creating an API gateway
- Changing it for private endpoint
- Creating Security Groups
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
- Your policy should be like the [IAM-Policy.json]
- Click "Next" and "Save changes". Close IAM browser tab

- Back to Lambda page, click "Code" top menu
- Double click "lambda_function.py" on the left. Delete all the content on the right pane
- Paste the content from file [lambda_function.py]
- Click "Deploy"


## Creating an API gateway

- Still in Lambda page, click "Add trigger" on "Function overview" 
- Select as the source "API Gateway"
- "Create a new API"
- "REST API"
- Security: API Key
- Click "Add"
- It will redirect you to Lambda page under "Configuration" menu. Submenu "Triggers".

## Changing it for private endpoint
- If your FortiGate communicates with Lambda using a VPC Endpoint (default for some CloudFormation templates provided by Fortinet) you should change the API Gateway to Private. If it is not your case, skip to the next section [Creating Security Groups](#creating-security-groups) 
- Open a new browser tab, in AWS console and go to VPC
- Click menu "Endpoints" and copy the VPC Endpoint ID from Fortigate VPC (service name ends with execute-api)
- Back to Lambda page, in "Triggers" submenu, click the API Gateway previously created
- Go to "Settings"
- Change the "Endpoint Type" to "Private". Scroll down and "Save Changes"
- Besides the API gateway name you will see an ID like "ChangeSG-API (2ytbk3v7fj)". This "2ytbk3v7fj" is your "API ID"
- Go to menu "Resource Policy" and paste the content below

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "execute-api:Invoke",
            "Resource": "arn:aws:execute-api:your-aws-region:your-aws-account-number:your-API-ID/*",
            "Condition": {
                "StringEquals": {
                    "aws:sourceVpce": "your-vpc-endpoint-id"
                }
            }
        }
    ]
}
```

- You can check an example in [resource-policy.json]
- Click "Save"
- Click menu "Resources" then in the menu "Actions" click "Deploy API"
- In "Deployment stage" choose "default". Click "Deploy"

## Creating Security Groups
- Now you will configure the security groups with no rules in it. This or these security groups will be attached to the EC2 in a case of a security event
- In AWS Console go to EC2
- Scroll down to Security Groups menu and click "Create security group"
- Give a "Security group name" (eg sg_no_access)
- Give a description of your choice
- Select the VPC
- Delete the "outbound rule" created

> **Note** 
> In this example, we are blocking all inbound and outbound traffic, so must be no rules in the security group. However, it is up to you, change it as you want.

- Click "Create security group"
- As SG (security group) is VPC based, please, create one in each VPC inspected by FortiGate using the same name

## Configuring automation stitch on FortiGate
- Access your FortiGate GUI
- Go to "Security Fabric" then "Automation"
- In "Stitch", click "Create New"
- Give a name (eg: ChangeSG)
- In "Add Trigger" click "Create"
- Select "Virus Logs". Give a name (eg Virus) and click "OK"
- Click "Virus" and "Apply"
- Click "Add Action" and click "Create"
- Select "AWS Lambda" and give a name (eg Lambda-ChangeSG)
- In URL paste your API Gateway URL. To get it, open a new browser tab, AWS Console -> Lambda -> Functions -> Select the lambda created -> Click "API Gateway" in Function Overview -> under Triggers menu check the API endpoint (this is your URL) -> expand "Details" and take a note of the API key

> **Note** 
> If you dont see an API Key in the details, you will need to add an API Key to you API Gateway. Please check this link https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-usage-plans-with-console.html

- Still in Fortigate AWS Lambda creation page, paste the API Key in its field
- Under HTTP header add:
    Name: srcip
    Value: %%log.srcip%%
- Click to add new HTTP Header, then:
    Name: sgname
    Value: the-name-of-your-security-group
- Click Ok
- Click the AWS Lambda name created and "Apply"
- Click Ok

## Finish

Great! now you have all configured. If you want to test, enable an AV filter in a Firewall policy and try to download EICAR, for example.

wget http://www.eicar.org/download/eicar.com.txt

