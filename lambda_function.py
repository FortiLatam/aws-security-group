import json
import boto3

ec2 = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

def lambda_handler(event, context):
    print(event)
    client_ip = event['multiValueHeaders']['srcip']
    group_name = event['multiValueHeaders']['sgname']
    
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'private-ip-address', 
                'Values': client_ip,
            },
        ]
    )
    
    instance_id = (response['Reservations'][0]['Instances'][0]['InstanceId'])
    vpc_id = (response['Reservations'][0]['Instances'][0]['VpcId'])

    response = ec2.describe_security_groups(
        Filters=[
            {
                'Name': 'group-name',
                'Values': group_name,
            },
            {
                'Name': 'vpc-id',
                'Values': [vpc_id],
            },
        ]
    )
    group_id = response['SecurityGroups'][0]['GroupId']

    result = ec2_resource.Instance(instance_id).modify_attribute(Groups=[group_id]) 
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }

