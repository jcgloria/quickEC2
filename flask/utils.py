import boto3
import paramiko
import requests
import os

class QuickEC2:
    AMAZON_AMI = 'ami-09ee0944866c73f62'
    UBUNTU_AMI = 'ami-0aaa5410833273cfe'
    def __init__(self, access_key, secret_key, region='us-east-1'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ec2 = boto3.client('ec2', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
        self.cf = boto3.client('cloudformation', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
        self.ownIp = requests.get('https://api.ipify.org').text + '/32'
        

    def get_instances(self,mock=False):
        if mock:
            return {'status': 'success', 'message': [{'name': 'mytest123', 'linuxType': 'amazon', 'publicIp': '18.135.96.158', 'privateIp': '10.0.0.143', 'status': 'running'},
                                                     {'name': 'othertest', 'linuxType': 'ubuntu', 'publicIp': '22.221.22.222', 'privateIp': '10.0.0.143', 'status': 'pending'}]}
        instances = []
        #check if vpc exists
        vpc_id = self.check_VPC()
        if vpc_id:
            try:
                aws_instances = self.ec2.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                for reservation in aws_instances['Reservations']:
                    for instance in reservation['Instances']:
                        instances.append({
                            'instanceId': instance['InstanceId'],
                            'name': [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'][0],
                            'linuxType': [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'LinuxType'][0],
                            'publicIp': '' if 'PublicIpAddress' not in instance else instance['PublicIpAddress'],
                            'privateIp': instance['PrivateIpAddress'],
                            'status': instance['State']['Name']
                        })
            except Exception as e:
                return {'status': 'error', 'message': e}
        return {'status': 'success', 'message': instances}
    
    def terminate_instance(self, instanceId, instanceName):
        try:
            # terminate instance
            print("terminating instance: " + instanceId)
            self.ec2.terminate_instances(InstanceIds=[instanceId])
            waiter = self.ec2.get_waiter('instance_terminated')
            print("waiting for instance to terminate...")
            waiter.wait(InstanceIds=[instanceId])
            # delete security group
            sg_name = instanceName+'-sg'
            sg_id = self.ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])['SecurityGroups'][0]['GroupId']
            print("removing security group: " + sg_name)
            self.ec2.delete_security_group(GroupId=sg_id)
            return {'status': 'success', 'message': 'Instance with id ' + instanceId + ' terminated successfully'}
        except Exception as e:
            return {'status': 'error', 'message': e}
    
    def stop_instance(self, instanceId):
        try:
            self.ec2.stop_instances(InstanceIds=[instanceId])
            return {'status': 'success', 'message': 'Instance with id ' + instanceId + ' stopped successfully'}
        except Exception as e:
            return {'status': 'error', 'message': e}
    
    def start_instance(self, instanceId):
        try:
            self.ec2.start_instances(InstanceIds=[instanceId])
            return {'status': 'success', 'message': 'Instance with id ' + instanceId + ' started successfully'}
        except Exception as e:
            return {'status': 'error', 'message': e}
            
    
    # Create a simple VPC with a public and private subnet, internet gateway, and route tables. 
    def create_VPC(self):
        #Check if VPC already exists
        vpc_id = self.check_VPC()
        if vpc_id:
            return {'status': 'error', 'message': 'VPC already exists'}
        try: 
            #Create VPC
            print('Creating VPC...')
            stackname = 'QuickEC2'
            self.cf.create_stack( StackName=stackname,TemplateBody=open('vpc.yaml', 'r').read())
            print('Waiting for VPC creation to complete...')
            self.cf.get_waiter('stack_create_complete').wait(StackName=stackname)
            print('VPC created successfully')
            return {'status': 'success', 'message': 'VPC created successfully'}
        except Exception as e:
            return {'status': 'error', 'message': e}
    
    #Check if managed VPC exists
    def check_VPC(self):
        try:
            vpcs = self.ec2.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': ['QuickEC2']}])
            return vpcs['Vpcs'][0]['VpcId'] if vpcs['Vpcs'] else None
        except Exception as e:
            return None
    
    #Delete managed VPC
    def delete_VPC(self):
        vpc_id = self.check_VPC()
        if vpc_id:
            try:
                #Delete VPC
                print('Deleting VPC...')
                stackname = 'QuickEC2'
                self.cf.delete_stack(StackName=stackname)
                print('Waiting for VPC deletion to complete...')
                self.cf.get_waiter('stack_delete_complete').wait(StackName=stackname)
                print('VPC deleted successfully')
                # Delete key pair
                print('Deleting key pair...')
                print('Key pair deleted successfully')
                return {'status': 'success', 'message': 'VPC deleted successfully'}
            except Exception as e:
                return {'status': 'error', 'message': e}
        else:
            return {'status': 'error', 'message': 'VPC does not exist'}
    
    #Launch an EC2 instance
    def launch(self, name, publicIp, type, sg_rules):
        try:
            self.gen_ssh_pair() #gen ssh pair if it doesn't exist
            if not self.check_VPC():
                return {'status': 'error', 'message': 'VPC does not exist'}
            #Check if there are no other instances with the same name
            instances = self.ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [name]}])
            if instances['Reservations']:
                return {'status': 'error', 'message': 'Instance with the same name already exists'}
            #Check if any security groups with the same name exist
            sgs = self.ec2.describe_security_groups(Filters=[{'Name': 'tag:Name', 'Values': [name+'-sg']}])
            if sgs['SecurityGroups']:
                return {'status': 'error', 'message': 'Security group with the same name already exists'}
            print("Creating security group...")
            sg_id = self.ec2.create_security_group(GroupName=name+'-sg', Description='QuickEC2 SG', VpcId=self.check_VPC(), TagSpecifications=[{'Tags': [{'Key': 'Name', 'Value': 'QuickEC2'}], 'ResourceType': 'security-group'}])['GroupId']
            sg_rules = [r for r in sg_rules if r['port'] > 0] #remove invalid ports
            for rule in sg_rules: #rule = {'port': 22, 'source': '1.2.3.4.5/32'}
                #map source to CIDR block
                if rule['source'] == 'public':
                    rule['source'] = '0.0.0.0/0'
                elif rule['source'] == 'vpc':
                    rule['source'] = '10.0.0.0/16'
                elif rule['source'] == 'own':
                    rule['source'] = self.ownIp
                else:
                    continue
                print("Adding rule for source", rule['source'], "and port", str(rule['port']) )
                self.ec2.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=[{'IpProtocol': 'tcp', 'FromPort': rule['port'], 'ToPort': rule['port'], 'IpRanges': [{'CidrIp': rule['source']}]}])
            subnet = self.ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [self.check_VPC()]}, {'Name': 'tag:SubnetExposure', "Values": ['Public' if publicIp else 'Private']}])['Subnets']
            print("Launching EC2 instance...")
            response = self.ec2.run_instances(MaxCount=1, MinCount=1,
                ImageId=QuickEC2.UBUNTU_AMI if type == 'ubuntu' else QuickEC2.AMAZON_AMI,
                Monitoring={'Enabled': False},
                TagSpecifications=[{'Tags': [{'Key': 'Name', 'Value': name}, {'Key': 'LinuxType', 'Value': type}], 'ResourceType': 'instance'}],
                InstanceType='t2.micro',
                SubnetId=subnet[0]['SubnetId'],
                KeyName='QuickEC2',
                SecurityGroupIds=[sg_id])
            iID = response['Instances'][0]['InstanceId']
            return {'status': 'success', 'message': 'Instance with instance ID: ' + iID + ' is being launched'}
        except Exception as e:
            return {'status': 'error', 'message': e}

    def get_key_path(self):
        if 'KEYSTORE_PATH' in os.environ:
            path = os.environ['KEYSTORE_PATH']
            if path[-1] != '/':
                path += '/'
        else:
            path = os.path.dirname(os.path.realpath(__file__)) + '/'
        return path + 'private_key.pem'
        
    def gen_ssh_pair(self):
        print('Checking if SSH keypair exists...')
        keypair = self.ec2.describe_key_pairs()
        for keypair in keypair['KeyPairs']:
            if keypair['KeyName'] == 'QuickEC2':
                return {'status': 'error', 'message': 'Keypair already exists'}
        print('Generating SSH keypair...')
        key = paramiko.RSAKey.generate(2048)
        path = '/keystore/' if 'KEYSTORE_PATH' in os.environ else os.path.dirname(os.path.realpath(__file__)) + '/'
        key.write_private_key_file(path + 'private_key.pem')
        with open(path + 'public_key.pem', 'w') as public_key_file:
            public_key_file.write(f'{key.get_name()} {key.get_base64()}')
        print('SSH keypair generated')
        self.ec2.import_key_pair(KeyName='QuickEC2', PublicKeyMaterial=open(path + 'public_key.pem', 'rb').read(), TagSpecifications=[{'Tags': [{'Key': 'Name', 'Value': 'QuickEC2'}], 'ResourceType': 'key-pair'}])
        return {'status': 'success', 'message': 'Keypair imported successfully'}