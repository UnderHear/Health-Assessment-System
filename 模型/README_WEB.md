# 运动处方推荐系统 - Web版

本项目已改造为前后端分离的Web应用。

## 目录结构

- `backend/`: 后端代码 (FastAPI)
- `frontend/`: 前端代码 (Vue 3 + Element Plus)
- `src/`: 核心业务逻辑 (原有代码)

## 运行指南

### 1. 后端 (Backend)

确保你已经安装了 Python 环境。

1.  进入项目根目录。
2.  激活你的虚拟环境 (如果有)。
3.  安装后端依赖：
    ```bash
    pip install fastapi uvicorn pydantic
    ```
    (注意：请确保原有的项目依赖也已安装，如 `torch`, `transformers`, `faiss-cpu` 等)

4.  启动后端服务：
    ```bash
    python backend/main.py
    ```
    或者：
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
    后端服务将在 `http://localhost:8000` 启动。

### 2. 前端 (Frontend)

确保你已经安装了 Node.js (建议 v16+)。

1.  进入前端目录：
    ```bash
    cd frontend
    ```
2.  安装依赖：
    ```bash
    npm install
    ```
3.  启动开发服务器：
    ```bash
    npm run dev
    ```
    前端页面将在 `http://localhost:5173` (默认端口) 启动。

## 使用说明

1.  打开浏览器访问前端地址。
2.  在左侧表单中输入体质测试数据。
3.  点击"生成运动处方"按钮。
4.  右侧将显示详细的分析报告。

## 注意事项

- 请确保后端服务正常运行且能连接到大模型API (DeepSeek)。
- 前端通过 `/api` 代理请求到后端，请确保 `vite.config.js` 中的代理配置正确 (默认指向 `http://127.0.0.1:8000`)。
