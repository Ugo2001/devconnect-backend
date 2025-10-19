# ============================================================================
# API Documentation Generator - generate_api_docs.py
# ============================================================================

"""
Generate API documentation
Usage: python generate_api_docs.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DevConnect.settings')
django.setup()

from django.urls import get_resolver
from rest_framework.schemas.openapi import SchemaGenerator


def generate_docs():
    generator = SchemaGenerator(title='DevConnect API')
    schema = generator.get_schema()
    
    # Save to file
    import json
    with open('api_schema.json', 'w') as f:
        json.dump(schema, f, indent=2)
    
    print("✓ API documentation generated: api_schema.json")
    print("\nEndpoints:")
    
    for path, path_item in schema.get('paths', {}).items():
        for method in path_item.keys():
            print(f"  {method.upper():<6} {path}")


if __name__ == '__main__':
    generate_docs()
