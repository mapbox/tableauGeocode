const awsx = require("@pulumi/awsx");
// Step 1: Create an ECS Fargate cluster.
const cluster = new awsx.ecs.Cluster("cluster");
// Step 2: Define the Networking for our service.
const alb = new awsx.lb.ApplicationLoadBalancer("tabPyLb", {
  external: true,
  securityGroup: cluster.securityGroup
});
const web = alb.createListener("web", { port: 80, external: true });
// Step 3: Build and publish a Docker image to a private ECR registry.
const img = awsx.ecs.Image.fromPath("tabpy", "../");
// Step 4: Create a Fargate service task that can scale out.
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
  desiredCount: 5
});
// Step 5: Export the Internet address for the service.
exports.url = web.endpoint.hostname;
