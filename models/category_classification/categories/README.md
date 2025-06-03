# Category Definitions

This directory contains category definitions and lists used by the child protection case classification model.

## Structure
- `list.json`: Comprehensive list of all categories used in classification
- Other files containing detailed category definitions and parameters

## Usage
```python
import json

# Load categories
with open('categories/list.json', 'r') as f:
    categories = json.load(f)
    
# Use categories in classification process
for category in categories:
    print(f"Category: {category['name']}, Description: {category['description']}")
```

## Extending Categories
To add new categories:
1. Add the category definition to the appropriate file
2. Update the `list.json` file with the new category
3. Retrain the model to recognize the new category

