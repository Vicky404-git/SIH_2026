#!/usr/bin/env bash
# Air-Gap Proof Script for SIH 2026 Sovereign Demo

NS="sovereign-demo"

echo "[+] Creating isolated network namespace: $NS"
sudo ip netns add $NS

echo "[+] Bringing up loopback interface inside $NS..."
sudo ip netns exec $NS ip link set dev lo up

echo "[+] Network namespace initialized with zero external routes."
echo "[+] Launching application inside isolated environment..."

# Run python app inside the restricted namespace as current user
sudo -E ip netns exec $NS su $USER -c "python3 main.py"

echo "[+] Cleaning up network namespace..."
sudo ip netns del $NS
