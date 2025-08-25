#!/usr/bin/env python3
"""
config/__init__.py - Package configuration
"""

# Imports des configurations
from .hydraulic_objects import (
    HYDRAULIC_OBJECT_TYPES,
    get_object_types,
    get_object_config,
    get_default_properties,
    validate_property,
    get_config_summary
)

__all__ = [
    'HYDRAULIC_OBJECT_TYPES',
    'get_object_types',
    'get_object_config', 
    'get_default_properties',
    'validate_property',
    'get_config_summary'
]