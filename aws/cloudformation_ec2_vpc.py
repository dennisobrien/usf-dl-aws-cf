"""

"""

from troposphere import (
    GetAtt,
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


ref_stack_id = Ref('AWS::StackId')
ref_region = Ref('AWS::Region')
ref_stack_name = Ref('AWS::StackName')


# export vpcId=`aws ec2 create-vpc --cidr-block 10.0.0.0/28 --query 'Vpc.VpcId' --output text`
# aws ec2 modify-vpc-attribute --vpc-id $vpcId --enable-dns-support "{\"Value\":true}"
# aws ec2 modify-vpc-attribute --vpc-id $vpcId --enable-dns-hostnames "{\"Value\":true}"

vpc = t.add_resource(
    VPC(
        'VPC',
        CidrBlock='10.0.0.0/16',
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        Tags=Tags(
            Application=ref_stack_id,
            Network="Public",
        )
    )
)

# export internetGatewayId=`aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text`

internetGateway = t.add_resource(
    InternetGateway(
        'InternetGateway',
        Tags=Tags(Application=ref_stack_id)
    )
)

# aws ec2 attach-internet-gateway --internet-gateway-id $internetGatewayId --vpc-id $vpcId

gatewayAttachment = t.add_resource(
    VPCGatewayAttachment(
        'InternetGatewayAttachment',
        VpcId=Ref(vpc),
        InternetGatewayId=Ref(internetGateway)
    )
)

# export subnetId=`aws ec2 create-subnet --vpc-id $vpcId --cidr-block 10.0.0.0/28 --query 'Subnet.SubnetId' --output text`

publicSubnet = t.add_resource(
    Subnet(
        'Subnet',
        CidrBlock='10.0.0.0/24',
        VpcId=Ref(vpc),
        Tags=Tags(
            Application=ref_stack_id,
            Network="Public",
        )
    )
)

# export routeTableId=`aws ec2 create-route-table --vpc-id $vpcId --query 'RouteTable.RouteTableId' --output text`

publicRouteTable = t.add_resource(
    RouteTable(
        'RouteTable',
        VpcId=Ref(vpc),
        Tags=Tags(
            Application=ref_stack_id,
            Network="Public",
        )
    )
)

# aws ec2 associate-route-table --route-table-id $routeTableId --subnet-id $subnetId

subnetRouteTableAssociation = t.add_resource(
    SubnetRouteTableAssociation(
        'SubnetRouteTableAssociation',
        SubnetId=Ref(publicSubnet),
        RouteTableId=Ref(publicRouteTable),
    )
)

# aws ec2 create-route --route-table-id $routeTableId --destination-cidr-block 0.0.0.0/0 --gateway-id $internetGatewayId

publicRoute = t.add_resource(
    Route(
        'Route',
        DependsOn='InternetGatewayAttachment',
        GatewayId=Ref(internetGateway),
        DestinationCidrBlock='0.0.0.0/0',
        RouteTableId=Ref(publicRouteTable),
    )
)

publicNetworkACL = t.add_resource(
    NetworkAcl(
        'NetworkAcl',
        VpcId=Ref(vpc),
        Tags=Tags(
            Application=ref_stack_id,
            Network="Public",
        )
    )
)

inboundHTTPPublicNetworkAclEntry = t.add_resource(
    NetworkAclEntry(
        'InboundHTTPNetworkAclEntry',
        NetworkAclId=Ref(publicNetworkACL),
        RuleNumber=100,
        Protocol=-1,
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange=PortRange(From=80, To=80)
    )
)

inboundHTTPSPublicNetworkAclEntry = t.add_resource(
    NetworkAclEntry(
        'InboundHTTPSNetworkAclEntry',
        NetworkAclId=Ref(publicNetworkACL),
        RuleNumber=110,
        Protocol=-1,
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange=PortRange(From=443, To=443)
    )
)

inboundSSHPublicNetworkAclEntry = t.add_resource(
    NetworkAclEntry(
        'InboundSSHNetworkAclEntry',
        NetworkAclId=Ref(publicNetworkACL),
        RuleNumber=120,
        Protocol=-1,
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange=PortRange(From=22, To=22)
    )
)

inboundEphemeralPublicNetworkAclEntry = t.add_resource(
    NetworkAclEntry(
        'InboundEphemeralNetworkAclEntry',
        NetworkAclId=Ref(publicNetworkACL),
        RuleNumber=130,
        Protocol=-1,
        RuleAction="allow",
        Egress=False,
        CidrBlock="0.0.0.0/0",
        PortRange=PortRange(From=8888, To=8898)
    )
)

outboundHTTPPublicNetworkAclEntry = t.add_resource(
    NetworkAclEntry(
        'OutboundHTTPNetworkAclEntry',
        NetworkAclId=Ref(publicNetworkACL),
        RuleNumber=100,
        Protocol=-1,
        RuleAction="allow",
        Egress=True,
        CidrBlock="0.0.0.0/0",
        PortRange=PortRange(From=0, To=65535)
    )
)

subnetNetworkAclAssociation = t.add_resource(
    SubnetNetworkAclAssociation(
        'SubnetNetworkAclAssociation',
        SubnetId=Ref(publicSubnet),
        NetworkAclId=Ref(publicNetworkACL)
    )
)


# export securityGroupId=`aws ec2 create-security-group --group-name my-security-group \
#   --description "Generated by setup_vpn.sh" --vpc-id $vpcId --query 'GroupId' --output text`
# aws ec2 authorize-security-group-ingress --group-id $securityGroupId --protocol tcp --port 22 --cidr 0.0.0.0/0
# aws ec2 authorize-security-group-ingress --group-id $securityGroupId --protocol tcp --port 8888-8898 --cidr 0.0.0.0/0

ec2SecurityGroup = t.add_resource(
    SecurityGroup(
        'InstanceSecurityGroup',
        GroupDescription='Enable SSH access via port 22',
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
        SecurityGroupEgress=[
            SecurityGroupRule(
                IpProtocol='tcp',
                FromPort='0',
                ToPort='65535',
                CidrIp='0.0.0.0/0'
            ),

        ],
        VpcId=Ref(vpc),
    )
)

# export instanceId=`aws ec2 run-instances --image-id ami-bc508adc --count 1 --instance-type p2.xlarge \
# --key-name aws-key --security-group-ids $securityGroupId --subnet-id $subnetId --associate-public-ip-address \
# --block-device-mapping "[ { \"DeviceName\": \"/dev/sda1\", \"Ebs\": { \"VolumeSize\": 128, \"VolumeType\": \"gp2\" } } ]" \
# --query 'Instances[0].InstanceId' --output text`
# export allocAddr=`aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text`
# FIXME: --count 1
# FIXME: --associate-public-ip-address
# FIXME: aws ec2 allocate-address
ec2Instance = t.add_resource(
    Instance(
        "Ec2Instance",
        DependsOn='InternetGatewayAttachment',
        BlockDeviceMappings=[
            BlockDeviceMapping(
                DeviceName="/dev/sda1",
                Ebs=EBSBlockDevice(
                    VolumeSize="128",
                    VolumeType="gp2",
                )
            ),
        ],
        ImageId=Ref(imageId_param),
        InstanceType=Ref(instanceType_param),
        KeyName=Ref(keyname_param),
        # NetworkInterfaces=[
        #     NetworkInterfaceProperty(
        #         GroupSet=[Ref(ec2SecurityGroup)],
        #         AssociatePublicIpAddress=True,
        #         DeviceIndex=0,
        #         DeleteOnTermination=True,
        #         SubnetId=Ref(publicSubnet),
        #     )
        # ]
        SecurityGroupIds=[Ref(ec2SecurityGroup)],
        SubnetId=Ref(publicSubnet),
        # UserData=Base64("80")
    )
)

# eip = t.add_resource(
#     EIP(
#         "EIP",
#         InstanceId=Ref(ec2Instance),
#         Domain=Ref(vpc)
#     )
# )

# eipAssociation = t.add_resource(
#     EIPAssociation(
#         'EIPAssociation',
#         InstanceId=Ref(ec2Instance),
#         AllocationId=Ref(eip),
#     )
# )

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
])

print(t.to_json())
