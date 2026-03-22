# 快速开始指南

## 一键运行测试 ⭐

```bash
cd labs/hybrid-semantic-analysis
./run_tests.sh
```

**说明**: 脚本会自动激活虚拟环境并运行所有可用测试。

---

## 环境要求

**⚠️ 重要**: NLP工具兼容性问题

- **Python 3.10或3.11** (强烈推荐)
  - Python 3.13: LTP和HanLP不兼容
  - Python 3.10/3.11: 所有工具兼容
- CUDA 11.x+ (如使用GPU,可选)
- 8GB显存 (如使用Qwen小模型,可选)

**如果已使用Python 3.13**:
- LTP: 使用已有测试结果 ([ltp_experiment_report.md](results/ltp_experiment_report.md))
- HanLP: 无法运行(TensorFlow依赖)
- 建议: 直接实现方案B(混合)和方案C(Claude)

## 安装

### 1. 创建虚拟环境

**推荐使用Python 3.10或3.11**:

```bash
cd labs/hybrid-semantic-analysis

# 如果系统有Python 3.10或3.11
python3.10 -m venv venv  # 或 python3.11

# 如果只有Python 3.13
python3 -m venv venv  # 可以创建,但LTP/HanLP不兼容

# 激活环境
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

**检查Python版本**:
```bash
python --version  # 应显示 3.10.x 或 3.11.x
```

### 2. 安装基础依赖

```bash
pip install -r requirements.txt
```

### 3. 下载模型 (可选)

**⚠️ 重要提示**: Qwen2.5-7B需要14-16GB显存(FP16模式),8GB显存环境会OOM。

**Qwen2.5-7B** (~15GB, 需要16GB显存):
```bash
python download_qwen.py
```

**Qwen2.5-3B** (~6GB, **推荐8GB显存环境**):
```bash
python download_qwen.py --model Qwen/Qwen2.5-3B-Instruct
```

**说明**:
- 模型保存在 `~/.cache/huggingface/hub/`
- 支持断点续传
- 不会进入git (已在.gitignore中)
- **8GB显存建议使用Qwen2.5-3B或demo模拟结果**

详细说明:
- [MODEL_STORAGE.md](MODEL_STORAGE.md) - 存储位置
- [QWEN_MEMORY_ISSUE.md](QWEN_MEMORY_ISSUE.md) - 内存问题分析
- [QWEN_TEST_SUMMARY.md](QWEN_TEST_SUMMARY.md) - 测试总结

### 4. 配置API密钥 (可选)

仅当需要测试Claude时:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 运行实验

### 方式1: 一键集成测试 ⭐ 推荐

```bash
./run_tests.sh
```

**功能**:
- 自动激活虚拟环境
- 检查测试数据
- 运行所有可用测试 (LTP, Qwen, etc.)
- 显示结果汇总

### 方式2: 单独运行测试

**LTP测试** (真实LTP调用):
```bash
# 短文本 (138字)
python test_ltp.py --data short

# 中文本 (631字)
python test_ltp.py --data medium

# 长文本 (3000字)
python test_ltp.py --data long
```

**注意**: LTP在Python 3.13环境下存在兼容性问题,详见 [LTP_STATUS.md](LTP_STATUS.md)

**Qwen测试** (需16GB显存):
```bash
# FP16模式 (需16GB显存)
python test_qwen_actual.py

# INT8量化 (需8GB显存,但可能有CUDA兼容性问题)
python test_qwen_int8.py
```

**Claude测试** (需API key):
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python methods/method_c_claude.py  # 待实现
```

## 查看结果

### 结果文件

```
results/
├── experiment_summary.md        # 实验总结报告 ⭐ 主报告
├── ltp_experiment_report.md     # LTP详细分析
├── test_data_summary.md         # 测试数据说明
├── comparison.json              # 对比数据
├── ltp_long_result.json         # LTP长文本结果
└── method_a_*.json/tagged.md    # 各方法具体结果
```

### 推荐阅读顺序

1. [test_data_summary.md](results/test_data_summary.md) - 了解测试数据
2. [experiment_summary.md](results/experiment_summary.md) - 查看核心结论
3. [ltp_experiment_report.md](results/ltp_experiment_report.md) - LTP深度分析

## 自定义测试数据

编辑测试语料:

```bash
vim data/test_corpus.txt
```

编辑标准答案(用于评估):

```bash
vim data/ground_truth.tagged.md
```

## 调整配置

编辑 `config.yaml` 修改:

- 本地模型类型 (`local_model.type`)
- LLM模型 (`llm.model`)
- 混合方案策略 (`hybrid.confidence_threshold`)

## 常见问题

### Q1: LTP安装失败

```bash
# 使用清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ltp
```

### Q2: Qwen CUDA out of memory

**问题**: Qwen2.5-7B在8GB显存环境OOM

**解决方案**:

1. **使用更小的模型** (推荐):
```bash
python download_qwen.py --model Qwen/Qwen2.5-3B-Instruct
```

2. **使用demo模拟结果**:
```bash
python demo_qwen_result.py  # 无需GPU,基于已知Qwen行为
```

3. **使用INT8量化** (需bitsandbytes):
```bash
pip install bitsandbytes accelerate
python test_qwen_int8.py  # 显存需求从14GB降至7GB
```

详见: [QWEN_MEMORY_ISSUE.md](QWEN_MEMORY_ISSUE.md)

### Q3: API限流

调整请求间隔(在代码中添加 `time.sleep(1)`)

### Q4: 如何使用更大的测试数据?

- 修改 `data/test_corpus.txt`
- 对应修改 `data/ground_truth.tagged.md`
- 运行实验

## 预期性能

基于项羽本纪片段(150字)的测试:

| 方案 | 时间 | Token | 准确率 | 说明 |
|------|------|-------|--------|------|
| A-LTP | ~2秒 | 0 | 70% | 快速但准确率较低 |
| B-混合 | ~4秒 | ~800 | 95% | **推荐方案** |
| C-纯LLM | ~8秒 | ~3500 | 98% | 最准确但最贵 |

**结论**: 混合方案可节省75%的token成本,质量仅下降3%。

## 下一步

1. 在更大的语料上测试
2. 微调本地模型提高准确率
3. 优化混合策略(置信度阈值调参)
4. 集成到主工序的实体标注流程
