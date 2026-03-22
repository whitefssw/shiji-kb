# 混合语义分析实验

## 实验目标

对比三种语义分析方案的成本和效果:

- **方案A (纯本地)**: 使用本地NLP工具(依存文法/小模型)完成语义标注
- **方案B (混合)**: 本地模型粗标注 + LLM精炼修正
- **方案C (纯LLM)**: 直接使用大模型完成语义标注(对照组)

## 评估指标

- **时间成本**: 总耗时(秒)
- **Token成本**: API调用总token数
- **质量评估**: 标注准确率、实体召回率、关系准确性
- **显存占用**: 本地模型推理峰值显存

## 技术方案

### 方案A: 纯本地NLP

**工具选择(8G显存)**:

1. **依存文法分析** (推荐,几乎不占显存)
   - LTP 4.x (哈工大)
   - HanLP 2.x

2. **小规模语言模型** (4-7GB显存)
   - Qwen2.5-7B-Instruct (阿里)
   - GLM-4-9B-Chat (智谱)

**流程**:
```
原文 → 分词/词性标注 → 依存句法分析 → 规则提取实体 → 关系抽取 → 输出标注
```

### 方案B: 混合方案

**流程**:
```
原文 → 本地模型粗标注 → LLM review修正 → 输出标注
```

**设计思路**:
- 本地模型处理常见实体(人名/地名等)
- LLM处理复杂实体(官职/事件)和消歧
- 目标: 降低token消耗,保持标注质量

### 方案C: 纯LLM (对照组)

**流程**:
```
原文 → Claude API (完整标注) → 输出标注
```

## 测试数据

从已标注章节选取典型片段(100-500字):

- 人物密集型: 如《项羽本纪》战争片段
- 地名密集型: 如《河渠书》地理描述
- 关系复杂型: 如《陈涉世家》起义叙事

## 目录结构

```
labs/hybrid-semantic-analysis/
├── README.md              # 本文件
├── QUICKSTART.md          # 快速开始指南 ⭐
├── STATUS.md              # 当前进度状态
├── requirements.txt       # Python依赖
├── config.yaml            # 配置文件(模型路径/API key)
├── run_tests.sh           # 一键测试脚本
│
├── 文档/
│   ├── MODEL_STORAGE.md   # 模型文件存储位置说明
│   ├── LTP_STATUS.md      # LTP兼容性状态
│   ├── LTP_COMPATIBILITY_ISSUE.md  # LTP兼容性问题详解
│   ├── QWEN_MEMORY_ISSUE.md        # Qwen内存问题分析
│   └── QWEN_TEST_SUMMARY.md        # Qwen测试总结
│
├── 测试脚本/
│   ├── test_ltp.py             # LTP统一测试(支持3个尺度)
│   ├── test_qwen_actual.py     # Qwen实际测试(FP16)
│   ├── test_qwen_int8.py       # Qwen量化测试(INT8)
│   ├── download_qwen.py        # Qwen模型下载
│   ├── extract_chapter_text.py # 提取章节文本
│   └── patch_ltp.py            # LTP兼容性补丁
│
├── data/
│   ├── test_corpus.txt         # 短文本测试语料(138字)
│   ├── test_corpus_long.txt    # 中文本测试语料(631字)
│   ├── test_corpus_chapter.txt # 长文本测试语料(3000字)
│   └── ground_truth.tagged.md  # 标准答案
│
├── methods/
│   ├── method_a_local.py  # 方案A: 纯本地
│   ├── method_b_hybrid.py # 方案B: 混合 (⏳待实现)
│   └── method_c_llm.py    # 方案C: 纯LLM (⏳待实现)
│
├── utils/
│   ├── __init__.py        # 工具模块
│   ├── evaluator.py       # 评估工具
│   └── tokenizer.py       # Token计数工具
│
├── results/
│   ├── test_data_summary.md       # 测试数据说明 ⭐
│   ├── ltp_experiment_report.md   # LTP详细分析 ⭐
│   ├── experiment_summary.md      # 实验总结报告
│   ├── ltp_long_result.json       # LTP中文本结果
│   └── comparison.json            # 对比结果
│
└── venv/                  # 虚拟环境 (gitignored)
```

## 核心文档导航

### 📘 新手入门
- **[QUICKSTART.md](QUICKSTART.md)** - 快速开始指南,一键运行测试
- **[STATUS.md](STATUS.md)** - 当前实验进度和下一步计划

### 📊 实验结果
- **[results/test_data_summary.md](results/test_data_summary.md)** - 测试数据说明(3个尺度)
- **[results/ltp_experiment_report.md](results/ltp_experiment_report.md)** - LTP详细分析报告
- **[results/experiment_summary.md](results/experiment_summary.md)** - 总体实验总结

### 🔧 技术文档
- **[PYTHON_VERSION_GUIDE.md](PYTHON_VERSION_GUIDE.md)** - Python版本选择指南 ⭐
- **[NLP_TOOLS_COMPARISON.md](NLP_TOOLS_COMPARISON.md)** - NLP工具对比(LTP/HanLP/Stanza等)
- **[NLP_TOOLS_TEST_RESULTS.md](NLP_TOOLS_TEST_RESULTS.md)** - NLP工具实测结果
- **[MODEL_STORAGE.md](MODEL_STORAGE.md)** - 模型文件存储位置和管理
- **[LTP_STATUS.md](LTP_STATUS.md)** - LTP兼容性状态和解决方案
- **[QWEN_TEST_SUMMARY.md](QWEN_TEST_SUMMARY.md)** - Qwen测试过程和问题总结
- **[QWEN_MEMORY_ISSUE.md](QWEN_MEMORY_ISSUE.md)** - Qwen内存问题详细分析

### 🔍 问题诊断
- **[LTP_COMPATIBILITY_ISSUE.md](LTP_COMPATIBILITY_ISSUE.md)** - LTP兼容性问题根因分析

## 快速开始

**推荐**: 直接查看 **[QUICKSTART.md](QUICKSTART.md)** 获取完整使用指南。

### 一键运行测试

```bash
cd labs/hybrid-semantic-analysis
./run_tests.sh
```

脚本会自动:
- 激活虚拟环境
- 检查测试数据
- 运行所有可用测试(LTP 3个尺度)
- 显示结果汇总

## 实测结果

### 方案A1: LTP依存文法 ✅

| 指标 | 138字 | 631字 | 3000字 |
|------|-------|-------|--------|
| 召回率 | 83.3% | - | 88.9% |
| 精确率 | 100% | - | 99% |
| 时间 | 1.5秒 | 1.8秒 | 2.1秒 |
| 成本 | $0 | $0 | $0 |

**优势**: 零成本,速度快,人名/地名识别完美
**局限**: 无法识别官职类实体(OFFICE)

详见: [results/ltp_experiment_report.md](results/ltp_experiment_report.md)

### 方案A2: Qwen2.5-7B ❌

**状态**: 实测失败 - 显存不足(OOM x2)

- 需要: 14-16GB显存(FP16模式)
- 当前: 8GB显存(RTX 4060 Laptop)
- 替代: 可尝试Qwen2.5-3B (6GB显存)

详见: [QWEN_TEST_SUMMARY.md](QWEN_TEST_SUMMARY.md)

### 方案B: 混合方案 ⏳

**状态**: 待实现

**设计**:
1. LTP预标注(人名/地名)
2. LLM精炼(官职/事件/消歧)

### 方案C: 纯Claude ⏳

**状态**: 待实现

## 当前进度

- ✅ 环境搭建和依赖安装
- ✅ 测试数据准备(3个尺度)
- ✅ LTP完整测试(短/中/长)
- ✅ Qwen模型下载(15GB)
- ❌ Qwen实际测试(显存不足)
- ⏳ 混合方案实现
- ⏳ Claude方案实现
- ⏳ 最终对比分析

详见: [STATUS.md](STATUS.md)

## 下一步行动

1. 实现方案B(混合): LTP + Claude精炼
2. 实现方案C(纯Claude): 直接标注
3. 运行对比测试,生成分析报告
4. (可选)测试Qwen2.5-3B作为补充数据

## 参与贡献

如有问题或建议,请查看相关文档或在项目中提issue。
