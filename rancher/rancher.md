# Rancher Setup & Internal Pod Network Management

## Managing Internal Kubernetes Workloads with Rancher on AWS EC2

This document outlines the steps to set up Rancher on an AWS EC2 instance for managing internal Kubernetes workloads. It includes Rancher installation, cluster configuration, workload visibility, and network management. This guide is useful for DevOps and SysAdmins managing Kubernetes clusters in cloud environments.

## 1. Overview

Rancher is a powerful, open-source container management platform for Kubernetes. It provides a central control plane to deploy, manage, and monitor Kubernetes clusters across multiple environments. With a user-friendly interface, Rancher simplifies cluster provisioning, application deployment, and workload monitoring.

This documentation covers Rancher installation on EC2, Kubernetes cluster connection (import or create), pod networking details, and optional observability tools.

## 2. Prerequisites

Ensure the following components are installed or available:

| Requirement | Details |
|-------------|---------|
| AWS EC2 Instance | Ubuntu 20.04/22.04 with minimum 4GB RAM |
| Docker | Installed on the EC2 server |
| Kubernetes | A running K8s cluster (RKE2/custom) |
| Security Groups | Ports 80, 443, and 22 open |
| Elastic IP | (Optional) For persistent access |

## 3. EC2 Instance Setup

### 3.1 Launch EC2 Instance

1. **Instance Type**: `t3.medium` or larger (minimum 4GB RAM)
2. **AMI**: Ubuntu Server 20.04 LTS or 22.04 LTS
3. **Storage**: 20GB+ EBS volume
4. **Security Group**: Configure the following ports:
   - SSH (22) - Your IP only
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
   - Custom TCP (9345) - For RKE2 communication

### 3.2 Install Docker on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

## 4. Running Rancher on EC2

### 4.1 Start Rancher Using Docker

```bash
# Create data directory for persistence
sudo mkdir -p /opt/rancher-data

# Run Rancher container
docker run -d --restart=unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v /opt/rancher-data:/var/lib/rancher \
  --name rancher \
  rancher/rancher:latest
```

### 4.2 Access Rancher Dashboard

Replace `YOUR_EC2_PUBLIC_IP` with your actual EC2 public IP address:

- **HTTP**: `http://YOUR_EC2_PUBLIC_IP`
- **HTTPS**: `https://YOUR_EC2_PUBLIC_IP`

> **Note**: Rancher will automatically redirect HTTP to HTTPS and generate a self-signed certificate.

## 5. Initial Rancher Configuration

### 5.1 First Login Setup

1. Open your browser and navigate to `https://YOUR_EC2_PUBLIC_IP`
2. Accept the self-signed certificate warning
3. Set the admin password (minimum 12 characters)
4. Accept the terms and conditions
5. Configure Rancher Server URL:
   - Use your EC2 public IP or domain name
   - Example: `https://YOUR_EC2_PUBLIC_IP`

### 5.2 Bootstrap Password (Alternative)

If you prefer to set a bootstrap password during container startup:

```bash
docker run -d --restart=unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v /opt/rancher-data:/var/lib/rancher \
  -e CATTLE_BOOTSTRAP_PASSWORD=YourSecurePassword123 \
  --name rancher \
  rancher/rancher:latest
```

## 6. Connecting a Kubernetes Cluster

### 6.1 Import an Existing Cluster

1. Go to **Cluster Management → Import Existing**
2. Enter cluster name (e.g., `production-cluster`)
3. Select **Generic** as the cluster type
4. Copy the `kubectl` command provided
5. Run the command on your existing Kubernetes cluster
6. Wait for the cluster to appear as **Active** in Rancher

### 6.2 Create a New RKE2 Cluster

1. Go to **Cluster Management → Create**
2. Choose **Custom** cluster type
3. Configure cluster settings:
   - **Name**: `internal-network-cluster`
   - **Kubernetes Version**: Latest stable
   - **Network Provider**: Calico (default)
4. Assign node roles and copy registration commands
5. Run commands on your target nodes

## 7. Verifying Cluster Status

Navigate to **Cluster Management** and verify:

- All nodes are in **Active** state