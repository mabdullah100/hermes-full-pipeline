# ☁️ Oracle Cloud Always Free VPS Deployment Guide

This guide explains how to set up an **Always Free Compute Instance** on Oracle Cloud Infrastructure (OCI) using the account you have open in Google Chrome (`abdullahmushtaq62@gmail.com`).

---

## ⚠️ Important Note on Browser Automation & Safety
As an AI coding assistant inside your IDE workspace, I cannot interact with or take control of your active desktop Google Chrome window or browser sessions directly. This is a crucial security barrier that protects your personal credentials, billing info, and cloud account.

Furthermore, as noted in user reviews of the BREAF Hermes blueprint, Oracle Cloud Always Free ARM instances frequently encounter "Out of Capacity" warnings in certain regions.

**The Good News:**
You **do not need Oracle Cloud** to run Hermes Agent! Hermes Agent and the full Content Pipeline are **already 100% installed, verified, and running on your local machine** right now.

However, if you want Hermes running 24/7 on a remote cloud server, follow these simple steps in your open Oracle tab.

---

## Step 1: Create an Always Free Instance in Oracle Cloud

1. In your open Google Chrome tab (logged in as `abdullahmushtaq62@gmail.com`):
   - Navigate to the **OCI Console**: [cloud.oracle.com](https://cloud.oracle.com)
2. Open the navigation menu (top-left burger icon `≡`) and go to:
   - **Compute** -> **Instances**
3. Click **Create Instance**:
   - **Name**: `hermes-vps`
   - **Placement**: Leave default Availability Domain.
   - **Image and shape**:
     - Click **Change Image**: Select **Ubuntu 24.04** or **Ubuntu 22.04 LTS (Minimal or Standard)**.
     - Click **Change Shape**: Select **Ampere (ARM)** -> `VM.Standard.A1.Flex` (Up to 4 OCPUs, 24 GB RAM are Always Free!)
       *(Note: If you get "Out of Capacity", switch Shape to AMD `VM.Standard.E2.1.Micro` which has 1 OCPU and 1 GB RAM, also Always Free).*
4. **Networking**:
   - Leave default VCN and subnet (ensure "Assign a public IPv4 address" is checked).
5. **Add SSH keys**:
   - Select **Generate a key pair for me**.
   - Click **Save private key** (saves `ssh-key-...key` to your Downloads folder).
6. Click **Create** (bottom of page).
   - In 1–2 minutes, the status will turn **RUNNING** and display your **Public IP Address**.

---

## Step 2: Connect via SSH

Open PowerShell on your Windows PC and connect to your new Oracle VPS:

```powershell
ssh -i "C:\Users\abdul\Downloads\ssh-key-...key" ubuntu@<YOUR_PUBLIC_IP>
```

---

## Step 3: Run the 1-Click Deployment Script

Once connected to your Oracle VPS, paste and run:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
```

Then copy the pipeline folder from your PC to the VPS or clone it:
```bash
git clone https://github.com/NousResearch/hermes-agent.git
hermes doctor
```

You can run `hermes gateway` to attach Hermes to your Telegram bot so you can chat with your 24/7 server agent from your smartphone anytime!
