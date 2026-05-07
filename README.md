# AutoJourney

多城市火车票智能规划工具。输入出发站与多个目的地，自动查询 12306 真实车次数据，通过智能算法选出性价比最优的车票方案。

## 功能

- **12306 实时查询** — 接入 12306 官方 API，获取真实车次、票价、余票信息
- **智能选票算法** — 综合价格、时间舒适度、跨日比价三维评分，自动推荐最优车次
  - 夜间长途车优先（节省住宿费）
  - 早间到达优先（最大化游玩时间）
  - 自动比较目标日期前后一天的价格
- **多城市串联规划** — 支持多个目的地，自动计算每段城际交通的出发日期
- **站点搜索** — 基于 12306 数据库的 5000+ 站点模糊搜索与自动补全
- **选票理由** — 每张推荐车票附带中文说明，解释为什么选择这趟车
- **实时进度** — SSE 流式推送查询进度

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python + FastAPI |
| 数据源 | 12306 官方 API + mcp_12306 站点库 |
| 站点解析 | mcp_12306（5000+ 站点模糊匹配） |
| 票价解码 | 12306 yp_info 字段解析（10字符分组：座位码 + 价格 + 编码） |

## 项目结构

```
AutoJourney/
├── backend/
│   ├── main.py                    # FastAPI 应用入口
│   ├── models/
│   │   └── schemas.py             # Pydantic 数据模型
│   ├── routers/
│   │   └── plan.py                # API 路由（/api/tickets, /api/stations）
│   ├── services/
│   │   └── ticket_service.py      # 12306 查询核心（站点解析、票价解码、智能选票）
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                # 全局样式 + Apple 风格 Element Plus 覆盖
│   │   ├── api/index.js           # API 调用模块（SSE 流式 + axios）
│   │   ├── components/
│   │   │   ├── InputForm.vue      # 输入表单（站点搜索、目的地管理、停留天数）
│   │   │   └── TransportInfo.vue  # 车票方案展示
│   │   └── views/
│   │       └── Home.vue           # 主页面（进度条、汇总、车票列表）
│   ├── vite.config.js             # Vite 配置（含 API 代理）
│   └── package.json
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:3000`。

## API 接口

### `GET /api/stations?q=北京&limit=15`

站点搜索，返回匹配的站点列表（名称、编码、所属城市）。

### `POST /api/tickets`

查询多段城际车票，SSE 流式返回。

**请求体：**
```json
{
  "departure": "北京南",
  "departure_date": "2026-05-15",
  "destinations": ["西安", "成都", "重庆"],
  "stay_days": [2, 3, 2]
}
```

**SSE 事件：**
- `progress` — 查询进度（`{ stage, percent, message }`）
- `result` — 最终结果（`{ segments, total_cost, total_days }`）
- `error` — 错误信息

### `GET /api/health`

健康检查，返回 `{"status": "ok"}`。

## 智能选票算法

每趟候选列车经过三维评分：

1. **价格分**（权重最高）— 归一化到 0-100，优先选二等座价格
2. **时间舒适度分** — 夜间长途 +30，早到 +20，晚到 -15，早发 +15
3. **日期偏离惩罚** — 非目标日期 +5 分惩罚

最终得分 = 价格分 + 时间分 + 日期惩罚，取最低分者为推荐车次。

## License

MIT
