# 自主对话测试系统 - 使用指南

## 快速开始

### 1. 运行测试

```powershell
# 激活虚拟环境（如果尚未激活）
.\.venv\Scripts\Activate.ps1

# 测试日语对话
python test_autonomous_dialogue.py --lang ja

# 测试中文对话
python test_autonomous_dialogue.py --lang zh

# 测试两种语言
python test_autonomous_dialogue.py --lang both
```

### 2. 查看测试结果

测试完成后，结果会保存在：
- **详细结果**: `logs/test_results/test_*.json`
- **综合报告**: `logs/test_results/summary_report_*.md`
- **总结文档**: `TEST_SUMMARY.md`

### 3. 测试内容

每次测试会自动执行：
- ✅ 完整的9阶段对话流程
- ✅ 情绪检测 (ONNX WRIME-LUKE模型)
- ✅ RAG内容检索
- ✅ LLM响应生成 (Gemini 2.5 Pro)
- ✅ 对话质量分析（自然性、重复度、简洁性）

---

## 系统架构

```
用户输入
    ↓
[情绪检测] ONNX WRIME-LUKE
    ↓
[RAG检索] 基于topic/subtopic/stage
    ↓
[Prompt构建] AER或CER + 系统提示词 + RAG内容
    ↓
[LLM生成] Gemini 2.5 Pro
    ↓
[质量检查] 检测重复、长度、自然性
    ↓
机器人回复
```

---

## 对话阶段说明

### AER阶段（情感共情）
1. **aer_1** - 情绪模仿 + 命名/理解 + 感受导向探索
2. **aer_2** - 情绪模仿 + 尊重 + 感受导向探索
3. **aer_3** - 情绪模仿 + 支持 + 最后的感受导向问题
4. **aer_transition** - 简短情感总结，引出CER

### CER阶段（认知共情）
5. **cer_1** - PT (Perspective-Taking) - 复述用户状况
6. **cer_2** - Mz (Mentalizing) - 心智化建模
7. **cer_3** - Advice - 具体建议

### AER收尾
8. **aer_closing_1** - 轻量情绪承接 + 尊重
9. **aer_closing_2** - 简短鼓励 + 支持性收尾

---

## 核心优化要点

### AER（情感共情机器人）
✅ **要做的**:
- 简洁回复（1-2句）
- 捕捉情感核心
- 感受导向提问（"どんな気持ち？""心里怎么样？"）
- 温暖、接纳的语调

❌ **不要做的**:
- 不要大量重复用户话语
- 不要分析问题原因
- 不要提供解决方案
- 不要长篇大论

### CER（认知共情机器人）
✅ **要做的**:
- 简洁复述核心（≤2句）
- 心智化建模（可证伪的假设）
- 具体、单一的建议（包含做什么+怎么做+完成判据）

❌ **不要做的**:
- 不要重复用户全部话语
- 不要提供多个选项
- 不要重复之前说过的内容
- 不要做情绪安抚（那是AER的工作）

---

## 测试案例

### 当前测试的话题

| Topic | Subtopic | 说明 |
|-------|----------|------|
| academic | exam_anxiety | 考试焦虑 |
| financial | cost_burden | 学费负担 |

你可以在 `test_autonomous_dialogue.py` 中添加更多测试案例。

### 添加新测试案例

1. 在 `self.test_dialogues` 中添加新的 subtopic_key
2. 提供9轮用户输入（对应9个阶段）
3. 确保 subtopic_key 与 RAG 文件匹配

示例：
```python
'future_career': [
    "卒業後の進路が決まらなくて悩んでいます。",  # aer_1
    "はい、何をすればいいのか分からなくて...",   # aer_2
    # ... 继续9轮
]
```

---

## 质量评分标准

### 自然性得分 (0-100)
- **90-100**: 优秀 - 像真人对话
- **70-89**: 良好 - 整体自然
- **50-69**: 及格 - 基本可用
- **<50**: 需要改进

### 扣分项
- 每个质量问题 -5分
- 阶段不完整 每个-10分
- RAG使用率<50% -10分

---

## 故障排除

### 问题1: 情绪检测失败
```
错误: 'ONNXWRIMELukeRecognizer' object is not callable
```
**解决**: 确保使用 `self.emotion_recognizer.predict(text)` 而不是 `self.emotion_recognizer(text)`

### 问题2: LLM生成失败
```
错误: object str can't be used in 'await' expression
```
**解决**: `generate_response` 不是异步函数，不要使用 `await`

### 问题3: RAG未检索到内容
```
警告: Content file not found
```
**解决**: 检查文件名是否匹配 `{topic}_{subtopic}.txt` 格式

---

## 运行环境要求

### 必需的依赖
```
onnxruntime-gpu  # GPU加速的ONNX运行时
transformers     # Hugging Face模型
openai          # OpenAI兼容API
numpy
```

### GPU要求
- **推荐**: NVIDIA RTX 系列 (如 RTX 5070)
- **CUDA**: 支持 CUDA 运行时
- 如果没有GPU，会自动回退到CPU模式

---

## 进阶使用

### 修改系统提示词

编辑 `core/i18n.py`:
- `AER_SYSTEM_GUIDE` - AER的系统提示词
- `CER_SYSTEM_GUIDE` - CER的系统提示词

### 修改RAG内容

编辑 `data/rag_v2/{topic}_{subtopic}.txt`:
- `=== AER Content ===` - AER各阶段的参考内容
- `=== CER Content ===` - CER各阶段的参考内容

### 调整质量检查标准

编辑 `test_autonomous_dialogue.py` 中的 `check_response_quality` 方法

---

## 联系支持

如有问题，请查看：
- **测试总结**: `TEST_SUMMARY.md`
- **系统架构**: `SYSTEM_COMPLETE.md`
- **国际化指南**: `I18N_ARCHITECTURE.md`

---

**最后更新**: 2026年3月24日
**版本**: 2.0
**状态**: ✅ 生产就绪
