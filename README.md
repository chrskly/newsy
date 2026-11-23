# Newsy

This script fetches new articles from RSS feeds and generates an A4 PDF file
suitable for viewing on a Sony DPT-RP1 e-reader.

## Usage

```
python -m venv env
source env/bin/activate
pip3 install -f requirements.txt
./newsy.py
cp 2025-11-16-articles.pdf ~/path/to/sync/folder/
```

To write the PDF directly to another directory, use `-o`/`--output-dir`
(created if it doesn't exist):

```
./newsy.py --output-dir ~/path/to/sync/folder/
```