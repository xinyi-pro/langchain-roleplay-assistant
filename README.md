# 角色扮演AI助手

基于**LangChain**框架构建的角色扮演AI助手应用，支持多种角色模拟，包括编程导师、旅行向导、心理咨询师等。

## 功能特性

- 👨‍🏫 **编程导师** - 帮助学习编程知识
- ✈️ **旅行向导** - 提供旅行建议和行程规划
- 🧠 **心理咨询师** - 倾听烦恼，给予安慰
- 📖 **故事作家** - 创作有趣的故事
- 💼 **职业规划师** - 职业发展建议

## 工具支持

- 🧮 **计算器** - 数学表达式计算
- ⏰ **时间查询** - 获取当前时间
- 🌤️ **天气查询** - 查询城市天气信息

## 技术架构

### 核心技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | LangChain 0.2+ | LLM应用开发框架 |
| 服务 | LangServe | 链服务部署 |
| 后端 | FastAPI | API服务 |
| 前端 | Streamlit | Web界面 |
| 模型 | DeepSeek / OpenAI | 支持多API提供商 |

### LangChain核心要素实现

- ✅ **LLM调用**: 使用 `ChatDeepSeek` / `ChatOpenAI`
- ✅ **Prompt工程**: 为每个角色设计专属系统提示词
- ✅ **Chain链式调用**: 使用 `prompt | llm | parser` 模式
- ✅ **Tool工具使用**: 集成计算器、时间、天气等工具
- ✅ **Memory记忆**: Streamlit会话状态管理

## 快速开始

### 环境要求

- Python 3.8+
- DeepSeek API Key 或 OpenAI API Key

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填写你的API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# API Provider: deepseek 或 openai
API_PROVIDER=deepseek

# DeepSeek API配置
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat

# OpenAI API配置 (备用)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# API基础地址
API_BASE_URL=http://localhost:8000
```

### 启动服务

**1. 启动后端服务（使用LangServe）**

```bash
python backend/server.py
```

**2. 启动前端应用**

```bash
streamlit run frontend/app.py
```

### 访问应用

打开浏览器访问: http://localhost:8501

## 项目结构

```
.
├── backend/
│   ├── server.py            # LangServe服务主文件
│   ├── chains.py            # Chain链定义
│   └── tools.py             # Tool工具定义
├── frontend/
│   └── app.py               # Streamlit前端应用
├── .env                     # 环境变量配置
├── .env.example             # 环境变量示例
├── requirements.txt         # 项目依赖
└── README.md                # 项目说明
```

## API接口

### 角色列表
```
GET /roles
```

### 对话接口（LangServe）
```
POST /{role_id}/invoke
{
  "input": "你的消息",
  "config": {}
}
```

### 工具接口
```
GET /tools                  # 列出所有工具
POST /tool/calculator       # 计算器
POST /tool/time             # 当前时间
POST /tool/weather          # 天气查询
```

## 使用说明

1. 从左侧角色列表选择一个角色
2. 在对话输入框中输入你的问题
3. 等待AI助手的回复
4. 可以随时切换角色开始新的对话

## 技术亮点

1. **前后端分离**: 后端使用LangServe提供RESTful API
2. **多模型支持**: 一键切换DeepSeek/OpenAI
3. **工具集成**: 支持计算器、时间、天气等工具调用
4. **链式调用**: 采用LangChain 0.2新API实现Chain链

## License

MIT

## 参考项目

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangServe](https://github.com/langchain-ai/langserve)
- [Streamlit](https://github.com/streamlit/streamlit)