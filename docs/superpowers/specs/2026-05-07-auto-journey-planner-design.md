# AutoJourney 自动旅行路线规划工具 - 设计文档

## 概述

一个 Web 应用，用户输入出发地、行程天数范围、目标地点，系统自动规划交通方式（高铁/火车）、游玩景点、每日路线，并计算详细预算。

## 技术栈

- **前端**：Vue 3 + Element Plus + 高德地图 JS API
- **后端**：Python FastAPI
- **AI**：DeepSeek API（结构化 JSON 输出）
- **构建工具**：Vite

## 核心功能

### 输入

| 字段 | 类型 | 说明 |
|------|------|------|
| departure | string | 出发城市 |
| min_days / max_days | int | 行程天数范围（滑块选择） |
| destinations | string[] | 目标城市列表 |
| mode | enum | "single-city" 或 "multi-city" |
| preferences | string? | 可选，个人偏好描述 |

### 输出

| 字段 | 说明 |
|------|------|
| actual_days | AI 推荐的实际天数 |
| overview | 行程概述 |
| daily_plans[] | 每日行程（主题、时间线、活动、费用） |
| transport[] | 城市间交通（高铁/火车，时长，费用） |
| budget_breakdown | 预算明细（交通/住宿/门票/餐饮/总计） |

### 返回数据结构

```json
{
  "actual_days": 6,
  "overview": "6天西安-成都深度文化美食之旅",
  "daily_plans": [
    {
      "day": 1,
      "city": "西安",
      "theme": "古都历史探索",
      "schedule": [
        { "time": "09:00", "activity": "参观兵马俑", "duration": "3小时", "cost": 120 }
      ],
      "accommodation": { "name": "钟楼附近酒店", "cost": 300 },
      "meals_cost": 150,
      "day_total": 740
    }
  ],
  "transport": [
    { "from": "北京", "to": "西安", "type": "高铁", "duration": "4.5小时", "cost": 515 }
  ],
  "budget_breakdown": {
    "transport": 778,
    "accommodation": 1500,
    "tickets": 680,
    "meals": 1200,
    "total": 4158
  }
}
```

## API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/plan` | 提交规划请求，返回完整行程 |
| GET | `/api/health` | 健康检查 |

## 架构

```
┌─────────────┐     HTTP/REST     ┌──────────────┐     DeepSeek API
│   Vue 3 前端  │ ◄──────────────► │  FastAPI 后端  │ ◄──────────────►  AI 模型
│  + 高德地图   │                   │              │
│  + Element UI │                   │   预算计算    │
└─────────────┘                   │   数据格式化   │
                                  └──────────────┘
```

## 前端页面布局

### 顶部 - 输入表单
- 出发城市：输入框 + 热门城市快捷标签
- 行程天数：滑块选择区间
- 目的地：标签式输入，支持多个城市
- 旅行模式：单选（单城市/多城市）
- 个人偏好：可选文本框
- "生成行程"按钮

### 中部 - 行程展示（左右分栏）
- 左侧：每日行程卡片列表，按天展示
- 右侧：高德地图，标注景点位置，城市间路线连线，点击卡片自动定位

### 底部 - 预算总览
- 饼图展示费用构成
- 总预算醒目数字

## 后端处理流程

1. 接收前端请求，校验输入
2. 根据 mode 选择 prompt 模板（单城市/多城市）
3. 组装 prompt，调用 DeepSeek API（response_format: json_object）
4. 解析返回 JSON，校验结构完整性
5. 二次计算预算总额（不依赖 AI 计算结果）
6. 返回完整行程数据

## Prompt 策略

- System prompt：定义旅行规划师角色，要求严格按 JSON 格式返回
- User prompt：包含出发地、天数范围、目的地、模式、偏好
- 约束：交通只考虑高铁/火车，预算分项明细，天数在范围内选最优值
- 输出：必须返回合法 JSON，不含额外文字

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| AI 返回非法 JSON | 重试一次，仍失败返回错误提示 |
| API 超时 | 30 秒超时，返回"服务繁忙" |
| 输入校验失败 | 前端即时校验 + 后端二次校验 |

## 项目目录结构

```
AutoJourney/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   └── plan.py
│   ├── services/
│   │   ├── ai_service.py
│   │   └── budget_service.py
│   ├── models/
│   │   └── schemas.py
│   ├── prompts/
│   │   ├── single_city.py
│   │   └── multi_city.py
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── views/
│   │   │   └── Home.vue
│   │   ├── components/
│   │   │   ├── InputForm.vue
│   │   │   ├── DailyCard.vue
│   │   │   ├── RouteMap.vue
│   │   │   └── BudgetChart.vue
│   │   ├── api/
│   │   │   └── index.js
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── docs/
```

## 交互细节

- 目的地输入支持热门城市快捷标签（北京、上海、西安、成都、杭州等）
- 滑块天数范围：5-7天 / 7-10天 / 10-14天 三档
- 地图上点击景点标记弹出详情气泡
- 行程生成中显示 loading 动画
- 预算饼图支持点击查看明细
