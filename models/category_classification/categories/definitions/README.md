# Category and Intervention Definitions

This directory contains definition files that specify the categories and interventions used in the child protection case classification system.

## Files
- `categories.csv`: Detailed definitions of case categories used in classification
- `interventions.csv`: List of possible interventions mapped to case categories

## Usage
These definition files are used to:
1. Train classification models
2. Map classification outputs to appropriate interventions
3. Provide standardized terminology across the system

```python
import pandas as pd

# Load category definitions
categories = pd.read_csv('definitions/categories.csv')

# Load intervention mappings
interventions = pd.read_csv('definitions/interventions.csv')

# Example: Map a category to possible interventions
def get_interventions_for_category(category_id):
    return interventions[interventions['category_id'] == category_id]
```

## Maintenance
When updating these definition files:
1. Maintain backward compatibility where possible
2. Document changes in version control
3. Notify stakeholders of definition changes
4. Retrain models if category definitions change significantly

