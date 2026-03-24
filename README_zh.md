# SCTERO

![Docker Build](https://github.com/SankHyan24/sctero/actions/workflows/build.yml/badge.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

[English](README.md)

极简、自托管的轻量级个人学术论文归档库。

## 🚀 快速开始

```bash
git clone https://github.com/SankHyan24/sctero.git
cd sctero
docker compose up -d --build
```
浏览器访问 `http://localhost:5577` (默认密码: `admin`)。

## ✨ 特性
- **自动化拉取**：输入 arXiv 链接，系统自动解析标题、作者并下载 PDF 本地归档。
- **文献管理**：支持修改分类、标签及添加阅读批注。
- **即时搜索**：毫秒级检索所有文献元数据及笔记。
- **物理删除**：数据库记录与 PDF 实体文件同步销毁。

## ⚙️ 配置
支持通过 `docker-compose.yml` 环境变量或 `config.json` 进行服务配置。
