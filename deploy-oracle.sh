#!/usr/bin/env bash
# ==============================================================================
# Hermes Agent & Content Pipeline - 1-Click Oracle Cloud VPS Deployment Script
# Tested for: Ubuntu 22.04 / 24.04 LTS (x86_64 and ARM64 / Ampere A1)
# ==============================================================================

set -e

echo "============================================================="
echo "   Setting up Hermes Agent & Content Pipeline on Oracle VPS  "
echo "============================================================="

# 1. Update system packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git python3 python3-pip python3-venv sqlite3 ripgrep ffmpeg

# 2. Install Hermes Agent
echo "Installing official Nous Research Hermes Agent..."
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 3. Source environment
export PATH="$HOME/.hermes/bin:$PATH"
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc" || true
fi

# 4. Clone / Deploy Hermes Content Pipeline
PIPELINE_DIR="$HOME/hermes-pipeline"
mkdir -p "$PIPELINE_DIR"
cd "$PIPELINE_DIR"

cat << 'EOF' > run_cron.sh
#!/usr/bin/env bash
cd "$HOME/hermes-pipeline"
python3 run_pipeline.py --auto-approve >> pipeline.log 2>&1
EOF
chmod +x run_cron.sh

# 5. Add Crontab entry for automated runs (runs every 6 hours)
(crontab -l 2>/dev/null; echo "0 */6 * * * $HOME/hermes-pipeline/run_cron.sh") | crontab -

echo "============================================================="
echo " ✅ Hermes Agent & Pipeline setup complete!"
echo " • Run Hermes interactively: hermes"
echo " • Run pipeline now:         python3 run_pipeline.py --auto-approve"
echo " • Cron scheduled:          Every 6 hours"
echo "============================================================="
