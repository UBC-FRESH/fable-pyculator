"""Sphinx configuration for FABLE Pyculator."""

project = "FABLE Pyculator"
author = "UBC FRESH Lab"
copyright = "2026, UBC FRESH Lab"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

html_theme = "sphinx_rtd_theme"
html_static_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

