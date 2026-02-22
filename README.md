# 你画我猜发牌器 & AI早报

基于 FastAPI + DeepSeek V3 的全栈应用

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 到 .env 并填入 API_KEY

# 启动服务
python main.py
```

访问: http://127.0.0.1:8000

## Render部署

1. Fork本项目到GitHub
2. 在Render新建Web Service
3. 连接GitHub仓库
4. 自动检测Python并开始构建
5. 在环境变量中添加:
   - `SILICONFLOW_API_KEY`: 你的SiliconeFlow API密钥
   - `PORT`: 8000

## 已修复问题

- [x] 前端使用相对路径,支持远程部署
- [x] 后端支持0.0.0.0监听端口
- [x] 环境变量配置端口支持Render
- [x] 添加Procfile自动部署配置
- [x] 修复AI响应空值处理
- [x] CORS配置增强

## 安全检查结果

✅ API密钥隔离到后端
✅ 无用户数据存储
✅ 无文件上传/下载风险
⚠️ CORS全开放(开发配置,建议生产环境限制域名)
