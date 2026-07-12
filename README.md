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
  <i>A complete DevSecOps and GitOps pipeline built on AWS EC2 with Jenkins, SonarQube, OWASP Dependency-Check, Trivy, ArgoCD, Helm, KinD, Prometheus, and Grafana.</i>
</p>

<p align="center">
  <b>App Stack:</b> Flask (Python) backend + React/Vite frontend + MySQL &nbsp;·&nbsp;
  <b>Docker Hub:</b> hamzamalik1
</p>

<br>

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Infrastructure](#infrastructure)
- [Project Structure](#project-structure)
- [Part 1 — Master EC2 Setup (Jenkins + SonarQube)](#part-1--master-ec2-setup)
- [Part 2 — Agent EC2 Setup (Docker, KinD & Tools)](#part-2--agent-ec2-setup)
- [Part 3 — Jenkins Plugins](#part-3--jenkins-plugins)
- [Part 4 — Jenkins Tools Configuration](#part-4--jenkins-tools-configuration)
- [Part 5 — SonarQube Project + Token Setup](#part-5--sonarqube-project--token-setup)
- [Part 6 — Jenkins Credentials (All 5)](#part-6--jenkins-credentials)
- [Part 7 — Jenkins SonarQube Server Configuration](#part-7--jenkins-sonarqube-server-configuration)
- [Part 8 — Jenkins Agent Node Setup](#part-8--jenkins-agent-node)
- [Part 9 — GitHub Webhook](#part-9--github-webhook)
- [Part 10 — Jenkins CI Job Setup](#part-10--jenkins-ci-job-setup)
- [Part 11 — Jenkins CD Job Setup](#part-11--jenkins-cd-job-setup)
- [Part 12 — Helm Chart Key Details](#part-12--helm-chart-key-details)
- [Part 13 — ArgoCD Setup](#part-13--argocd-setup)
- [Part 14 — Monitoring Setup (Prometheus + Grafana)](#part-14--monitoring-setup)
- [Part 15 — Port Forwards After EC2 Restart](#part-15--port-forwards-after-ec2-restart)
- [Part 16 — Common Issues & Exact Fixes](#part-16--common-issues--exact-fixes)
- [Part 17 — Verification Commands](#part-17--verification-commands)
- [Part 18 — Known Architectural Issue (MySQL as Deployment)](#part-18--known-architectural-issue-intentional)
- [Quick Reference](#quick-reference)
- [License](#license)

---

## Architecture Overview

```
Developer pushes code to GitHub (main branch)
        ↓  webhook triggers
Jenkins CI runs on Agent EC2
  Stage 1 → Checkout code, set IMAGE_TAG = sha-<7char>
  Stage 2 → SonarQube SAST scan (Python + JS)
  Stage 3 → OWASP Dependency Check (requirements.txt + package.json)
  Stage 4 → SonarQube Quality Gate (waits for verdict)
  Stage 5 → Docker Build (backend + frontend images)
  Stage 6 → Trivy image scan (CRITICAL/HIGH CVEs)
  Stage 7 → Push to Docker Hub
  Stage 8 → Archive reports
        ↓  CI triggers CD on success
Jenkins CD runs on Agent EC2
  → Updates helm/samurai-app/values.yaml with new SHA tag
  → git commit + push to GitHub
        ↓  ArgoCD detects values.yaml change
ArgoCD (inside KinD on Agent EC2)
  → Pulls updated Helm chart from GitHub
  → Runs helm upgrade in samurai namespace
  → Kubernetes pulls new images from Docker Hub
        ↓
App live at http://<agent-ip>:30080
Prometheus + Grafana monitoring active
```

---

## Infrastructure

| Machine | Instance Type | RAM | Role |
|---------|---------------|-----|------|
| **Master** | Any (t3.medium minimum) | 4GB+ | Jenkins Controller + SonarQube |
| **Agent** | m7i-flex.large | **8GB required** | Jenkins Agent + KinD + ArgoCD + Monitoring |

> **⚠️ Critical:** Agent needs 8GB RAM minimum. Running KinD (4 nodes) + ArgoCD + Prometheus/Grafana + samurai app + Jenkins agent all together requires it. Anything less causes OOM crashes after restart.

---

## Project Structure

```
samurai-themed-e-commerce-store/
├── backend/
│   ├── app.py               ← Flask app, create_app(), _seed_admin()
│   ├── config.py            ← reads MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
│   ├── Dockerfile
│   ├── extensions.py
│   ├── models/
│   ├── requirements.txt
│   └── routes/
├── database/
│   ├── init.sql             ← creates all tables with DEFAULT CURRENT_TIMESTAMP
│   └── seed.sql             ← inserts categories, products, bundles
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf           ← listens on port 80, proxies /api/ to backend-service:5000
│   ├── package.json
│   └── src/
├── helm/
│   └── samurai-app/
│       ├── Chart.yaml
│       ├── values.yaml      ← CD pipeline updates backend.image.tag + frontend.image.tag here
│       ├── initdb/
│       │   ├── init.sql     ← copy of database/init.sql (mounted into MySQL on fresh start)
│       │   └── seed.sql     ← copy of database/seed.sql
│       └── templates/
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml      ← ClusterIP, port 5000
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml     ← NodePort 30080
│           ├── ingress.yaml              ← disabled (ingress.enabled: false)
│           ├── mysql-deployment.yaml     ← NOTE: uses Deployment not StatefulSet (see Part 18)
│           ├── mysql-initdb-configmap.yaml
│           ├── mysql-pvc.yaml
│           ├── mysql-secret.yaml
│           └── mysql-service.yaml        ← ClusterIP, port 3306
├── Devsecops+gitops/
│   ├── Jenkins-CI.yml       ← 8-stage CI pipeline
│   ├── Jenkins-CD.yml       ← 3-stage CD pipeline (values.yaml update only)
│   └── argocd-app.yaml      ← applied once to register app with ArgoCD
└── docker-compose.yml       ← for local development only
```

---

## Part 1 — Master EC2 Setup

### 1.1 Install Jenkins

```bash
docker run -d \
  --name jenkins \
  --restart=always \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

Get initial admin password:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Access at `http://<master-public-ip>:8080` → complete setup wizard → install suggested plugins.

### 1.2 Install SonarQube

```bash
docker run -d \
  --name sonarqube \
  --restart=always \
  -p 9000:9000 \
  sonarqube:lts-community
```

Wait 60–90 seconds. Access at `http://<master-public-ip>:9000`

Default login: `admin` / `admin` → you will be forced to change password on first login.

> **Important:** SonarQube must run on master ONLY. Do not run it on agent — agent has limited RAM and it will cause OOM crashes.

### 1.3 Master EC2 Security Group — Inbound Rules

| Port | Source | Purpose |
|------|--------|---------|
| 8080 | `0.0.0.0/0` | Jenkins UI |
| 9000 | `0.0.0.0/0` | SonarQube UI |
| 50000 | Agent private IP | Jenkins agent JNLP connection |
| 22 | Your IP | SSH |

---

## Part 2 — Agent EC2 Setup

### 2.1 Install Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo usermod -aG docker ubuntu
newgrp docker
docker --version
```

### 2.2 Install Java

```bash
sudo apt install -y openjdk-21-jdk
java --version
```

### 2.3 Install Git

```bash
sudo apt install -y git
git --version
```

### 2.4 Install Trivy

```bash
sudo apt install -y wget apt-transport-https gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | \
  sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] \
  https://aquasecurity.github.io/trivy-repo/deb generic main" | \
  sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install -y trivy
trivy --version
```

### 2.5 Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s \
  https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
```

### 2.6 Install KinD

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind --version
```

### 2.7 Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

### 2.8 Create KinD Cluster

```bash
kind create cluster --name bushido-brand
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

### 2.9 Agent EC2 Security Group — Inbound Rules

| Port | Source | Purpose |
|------|--------|---------|
| 22 | Your IP | SSH |
| 8080 | `0.0.0.0/0` | ArgoCD UI (port-forwarded) |
| 9090 | `0.0.0.0/0` | Prometheus UI (port-forwarded) |
| 3000 | `0.0.0.0/0` | Grafana UI (port-forwarded) |
| 30080 | `0.0.0.0/0` | Samurai App frontend |

---

## Part 3 — Jenkins Plugins

Go to **Manage Jenkins → Plugins → Available plugins** — search and install each:

| Plugin Name | Purpose |
|-------------|---------|
| **SonarQube Scanner for Jenkins** | Runs `sonar-scanner` CLI in pipeline |
| **OWASP Dependency-Check** | SCA scan + publishes report in Jenkins UI |
| **Docker Pipeline** | `docker build` and `docker push` steps |
| **Sonar Quality Gates Plugin** | `waitForQualityGate` step |
| **Pipeline Stage View** | Shows stage grid in Jenkins job UI |

Restart Jenkins after installing all plugins.

---

## Part 4 — Jenkins Tools Configuration

Go to **Manage Jenkins → Tools**

### SonarQube Scanner

```
Name:                 SonarQube Scanner
☑ Install automatically
Version:              SonarQube Scanner 8.1.0.6389
Install from:         Maven Central
```

### Dependency-Check

```
Name:                 OWASP-DC
☑ Install automatically
Version:              latest
```

> **⚠️ Critical:** The name `OWASP-DC` must match exactly what is referenced in the Jenkinsfile `odcInstallation: 'OWASP-DC'`. If you use a different name here, update the Jenkinsfile too.

Click **Save**.

---

## Part 5 — SonarQube Project + Token Setup

This section covers everything you need to do in SonarQube — creating the project, generating the Jenkins authentication token, creating a custom quality gate (since we have no unit tests), and reviewing security hotspots after the first CI run.

### 5.1 Create Project

1. Login to `http://<master-public-ip>:9000`
2. Click **Projects** in top nav
3. Click **Create Project** button (top right)
4. Select **Manually**
5. Fill in the form:
   ```
   Project display name: samurai ecommerce app
   Project key:          samurai-ecommerce-app
   Main branch name:     main
   ```
6. Click **Set Up**
7. The next screen shows a DevOps platform wizard (Bitbucket, GitHub, GitLab buttons) — **ignore this completely**, navigate away from it. The project is already created by clicking Set Up.

### 5.2 Generate Token (This is the key to connecting SonarQube with Jenkins)

This token is what Jenkins will use to authenticate with SonarQube. Follow these exact steps:

1. Click the **A** avatar button (top right of SonarQube)
2. Click **My Account**
3. Click the **Security** tab
4. Under **Generate Tokens**, fill in:
   ```
   Name:       jenkins-token
   Type:       User Token
   Expires in: No expiration
   ```
5. Click **Generate**
6. **🔴 COPY THE TOKEN VALUE IMMEDIATELY** — it is shown only once and cannot be retrieved again. If you lose it, you must generate a new one.
7. Save it somewhere safe — you will paste it into Jenkins credentials in [Part 6 — Credential 1](#credential-1--sonarqube-token).

### 5.3 Create Custom Quality Gate

The default `Sonar way` gate is BUILT-IN and cannot be edited. It requires 80% test coverage which will always fail since we have no unit tests. You must create a custom gate.

1. Click **Quality Gates** in top nav
2. Click **Create** button
3. Name: `Samurai Gate` → **Save**
4. You will see it has copied conditions from `Sonar way`. Click **Unlock editing**
5. Click the red trash icon next to these conditions to **delete** them:
   - Coverage is less than 80%
   - Duplicated Lines (%) is greater than 3%
   - Maintainability Rating is worse than A
6. Keep only these three conditions:
   - Reliability Rating is worse than A
   - Security Hotspots Reviewed is less than 100%
   - Security Rating is worse than A
7. Click **Save**

### 5.4 Assign Quality Gate to Project

1. Go to **Projects → Samurai E-Commerce App**
2. Click **Project Settings** (top right dropdown)
3. Click **Quality Gate**
4. Select **Samurai Gate** from the dropdown
5. Click **Save**

### 5.5 Review Security Hotspots (After First CI Run)

After CI runs for the first time, SonarQube will flag 2 security hotspots. Until you review them, `Security Hotspots Reviewed` stays at 0% and the gate fails.

1. Go to your project → click the **Security Hotspots** tab
2. You will see 2 hotspots:
   - **Cross-Site Request Forgery (CSRF)** — HIGH — in `backend/app.py`
   - **Permission** — MEDIUM
3. Click on **Cross-Site Request Forgery (CSRF)**
4. Click the **Change status** button → select **Safe**
5. Add this comment explaining why:
   ```
   API intentionally allows all origins as it serves a dedicated frontend client running on a known EC2 host.
   ```
6. Click **Save**
7. Click on the **Permission** hotspot → same steps → mark as **Safe**

After both are marked Safe, **Security Hotspots Reviewed** shows 100% and the Quality Gate passes.

---

## Part 6 — Jenkins Credentials

Go to **Manage Jenkins → Credentials → System → Global credentials (unrestricted) → Add Credentials**

Add all **five** credentials one by one. Each has specific required fields shown below.

---

### Credential 1 — SonarQube Token

This credential stores the token you generated in [Part 5.2](#52-generate-token). Jenkins uses it to authenticate with SonarQube when running SAST scans and checking the Quality Gate.

```
Kind:        Secret text
Secret:      <paste the jenkins-token value from SonarQube Step 5.2>
ID:          sonar-token
Description: SonarQube Token
```

> **Used by:** SonarQube server configuration (Part 7) + CI Stage 2 (SAST Scan) + CI Stage 4 (Quality Gate)

---

### Credential 2 — Docker Hub

Jenkins uses this to push built Docker images to Docker Hub.

```
Kind:        Username with password
Username:    hamzamalik1
Password:    <Docker Hub password or access token>
ID:          dockerhub-creds
Description: Docker Hub Credentials
```

> **Used by:** CI Stage 7 (Push to Docker Hub)

---

### Credential 3 — GitHub

Jenkins uses this to clone the repository and to push updated `values.yaml` back (in the CD pipeline). The token needs `repo` scope and webhook permissions.

```
Kind:        Username with password
Username:    HamzaMaLik121
Password:    <GitHub Personal Access Token with repo + webhook permissions>
ID:          github-creds
Description: GitHub PAT
```

> **Used by:** CI + CD checkout + CD git push

---

### Credential 4 — NVD API Key

OWASP Dependency-Check uses the NVD (National Vulnerability Database) API to look up CVE data. Get a free API key from [https://nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key).

```
Kind:        Secret text
Secret:      <your NVD API key from nvd.nist.gov>
ID:          nvd-api-key
Description: NVD API Key
```

> **Used by:** CI Stage 3 (OWASP Dependency Check — NVD database queries)

---

### Credential 5 — Agent SSH Key

Jenkins uses this to SSH into the agent EC2 and run pipeline stages.

```
Kind:              SSH Username with private key
Username:          ubuntu
Private Key:       Enter directly → paste full contents of agent .pem file
ID:                hamza-agent-key
Description:       Agent SSH Key
```

> **Used by:** Jenkins agent node connection (Part 8)

---

### Credentials Quick Reference

| ID | Kind | Used By |
|----|------|---------|
| `sonar-token` | Secret text | SonarQube server config + CI Stage 2/4 |
| `dockerhub-creds` | Username/Password | CI Stage 7 (push images) |
| `github-creds` | Username/Password | CI + CD checkout + CD git push |
| `nvd-api-key` | Secret text | CI Stage 3 (OWASP NVD database) |
| `hamza-agent-key` | SSH private key | Jenkins agent node connection |

---

## Part 7 — Jenkins SonarQube Server Configuration

This is where you **connect SonarQube to Jenkins** using the credential you created. This must be done for the pipeline to be able to run SonarQube scans. **Do not skip this step.**

Go to **Manage Jenkins → System** → scroll down to the **SonarQube servers** section.

```
☑ Environment variables    ← check this box (makes SONAR_HOST_URL and SONAR_AUTH_TOKEN available)
Name:                      SonarQube
Server URL:                http://<master-PRIVATE-ip>:9000
Server authentication:     sonar-token   ← select from the dropdown (created in Part 6 — Credential 1)
```

Click **Save**.

> **🚨 Important:** Use the **private IP** of master, not public IP. Jenkins agent communicates with SonarQube over the internal AWS network. If you use the public IP, the connection will be slower and potentially blocked by security groups.

---

## Part 8 — Jenkins Agent Node

Go to **Manage Jenkins → Nodes → New Node**

```
Node name:                   hamza-agent
Type:                        Permanent Agent
Remote root directory:       /home/ubuntu/jenkins-agent
Labels:                      hamza-agent
Usage:                       Use this node as much as possible
Launch method:               Launch agents via SSH
Host:                        <agent-PRIVATE-ip>
Credentials:                 hamza-agent-key
Host Key Verification:       Non verifying
```

Click **Save** → Jenkins automatically connects. Wait for the node to show a green circle in **Manage Jenkins → Nodes**.

---

## Part 9 — GitHub Webhook

For CI to trigger automatically on every git push:

1. Go to your GitHub repo → **Settings → Webhooks → Add webhook**
2. Fill in:
   ```
   Payload URL:   http://<master-PUBLIC-ip>:8080/github-webhook/
   Content type:  application/json
   Secret:        (leave empty)
   Events:        ☑ Just the push event
   Active:        ☑ checked
   ```
3. Click **Add webhook**

Then in Jenkins → **samurai-ci job → Configure → Build Triggers**:

```
☑ GitHub hook trigger for GITScm polling
```

---

## Part 10 — Jenkins CI Job Setup

1. **New Item → samurai-ci → Pipeline → OK**
2. Under **Build Triggers**: `☑ GitHub hook trigger for GITScm polling`
3. Under **Pipeline**:
   ```
   Definition:   Pipeline script from SCM
   SCM:          Git
   Repository:   https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
   Credentials:  github-creds
   Branch:       */main
   Script Path:  Devsecops+gitops/Jenkins-CI.yml
   ```
4. Click **Save**

### CI Pipeline — 8 Stages

| # | Stage | What Happens |
|---|-------|-------------|
| **1** | **Checkout** | Pulls main branch. Sets `IMAGE_TAG = sha-<7char commit hash>` |
| **2** | **SAST — SonarQube Scan** | Scans `backend/` (Python) and `frontend/src/` (JS/React). Excludes `node_modules`, `__pycache__`, `database/` |
| **3** | **SCA — OWASP Dependency Check** | Scans `backend/requirements.txt` and `frontend/package.json` against NVD CVE database (uses `nvd-api-key`) |
| **4** | **SonarQube Quality Gate** | Jenkins waits up to 5 minutes for SonarQube to process the scan. Pipeline aborts if gate returns ERROR |
| **5** | **Docker Build** | Builds `hamzamalik1/samurai-backend:sha-xxxx` and `hamzamalik1/samurai-frontend:sha-xxxx` |
| **6** | **Image Scan — Trivy** | Scans both images for CRITICAL and HIGH CVEs. `--exit-code 1` fails pipeline if vulnerabilities found |
| **7** | **Push to Docker Hub** | Pushes both images. Only reachable if all above stages passed |
| **8** | **Publish Reports** | Archives OWASP HTML/JSON/XML + Trivy scan txt files in Jenkins build artifacts |

On success: CI automatically triggers `samurai-cd` job and passes `IMAGE_TAG` as a parameter.

### IMAGE_TAG Strategy

Every commit gets a unique immutable tag:

```
sha-d7f408d  ← commit d7f408d
sha-abc1234  ← commit abc1234
sha-xyz9999  ← commit xyz9999
```

**Never use `:latest` in GitOps.** ArgoCD only redeploys when `values.yaml` changes — if tag stays `:latest` even with a new image, ArgoCD sees no change and does nothing.

---

## Part 11 — Jenkins CD Job Setup

1. **New Item → samurai-cd → Pipeline → OK**
2. Under **Pipeline**:
   ```
   Definition:   Pipeline script from SCM
   SCM:          Git
   Repository:   https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
   Credentials:  github-creds
   Branch:       */main
   Script Path:  Devsecops+gitops/Jenkins-CD.yml
   ```
3. Click **Save**

### CD Pipeline — 3 Stages

| # | Stage | What Happens |
|---|-------|-------------|
| **1** | **Checkout** | Pulls repo to access `helm/samurai-app/values.yaml` |
| **2** | **Update Image Tag** | `sed` replaces image tags in `helm/samurai-app/values.yaml` |
| **3** | **Push to GitHub** | `git commit + push` — ArgoCD detects this change and deploys |

### sed Commands — Why Two Are Needed

```bash
# First run ever — tag is still 'latest'
sed -i 's|tag: latest|tag: sha-abc1234|g' helm/samurai-app/values.yaml

# All subsequent runs — tag is already 'sha-oldvalue'
sed -i 's|tag: sha-[a-f0-9]*|tag: sha-abc1234|g' helm/samurai-app/values.yaml
```

> **⚠️ Important:** Remove any inline comments from the tag lines in `values.yaml`. Comments break the sed pattern:
> ```yaml
> # ❌ Wrong — sed won't reliably match this
> tag: latest    # ← CI will override this with sha-<commit>
>
> # ✅ Correct — clean line, no comment
> tag: latest
> ```

---

## Part 12 — Helm Chart Key Details

### values.yaml — Tag Lines Must Be Clean

```yaml
backend:
  image:
    repository: hamzamalik1/samurai-backend
    tag: latest          ← no comment after this line
    pullPolicy: Always
  env:
    MYSQL_HOST: mysql-service      ← K8s service name, not localhost
    MYSQL_PORT: "3306"
    MYSQL_DATABASE: samurai_db
    MYSQL_USER: samurai_user

frontend:
  image:
    repository: hamzamalik1/samurai-frontend
    tag: latest          ← no comment after this line
    pullPolicy: Always
  port: 80               ← must match nginx.conf listen port
  service:
    type: NodePort
    port: 80
    nodePort: 30080
```

### MySQL Secret — Password Encoding

```bash
# Encode passwords
echo -n 'rootpassword123' | base64     # → cm9vdHBhc3N3b3JkMTIz
echo -n 'samurai_pass_2026' | base64   # → c2FtdXJhaV9wYXNzXzIwMjY=
```

The password in the secret must exactly match the password MySQL was initialized with on its first fresh start.

### Volume Mount Structure — Common Mistake

This is a very common YAML error that causes ArgoCD sync failures. **Memorize this pattern:**

```yaml
# ❌ WRONG — configMap inside volumeMounts (causes YAML parse error)
volumeMounts:
  - name: mysql-initdb
    mountPath: /docker-entrypoint-initdb.d
  - name: mysql-initdb     ← WRONG POSITION
    configMap:
      name: mysql-initdb

# ✅ CORRECT — configMap goes in volumes, not volumeMounts
volumeMounts:
  - name: mysql-data
    mountPath: /var/lib/mysql
  - name: mysql-initdb
    mountPath: /docker-entrypoint-initdb.d

volumes:                   ← at pod level, outside containers section
  - name: mysql-data
    persistentVolumeClaim:
      claimName: mysql-pvc
  - name: mysql-initdb
    configMap:             ← CORRECT POSITION
      name: mysql-initdb
```

**Rule:** `volumeMounts` only has `name` + `mountPath`. Everything else (PVC, ConfigMap, Secret source) goes in `volumes`.

### nginx.conf — Two Critical Settings

```nginx
server {
    listen 80;        ← must be 80, NOT 3000 (3000 is docker-compose only)

    location /api/ {
        proxy_pass http://backend-service:5000/api/;  ← backend-service not backend
    }
}
```

### backend/config.py — Env Var Names

These must match exactly what Helm injects via `backend-deployment.yaml`:

```python
MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'samurai_db')
MYSQL_USER     = os.environ.get('MYSQL_USER', 'samurai_user')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'samurai_pass_2026')
```

**Env Var Mapping Table:**

| config.py Variable | Env Var Name | Helm values.yaml Path |
|-------------------|-------------|----------------------|
| `MYSQL_HOST` | `MYSQL_HOST` | `backend.env.MYSQL_HOST` |
| `MYSQL_PORT` | `MYSQL_PORT` | `backend.env.MYSQL_PORT` |
| `MYSQL_DATABASE` | `MYSQL_DATABASE` | `backend.env.MYSQL_DATABASE` |
| `MYSQL_USER` | `MYSQL_USER` | `backend.env.MYSQL_USER` |
| `MYSQL_PASSWORD` | `MYSQL_PASSWORD` | `backend.env.MYSQL_PASSWORD` |

### backend/app.py — Order Matters (Critical)

```python
def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register all blueprints
    from routes.auth import auth_bp
    # ... all other blueprints ...
    app.register_blueprint(auth_bp)

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    # CRITICAL: db.create_all() must come BEFORE _seed_admin()
    with app.app_context():
        db.create_all()   ← creates tables first
        _seed_admin()     ← then seeds admin user

    return app
```

> **🚨 Do NOT define `create_app()` twice.** The second definition overwrites the first and you lose all blueprints and extensions. This will cause `Table 'samurai_db.users' doesn't exist` errors.

---

## Part 13 — ArgoCD Setup

### 13.1 Install ArgoCD

```bash
kubectl create namespace argocd

kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait for all pods to be Running (2–3 minutes):

```bash
kubectl get pods -n argocd -w
```

All 7 pods should show `1/1 Running`:

```
argocd-application-controller-0
argocd-applicationset-controller-xxx
argocd-dex-server-xxx
argocd-notifications-controller-xxx
argocd-redis-xxx
argocd-repo-server-xxx
argocd-server-xxx
```

### 13.2 Expose ArgoCD UI

ArgoCD runs inside KinD which is inside EC2, so use port-forward:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80 --address 0.0.0.0 &
```

Access at: `http://<agent-public-ip>:8080`

Get the initial admin password:

```bash
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

Login: `admin` / `<output from above>`

### 13.3 Connect GitHub Repo in ArgoCD

In the ArgoCD UI:
1. **Settings → Repositories → Connect Repo**
2. Fill in:
   ```
   Connection method: HTTPS
   Type:              git
   Project:           default
   Repository URL:    https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store.git
   Username:          HamzaMaLik121
   Password:          <GitHub PAT>
   ```
3. Click **Connect** — should show green **Successful**

### 13.4 Register App with ArgoCD (One Time Only)

```bash
kubectl apply -f Devsecops+gitops/argocd-app.yaml
```

This one command does everything. After this you never touch ArgoCD configuration again — it watches GitHub automatically forever.

`argocd-app.yaml` contents:

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
      prune: true       ← deletes removed resources
      selfHeal: true    ← reverts manual kubectl changes
    syncOptions:
      - CreateNamespace=true  ← creates samurai namespace automatically
```

### 13.5 How ArgoCD Connects to Cluster

ArgoCD runs **inside** the same KinD cluster it deploys to. So it uses `https://kubernetes.default.svc` — the internal Kubernetes API server address. No external cluster configuration needed.

ArgoCD polls GitHub every 3 minutes. When it detects `values.yaml` changed (new image tag), it pulls the Helm chart and runs `helm upgrade` internally.

---

## Part 14 — Monitoring Setup

### 14.1 Install kube-prometheus-stack

One Helm chart installs Prometheus + Grafana + AlertManager + all Kubernetes exporters:

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

Wait for all pods:

```bash
kubectl get pods -n monitoring
```

### 14.2 Access Prometheus

```bash
kubectl port-forward \
  svc/prometheus-monitoring-kube-prometheus-prometheus \
  -n monitoring 9090:9090 --address 0.0.0.0 &
```

Access at: `http://<agent-public-ip>:9090`

Verify scraping: **Status → Target health** — all targets should show green UP.

### 14.3 Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana \
  -n monitoring 3000:80 --address 0.0.0.0 &
```

Access at: `http://<agent-public-ip>:3000`

```
Username: admin
Password: admin123
```

### 14.4 Import Dashboards

Go to **Dashboards → Import** and import by ID:

| ID | Dashboard |
|----|-----------|
| **1860** | Node Exporter Full (most detailed system metrics) |
| **15661** | Kubernetes Cluster Overview |

Pre-built K8s dashboards also available under **Dashboards → Kubernetes** folder after installation.

---

## Part 15 — Port Forwards After EC2 Restart

Every EC2 restart kills port-forwards. Run all at once:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80 --address 0.0.0.0 &
kubectl port-forward svc/frontend-service -n samurai 30080:80 --address 0.0.0.0 &
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80 --address 0.0.0.0 &
kubectl port-forward svc/prometheus-monitoring-kube-prometheus-prometheus -n monitoring 9090:9090 --address 0.0.0.0 &
```

Also restart SonarQube on master if it stopped:

```bash
docker start sonarqube
```

---

## Part 16 — Common Issues & Exact Fixes

### 🔴 Issue 1 — MySQL Access Denied

**Error:** `Access denied for user 'samurai_user'@'10.x.x.x' (using password: YES)`

**Cause:** MySQL PVC has old data initialized with a different password. Changing the secret doesn't affect an already-initialized MySQL — it only reads env vars on fresh empty-disk startup.

**Fix:**

```bash
# 1. Pause ArgoCD auto-sync first (otherwise it recreates namespace immediately)
kubectl patch application samurai-app -n argocd \
  --type merge \
  -p '{"spec":{"syncPolicy":{"automated":null}}}'

# 2. Delete MySQL deployment to release the PVC
kubectl delete deployment mysql -n samurai

# 3. If PVC stuck in Terminating, remove the finalizer
kubectl patch pvc mysql-pvc -n samurai \
  -p '{"metadata":{"finalizers":[]}}' --type merge

# 4. Delete PVC
kubectl delete pvc mysql-pvc -n samurai

# 5. Re-enable auto-sync
kubectl apply -f Devsecops+gitops/argocd-app.yaml
```

MySQL initializes fresh with the correct password from the secret.

---

### 🔴 Issue 2 — Table Does Not Exist

**Error:** `Table 'samurai_db.users' doesn't exist`

**Cause:** `_seed_admin()` runs before tables are created, OR `create_app()` is defined twice (second definition has `db.create_all()` but loses all blueprints from first definition).

**Fix:** Single `create_app()` function with correct order:

```python
with app.app_context():
    db.create_all()   # FIRST
    _seed_admin()     # SECOND
```

---

### 🔴 Issue 3 — SonarQube Quality Gate Always ERROR

**Cause:** Project is using the `Sonar way` default gate which requires 80% coverage. This will always fail with no unit tests.

**Fix:** Create `Samurai Gate` (see [Part 5.3](#53-create-custom-quality-gate)), delete coverage + duplication + maintainability conditions, then assign it to your project (see [Part 5.4](#54-assign-quality-gate-to-project)).

---

### 🔴 Issue 4 — ArgoCD Sync Error — YAML Parse

**Error:** `YAML parse error on mysql-deployment.yaml: did not find expected key`

**Cause:** `configMap` key placed inside `volumeMounts` block instead of `volumes` block.

**Fix:** See [Part 12 — Volume Mount Structure](#volume-mount-structure--common-mistake) — `configMap` must go under `volumes` at pod level.

---

### 🔴 Issue 5 — CD Pipeline — Nothing to Commit

**Error:** `nothing to commit, working tree clean`

**Cause 1:** Tag lines in `values.yaml` have inline comments — sed can't match them reliably.
**Cause 2:** Only one sed command used — first run when tag is `latest` doesn't match `sha-` pattern.

**Fix:** Remove all inline comments from tag lines AND use both sed commands (see [Part 11](#sed-commands--why-two-are-needed)).

---

### 🔴 Issue 6 — Frontend CrashLoopBackOff — nginx host not found

**Error:** `host not found in upstream "backend" in nginx.conf:11`

**Cause:** nginx.conf uses `backend` but the Kubernetes service is named `backend-service`.

**Fix:** In `frontend/nginx.conf`, change:

```nginx
# ❌ Wrong
proxy_pass http://backend:5000;

# ✅ Correct
proxy_pass http://backend-service:5000/api/;
```

Also change `listen 3000` to `listen 80` — port 3000 is docker-compose only.

---

### 🔴 Issue 7 — Backend Can't Connect to MySQL via Socket

**Error:** `Can't connect to local server through socket '/run/mysqld/mysqld.sock'`

**Cause:** `config.py` reads env var names that don't match what Helm injects. Backend tries to connect to localhost socket instead of over TCP to `mysql-service`.

**Fix:** Verify `config.py` reads `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` and verify `backend-deployment.yaml` injects exactly those names (see [Part 12 — Env Var Mapping](#backendconfigpy--env-var-names)).

---

### 🔴 Issue 8 — Pods Crashing After EC2 Restart

**Cause:** All pods start simultaneously on restart causing OOM (Out of Memory). 4GB RAM agent cannot handle KinD + ArgoCD + monitoring + app starting all at once.

**Fix:** Use `m7i-flex.large` (8GB RAM) minimum for agent. After restart wait 3–5 minutes. If specific pods still crash, restart them one at a time:

```bash
kubectl rollout restart deployment/argocd-redis -n argocd
sleep 30
kubectl rollout restart deployment/argocd-server -n argocd
kubectl rollout restart deployment/samurai-frontend -n samurai
```

---

## Part 17 — Verification Commands

Run these after deployment to verify everything is working:

```bash
# All samurai app pods should be 1/1 Running
kubectl get pods -n samurai

# ArgoCD should show Synced + Healthy
kubectl get application -n argocd

# All monitoring pods running
kubectl get pods -n monitoring

# Confirm image tag updated by CD
kubectl get deployment samurai-backend -n samurai \
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# Confirm MySQL has correct password
kubectl exec -n samurai deployment/mysql -- \
  mysql -u samurai_user -psamurai_pass_2026 -e "SELECT 1;"

# Confirm tables exist
kubectl exec -n samurai deployment/mysql -- \
  mysql -u samurai_user -psamurai_pass_2026 samurai_db -e "SHOW TABLES;"
```

All should return success. If any fail, check [Part 16 — Common Issues](#part-16--common-issues--exact-fixes).

---

## Part 18 — Known Architectural Issue (Intentional)

MySQL runs as a **Deployment** — this is intentional in this project but architecturally incorrect for production databases in Kubernetes.

### Why It's Wrong

Deployments are for stateless workloads. The ArgoCD tree shows this clearly — multiple old ReplicaSets hanging around (`mysql-8588b84544`, `mysql-787d669f75`, `mysql-755f7f799`) from rolling updates. This happens because Deployment rollouts create new ReplicaSets. For a database this is dangerous — if two pods tried to start simultaneously they would both try to write to the same PVC.

The strategy `type: Recreate` in the deployment mitigates this partially (stops old pod before starting new one) but the fundamental issue remains — Deployments have no stable pod identity.

### Correct Approach — StatefulSet

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
  volumeClaimTemplates:       ← StatefulSet manages PVC per pod
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

### StatefulSet Benefits

- **Stable pod name:** always `mysql-0` not `mysql-abc123-xyz`
- **Ordered startup/shutdown:** pods start and stop in a specific order
- **Each pod gets its own PVC** automatically via `volumeClaimTemplates`
- **Proper identity** for database replication

---

## Quick Reference

### Service URLs

| Service | URL | Login |
|---------|-----|-------|
| 🛒 **Samurai App** | `http://<agent-ip>:30080` | `admin@bushido.com` / `bushido2026` |
| 🤖 **Jenkins** | `http://<master-ip>:8080` | admin / your-password |
| 📊 **SonarQube** | `http://<master-ip>:9000` | admin / your-password |
| 🚀 **ArgoCD** | `http://<agent-ip>:8080` | admin / `kubectl get secret` |
| 📈 **Grafana** | `http://<agent-ip>:3000` | admin / `admin123` |
| 🔍 **Prometheus** | `http://<agent-ip>:9090` | (no auth) |

### Jenkins Credentials Summary

| ID | Kind | Used By |
|----|------|---------|
| `sonar-token` | Secret text | SonarQube server config + CI Stage 2/4 |
| `dockerhub-creds` | Username/Password | CI Stage 7 (push images) |
| `github-creds` | Username/Password | CI + CD checkout + CD git push |
| `nvd-api-key` | Secret text | CI Stage 3 (OWASP NVD database) |
| `hamza-agent-key` | SSH private key | Jenkins agent node connection |

### Kubernetes Namespaces

| Namespace | Contents |
|-----------|----------|
| `samurai` | mysql, samurai-backend, samurai-frontend |
| `argocd` | ArgoCD all pods |
| `monitoring` | Prometheus, Grafana, AlertManager, exporters |
| `kube-system` | KinD cluster internals |

---

<div align="center">
  <br>
  <h3>⚔️ Samurai E-Commerce Store ⚔️</h3>
  <p>
    <i>Built by <b>Hamza Ali</b> — BS Software Engineering, Sarhad University, Peshawar</i>
  </p>
  <p>
    <a href="https://github.com/HamzaMaLik121/samurai-themed-e-commerce-store">
      <img src="https://img.shields.io/badge/GitHub-HamzaMaLik121-181717?style=for-the-badge&logo=github" alt="GitHub">
    </a>
    <a href="#">
      <img src="https://img.shields.io/badge/Docker%20Hub-hamzamalik1-2496ED?style=for-the-badge&logo=docker" alt="Docker Hub">
    </a>
  </p>
  <br>
  <sub>Built with ❤️ and the Bushido spirit</sub>
</div>
