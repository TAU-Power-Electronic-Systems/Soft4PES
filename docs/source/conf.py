# MIT License
#
# Copyright (c) [2024] [Aalto Electric Drives]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# This file is based on code from the following repository:
# [https://github.com/Aalto-Electric-Drives/motulator]

# pylint: disable=all

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../soft4pes"))

# -- Project information -----------------------------------------------------

project = "Soft4PES"
copyright = "2024 TAU Power Electronic Systems"
author = "TAU Power Electronic Systems"

# -- General configuration ---------------------------------------------------

# This value contains a list of modules to be mocked up.
# This is useful when some external dependencies are not met at build time and
# break the building process. You may only specify the root package of the
# dependencies themselves and omit the sub-modules:
autodoc_mock_imports = ["numpy", "matplotlib", "scipy"]

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "numpydoc",
    "sphinx_copybutton",
    "sphinx.ext.mathjax",  # "sphinx_gallery.gen_gallery"
    "autoapi.extension"
]

autoapi_type = "python"
autoapi_dirs = ["../../soft4pes"]
autodoc_typehints = "description"
autoapi_options = [
    "members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
    "special-members",
]

autoapi_python_class_content = "class"
autoapi_keep_files = False
autoapi_add_toctree_entry = False

# from sphinx_gallery.sorting import ExplicitOrder

# sphinx_gallery_conf = {
#     "examples_dirs":
#     "../../examples",  # path to your example scripts
#     "gallery_dirs":
#     "auto_examples",  # path to where to save gallery generated output
#     "nested_sections":
#     True,
#     "subsection_order":
#     ExplicitOrder([
#         "../../examples/rl_grid_lin_curr_ctr",
#         "../../examples/rl_grid_mpc_enum",
#     ]),
# }

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["../../.idea", "../../__pycache__", "../../venv"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url":
    "https://github.com/TAU-Power-Electronic-Systems/Soft4PES",
    "use_repository_button": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
