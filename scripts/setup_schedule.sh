#!/bin/bash
# Setup launchd schedules for Daily Market Digest

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_DIR="$HOME/Library/LaunchAgents"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$PLIST_DIR"

echo "Setting up Daily Market Digest schedules..."
echo "Project directory: $PROJECT_DIR"

# Create pre-market plist (21:00 Taiwan time)
cat > "$PLIST_DIR/com.dailymarketdigest.premarket.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailymarketdigest.premarket</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/.venv/bin/python</string>
        <string>$PROJECT_DIR/src/main.py</string>
        <string>pre-market</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/premarket.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/premarket.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# Create post-market plist (05:00 Taiwan time)
cat > "$PLIST_DIR/com.dailymarketdigest.postmarket.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailymarketdigest.postmarket</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/.venv/bin/python</string>
        <string>$PROJECT_DIR/src/main.py</string>
        <string>post-market</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>5</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/postmarket.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/postmarket.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

echo ""
echo "Created plist files:"
echo "  - $PLIST_DIR/com.dailymarketdigest.premarket.plist"
echo "  - $PLIST_DIR/com.dailymarketdigest.postmarket.plist"
echo ""
echo "To enable the schedules, run:"
echo "  launchctl load $PLIST_DIR/com.dailymarketdigest.premarket.plist"
echo "  launchctl load $PLIST_DIR/com.dailymarketdigest.postmarket.plist"
echo ""
echo "To disable the schedules, run:"
echo "  launchctl unload $PLIST_DIR/com.dailymarketdigest.premarket.plist"
echo "  launchctl unload $PLIST_DIR/com.dailymarketdigest.postmarket.plist"
echo ""
echo "To test immediately, run:"
echo "  cd $PROJECT_DIR && .venv/bin/python src/main.py test"
