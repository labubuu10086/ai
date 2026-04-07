# Render 部署说明

这个项目已经补好了适合 Render 的基础配置：

- `requirements.txt` 已包含 `gunicorn`
- `render.yaml` 已提供默认 Web Service + Postgres 配置
- `.gitignore` 已忽略 `.env`、日志和虚拟环境
- 已支持云端存档接口
- 已提供 GitHub Actions 保活工作流模板

## 1. 推到 GitHub

把项目初始化并推到你自己的仓库：

```powershell
git init
git add .
git commit -m "Prepare project for Render deployment"
git branch -M main
git remote add origin <你的 GitHub 仓库地址>
git push -u origin main
```

## 2. 在 Render 创建服务

1. 登录 Render
2. 选择 `New +`
3. 选择 `Blueprint`
4. 连接你的 GitHub 仓库

如果 Render 识别到 `render.yaml`，直接按默认配置创建即可。

## 3. 需要配置的环境变量

最少需要这几个：

- `GEN1_API_KEY`
- `GEN1_MODEL`

可选：

- `GEN1_BASE_URL`
- `GEN2_API_KEY`
- `GEN2_MODEL`
- `GEN2_BASE_URL`
- `RENDER_PING_URL`（这个不是 Render 环境变量，而是 GitHub Actions Secret，见下文）

如果你用 OpenAI 官方接口，通常只需要：

- `GEN1_BASE_URL=https://api.openai.com/v1`
- `GEN1_API_KEY=你的 key`
- `GEN1_MODEL=你的模型名`

## 4. 启动命令

Render 会使用：

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

本地开发仍然可以继续用：

```bash
python app.py
```

## 5. 云端存档

项目现在已经带了“云端存档”面板。

- 如果只是关掉页面再打开，同一台设备、同一个浏览器下，本地草稿通常不会丢，因为浏览器本地存储还在
- 如果想在手机和电脑之间同步，或者担心浏览器缓存丢失，就用页面里的“云端存档”
- Render 部署时，`render.yaml` 会给 Web Service 绑定一个免费 Postgres，存档默认会进数据库

## 6. Render 免费保活

仓库里已经带了一个 GitHub Actions 工作流：

- `.github/workflows/render-keepalive.yml`

你需要去 GitHub 仓库设置里加一个 Secret：

- `RENDER_PING_URL`

值填成你的健康检查地址，例如：

```text
https://你的服务名.onrender.com/healthz
```

工作流会每 10 分钟 ping 一次。

注意：

- 这不是 Render 官方“永不休眠”方案，而是外部保活
- 保活会持续消耗免费实例时长
- 免费额度用尽后，服务仍然会停

## 7. 手机上使用

部署成功后，Render 会给你一个：

```text
https://你的服务名.onrender.com
```

手机浏览器直接打开就能用。

注意：

- 免费实例闲置后会休眠，第一次打开可能会慢一些
- 现在支持云端存档，手机和电脑可以通过同一个存档编号同步内容
- 本地 API 配置仍然走浏览器本地存储，手机和电脑不会自动同步
- 如果你把 API Key 配到 Render 环境变量里，手机端就不需要再单独填一遍
