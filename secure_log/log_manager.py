# secure_log/log_manager.py
# Manages the append-only secure log.

import json
from secure_log.merkle import Leaf, build_merkle_tree

LOG_FILE = "secure_audit.log"
ROOT_FILE = "merkle_root.txt"

# Point-wise comment: Add a new entry to the secure log
def add_log(log_data: dict):
    # --- 1. Read existing logs ---
    try:
        with open(LOG_FILE, 'r') as f:
            logs = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        logs = []

    # --- 2. Add new log and create leaves ---
    new_log_line = json.dumps(log_data)
    all_logs = logs + [new_log_line]
    leaves = [Leaf(log) for log in all_logs]

    # --- 3. Build Merkle Tree and get the new root ---
    merkle_root = build_merkle_tree(leaves).value

    # --- 4. Save the new Merkle root ---
    with open(ROOT_FILE, 'w') as f:
        f.write(merkle_root)

    # --- 5. Append the new log entry to the file ---
    with open(LOG_FILE, 'a') as f:
        f.write(new_log_line + '\n')
        
    print(f"New log entry added. New Merkle Root: {merkle_root}")

# Point-wise comment: Verify the integrity of the log
def verify_log_integrity() -> bool:
    try:
        with open(LOG_FILE, 'r') as f:
            logs = [line.strip() for line in f.readlines()]
        with open(ROOT_FILE, 'r') as f:
            stored_root = f.read().strip()
    except FileNotFoundError:
        return True # No logs, so it's valid

    if not logs:
        return stored_root == ''

    leaves = [Leaf(log) for log in logs]
    calculated_root = build_merkle_tree(leaves).value

    return calculated_root == stored_root
