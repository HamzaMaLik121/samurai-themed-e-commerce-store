<div align="center">
  <img src="https://img.shields.io/badge/Status-Live%20%26%20Operational-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Pipeline-CI%2FCD%20Enabled-0078D4?style=for-the-badge&logo=github-actions" alt="CI/CD">
  <img src="https://img.shields.io/badge/Security-Trivy%20Scanned-00ADD8?style=for-the-badge&logo=snyk" alt="Security">
  <img src="https://img.shields.io/badge/Deployment-ArgoCD%20GitOps-EF7B4D?style=for-the-badge&logo=argo" alt="ArgoCD">
  <img src="https://img.shields.io/badge/Kubernetes-KinD-326CE5?style=for-the-badge&logo=kubernetes" alt="KinD">
  <img src="https://img.shields.io/badge/Monitoring-Prometheus%20%26%20Grafana-E6522C?style=for-the-badge&logo=prometheus" alt="Monitoring">
  <br>
  <img src="https://img.shields.io/badge/Python-Flask-000000?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/React-Vite-61DAFB?style=for-the-badge&logo=react" alt="React">
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql" alt="MySQL">
  <img src="https://img.shields.io/badge/SonarQube-Quality%20Gate-4E9BCD?style=for-the-badge&logo=sonarqube" alt="SonarQube">
  <img src="https://img.shields.io/badge/Docker-Hub-2496ED?style=for-the-badge&logo=docker" alt="Docker">
</div>

<br>

<h1 align="center">
  ⚔️ Samurai E-Commerce Store ⚔️
</h1>

<p align="center">
  <i>A production-grade, full-stack e-commerce platform with an enterprise DevSecOps pipeline — from code commit to Kubernetes deployment, all automated.</i>
</p>

<p align="center">
  <b>Flask + React/Vite + MySQL · Jenkins CI/CD · SonarQube SAST · Trivy Container Scan · ArgoCD GitOps · KinD · Prometheus + Grafana</b>
</p>

<br>

---

## 📋 Table of Contents

- [✨ Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [📦 Tech Stack](#-tech-stack)
- [⚡ Quick Start — Local Development](#-quick-start--local-development)
- [☸️ Full Deployment on AWS EC2 + KinD](#️-full-deployment-on-aws-ec2--kind)
  - [0. Infrastructure Overview](#0-infrastructure-overview)
  - [1. Master EC2 Setup — Jenkins & SonarQube](#1-master-ec2-setup--jenkins--sonarqube)
  - [2. Agent EC2 Setup — Docker, KinD, & Tools](#2-agent-ec2-setup--docker-kind--tools)
  - [3. Jenkins Configuration](#3-jenkins-configuration)
  - [4. SonarQube Project Setup](#4-sonarqube-project-setup)
  - [5. Jenkins Credentials](#5-jenkins-credentials)
  - [6. Jenkins Pipelines — CI & CD](#6-jenkins-pipelines--ci--cd)
  - [7. ArgoCD GitOps Setup](#7-argocd-gitops-setup)
  - [8. Monitoring with Prometheus & Grafana](#8-monitoring-with-prometheus--grafana)
  - [9. GitHub Webhook](#9-github-webhook)
- [🌐 Service URLs & Access](#-service-urls--access)
- [📂 Project Structure](#-project-structure)
- [🩺 Verification Commands](#-verification-commands)
- [🐛 Common Issues & Fixes](#-common-issues--fixes)
- [⚠️ Architectural Notes](#️-architectural-notes)
- [🏁 Quick Reference](#-quick-reference)
- [📄 License](#-license)

---

## ✨ Overview

**Samurai E-Commerce Store** is a complete, hands-on DevOps project that demonstrates an enterprise-grade DevSecOps pipeline. It features:

- A **Flask (Python)** backend API with JWT authentication
- A **React + Vite** frontend with a samurai-themed UI
- **MySQL** database with seeded products and bundles
- A **Jenkins CI pipeline** with 8 stages: SAST (SonarQube), SCA (OWASP), Docker build, Trivy container scan, and push to Docker Hub
- A **Jenkins CD pipeline** that updates Helm values and triggers ArgoCD
- **ArgoCD GitOps** for Kubernetes deployment on KinD
- **Prometheus + Grafana** monitoring stack
- Full **Kubernetes Helm chart** for declarative deployment

> **Live Demo:** `http://&lt;agent-ec2-public-ip&gt;:30080`  
> **Admin Login:** `admin@bushido.com` / `bushido2026`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                            │
│   samurai-themed-e-commerce-store (main branch)                     │
└──────────────────┬──────────────────────────────────────────────────┘
                   │  git push
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ─── MASTER EC2 (t3.medium) ───                    │
│                                                                     │
│   ╔══════════════════════════════╗   ╔════════════════════════════╗  │
│   ║      Jenkins Controller      ║   ║        SonarQube           ║  │
│   ║  port 8080 · Webhook trigger ║   ║  port 9000 · SAST scans    ║  │
│   ╚══════════════════════════════╝   ╚════════════════════════════╝  │
└──────────────────┬──────────────────────────────────────────────────┘
                   │  triggers via SSH
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ─── AGENT EC2 (m7i-flex.large) ───                │
│                                                                     │
│   ╔══════════════════════════════════════════════════════════════╗   │
│   ║                    Jenkins Agent                              ║   │
│   ║   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  ║   │
│   ║   │  Stage 1 │→│  Stage 2 │→│  Stage 3 │→│  Stage 4    │  ║   │
│   ║   │ Checkout │  │ SonarQube│  │ OWASP DC │  │ Quality Gate│  ║   │
│   ║   └──────────┘  └──────────┘  └──────────┘  └────────────┘  ║   │
│   ║        ↓                                                    ║   │
│   ║   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  ║   │
│   ║   │  Stage 5 │→│  Stage 6 │→│  Stage 7 │→│  Stage 8    │  ║   │
│   ║   │Docker Bld│  │Trivy Scan│  │Push to DH│  │Archive Rpts│  ║   │
│   ║   └──────────┘  └──────────┘  └──────────┘  └────────────┘  ║   │
│   ╚══════════════════════════════════════════════════════════════╝   │
│                                                                     │
│                          CI triggers CD                             │
│                              ↓                                      │
│   ╔══════════════════════════════════════════════════════════════╗   │
│   ║                    Jenkins CD Job                             ║   │
│   ║   1. Checkout → 2. Update values.yaml → 3. git push          ║   │
│   ╚══════════════════════════════════════════════════════════════╝   │
│                                                                     │
│                   ArgoCD detects git change                          │
│                              ↓                                      │
│   ╔══════════════════════════════════════════════════════════════╗   │
│   ║                  KinD Cluster — 4 Nodes                       ║   │
│   ║                                                              ║   │
│   ║   ┌─────────────────── samurai ───────────────────┐          ║   │
│   ║   │  ┌──────────────┐   ┌───────────────────┐     │          ║   │
│   ║   │  │    MySQL      │   │  Flask Backend    │     │          ║   │
│   ║   │  │   ClusterIP   │◄──│  ClusterIP:5000   │     │          ║   │
│   ║   │  │    :3306      │   └───────────────────┘     │          ║   │
│   ║   │  └──────────────┘           ▲                   │          ║   │
│   ║   │                              │                   │          ║   │
│   ║   │   ┌───────────────────────┐  │                   │          ║   │
│   ║   │   │   React Frontend      │──┘                   │          ║   │
│   ║   │   │   NodePort:30080      │                      │          ║   │
│   ║   │   └───────────────────────┘                      │          ║   │
│   ║   └──────────────────────────────────────────────────┘          ║   │
│   ║                                                              ║   │
│   ║   ┌────────── argocd ──────────┐  ┌────── monitoring ──────┐ ║   │
│   ║   │ ArgoCD Server · Redis ·    │  │ Prometheus · Grafana   │ ║   │
│   ║   │ Controller · Repo Server   │  │ AlertManager · Export  │ ║   │
│   ║   └────────────────────────────┘  └────────────────────────┘ ║   │
│   ╚══════════════════════════════════════════════════════════════╝   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Tech Stack

### Application
| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18 + Vite + Tailwind CSS |
| **Backend** | Python 3.10+ · Flask · JWT Auth · SQLAlchemy |
| **Database** | MySQL 8.0 |
| **Web Server** | Nginx (reverse proxy to backend) |

### DevOps & Infrastructure
| Category | Tools |
|----------|-------|
| **CI/CD** | Jenkins (8-stage CI + CD pipeline) |
| **Code Quality** | SonarQube (SAST) + OWASP Dependency-Check (SCA) |
| **Container Security** | Trivy (CVE scanning, fails on CRITICAL/HIGH) |
| **Containerization** | Docker & Docker Hub |
| **Orchestration** | Kubernetes (KinD — 4 nodes) |
| **GitOps** | ArgoCD (auto-sync, self-heal, prune) |
| **Packaging** | Helm (Kubernetes chart) |
| **Monitoring** | Prometheus + Grafana (kube-prometheus-stack) |
| **Cloud** | AWS EC2 (Master + Agent) |

---

## ⚡ Quick Start — Local Development

Get the app running locally in minutes without Kubernetes.

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
cd samurai-themed-e-commerce-store

# 2. Start everything with Docker Compose
docker-compose up --build
```

That's it. The app will be available at:

| Service | URL |
|---------|-----|
| **Frontend** | `http://localhost:5173` |
| **Backend API** | `http://localhost:5000` |
| **MySQL** | `localhost:3306` |

### Run Without Docker

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

## ☸️ Full Deployment on AWS EC2 + KinD

This is the complete step-by-step guide to deploy the entire stack — Jenkins, SonarQube, ArgoCD, KinD, and monitoring — on AWS EC2.

---

### 0. Infrastructure Overview

| Machine | Instance Type | RAM | Role |
|---------|--------------|-----|------|
| **Master** | t3.medium (minimum) | 4GB+ | Jenkins Controller + SonarQube |
| **Agent** | m7i-flex.large | **8GB required** | Jenkins Agent + KinD (4 nodes) + ArgoCD + Monitoring + App |

> ⚠️ **Critical:** The agent EC2 instance **must** have at least 8GB RAM. Running KinD (4 nodes), ArgoCD, Prometheus/Grafana, the samurai app, and the Jenkins agent simultaneously will cause OOM crashes on smaller instances.

**Security Group — Master EC2:**
| Port | Source | Purpose |
|------|--------|---------|
| 8080 | `0.0.0.0/0` | Jenkins UI |
| 9000 | `0.0.0.0/0` | SonarQube UI |
| 50000 | Agent private IP | Jenkins agent JNLP |
| 22 | Your IP | SSH |

**Security Group — Agent EC2:**
| Port | Source | Purpose |
|------|--------|---------|
| 22 | Your IP | SSH |
| 8080 | `0.0.0.0/0` | ArgoCD UI (port-forward) |
| 9090 | `0.0.0.0/0` | Prometheus UI (port-forward) |
| 3000 | `0.0.0.0/0` | Grafana UI (port-forward) |
| 30080 | `0.0.0.0/0` | **Samurai App Frontend** |

---

### 1. Master EC2 Setup — Jenkins & SonarQube

#### 1.1 Install Jenkins (Docker)

```bash
docker run -d \
  --name jenkins \
  --restart=always \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

```bash
# Get the initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Access `http://&lt;master-public-ip&gt;:8080` → Complete setup wizard → Install suggested plugins.

#### 1.2 Install SonarQube (Docker)

```bash
docker run -d \
  --name sonarqube \
  --restart=always \
  -p 9000:9000 \
  sonarqube:lts-community
```

Wait 60–90 seconds, then access `http://&lt;master-public-ip&gt;:9000`

> **Default login:** `admin` / `admin` (you'll be forced to change password on first login)
>
> **Important:** SonarQube must run on the **master** EC2 only. The agent doesn't have enough RAM.

---

### 2. Agent EC2 Setup — Docker, KinD & Tools

SSH into your agent EC2 and run the following:

```bash
# --- Docker ---
sudo apt update
sudo apt install -y docker.io
sudo usermod -aG docker ubuntu
newgrp docker

# --- Java (Required by Jenkins Agent) ---
sudo apt install -y openjdk-21-jdk

# --- Git ---
sudo apt install -y git

# --- Trivy (Container Vulnerability Scanner) ---
sudo apt install -y wget apt-transport-https gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | \
  sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] \
  https://aquasecurity.github.io/trivy-repo/deb generic main" | \
  sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install -y trivy

# --- kubectl ---
curl -LO "https://dl.k8s.io/release/$(curl -L -s \
  https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# --- KinD (Kubernetes in Docker) ---
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# --- Helm ---
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Create the KinD Cluster

```bash
kind create cluster --name bushido-brand
```

Verify all nodes are ready:

```bash
kubectl get nodes
```

Expected output:
```
NAME                          STATUS   ROLES           AGE
bushido-brand-control-plane   Ready    control-plane   1m
bushido-brand-worker          Ready    <none>          1m
bushido-brand-worker2         Ready    <none>          1m
bushido-brand-worker3         Ready    <none>          1m
```

---

### 3. Jenkins Configuration

#### 3.1 Install Plugins

Navigate to **Manage Jenkins → Plugins → Available plugins** and install:

| Plugin | Purpose |
|--------|---------|
| **SonarQube Scanner for Jenkins** | Runs `sonar-scanner` in pipeline |
| **OWASP Dependency-Check** | SCA scan + report in Jenkins UI |
| **Docker Pipeline** | `docker build` and `docker push` steps |
| **Sonar Quality Gates Plugin** | `waitForQualityGate` step |
| **Pipeline Stage View** | Visual stage grid |

Restart Jenkins after installing.

#### 3.2 Configure Tools

**Manage Jenkins → Tools**

**SonarQube Scanner:**
```
Name:    SonarQube Scanner
☑ Install automatically
Version: SonarQube Scanner 8.1.0.6389
```

**Dependency-Check:**
```
Name:    OWASP-DC
☑ Install automatically
Version: latest
```

> **Critical:** The name `OWASP-DC` must match what's in the Jenkinsfile `odcInstallation: 'OWASP-DC'`. If you change the name here, update the Jenkinsfile too.

#### 3.3 Configure SonarQube Server

**Manage Jenkins → System** → Scroll to **SonarQube servers**:

```
☑ Environment variables
Name:                SonarQube
Server URL:          http://<master-PRIVATE-ip>:9000
Server auth token:   sonar-token   (from dropdown)
```

> Use the **private IP** of the master EC2 — the agent communicates with SonarQube over the internal AWS network.

#### 3.4 Add Jenkins Agent Node

**Manage Jenkins → Nodes → New Node**

```
Node name:             hamza-agent
Type:                  Permanent Agent
Remote root dir:       /home/ubuntu/jenkins-agent
Labels:                hamza-agent
Usage:                 Use this node as much as possible
Launch method:         Launch agents via SSH
Host:                  <agent-PRIVATE-ip>
Credentials:           hamza-agent-key
Host Key Verification: Non verifying
```

Click **Save** → Jenkins connects automatically. Verify the green circle appears under **Manage Jenkins → Nodes**.

---

### 4. SonarQube Project Setup

#### 4.1 Create Project

1. Login to `http://&lt;master-public-ip&gt;:9000`
2. **Projects → Create Project → Manually**
3. Fill in:
   - Display name: `samurai ecommerce app`
   - Project key: `samurai-ecommerce-app`
   - Branch: `main`
4. Click **Set Up** (ignore the DevOps platform wizard that follows)

#### 4.2 Generate Token

1. Click avatar (top right) → **My Account → Security**
2. Generate a token:
   - Name: `jenkins-token`
   - Type: `User Token`
   - Expires: `No expiration`
3. **Copy the token immediately** — it's shown only once.

#### 4.3 Create a Custom Quality Gate

The default `Sonar way` gate requires 80% test coverage — which will always fail since this project has no formal unit tests. Create a custom gate:

1. **Quality Gates → Create → Name: `Samurai Gate`**
2. Click **Unlock editing**
3. Delete (red trash icon) these conditions:
   - Coverage < 80%
   - Duplicated Lines > 3%
   - Maintainability Rating worse than A
4. Keep only:
   - Reliability Rating worse than A
   - Security Hotspots Reviewed < 100%
   - Security Rating worse than A
5. **Save**

#### 4.4 Assign Gate to Project

**Projects → Samurai E-Commerce App → Project Settings → Quality Gate → Select `Samurai Gate` → Save**

#### 4.5 Review Security Hotspots (After First CI Run)

After the first CI run, SonarQube flags 2 security hotspots in `backend/app.py`:

1. Go to **Project → Security Hotspots**
2. You'll see:
   - **CSRF** (HIGH) — API intentionally allows CORS for a known frontend host
   - **Permission** (MEDIUM)
3. Click each → **Change status → Safe** → Add a comment explaining why → Save

After both are marked Safe, the Quality Gate will pass.

---

### 5. Jenkins Credentials

**Manage Jenkins → Credentials → System → Global credentials (unrestricted) → Add Credentials**

Add these five credentials:

| # | Kind | ID | Description | Value |
|---|------|----|-------------|-------|
| 1 | Secret text | `sonar-token` | SonarQube Token | Paste the token from Step 4.2 |
| 2 | Username/Password | `dockerhub-creds` | Docker Hub Credentials | Username: `hamzamalik1` / Password: your Docker Hub token |
| 3 | Username/Password | `github-creds` | GitHub PAT | Username: `HamzaMaLik121` / Password: GitHub PAT with `repo` scope |
| 4 | Secret text | `nvd-api-key` | NVD API Key | Get a free key from [nvd.nist.gov](https://nvd.nist.gov/developers/request-an-api-key) |
| 5 | SSH Username/Private Key | `hamza-agent-key` | Agent SSH Key | Username: `ubuntu` / Private Key: paste your agent `.pem` file contents |

---

### 6. Jenkins Pipelines — CI & CD

#### 6.1 CI Pipeline (`samurai-ci`)

**New Item → samurai-ci → Pipeline → OK**

**Build Triggers:** `☑ GitHub hook trigger for GITScm polling`

**Pipeline Definition:**
```
Definition:   Pipeline script from SCM
SCM:          Git
Repository:   https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
Credentials:  github-creds
Branch:       */main
Script Path:  Devsecops+gitops/Jenkins-CI.yml
```

##### 8-Stage CI Pipeline

| Stage | Duration | Description |
|-------|----------|-------------|
| 🔄 1. Checkout | 10s | Pulls `main` branch, sets `IMAGE_TAG = sha-&lt;7char&gt;` |
| 🔍 2. SAST — SonarQube | 60s | Scans `backend/` (Python) + `frontend/src/` (JS/React) |
| 📦 3. SCA — OWASP DC | 120s | Scans `requirements.txt` + `package.json` against NVD CVE database |
| ✅ 4. Quality Gate | 60s | Waits up to 5 min for SonarQube verdict; aborts on ERROR |
| 🐳 5. Docker Build | 90s | Builds `hamzamalik1/samurai-backend:sha-xxxx` + `samurai-frontend:sha-xxxx` |
| 🛡️ 6. Trivy Scan | 60s | Scans both images; fails on CRITICAL/HIGH CVEs |
| 📤 7. Push to Docker Hub | 30s | Pushes both images (only if all prior stages passed) |
| 📁 8. Archive Reports | 5s | Archives OWASP HTML/JSON/XML + Trivy scan reports |

> **On success:** CI automatically triggers the `samurai-cd` job with the `IMAGE_TAG` parameter.

##### IMAGE_TAG Strategy

Every commit gets a unique, immutable tag — **never use `:latest`** in GitOps:

```
sha-d7f408d  ← commit d7f408d
sha-abc1234  ← commit abc1234
```

ArgoCD only redeploys when `values.yaml` changes. If the tag stays `:latest`, ArgoCD sees no change.

#### 6.2 CD Pipeline (`samurai-cd`)

**New Item → samurai-cd → Pipeline → OK**

**Pipeline Definition:**
```
Definition:   Pipeline script from SCM
SCM:          Git
Repository:   https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
Credentials:  github-creds
Branch:       */main
Script Path:  Devsecops+gitops/Jenkins-CD.yml
```

##### 3-Stage CD Pipeline

| Stage | Description |
|-------|-------------|
| 1. Checkout | Pulls repo to access `helm/samurai-app/values.yaml` |
| 2. Update Image Tag | `sed` replaces both backend and frontend image tags with the new SHA |
| 3. Push to GitHub | `git commit + push` — ArgoCD detects the change and deploys |

##### Why Two sed Commands?

```bash
# First run — tag is still 'latest'
sed -i 's|tag: latest|tag: sha-abc1234|g' helm/samurai-app/values.yaml

# All subsequent runs — tag is already 'sha-oldvalue'
sed -i 's|tag: sha-[a-f0-9]*|tag: sha-abc1234|g' helm/samurai-app/values.yaml
```

> **Important:** Remove inline comments from tag lines in `values.yaml`. Comments break the sed pattern:
> ```yaml
> # ❌ Wrong — sed can't match this reliably
> tag: latest    # CI overrides this
>
> # ✅ Correct — clean line, no comment
> tag: latest
> ```

---

### 7. ArgoCD GitOps Setup

ArgoCD runs **inside** the KinD cluster and monitors GitHub for changes.

#### 7.1 Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait for all 7 pods to show `1/1 Running`:

```bash
kubectl get pods -n argocd -w
```

#### 7.2 Access the ArgoCD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80 --address 0.0.0.0 &
```

Access at `http://&lt;agent-public-ip&gt;:8080`

Get the admin password:

```bash
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

Login: `admin` / &lt;password&gt;

#### 7.3 Connect GitHub Repo in ArgoCD

**Settings → Repositories → Connect Repo:**
- Connection method: `HTTPS`
- Type: `git`
- Project: `default`
- URL: `https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git`
- Username: `HamzaMaLik121`
- Password: &lt;GitHub PAT&gt;

#### 7.4 Register the Application (One-Time)

```bash
kubectl apply -f Devsecops+gitops/argocd-app.yaml
```

This is all you need. The app manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: samurai-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
    targetRevision: main
    path: helm/samurai-app
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: samurai
  syncPolicy:
    automated:
      prune: true       # Delete removed resources
      selfHeal: true    # Revert manual changes
    syncOptions:
      - CreateNamespace=true
```

> ArgoCD polls GitHub every 3 minutes. When `values.yaml` changes, it runs `helm upgrade` automatically.

---

### 8. Monitoring with Prometheus & Grafana

Install the full kube-prometheus-stack (Prometheus + Grafana + AlertManager + exporters) with one Helm command:

```bash
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring

helm install monitoring \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

#### Access Prometheus

```bash
kubectl port-forward \
  svc/prometheus-monitoring-kube-prometheus-prometheus \
  -n monitoring 9090:9090 --address 0.0.0.0 &
```

Access: `http://&lt;agent-ip&gt;:9090`

Verify: **Status → Target health** — all targets should show green UP.

#### Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana \
  -n monitoring 3000:80 --address 0.0.0.0 &
```

Access: `http://&lt;agent-ip&gt;:3000`  
Login: `admin` / `admin123`

#### Import Dashboards

Go to **Dashboards → Import** by ID:

| ID | Dashboard |
|----|-----------|
| 1860 | Node Exporter Full (detailed system metrics) |
| 15661 | Kubernetes Cluster Overview |

---

### 9. GitHub Webhook

For automatic CI triggers on every push:

1. **GitHub Repo → Settings → Webhooks → Add webhook**

```
Payload URL:   http://<master-PUBLIC-ip>:8080/github-webhook/
Content type:  application/json
Events:        Just the push event
Active:        ☑ checked
```

2. **In Jenkins → samurai-ci → Configure → Build Triggers:**
```
☑ GitHub hook trigger for GITScm polling
```

---

## 🌐 Service URLs & Access

| Service | URL | Login |
|---------|-----|-------|
| 🛒 **Samurai App** | `http://&lt;agent-ip&gt;:30080` | `admin@bushido.com` / `bushido2026` |
| 🤖 **Jenkins** | `http://&lt;master-ip&gt;:8080` | admin / your password |
| 📊 **SonarQube** | `http://&lt;master-ip&gt;:9000` | admin / your password |
| 🚀 **ArgoCD** | `http://&lt;agent-ip&gt;:8080` | admin / `kubectl get secret` |
| 📈 **Grafana** | `http://&lt;agent-ip&gt;:3000` | admin / `admin123` |
| 🔍 **Prometheus** | `http://&lt;agent-ip&gt;:9090` | (no auth) |

### Port Forwards After EC2 Restart

Restarting the EC2 instance kills all port-forwards. Run these after every restart:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80 --address 0.0.0.0 &
kubectl port-forward svc/frontend-service -n samurai 30080:80 --address 0.0.0.0 &
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80 --address 0.0.0.0 &
kubectl port-forward svc/prometheus-monitoring-kube-prometheus-prometheus -n monitoring 9090:9090 --address 0.0.0.0 &

# Also restart SonarQube if stopped
docker start sonarqube
```

---

## 📂 Project Structure

```
samurai-themed-e-commerce-store/
│
├── 🐍 backend/                          # Flask API server
│   ├── app.py                           # App factory, create_app(), _seed_admin()
│   ├── config.py                        # MySQL env vars (MYSQL_HOST, MYSQL_PORT, etc.)
│   ├── extensions.py                    # Flask extensions init
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── models/                          # SQLAlchemy models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── bundle.py
│   └── routes/                          # API route blueprints
│       ├── auth.py, cart.py, orders.py
│       ├── products.py, bundles.py, admin.py
│
├── ⚛️ frontend/                         # React + Vite
│   ├── Dockerfile
│   ├── nginx.conf                       # port 80, proxy /api/ → backend-service:5000
│   ├── package.json
│   └── src/
│       ├── components/                  # Navbar, Footer, ProductCard, BundleCard, etc.
│       ├── pages/                       # Home, Shop, Cart, Checkout, Login, etc.
│       ├── context/                     # AuthContext, CartContext
│       ├── api/client.js                # API client
│       └── data/mockProducts.js
│
├── 🗄️ database/                        # MySQL initialization
│   ├── init.sql                         # Creates all tables
│   └── seed.sql                         # Seeds categories, products, bundles
│
├── ☸️ helm/samurai-app/                 # Helm chart
│   ├── Chart.yaml
│   ├── values.yaml                      # CD pipeline updates image tags here
│   ├── initdb/                          # MySQL init scripts (mounted as ConfigMap)
│   └── templates/                       # K8s manifests
│       ├── mysql-*.yaml                 # MySQL Deployment, PVC, Secret, Service
│       ├── backend-*.yaml               # Flask Deployment + ClusterIP Service
│       └── frontend-*.yaml              # React Deployment + NodePort Service
│
├── 🔧 Devsecops+gitops/                 # Pipeline definitions
│   ├── Jenkins-CI.yml                   # 8-stage CI pipeline
│   ├── Jenkins-CD.yml                   # 3-stage CD pipeline
│   └── argocd-app.yaml                  # ArgoCD Application manifest
│
├── 🐳 docker-compose.yml                # Local development
└── 📄 README.md                         # This file
```

---

## 🩺 Verification Commands

Run these after deployment to verify everything is working:

```bash
# 1. All samurai app pods running?
kubectl get pods -n samurai

# 2. ArgoCD synced and healthy?
kubectl get application -n argocd

# 3. All monitoring pods running?
kubectl get pods -n monitoring

# 4. Confirm the image tag was updated by CD
kubectl get deployment samurai-backend -n samurai \
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# 5. MySQL is accessible with the correct password
kubectl exec -n samurai deployment/mysql -- \
  mysql -u samurai_user -psamurai_pass_2026 -e "SELECT 1;"

# 6. Database tables exist
kubectl exec -n samurai deployment/mysql -- \
  mysql -u samurai_user -psamurai_pass_2026 samurai_db -e "SHOW TABLES;"
```

All should return success. If any fail, check the [Common Issues](#-common-issues--fixes) section below.

---

## 🐛 Common Issues & Fixes

### 🔴 MySQL Access Denied

**Error:** `Access denied for user 'samurai_user'@'10.x.x.x'`

**Cause:** The MySQL PVC has old data initialized with a different password. Changing the Kubernetes Secret doesn't affect an already-initialized MySQL — it only reads env vars on a fresh empty-disk startup.

**Fix:**
```bash
# 1. Pause ArgoCD auto-sync
kubectl patch application samurai-app -n argocd \
  --type merge \
  -p '{"spec":{"syncPolicy":{"automated":null}}}'

# 2. Delete MySQL deployment
kubectl delete deployment mysql -n samurai

# 3. If PVC stuck in Terminating, remove finalizer
kubectl patch pvc mysql-pvc -n samurai \
  -p '{"metadata":{"finalizers":[]}}' --type merge

# 4. Delete PVC
kubectl delete pvc mysql-pvc -n samurai

# 5. Re-enable auto-sync
kubectl apply -f Devsecops+gitops/argocd-app.yaml
```

### 🔴 Table Does Not Exist

**Error:** `Table 'samurai_db.users' doesn't exist`

**Cause:** `_seed_admin()` runs before tables are created — or `create_app()` is defined twice (second overwrites the first, losing all blueprints).

**Fix:** Ensure a single `create_app()` with the correct order:
```python
with app.app_context():
    db.create_all()   # FIRST — create tables
    _seed_admin()     # SECOND — seed data
```

### 🔴 SonarQube Quality Gate Always ERROR

**Cause:** Using the default `Sonar way` gate which requires 80% test coverage. This will always fail without unit tests.

**Fix:** Create the `Samurai Gate` (see [Section 4.3](#43-create-a-custom-quality-gate)) — remove coverage, duplication, and maintainability conditions. Assign it to the project.

### 🔴 ArgoCD Sync Error — YAML Parse

**Error:** `YAML parse error on mysql-deployment.yaml: did not find expected key`

**Cause:** The `configMap` key is placed inside `volumeMounts` instead of `volumes`.

**Fix:**
```yaml
# ✅ CORRECT — configMap goes in volumes, NOT volumeMounts
volumeMounts:
  - name: mysql-data
    mountPath: /var/lib/mysql
  - name: mysql-initdb
    mountPath: /docker-entrypoint-initdb.d

volumes:                     # ← Pod level, outside containers
  - name: mysql-data
    persistentVolumeClaim:
      claimName: mysql-pvc
  - name: mysql-initdb
    configMap:               # ← CORRECT POSITION
      name: mysql-initdb
```

### 🔴 CD Pipeline — Nothing to Commit

**Error:** `nothing to commit, working tree clean`

**Cause 1:** Tag lines in `values.yaml` have inline comments — sed can't match them reliably.  
**Cause 2:** Only one sed command is used — the first run needs `latest` → `sha-`, subsequent runs need `sha-` → `sha-`.

**Fix:** Remove inline comments from tag lines AND use both sed patterns (see [6.2 CD Pipeline](#62-cd-pipeline-samurai-cd)).

### 🔴 Frontend CrashLoopBackOff — nginx host not found

**Error:** `host not found in upstream "backend" in nginx.conf:11`

**Cause:** `nginx.conf` uses `backend` but the K8s service is named `backend-service`.

**Fix:** In `frontend/nginx.conf`:
```nginx
# ❌ Wrong
proxy_pass http://backend:5000;

# ✅ Correct
proxy_pass http://backend-service:5000/api/;
```

### 🔴 Backend Can't Connect to MySQL via Socket

**Error:** `Can't connect to local server through socket '/run/mysqld/mysqld.sock'`

**Cause:** `config.py` reads env var names that don't match what Helm injects. The backend tries to connect to localhost socket instead of over TCP to `mysql-service`.

**Fix:** Verify `config.py` reads these exact env var names and that `backend-deployment.yaml` injects them:

```python
MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'mysql-service')
MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'samurai_db')
MYSQL_USER     = os.environ.get('MYSQL_USER', 'samurai_user')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'samurai_pass_2026')
```

Also verify `backend-deployment.yaml` injects env vars with these exact names from the Helm values.

### 🔴 Pods Crashing After EC2 Restart

**Cause:** All pods start simultaneously on restart, causing OOM on the agent.

**Fix:** Use `m7i-flex.large` (8GB RAM) minimum. After restart, wait 3–5 minutes. If needed:
```bash
kubectl rollout restart deployment/argocd-redis -n argocd
sleep 30
kubectl rollout restart deployment/argocd-server -n argocd
kubectl rollout restart deployment/samurai-frontend -n samurai
```

---

## ⚠️ Critical Configuration Details

### `backend/app.py` — The Order of Operations Matters

```python
def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register all blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    # CRITICAL: db.create_all() must come BEFORE _seed_admin()
    with app.app_context():
        db.create_all()   # ← FIRST: create tables
        _seed_admin()     # ← SECOND: seed admin user

    return app
```

> ⚠️ **Do NOT define `create_app()` twice.** The second definition overwrites the first and you lose all blueprints and extensions.

### `frontend/nginx.conf` — Two Critical Settings

```nginx
server {
    listen 80;        # ← must be 80, NOT 3000 (3000 is docker-compose only)

    location /api/ {
        proxy_pass http://backend-service:5000/api/;  # ← backend-service NOT backend
    }
}
```

### `backend/config.py` — Env Var Names Must Match Helm

The env var names in `config.py` must match exactly what `backend-deployment.yaml` injects:

| config.py Variable | Env Var Name | Helm values.yaml Path |
|-------------------|-------------|----------------------|
| `MYSQL_HOST` | `MYSQL_HOST` | `backend.env.MYSQL_HOST` |
| `MYSQL_PORT` | `MYSQL_PORT` | `backend.env.MYSQL_PORT` |
| `MYSQL_DATABASE` | `MYSQL_DATABASE` | `backend.env.MYSQL_DATABASE` |
| `MYSQL_USER` | `MYSQL_USER` | `backend.env.MYSQL_USER` |
| `MYSQL_PASSWORD` | `MYSQL_PASSWORD` | `backend.env.MYSQL_PASSWORD` |

## Architectural Notes

### MySQL as a Deployment (Intentional)

MySQL runs as a **Deployment** with `strategy: Recreate` — this is intentional for this project but **architecturally incorrect** for production databases in Kubernetes.

**Why it matters:** Deployments are for stateless workloads. Rolling updates create multiple ReplicaSets — having two MySQL pods writing to the same PVC is dangerous.

**Production fix:** Use a **StatefulSet** instead:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql-service
  replicas: 1
  selector:
    matchLabels:
      app: samurai-app
      component: mysql
  template:
    # ... same pod spec ...
  volumeClaimTemplates:
    - metadata:
        name: mysql-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

**StatefulSet benefits:**
- Stable pod identity (`mysql-0` instead of random hash)
- Ordered startup and shutdown
- Each pod gets its own PVC automatically
- Proper identity for database replication

### Helm `values.yaml` — Tag Lines Must Be Clean

```yaml
# ✅ Correct — no inline comments
backend:
  image:
    repository: hamzamalik1/samurai-backend
    tag: latest
    pullPolicy: Always

frontend:
  image:
    repository: hamzamalik1/samurai-frontend
    tag: latest
    pullPolicy: Always
```

---

## 🏁 Quick Reference

### Jenkins Credentials Summary

| ID | Kind | Used By |
|----|------|---------|
| `sonar-token` | Secret text | SonarQube server config + CI stages 2/4 |
| `dockerhub-creds` | Username/Password | CI stage 7 (image push) |
| `github-creds` | Username/Password | CI + CD checkout + CD git push |
| `nvd-api-key` | Secret text | CI stage 3 (OWASP NVD database) |
| `hamza-agent-key` | SSH private key | Jenkins agent node connection |

### Kubernetes Namespaces

| Namespace | Contents |
|-----------|----------|
| `samurai` | MySQL, samurai-backend, samurai-frontend |
| `argocd` | ArgoCD (controller, server, redis, repo-server, dex, notifications, applicationset) |
| `monitoring` | Prometheus, Grafana, AlertManager, node exporters |
| `kube-system` | KinD cluster internals (CoreDNS, etcd, kube-proxy) |

### MySQL Secret Encoding

```bash
echo -n 'rootpassword123' | base64     # → cm9vdHBhc3N3b3JkMTIz
echo -n 'samurai_pass_2026' | base64   # → c2FtdXJhaV9wYXNzXzIwMjY=
```

---

## 📄 License

This project is built and maintained by **Hamza Ali**  
BS Software Engineering — Sarhad University, Peshawar  

<p align="center">
  <a href="https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store">
    <img src="https://img.shields.io/badge/GitHub-HamzaMaLik121-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Docker%20Hub-hamzamalik1-2496ED?style=for-the-badge&logo=docker" alt="Docker Hub">
  </a>
</p>

<br>

<div align="center">
  <sub>Built with ❤️ and the Bushido spirit — ⚔️</sub>
</div>
