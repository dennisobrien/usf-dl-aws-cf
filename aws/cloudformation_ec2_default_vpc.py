"""

"""

from troposphere import (
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Tags,
    Template
)
from troposphere.ec2 import (
    BlockDeviceMapping,
    EBSBlockDevice,
    EIP,
    EIPAssociation,
    Instance,
    InternetGateway,
    NetworkAcl,
    NetworkAclEntry,
    NetworkInterfaceProperty,
    PortRange,
    Route,
    RouteTable,
    SecurityGroup,
    SecurityGroupRule,
    Subnet,
    SubnetNetworkAclAssociation,
    SubnetRouteTableAssociation,
    VPC,
    VPCGatewayAttachment
)
from troposphere.route53 import RecordSetType


t = Template()
t.add_version('2010-09-09')

keyname_param = t.add_parameter(
    Parameter(
        'KeyName',
        ConstraintDescription='must be the name of an existing EC2 KeyPair.',
        Description='Name of an existing EC2 KeyPair to enable SSH access to the instance',
        Type='AWS::EC2::KeyPair::KeyName',
    )
)

sshlocation_param = t.add_parameter(
    Parameter(
        'SSHLocation',
        Description=' The IP address range that can be used to SSH to the EC2 instances',
        Type='String',
        MinLength='9',
        MaxLength='18',
        Default='0.0.0.0/0',
        AllowedPattern="(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})",
        ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
    )
)

instanceType_param = t.add_parameter(
    Parameter(
        'InstanceType',
        Type='String',
        Description='EC2 instance type',
        Default='t2.micro',
        AllowedValues=[
            't1.micro',
            't2.micro',
            't2.small',
            't2.medium',
            'm1.small',
            'm1.medium',
            'm1.large',
            'm1.xlarge',
            'm2.xlarge',
            'm2.2xlarge',
            'm2.4xlarge',
            'm3.medium',
            'm3.large',
            'm3.xlarge',
            'm3.2xlarge',
            'c1.medium',
            'c1.xlarge',
            'c3.large',
            'c3.xlarge',
            'c3.2xlarge',
            'c3.4xlarge',
            'c3.8xlarge',
            'g2.2xlarge',
            'p2.xlarge',
            'r3.large',
            'r3.xlarge',
            'r3.2xlarge',
            'r3.4xlarge',
            'r3.8xlarge',
            'i2.xlarge',
            'i2.2xlarge',
            'i2.4xlarge',
            'i2.8xlarge',
            'hi1.4xlarge',
            'hs1.8xlarge',
            'cr1.8xlarge',
            'cc2.8xlarge',
            'cg1.4xlarge',
        ],
        ConstraintDescription='must be a valid EC2 instance type.',
    )
)

imageId_param = t.add_parameter(
    Parameter(
        'ImageId',
        Type='String',
        Description='ImageId to use for the EC2 instance.',
        Default='ami-a9d276c9',  # Assumes Debian based
    )
)

hostedZone_param = t.add_parameter(
    Parameter(
        'HostedZone',
        Type='String',
        Description='The DNS name of an existing Amazon Route 53 hosted zone'
    )
)

hostName_param = t.add_parameter(
    Parameter(
        'HostName',
        Type='String',
        Description='CNAME to prepend to the HostedZone'
    )
)


ref_stack_id = Ref('AWS::StackId')
ref_region = Ref('AWS::Region')
ref_stack_name = Ref('AWS::StackName')


ec2SecurityGroup = t.add_resource(
    SecurityGroup(
        'InstanceSecurityGroup',
        GroupDescription='Enable Inbound Access',
        SecurityGroupIngress=[
            SecurityGroupRule(
                IpProtocol='tcp',
                FromPort='22',
                ToPort='22',
                CidrIp=Ref(sshlocation_param)),
            SecurityGroupRule(
                IpProtocol='tcp',
                FromPort='8888',
                ToPort='8898',
                CidrIp='0.0.0.0/0')],
    )
)


ec2Instance = t.add_resource(
    Instance(
        "Ec2Instance",
        InstanceType=Ref(instanceType_param),
        SecurityGroupIds=[Ref(ec2SecurityGroup)],
        ImageId=Ref(imageId_param),
        KeyName=Ref(keyname_param),
        BlockDeviceMappings=[
            BlockDeviceMapping(
                DeviceName="/dev/sda1",
                Ebs=EBSBlockDevice(
                    VolumeSize="128",
                    VolumeType="gp2",
                )
            ),
        ],
        Tags=Tags(
            Application=ref_stack_id,
            Network="Public",
            Rev="0.0.3"
        ),
    )
)

ec2EIP = t.add_resource(
    EIP(
        "ec2EIP",
        InstanceId=Ref(ec2Instance),
        Domain='vpc',
    )
)

hostRecordSet = t.add_resource(
    RecordSetType(
        "hostRecordSet",
        HostedZoneName=Join("", [Ref(hostedZone_param), "."]),
        Comment="DNS name for my instance.",
        Name=Join(".", [Ref(hostName_param), Ref(hostedZone_param)]),
        Type="A",
        TTL="900",
        ResourceRecords=[GetAtt("Ec2Instance", "PublicIp")],
    )
)

t.add_output([
    Output(
        "InstanceId",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(ec2Instance),
    ),
    Output(
        "AZ",
        Description="Availability Zone of the newly created EC2 instance",
        Value=GetAtt(ec2Instance, "AvailabilityZone"),
    ),
    Output(
        "PublicIP",
        Description="Public IP address of the newly created EC2 instance",
        Value=GetAtt(ec2Instance, "PublicIp"),
    ),
    Output(
        "PrivateIP",
        Description="Private IP address of the newly created EC2 instance",
        Value=GetAtt(ec2Instance, "PrivateIp"),
    ),
    Output(
        "PublicDNS",
        Description="Public DNSName of the newly created EC2 instance",
        Value=GetAtt(ec2Instance, "PublicDnsName"),
    ),
    Output(
        "PrivateDNS",
        Description="Private DNSName of the newly created EC2 instance",
        Value=GetAtt(ec2Instance, "PrivateDnsName"),
    ),
    Output(
        "DomainName",
        Value=Ref(hostRecordSet)
    ),
])

print(t.to_json())
