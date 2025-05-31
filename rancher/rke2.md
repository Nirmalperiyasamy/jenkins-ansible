# RKE2 Kubernetes Cluster Setup Guide

This guide provides step-by-step instructions to install and configure **RKE2 (Rancher Kubernetes Engine 2)** on **Ubuntu** systems for both **server (master)** and **agent (worker)** nodes. It also covers connecting multiple agents to a single RKE2 server.

## Prerequisites (All Nodes)

- Ubuntu 20.04 or 22.04
- Root or sudo access
- All nodes must be network reachable
- Port 9345 must be open from agents to server

## Step 1: System Preparation

### On All Nodes (Server and Agents)

```bash
# Disable and stop UFW firewall
sudo systemctl disable --now ufw

# Update and install required packages
sudo apt update
sudo apt install -y nfs-common iptables
sudo apt upgrade -y

# Clean up unused packages
sudo apt autoremove -y
```

## Step 2: Install RKE2 Server (Master Node)

### On the first master node

```bash
curl -sfL https://get.rke2.io | INSTALL_RKE2_TYPE=server sh -
```

### Configure RKE2 Server

```bash
sudo mkdir -p /etc/rancher/rke2/
echo "token: bootStrapAllTheThings" | sudo tee /etc/rancher/rke2/config.yaml
```

### Enable and Start the Server

```bash
sudo systemctl enable --now rke2-server.service
```

## Step 3: Enable kubectl CLI on Server

```bash
# Create symlink for kubectl
sudo ln -s $(find /var/lib/rancher/rke2/data/ -name kubectl) /usr/local/bin/kubectl

# Add KUBECONFIG and PATH to bashrc
echo "export KUBECONFIG=/etc/rancher/rke2/rke2.yaml PATH=\$PATH:/usr/local/bin:/var/lib/rancher/rke2/bin" >> ~/.bashrc
source ~/.bashrc

# Check node status
kubectl get nodes
```

## Step 4: Install Rancher with Helm (on Server)

### Install Helm

```bash
curl -#L https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Add Helm Repositories

```bash
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest --force-update
helm repo add jetstack https://charts.jetstack.io --force-update
```

### Install cert-manager

```bash
helm upgrade -i cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace --set crds.enabled=true
```

### Install Rancher

Replace `35.200.169.160` with your server's IP.

```bash
export RANCHER1_IP=35.200.169.160

helm upgrade -i rancher rancher-latest/rancher \
  --create-namespace --namespace cattle-system \
  --set hostname=rancher.$RANCHER1_IP.sslip.io \
  --set bootstrapPassword=bootStrapAllTheThings \
  --set replicas=1
```

### Verify Installation

```bash
kubectl get pods -A
helm list -A
```

Access Rancher UI at: `https://rancher.35.200.169.160.sslip.io`

## Step 5: Install RKE2 Agent (Worker Node)

### On each agent node

```bash
export RANCHER1_IP=35.200.169.160
```

### Install RKE2 Agent

```bash
curl -sfL https://get.rke2.io | INSTALL_RKE2_TYPE=agent sh -
```

### Configure Agent

```bash
sudo mkdir -p /etc/rancher/rke2/
cat << EOF | sudo tee /etc/rancher/rke2/config.yaml
server: https://$RANCHER1_IP:9345
token: bootStrapAllTheThings
EOF
```

### Enable and Start Agent

```bash
sudo systemctl enable --now rke2-agent.service
```

## Connecting Multiple Agents

- All agent nodes use the same server IP and token in their config
- You can install and connect **multiple agent nodes** by repeating the agent install and config steps
- Ensure all agents can reach the server on port 9345

### Check Agent Registration on Master

```bash
kubectl get nodes
```

## Access URLs and Credentials

Once Rancher is successfully deployed, you can access the Rancher UI using the following details:

- **URL:** `https://rancher.35.200.169.160.sslip.io`
- **Username:** `admin`
- **Password:** `bootStrapAllTheThings`

> **Note:** Make sure the hostname resolves correctly and port 443 (HTTPS) is open to access the web interface.

## Troubleshooting

### Common Issues

- Ensure all required ports are open (9345 for RKE2, 443 for Rancher UI)
- Verify network connectivity between nodes
- Check system logs: `sudo journalctl -u rke2-server.service -f` or `sudo journalctl -u rke2-agent.service -f`
- Ensure the token matches between server and agent configurations

### Useful Commands

```bash
# Check RKE2 server status
sudo systemctl status rke2-server

# Check RKE2 agent status
sudo systemctl status rke2-agent

# View server logs
sudo journalctl -u rke2-server.service -f

# View agent logs
sudo journalctl -u rke2-agent.service -f
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.