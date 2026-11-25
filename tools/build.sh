#!/bin/sh
# Rebuild generated parts of the site, in order: area pages, artwork, translations, sitemap.
set -e
cd "$(dirname "$0")/.."
python3 tools/support.py
python3 tools/pages.py
python3 tools/art.py > /dev/null
python3 tools/i18n.py
python3 tools/pages.py > /dev/null   # refresh the sitemap with the language pages
python3 tools/art.py > /dev/null
python3 tools/i18n.py
