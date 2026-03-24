# SCTERO

![Docker Build](https://github.com/SankHyan24/sctero/actions/workflows/build.yml/badge.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

[中文说明](README_zh.md)

A minimalist, self-hosted academic paper manager.

## Quick Start

```bash
git clone https://github.com/SankHyan24/sctero.git
cd sctero
docker compose up -d --build
```
Access at `http://localhost:5577` (Default pass: `admin`).

## Features
- **Auto-archive**: Drop an arXiv URL; SCTERO grabs the metadata and PDF.
- **Organization**: Assign categories, tags, and annotations.
- **Instant Search**: Query across all paper metadata and notes.
- **Physical Deletion**: Cleanly removes both database entries and local PDFs.

## Configuration
Configure environments in `docker-compose.yml` or local `config.json`.
