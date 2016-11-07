# usf-dl-aws-cf

Scripts and tools for spinning up deep learning stacks using AWS CloudFormation.  Experimental.

Based on shell scripts provided by Jeremy Howard in the Deep Learning I course at USF.

## Requirements

- ansible
- troposphere
- AWS account

## Resources

These are projects and posts I found helpful while putting this together.

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