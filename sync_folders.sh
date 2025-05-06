#!/bin/bash

# Configuration
SOURCE_DIR="/Users/mac/rest_api"
TARGET_DIR="/Users/mac/ai/backend"

# Ensure directories exist
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory not found ($SOURCE_DIR)"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory not found ($TARGET_DIR)"
    exit 1
fi

# Sync files (copy only modified/new files)
echo "Syncing files from $SOURCE_DIR to $TARGET_DIR..."
rsync -avh --progress --update "$SOURCE_DIR/" "$TARGET_DIR/"

# Verify changes
echo -e "\nSync complete. Summary of changes:"
diff -rq "$SOURCE_DIR" "$TARGET_DIR" | grep -v "Only in" || echo "No differences found."

# Optional: Set permissions (uncomment if needed)
# chmod -R 755 "$TARGET_DIR"
