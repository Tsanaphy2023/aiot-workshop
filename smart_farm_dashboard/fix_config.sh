#!/bin/sh
CFG="/mnt/data/supervisor/homeassistant/configuration.yaml"

# Backup first
cp "$CFG" "$CFG.bak"

# Use python inside homeassistant container to reformat configuration.yaml cleanly!
docker exec homeassistant python3 -c '
path = "/config/configuration.yaml"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = 0
for i, line in enumerate(lines):
    if "ai_autonomous_irrigation:" in line:
        skip = 3 # skip ai_autonomous_irrigation and its 2 sub-properties
        continue
    if skip > 0:
        skip -= 1
        continue
    if line.strip() == "input_number:":
        # Insert ai_autonomous_irrigation under input_boolean before input_number
        new_lines.append("  ai_autonomous_irrigation:\n")
        new_lines.append("    name: \"AI Autonomous Irrigation\"\n")
        new_lines.append("    icon: mdi:robot\n\n")
    new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("CONFIG_UPDATED_SUCCESSFULLY")
'
