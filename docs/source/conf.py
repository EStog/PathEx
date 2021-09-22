# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = 'PathEx'
copyright = f'2019-{datetime.today().year}, Ernesto Soto Gómez'
author = 'Ernesto Soto Gómez'

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

needs_sphinx = '3.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
    'sphinx.ext.todo',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosectionlabel',
    # 'sphinx.ext.duration',
    'sphinxcontrib.bibtex',
    'sphinxcontrib.apidoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

modindex_common_prefix = [
    'pathex.',
    'pathex.adts.',
    'pathex.adts.cached_generators.',
    'pathex.adts.containers.',
    'pathex.adts.concurrency.',
    'pathex.adts.concurrency.atomics.',
    'pathex.expressions.',
    'pathex.expressions.nary_operators.',
    'pathex.expressions.terms.',
    'pathex.expressions.terms.letters_unions.',
    'pathex.expressions.repetitions.',
    'pathex.generation.',
    'pathex.managing.'
]

# other general options
add_module_names = False
python_use_unqualified_type_names = True
rst_epilog = f"""
.. |pe| replace:: {project}
"""

# sphinx.ext.autodoc options
autoclass_content = 'both'
autodoc_typehints = 'both'
autodoc_typehints_description_target = 'documented'
# autodoc_preserve_defaults = True
autodoc_member_order = 'groupwise'
autodoc_type_aliases = {
}


# sphinx.ext.napoleon options
napoleon_include_special_with_doc = True


# sphinx.ext.imgmath options
imgmath_image_format = 'svg'
imgmath_use_preview = True
imgmath_font_size = 13


# sphinx.ext.intersphinx options
intersphinx_mapping = {'python': ('https://docs.python.org/3',
                                  (None, 'python-objects.inv'))}


# sphinxcontrib-bibtex options
bibtex_bibfiles = ['refs.bib']


# sphinxcontrib-apidoc options
apidoc_module_dir = '../../pathex'
apidoc_output_dir = './API'
apidoc_separate_modules = True
apidoc_toc_file = False
apidoc_module_first = True
apidoc_extra_args = ['-f', '-E']
