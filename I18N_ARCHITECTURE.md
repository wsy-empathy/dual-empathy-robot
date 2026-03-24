# 多语言系统架构说明

## 概述

本系统实现了**完整的日中双语支持**，从UI界面到AI对话响应全部支持两种语言。多语言配置**完全独立于主程序**，便于维护和扩展。

## 核心特性

### 1. 独立的i18n模块
- **位置**: `core/i18n.py`
- **功能**: 统一管理所有多语言文本和提示词
- **优势**: 与主程序解耦，易于维护和扩展新语言

### 2. 全流程多语言支持

#### 用户界面（前端）
- ✅ 标题、按钮、提示文本
- ✅ 话题和子话题显示（双语对照）
- ✅ 错误消息和系统提示

#### 系统消息（后端）
- ✅ 会话创建欢迎消息
- ✅ 话题选择引导消息
- ✅ 子话题选择提示
- ✅ 对话完成消息

#### AI对话响应
- ✅ AER情感共情对话（根据语言生成）
- ✅ CER认知共情对话（根据语言生成）
- ✅ RAG检索内容（对应语言的语料库）
- ✅ 阶段说明和引导（双语）

## 实现架构

### 1. i18n模块结构

```python
core/i18n.py
├── Language = Literal['ja', 'zh']              # 语言类型定义
├── SYSTEM_MESSAGES                             # 系统消息翻译字典
│   ├── session_start                          # 会话开始
│   ├── topic_selected                         # 话题选择
│   ├── subtopic_selected                      # 子话题选择
│   └── stage_complete                         # 对话完成
│
├── AER_SYSTEM_GUIDE                           # AER提示词（日/中）
├── CER_SYSTEM_GUIDE                           # CER提示词（日/中）
├── RAG_PROMPT_TEMPLATE                        # RAG检索提示词模板
│
└── 工具函数
    ├── get_message(lang, key, **kwargs)      # 获取系统消息
    ├── get_aer_system_prompt(lang)           # 获取AER提示词
    ├── get_cer_system_prompt(lang)           # 获取CER提示词
    ├── format_agent_prompt(...)              # 完整提示词格式化
    └── detect_language(text)                 # 自动语言检测
```

### 2. Agent多语言集成

```python
# AER Agent
class AERAgent:
    def format_prompt(
        language: Language,  # 新增语言参数
        stage: str,
        user_input: str,
        ...
    ):
        # 从i18n获取对应语言的系统提示词
        system_prompt = get_aer_system_prompt(language)
        
        # 阶段说明根据语言选择
        stage_instructions[language][stage]
        
        # 构建多语言prompt并发送给Gemini
```

### 3. 会话语言管理

```python
class SessionState:
    def __init__(self, session_id: str, language: str = 'ja'):
        self.language = language  # 存储用户选择的语言
        # 整个对话过程保持语言一致性
```

### 4. API多语言流程

```
前端选择语言 (ja/zh)
       ↓
POST /api/session/create {user_id: 'zh'}
       ↓
创建SessionState(language='zh')
       ↓
返回中文欢迎消息: "最近有什么让你担心的事情吗？"
       ↓
POST /api/chat {session_id, message}
       ↓
获取 session.language = 'zh'
       ↓
aer_agent.format_prompt(language='zh', ...)
       ↓
Gemini生成中文响应
       ↓
返回中文对话: "你感到压力很大啊..."
```

## 语言切换流程

### 1. 前端语言切换
```typescript
// 用户点击"中文"按钮
setLanguage('zh')

// 创建新会话时传递语言
axios.post('/api/session/create', { user_id: 'zh' })

// 所有UI文本使用翻译函数
t('startButton')  // → "开始对话"
```

### 2. 后端语言处理
```python
# 接收语言参数
lang = request.user_id  # 'ja' or 'zh'

# 创建带语言的会话
session = session_manager.create_session(session_id, lang)

# 使用i18n模块生成消息
message = get_message(lang, 'session_start')
```

### 3. Agent语言响应
```python
# Agent接收语言参数
messages = aer_agent.format_prompt(
    language=session.language,  # 'zh'
    stage='aer_1',
    user_input='我最近很焦虑',
    ...
)

# Gemini根据中文提示词生成中文响应
response = llm.generate(messages)  # → "你最近感到很焦虑啊..."
```

## 添加新语言

要添加新语言（如韩语 'ko'），只需修改 `core/i18n.py`：

```python
# 1. 更新类型定义
Language = Literal['ja', 'zh', 'ko']

# 2. 添加系统消息翻译
SYSTEM_MESSAGES = {
    'ko': {
        'session_start': '최근 걱정되는 일이 있나요?',
        ...
    }
}

# 3. 添加Agent提示词
AER_SYSTEM_GUIDE = {
    'ko': """# AER 시스템 프롬프트
    ..."""
}
```

**无需修改主程序代码！**

## 测试验证

### 1. 测试会话创建
```bash
# 日文
curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "ja"}'

# 中文
curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"user_id": "zh"}'
```

### 2. 测试完整对话流程
1. 在浏览器打开 http://localhost:3000
2. 点击右上角"中文"按钮
3. 点击"开始对话" → 应显示中文欢迎消息
4. 选择话题 → 应显示中文引导消息
5. 开始对话 → AER/CER应返回中文响应

## 优势总结

✅ **模块化**: i18n配置完全独立，易于维护
✅ **扩展性**: 添加新语言只需修改i18n.py
✅ **一致性**: 整个对话流程语言保持一致
✅ **完整性**: 从UI到AI响应全部支持多语言
✅ **解耦性**: 主程序逻辑与语言配置分离

## 文件清单

### 核心文件
- `core/i18n.py` - 多语言配置模块（独立）
- `frontend/app/i18n.ts` - 前端多语言配置（独立）

### 修改的文件
- `core/agents/aer_agent.py` - 支持多语言
- `core/agents/cer_agent.py` - 支持多语言
- `core/session_manager.py` - 会话语言管理
- `api_server.py` - API多语言支持
- `frontend/app/page.tsx` - UI多语言实现

## 注意事项

1. **语言一致性**: 一旦创建会话，语言不可更改（需重新开始）
2. **RAG内容**: 目前RAG语料库为日文，需要添加对应的中文语料库以获得更好效果
3. **Gemini响应**: 由于使用同一个LLM模型，中文和日文响应质量取决于Gemini对两种语言的支持
4. **前端刷新**: 修改前端i18n.ts后需要刷新浏览器（Ctrl+F5）

## 下一步优化建议

1. **RAG多语言**: 创建中文版的RAG语料库（12个文件）
2. **语言自动检测**: 根据用户输入自动切换语言
3. **混合语言**: 支持在对话中切换语言
4. **更多语言**: 添加英语等其他语言支持
