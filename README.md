# 视频平台前端应用 (基于Python Flask)

这是一个基于Flask的视频平台前端应用，与Go语言构建的视频点播(VOD)平台后端MVP配合使用。

## 功能特性

### 用户系统

- 用户注册、登录、登出
- 基于会话的身份验证

### 视频功能

- 视频列表展示
- 视频详情页与播放器
- 视频上传流程(直接上传到MinIO)
- 多清晰度切换播放

### 互动功能

- 发表评论和弹幕
- 评论列表展示
- 实时弹幕效果

## 技术栈

- 前端框架: Flask (Python)
- 模板引擎: Jinja2
- HTTP客户端: requests
- 前端样式: Bootstrap 5
- 视频播放器: Video.js (支持HLS)
- 弹幕系统: 原生JavaScript实现

## 项目结构

```
video-platform-frontend/
├── app.py # Flask主应用
├── requirements.txt # Python依赖
├── static/
│ ├── css/
│ │ └── styles.css # 自定义样式
│ └── js/
│ └── main.js # 主JavaScript逻辑
└── templates/ # 模板文件
├── base.html # 基础模板
├── index.html # 首页
├── video_detail.html # 视频详情页
├── upload.html # 上传页面
├── login.html # 登录页面
└── register.html # 注册页面
```

## 安装与运行

### 前提条件

- Python 3.8+
- 已运行的Go后端服务
- Node.js (可选，用于前端资源构建)

### 安装步骤

1. 克隆仓库：

    ```bash
    git clone https://github.com/lleey/video-platform-frontend.git
    cd video-platform-frontend
    ```

2. 创建并激活虚拟环境：

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. 安装依赖：

    ```bash
    pip install -r requirements.txt
    ```

4. 配置环境变量：
    创建 `.env` 文件并配置：

    ```ini
    FLASK_APP=app.py
    FLASK_ENV=development
    API_BASE_URL=http://localhost:8000/api/v1  # 指向您的Go后端API
    SECRET_KEY=your-secret-key-here
    ```

5. 运行应用：

    ```bash
    flask run
    ```

    访问 `http://localhost:5000`

## 配置说明

### 主要配置项

- `API_BASE_URL`: 后端API基础URL
- `SECRET_KEY`: Flask会话加密密钥

### 与后端集成

确保后端服务已配置以下API端点：

- 用户认证: `/users/register`, `/users/login`
- 视频管理: `/videos`, `/videos/upload/initiate`, `/videos/upload/complete`
- 评论系统: `/videos/<id>/comments`
