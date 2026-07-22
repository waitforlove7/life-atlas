# Life Atlas

[English Documentation](README.en.md)

Life Atlas 是一个个人旅行与生活地图，用来记录去过、居住、工作、学习或计划前往的地点，并在地图和统计面板中查看自己的经历。

## 功能

- 国家、省/州及地点三级地图浏览
- 地点状态：`visited`、`wishlist`、`lived`、`worked`、`studied`
- 地点详情、描述和封面图片
- 访问记录及按月份统计的 Timeline
- 国家、省/州、地点数量统计
- PostgreSQL + PostGIS 地理数据存储

## 技术栈

- 前端：Next.js、React、TypeScript、MapLibre GL
- 后端：FastAPI、SQLAlchemy、Alembic
- 数据库：PostgreSQL + PostGIS
- 部署：Docker Compose

## 快速启动：Docker

要求：已安装 Docker Desktop，并确保 Docker 服务正在运行。

```powershell
# 在项目根目录执行
docker compose up -d --build
```

启动后访问：

- 前端：http://localhost:3000
- API：http://localhost:8000
- API 文档：http://localhost:8000/docs

检查服务状态：

```powershell
docker compose ps
docker compose logs -f api
```

停止服务：

```powershell
docker compose down
```

数据库数据保存在 Docker volume `pgdata` 中，地点封面保存在 `covers` volume 中。

## 本地开发

### 1. 启动数据库

如果本机没有 PostgreSQL/PostGIS，先启动 Docker 中的数据库：

```powershell
docker compose up -d db
```

### 2. 启动后端

```powershell
cd apps/api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn main:app --reload --port 8000
```

验证后端是否正常：

```text
http://localhost:8000/
```

正常响应：

```json
{"message":"Life Atlas API running"}
```

### 3. 启动前端

新开一个终端：

```powershell
cd apps/web
npm install
npm run dev
```

前端地址：http://localhost:3000

如果 PowerShell 禁止执行 `npm.ps1`，使用对应的命令行入口：

```powershell
npm.cmd run dev
```

## 常用命令

在项目根目录：

```powershell
npm run dev:web
npm run dev:api
npm run build
```

前端检查和构建：

```powershell
npm.cmd run lint --prefix apps/web
npm.cmd run build --prefix apps/web
```

后端测试：

```powershell
cd apps/api
pytest
```

## API 概览

主要接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | API 健康检查 |
| GET | `/places` | 获取地点列表 |
| GET | `/stats/summary` | 获取汇总统计 |
| GET | `/stats/countries` | 获取国家统计 |
| GET | `/stats/provinces` | 获取省/州统计 |
| GET | `/stats/status-breakdown` | 获取地点状态分布 |
| GET | `/stats/timeline` | 按访问日期返回月度访问次数和累计次数 |

Timeline 使用 `visits.visit_date` 统计访问记录，而不是地点的创建时间。同一地点多次访问会按多条访问记录分别计数。

## 环境变量

本地开发时可复制 `.env.example` 并按需修改：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://atlas:atlas@localhost:5432/lifeatlas` | 数据库连接地址 |
| `BACKEND_PORT` | `8000` | 后端端口配置 |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | 前端访问 API 的地址 |

Docker Compose 会自动为容器设置数据库地址和 API 地址。

## 地图边界数据

地图边界文件位于 `apps/web/public/data`。如果需要重新生成边界数据：

```powershell
python scripts/fetch_boundaries.py
```

边界数据说明见 [docs/map-boundaries.md](docs/map-boundaries.md)。

## 常见问题

### `API unavailable: http://localhost:8000/...`

说明前端无法连接后端。确认 API 已启动，并检查 8000 端口：

```powershell
Invoke-WebRequest http://localhost:8000/
```

如果使用 Docker：

```powershell
docker compose up -d api
docker compose logs api
```

### `/stats/timeline` 返回 500

先确认数据库迁移已执行：

```powershell
cd apps/api
alembic upgrade head
```

然后重启 API。Timeline 依赖 `visits` 表及 `visit_date` 字段。

### 端口被占用

查看端口占用：

```powershell
netstat -ano | Select-String ':8000'
netstat -ano | Select-String ':3000'
```

可以停止占用端口的旧进程，或修改前后端启动端口及 `NEXT_PUBLIC_API_URL`。

## 项目结构

```text
Life-Atlas/
├─ apps/
│  ├─ api/                 # FastAPI 后端、模型、路由和迁移
│  └─ web/                 # Next.js 前端
├─ database/               # 数据库相关资源
├─ docs/                   # 项目文档
├─ docker/                 # API 和 Web Dockerfile
├─ scripts/                # 辅助脚本
├─ storage/                # 本地存储目录
├─ docker-compose.yml
└─ package.json
```
