# Code Style Guide

This guide outlines our coding standards and style guidelines.

## Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use double quotes for strings
- Use trailing commas in multi-line structures

## Code Formatting

We use Black for automatic code formatting:

```bash
# Format a single file
black file.py

# Format the entire project
black .
```

## Import Order

Use isort for import ordering:

```python
# Standard library imports
import os
import sys

# Third-party imports
import numpy as np
import pandas as pd

# Local imports
from amega_ai import utils
from amega_ai.models import Model
```

## Documentation

- Use Google-style docstrings
- Document all public functions and classes
- Include type hints

Example:
```python
def process_data(data: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Process the input data using the specified threshold.

    Args:
        data: Input DataFrame to process
        threshold: Filtering threshold value

    Returns:
        Processed DataFrame
    """
    return data[data['score'] > threshold]
``` 