# Jenkins on Kubernetes - Ansible Deployment

This Ansible project automates the complete deployment of Jenkins on a Kubernetes cluster running on AWS EC2. It provisions the AWS infrastructure, sets up Kubernetes, and deploys Jenkins with proper ingress configuration.

## Architecture Overview

The deployment creates:
- AWS VPC with public subnet
- EC2 instance (t2.medium) with security groups
- Single-node Kubernetes cluster with Calico networking
- Jenkins deployment on Kubernetes with ingress

## Prerequisites

### Local Requirements
1. **Ansible** (version 2.9+)
   ```bash
   pip install ansible
   ```

2. **Required Ansible Collections**
   ```bash
   ansible-galaxy collection install amazon.aws
   ansible-galaxy collection install kubernetes.core
   ```

3. **Python Dependencies**
   ```bash
   pip install boto3 botocore kubernetes
   ```

4. **AWS CLI** configured with appropriate credentials
   ```bash
   aws configure
   ```

### AWS Requirements
1. **AWS Account** with appropriate permissions
2. **EC2 Key Pair** created in your target region
3. **ECR Repository** for Jenkins image (optional, see customization section)

### Required AWS Permissions
Your AWS user/role needs the following permissions:
- EC2: Full access (launch instances, manage VPCs, security groups)
- Route53: If using custom domain for ingress

## Configuration

### 1. Update Variables
Edit the variables in `provision-infrastructure.yml`:

```yaml
vars:
  region: us-east-1              # Your preferred AWS region
  key_name: my-key               # Your EC2 key pair name
  instance_type: t2.medium       # Instance size (minimum t2.medium recommended)
  ami: ami-0c02fb55956c7d316     # Ubuntu 20.04 LTS AMI for us-east-1
  vpc_cidr: "10.0.0.0/16"       # VPC CIDR block
  subnet_cidr: "10.0.1.0/24"    # Subnet CIDR block
```

### 2. Jenkins Image Configuration
In `setup-jenkins-k8s.yml`, update the Jenkins image:

```yaml
image: <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/my-jenkins:latest
```

Options:
- Use official Jenkins image: `jenkins/jenkins:lts`
- Use your custom ECR image: Replace `<AWS_ACCOUNT_ID>` with your AWS account ID
- Build and push custom image (see Custom Jenkins Image section)

### 3. Ingress Configuration
Update the ingress host in `setup-jenkins-k8s.yml`:

```yaml
rules:
  - host: jenkins.example.com  # Replace with your domain
```

## Deployment Steps

### Step 1: Provision AWS Infrastructure
```bash
ansible-playbook provision-infrastructure.yml
```

This playbook will:
- Create VPC and subnet
- Set up security group with required ports (22, 80, 443, 8080)
- Launch EC2 instance
- Add the instance to Ansible inventory

### Step 2: Setup Kubernetes and Deploy Jenkins
Wait for the EC2 instance to be fully ready (2-3 minutes), then run:

```bash
ansible-playbook -i inventory setup-jenkins-k8s.yml
```

This playbook will:
- Update system packages
- Install and configure containerd
- Install Kubernetes components (kubelet, kubeadm, kubectl)
- Initialize Kubernetes cluster
- Install Calico network plugin
- Deploy Jenkins with service and ingress

### Complete Deployment (One Command)
You can also run both playbooks in sequence:

```bash
ansible-playbook provision-infrastructure.yml && sleep 120 && ansible-playbook -i inventory setup-jenkins-k8s.yml
```

## Post-Deployment Configuration

### 1. Access Jenkins
After deployment, Jenkins will be accessible via:
- **Direct IP access**: `http://<EC2_PUBLIC_IP>:8080`
- **Ingress (if configured)**: `http://jenkins.example.com`

### 2. Get Jenkins Initial Password
SSH into your EC2 instance and get the initial admin password:

```bash
# SSH to EC2 instance
ssh -i /path/to/your/key.pem ubuntu@<EC2_PUBLIC_IP>

# Get Jenkins pod name
kubectl get pods

# Get initial admin password
kubectl exec <jenkins-pod-name> -- cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Configure Ingress Controller (Optional)
If using the ingress, install NGINX Ingress Controller:

```bash
# SSH to EC2 instance
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### 4. DNS Configuration (If Using Custom Domain)
Point your domain to the EC2 instance's public IP:
```
jenkins.example.com -> <EC2_PUBLIC_IP>
```

## Custom Jenkins Image (Optional)

### Create Custom Dockerfile
```dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt-get update && apt-get install -y docker.io
USER jenkins
```

### Build and Push to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name my-jenkins

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t my-jenkins .
docker tag my-jenkins:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/my-jenkins:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/my-jenkins:latest
```

## Troubleshooting

### Common Issues

1. **Playbook fails at EC2 instance creation**
   - Check AWS credentials: `aws sts get-caller-identity`
   - Verify key pair exists in the specified region
   - Ensure you have EC2 permissions

2. **Kubernetes initialization fails**
   - Instance might be too small (use t2.medium minimum)
   - Check if ports are blocked by security group

3. **Jenkins pod doesn't start**
   - Check if ECR image exists and is accessible
   - Use public Jenkins image for testing: `jenkins/jenkins:lts`

4. **Can't access Jenkins UI**
   - Check security group allows port 8080
   - Verify Jenkins service is running: `kubectl get svc`

### Debug Commands
```bash
# Check Kubernetes cluster status
kubectl cluster-info
kubectl get nodes
kubectl get pods -A

# Check Jenkins deployment
kubectl get deployment jenkins
kubectl describe deployment jenkins
kubectl logs deployment/jenkins

# Check services and ingress
kubectl get svc
kubectl get ingress
```

## Security Considerations

1. **Update default passwords** immediately after deployment
2. **Configure proper RBAC** for Kubernetes
3. **Use HTTPS** in production (configure TLS certificates)
4. **Restrict security group rules** to specific IP ranges
5. **Enable AWS CloudTrail** for audit logging
6. **Regular security updates** for all components

## Cleanup

To destroy the infrastructure:

```bash
# Delete Kubernetes resources
kubectl delete -f <jenkins-manifests>

# Terminate EC2 instance and clean up AWS resources
# (You may need to do this manually via AWS Console or create a cleanup playbook)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Ansible and Kubernetes logs
3. Ensure all prerequisites are met
4. Verify AWS permissions and quotas

## License

This project is provided as-is for educational and development purposes.