# Deploying TabPy to AWS

The code in this sub-folder will deploy TabPy to Amazon Web Services Elastic Container Service (ECS). It will also place a load balancer in front of your instances to provide users with a single URL for use.

## Install

You must have Docker and Pulumi installed on your machine in order to use this script. You must also have an [AWS account](https://aws.amazon.com/getting-started/) with credentials available to your environment.

To install:

Mac

```bash
brew install pulumi
```

PC

```bash
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://get.pulumi.com/install.ps1'))" && SET "PATH=%PATH%;%USERPROFILE%\.pulumi\bin"
```

To install Docker, follow their [Getting Started](https://docs.docker.com/install/) guide.

## Deploy

After cloning the repository

```bash
cd src/depoy
npm ci
pulumi config set aws:region <yourAWSRegion>
pulumi up -y
```

This will begin a Docker build and deployment to AWS. At the end of the process you will be shown a URL. That is the URL you will use in Tableau for geocoding (or any other TabPy needs).

## Details

This script works as follows

1. Create AWS Fargate cluster. This is a cluster to place your TabPy container. Fargate manages scale and size for you, so you do not have to manage core resources.
2. Create Load Balancer. Your cluster will have between 1-N containers running on it, and the ALB will route requests to those containers as needed.
3. TabPy Service. The normal TabPy application is wrapped in Docker to make it simpler to deploy. It is configured to use port 80 for all communications. Fargate allows you to run as many replicas of your container as needed for scale.

```javascript
const appService = new awsx.ecs.FargateService("tabpy-service", {
  cluster,
  taskDefinitionArgs: {
    container: {
      image: img,
      cpu: 1024 /*100% of 1024*/,
      memory: 2048 /*MB*/,
      portMappings: [web]
    }
  },
  ///This is where you define how many replicas you want running at all times.
  desiredCount: 5
});
```

## Teardown

If you wish to remove the stack, run `pulumi destroy -y`.