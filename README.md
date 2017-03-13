# usf-dl-aws-cf

Scripts and tools for spinning up deep learning stacks using AWS CloudFormation.  Experimental.

Based on shell scripts provided by Jeremy Howard in the Deep Learning I course at USF.

## Requirements

In order to run the deploy playbook you will need these installed.

- python2 - Ansible 2.1.x does not yet fully support Python3.  I recommend using a conda environment with Python 2 as the interpreter.
- ansible - Used for setting up the AWS stack and provisioning the EC2 machine.
- troposphere - Nice pythonic alternative to writing CloudFormation templates.
- boto - Used by ansible for AWS services.

In addition to the software setup there are a few additional prerequisites:

- AWS account - This is spinning up AWS services that might cost you money.
- AWS private key - I'm assuming you have already configured keys in AWS and have access to the private key locally.

## Pre-flight Check

- `vars.yml` - Create a `vars.yml` file by copying vars.template.yml and customizing the values.
    - This is ignored by git and will not be committed.
- `passwords.yml` - Create a `passwords.yml` using `ansible-vault`.
    - `$ ansible-vault create passwords.yml`
    - Add the following values:
```YAML
---
  jupyter_notebook_password: "your_notebook_password_here"
  github_username: your_github_username
  github_access_key: your_github_access_key
```
    - This is ignored by git and will not be committed.
- Download `cudnn-8.0-linux-x64-v5.1.tgz` from the nVidia developer program. Copy it to `files/`.

## Deploying

`$ ansible-playbook -vv --private-key ~/.ssh/YOUR_AWS_KEY deploy.yml --ask-vault-pass`

- The environment variable `ANSIBLE_HOST_KEY_CHECKING` is required since the ec2 instance is created the first time
this playbook is run so it will not be in your known_hosts.

This does the following:

- Provisions an EC2 machine based on the instance type specified in `vars.yml`.
- Installs system software on the EC2 instance.
- Installs Anaconda.
- Generates SSL certs and copies configuration files to secure Jupyter notebook server.
- Installs nVidia CUDA.
- Installs nVidia cuDNN.
- Creates a conda environment "py3" and installs packages.
- Writes `.theanorc` to configure Theano for GPU.
- (Re-)starts Jupyter notebook service via systemd.

## TODO

- Separate the playbook into multiple roles.
- Use the cloudformation template that creates an elastic ip (and VPC, subnet, etc.).
- Deploying will restart `jupyter notebook` if there is a change to the `jupyter-notebook.service` definition.  In this
case, if there are any currently running kernels, they will be restarted.  It would be nice to at least warn if this
were the case.
- Look into using EC2 spot pricing using block durations.  This gives a guaranteed block of time for the instance to
persist before being terminated.  This seems good for many types of interactive sessions.
    - More research needed here.  I think this would require attaching existing EBS volumes to newly created EC2 instances.
- Look into using Terraform instead of Troposphere as an API layer on top of AWS.
- Spawn the spot block EC2 from JupyterHub.
    - https://github.com/jupyterhub/batchspawner
    - https://github.com/jupyterhub/wrapspawner

## Resources

These are projects and posts I found helpful while putting this together.

- Jeremy Howard's scripts and setup of EC2 machines for Deep Learning.
- troposphere
    - [cloudtools/troposphere](https://github.com/cloudtools/troposphere)
    - [remind101/stacker](https://github.com/remind101/stacker)
    Deploy tool built on top of troposphere
    - [How to build a scalable AWS web app stack using ECS and CloudFormation](http://jeanphix.me/2016/06/13/howto-cloudformation-ecs/):
    a detailed guide to using troposphere for AWS.  In this case, AWS ECS.
    - [twingo-b/cloudformation_troposphere](https://github.com/twingo-b/cloudformation_troposphere):
    Github project that uses troposphere.
- Ansible
    - [Ansible AWS Guide](http://docs.ansible.com/ansible/guide_aws.html)
    - [Ansible: cloudformation](http://docs.ansible.com/ansible/cloudformation_module.html)
    - [AWS Automation: CloudFormation, Ansible, and Beyond](https://codeblog.io/aws/automation/2016/05/21/aws-automation-cloudformation-ansible-and-beyond.html)
    An in-depth post on using Ansible with Cloudformation.
    - [andrewrothstein/ansible-anaconda](https://github.com/andrewrothstein/ansible-anaconda)
    Github project to install Anaonda via Ansible.
- Cloudformation
    - [AWS Cloudformation sample templates](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/sample-templates-services-us-west-2.html)
- nVidia and CUDA install
    - http://docs.nvidia.com/cuda/cuda-installation-guide-linux
    - https://github.com/christopher5106/install-nvidia-cuda-torch-theano-on-ubuntu-16.04/blob/master/README.md
    - https://gist.github.com/wangruohui/df039f0dc434d6486f5d4d098aa52d07
    - https://github.com/NVIDIA/nvidia-docker/blob/master/ubuntu-16.04/cuda/8.0/runtime/Dockerfile
- Jupyter and JupyterHub
    - https://github.com/jupyterhub/jupyterhub
    - https://github.com/koslab/ansible-pydatalab
    - http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#securing-a-notebook-server
    - http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#using-ssl-for-encrypted-communication
    - https://medium.com/@ybarraud/setting-up-jupyterhub-with-sudospawner-and-anaconda-844628c0dbee#.rs1t6hfci