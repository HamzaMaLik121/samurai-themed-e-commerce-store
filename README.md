# 🗡️ Samurai E-Commerce Store

A full-stack e-commerce application with a **Flask (Python)** backend, **React + Vite** frontend, **MySQL** database, and a complete **DevSecOps CI/CD pipeline** powered by **Jenkins**, **ArgoCD**, and **Kubernetes (KinD)**.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [CI/CD Pipeline Flow](#cicd-pipeline-flow)
- [Jenkins Pipeline](#jenkins-pipeline)
- [ArgoCD GitOps](#argocd-gitops)
- [Helm Chart](#helm-chart)
- [Setting Up Credentials](#setting-up-credentials)
- [Local Development](#local-development)
- [Deploying to KinD](#deploying-to-kind)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │ ──▶ │  Frontend    │ ──▶ │   Backend   │
│  :30080     │     │  NodePort    │     │  ClusterIP  │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                         ┌──────▼──────┐
                                         │    MySQL    │
                                         │  ClusterIP  │
                                         └─────────────┘
```

| Component | Type | Port | Access |
|-----------|------|------|--------|
| Frontend (React + Nginx) | NodePort | 30080 | Browser |
| Backend (Flask + Gunicorn) | ClusterIP | 5000 | Internal only |
| MySQL | ClusterIP | 3306 | Internal only |

---

## CI/CD Pipeline Flow

The pipeline follows a **shift-left security** approach: container scanning happens **before** images are pushed, ensuring vulnerable images never reach the registry.

```
                    ┌─────────────────────────────────────┐
                    │         Developer pushes code        │
                    │         to GitHub (main branch)      │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │         Jenkins Pipeline Triggers    │
                    │         (GitHub Webhook)             │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │  Step 1: Checkout & Code Analysis    │
                    │  ├── Git checkout                    │
                    │  ├── Build backend & frontend        │
                    │  └── Run unit tests                  │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │  Step 2: Build Docker Images         │
                    │  ├── Build backend:5000              │
                    │  └── Build frontend:80               │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │  Step 3: Security Scanning (Trivy)   │
                    │  ├── Scan backend image for CVEs     │
                    │  ├── Scan frontend image for CVEs    │
                    │  └── FAIL pipeline if CRITICAL/HIGH  │
                    │      vulnerabilities found           │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │  Step 4: Push to Docker Hub          │
                    │  ├── Tag with commit SHA             │
                    │  │   (hamzamalik1/samurai-backend:   │
                    │  │    sha-<commit>)                  │
                    │  └── Push images to Docker Hub       │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │  Step 5: Update GitOps Repo          │
                    │  ├── Update values.yaml              │
                    │  │   image tags to new SHA           │
                    │  └── Git push to main branch         │
                    └────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │  ArgoCD detects drift                │
                    │  ├── Auto-syncs to new chart version │
                    │  ├── Deploys updated images          │
                    │  └── Self-heals if manual changes    │
                    └─────────────────────────────────────┘
```

---

## Jenkins Pipeline

The pipeline is defined in [`Devsecops+gitops/Jenkins-CI.yml`](Devsecops+gitops/Jenkins-CI.yml).

### Pipeline Stages

| Stage | Description |
|-------|-------------|
| **Checkout SCM** | Pulls latest code from GitHub `main` branch |
| **Build Backend** | Installs Python deps, runs tests |
| **Build Frontend** | Installs Node deps, builds Vite project |
| **Build Docker Images** | Builds `hamzamalik1/samurai-backend` and `hamzamalik1/samurai-frontend` |
| **Security Scan (Trivy)** | Scans images for vulnerabilities. Fails on HIGH/CRITICAL |
| **Push to Docker Hub** | Tags images with commit SHA (`sha-<short_commit>`) and pushes |
| **Update GitOps** | Updates `helm/samurai-app/values.yaml` with new image tags, commits, and pushes |

### Setting Up Jenkins Credentials

The pipeline requires the following credentials configured in Jenkins:

| Credential ID | Type | Purpose |
|---------------|------|---------|
| `github-cred` | Username with password (or SSH key) | Push updated `values.yaml` to GitHub |
| `docker-hub-credentials` | Username with password | Push images to Docker Hub |

**How to add credentials in Jenkins:**

1. Open Jenkins Dashboard → **Manage Jenkins** → **Credentials**
2. Click **System** → **Global credentials (unrestricted)** → **Add Credentials**
3. For **GitHub credentials**:
   - Kind: **Username with password** (or SSH key)
   - Username: Your GitHub username
   - Password: A [GitHub Personal Access Token](https://github.com/settings/tokens) with `repo` scope
   - ID: `github-cred`
4. For **Docker Hub credentials**:
   - Kind: **Username with password**
   - Username: Your Docker Hub username
   - Password: Your Docker Hub password / access token
   - ID: `docker-hub-credentials`

### Setting Up Jenkins Pipeline Job

1. **Install required plugins**:
   - Pipeline
   - Docker Pipeline
   - GitHub Integration
   - Blue Ocean (optional, for better UI)

2. **Create a new Pipeline job**:
   - New Item → **Pipeline** → Name: `samurai-app-pipeline`
   - **Pipeline Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git`
   - **Script Path**: `Devsecops+gitops/Jenkins-CI.yml`

3. **Configure GitHub Webhook** (for automatic triggers):
   - Go to GitHub repo → **Settings** → **Webhooks** → **Add webhook**
   - Payload URL: `http://<jenkins-url>/github-webhook/`
   - Content type: `application/json`
   - Events: **Just the push event**

> ⚠️ **Note for Jenkins on EC2:** If your Jenkins instance runs on EC2 without a public domain, set `JENKINS_URL` in Jenkins configuration or use ngrok for webhook forwarding.

---

## ArgoCD GitOps

The ArgoCD Application manifest is defined in [`Devsecops+gitops/argocd-app.yaml`](Devsecops+gitops/argocd-app.yaml).

### How ArgoCD Works

ArgoCD continuously monitors the Git repository and syncs the cluster state to match what's defined in the Helm chart. When Jenkins pushes updated image tags to `values.yaml`, ArgoCD detects the change and automatically rolls out the new version.

### Application Configuration

| Setting | Value |
|---------|-------|
| **Repo URL** | `https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git` |
| **Target Revision** | `main` |
| **Chart Path** | `helm/samurai-app` |
| **Destination** | `https://kubernetes.default.svc` (KinD) |
| **Namespace** | `samurai` |
| **Sync Policy** | Automated (prune: true, selfHeal: true) |

### Setting Up ArgoCD on KinD

1. **Install KinD cluster**:
   ```bash
   kind create cluster --name samurai-cluster
   ```

2. **Install ArgoCD**:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

3. **Access ArgoCD UI**:
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```
   Open `https://localhost:8080`

4. **Get admin password**:
   ```bash
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

5. **Create the Application**:
   ```bash
   kubectl apply -f Devsecops+gitops/argocd-app.yaml
   ```

6. **Verify sync**:
   ```bash
   argocd app get samurai-app
   ```

---

## Helm Chart

The Kubernetes manifests are packaged as a Helm chart located at [`helm/samurai-app/`](helm/samurai-app/).

### Chart Structure

```
helm/samurai-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # All configuration (CI updates image tags)
└── templates/
    ├── mysql-secret.yaml       # DB passwords (base64)
    ├── mysql-pvc.yaml          # MySQL persistent storage
    ├── mysql-deployment.yaml   # MySQL deployment
    ├── mysql-service.yaml      # MySQL ClusterIP service
    ├── backend-deployment.yaml # Flask backend
    ├── backend-service.yaml    # Backend ClusterIP service
    ├── frontend-deployment.yaml # React frontend
    ├── frontend-service.yaml   # Frontend NodePort service (port 30080)
    ├── ingress.yaml            # Ingress (disabled by default)
    └── NOTES.txt               # Post-install usage instructions
```

### Common Helm Commands

```bash
# Lint the chart
helm lint helm/samurai-app/

# Render templates locally
helm template helm/samurai-app/

# Install the chart
helm install samurai-app helm/samurai-app/ --namespace samurai --create-namespace

# Upgrade with new image tags
helm upgrade samurai-app helm/samurai-app/ \
  --set backend.image.tag=sha-abc1234 \
  --set frontend.image.tag=sha-def5678

# Uninstall
helm uninstall samurai-app --namespace samurai
```

### MySQL Secrets

Passwords are stored as base64-encoded values in `mysql-secret.yaml`.

**To change passwords:**

```bash
# Encode new password
echo -n 'your_new_password' | base64

# Update the values in helm/samurai-app/templates/mysql-secret.yaml
# Then re-deploy the chart
```

---

## Local Development

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### Run with Docker Compose

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173` (Vite dev server)
- Backend: `http://localhost:5000`
- MySQL: `localhost:3306`

### Run without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Deploying to KinD

### One-time Setup

```bash
# Create cluster
kind create cluster --name samurai-cluster

# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --namespace argocd --for=condition=ready pod --selector=app.kubernetes.io/name=argocd-server --timeout=300s

# Deploy the app via Helm directly (without ArgoCD)
helm install samurai-app helm/samurai-app/ --namespace samurai --create-namespace

# Or deploy via ArgoCD
kubectl apply -f Devsecops+gitops/argocd-app.yaml
```

### Access the Application

```bash
# Get KinD node IP
export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')

# Open in browser
echo "http://$NODE_IP:30080"

# Or port-forward
kubectl port-forward svc/frontend-service -n samurai 8080:80
# Open http://localhost:8080
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **ArgoCD not syncing** | Check `argocd app logs samurai-app` for errors |
| **Pod stuck in CrashLoopBackOff** | `kubectl describe pod <pod-name> -n samurai` |
| **MySQL connection refused** | Ensure MySQL pod is healthy: `kubectl get pods -n samurai` |
| **ImagePullBackOff** | Check Docker Hub credentials / image tags |
| **Jenkins pipeline fails on scan** | Fix vulnerabilities or whitelist in Trivy config |
| **Can't push to GitHub from Jenkins** | Verify `github-cred` credentials in Jenkins |
| **NodePort not accessible** | Check KinD networking: `kubectl get nodes -o wide` |

---

## Repository Structure

```
samurai-themed-e-commerce-store/
├── backend/                  # Flask API server
├── frontend/                 # React + Vite app
├── database/                 # MySQL init scripts
├── files/                    # Legacy k8s manifests (pre-Helm)
├── helm/
│   └── samurai-app/          # Helm chart (current deployment method)
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── Devsecops+gitops/
│   ├── Jenkins-CI.yml        # Jenkins pipeline definition
│   └── argocd-app.yaml       # ArgoCD Application manifest
├── docker-compose.yml        # Local dev setup
└── README.md                 # This file
```

---

## License

MIT
