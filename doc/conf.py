import sys
import os
import sphinx_rtd_theme


sys.path.append(os.path.abspath('extensions'))


project = 'sphinxrust'
version = '0.1'
release = version

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = ['sphinxrust']

master_doc = 'index'
copyright = u'2016, Luke Frisken and contributors'
primary_domain = 'rst'