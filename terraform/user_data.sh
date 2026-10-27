#!/bin/bash
#
# user_data.sh — runs once, as root, on the VM's first boot via cloud-init.
#
# No TTY and no one to answer a prompt, so every command below is
# non-interactive. Output is teed to /var/log/user-data.log; if the app isn't
# up after a boot, read that file first.
#
# What it does, in order:
#   1. install Docker + Compose from Docker's own apt repo
#   2. open 80/443 in the host firewall (OCI's Ubuntu images block them)
#   2b. add 2 GB of swap so the React build survives 1 GB of RAM
#   3. clone the repo
#   4. generate secrets and write a chmod 600 .env
#   5. map the frontend to port 80
#   6. build and start the stack
#   7. seed the prime catalog

set -euo pipefail
exec > >(tee -a /var/log/user-data.log) 2>&1
echo "=== user_data starting: $(date -u) ==="

export DEBIAN_FRONTEND=noninteractive

REPO_URL="https://github.com/Apophis246/warframe-prime-part-tracker.git"
APP_DIR="/opt/warframe-prime-part-tracker"

POSTGRES_USER="apop"
POSTGRES_DB="prime_parts_tracker"


# --- 1. Docker ------------------------------------------------------------
# From Docker's apt repo rather than Ubuntu's, because Ubuntu's docker.io
# package has no compose plugin and lags well behind.

apt-get update -y
apt-get install -y ca-certificates curl git gnupg openssl

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

cat > /etc/apt/sources.list.d/docker.list <<EOF
deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable
EOF

apt-get update -y
apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

systemctl enable --now docker

# So `docker` works without sudo when you SSH in. Takes effect on next login.
usermod -aG docker ubuntu


# --- 2. Host firewall -----------------------------------------------------
# OCI's Ubuntu images ship iptables rules that only permit 22 inbound. The
# VCN security list opening 80/443 is necessary but NOT sufficient — without
# this the ports are open at the network edge and rejected on the box.
#
# Inserted before the catch-all REJECT rather than appended, since iptables
# matches top-down and the REJECT would otherwise win. Saved so the rules
# survive a reboot.

iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT
iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
netfilter-persistent save


# --- 2b. Swap -------------------------------------------------------------
# E2.1.Micro has 1 GB of RAM. That is plenty to RUN the stack (Postgres idles
# around 100 MB, uvicorn 100-150 MB, nginx is negligible) but not to BUILD it:
# the Vite/esbuild step wants well over 1 GB and gets OOM-killed without this.
#
# 2 GB swapfile. The build is slow because swap is disk, but it completes, and
# it is a one-time cost per deploy rather than something felt at runtime.

if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Prefer RAM, but let the kernel reach for swap before it starts killing the
# build. The default of 60 thrashes on a box this small.
sysctl -w vm.swappiness=10
echo 'vm.swappiness=10' > /etc/sysctl.d/99-swappiness.conf


# --- 3. The app -----------------------------------------------------------

git clone --depth 1 "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"


# --- 4. Secrets -----------------------------------------------------------
# Generated here, on the box, so they exist nowhere else — not in git, not in
# terraform.tfstate, not in cloud-init logs. umask 077 means the file is
# never briefly world-readable between creation and chmod.
#
# To read them later: sudo cat /opt/warframe-prime-part-tracker/.env
# They are not recoverable any other way, by design.

POSTGRES_PASSWORD="$(openssl rand -hex 32)"
JWT_SECRET_KEY="$(openssl rand -hex 32)"

umask 077
cat > "$APP_DIR/.env" <<EOF
# Generated on first boot by user_data.sh — do not commit, do not edit by hand.
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB

DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_DB
JWT_SECRET_KEY=$JWT_SECRET_KEY
EOF
chmod 600 "$APP_DIR/.env"


# --- 5. Port mapping -----------------------------------------------------
# docker-compose.yml maps the frontend to 8180 to dodge a port clash on the
# dev machine. On the VM it has to be 80, which is what the security list
# opens. Compose auto-loads docker-compose.override.yml, so this adds the
# mapping without editing the committed file.
#
# The dev ports (8180, 8100) stay mapped as well — Compose merges port lists
# rather than replacing them. Harmless: both are blocked by the security list
# and by iptables above.

cat > "$APP_DIR/docker-compose.override.yml" <<'EOF'
services:
  frontend:
    ports:
      - "80:80"
EOF


# --- 6. Start ------------------------------------------------------------
# --build because no images are published anywhere; the VM builds its own.
# The React build is the slow part — expect several minutes on 1 OCPU.

docker compose up -d --build


# --- 7. Seed the catalog -------------------------------------------------
# One-shot: creates the prime items and part requirements. `run --rm` starts a
# throwaway container rather than touching the running backend. Postgres is
# gated by a healthcheck in compose, so it is ready by the time this runs.
#
# Not fatal if it fails — the app still starts, and seeding can be re-run by
# hand. So this one line is allowed to fail without killing the script.

docker compose run --rm backend python -m app.seed || \
    echo "WARNING: seeding failed — re-run by hand with:" \
         "cd $APP_DIR && docker compose run --rm backend python -m app.seed"

echo "=== user_data finished: $(date -u) ==="
