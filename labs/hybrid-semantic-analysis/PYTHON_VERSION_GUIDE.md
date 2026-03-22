# Python版本选择指南

## TL;DR

**推荐**: **Python 3.10** 或 **Python 3.11**

**原因**: Python 3.13太新,深度学习生态支持不足

## 兼容性对比

| Python版本 | LTP | HanLP | Qwen | Claude API | 推荐度 |
|-----------|-----|-------|------|-----------|--------|
| 3.10 | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| 3.11 | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| 3.12 | ⚠️ | ⚠️ | ✅ | ✅ | ⭐⭐⭐ |
| 3.13 | ❌ | ❌ | ✅ | ✅ | ⭐⭐ |

## 详细说明

### Python 3.10 (⭐⭐⭐⭐⭐ 最推荐)

**优势**:
- ✅ 所有NLP工具完美支持
- ✅ 生态最成熟
- ✅ LTP、HanLP、Stanza、spaCy都兼容
- ✅ TensorFlow、PyTorch稳定

**劣势**:
- 无

**使用**:
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install ltp 'hanlp[full]' stanza
```

### Python 3.11 (⭐⭐⭐⭐⭐ 推荐)

**优势**:
- ✅ 所有NLP工具支持
- ✅ 性能更好(比3.10快10-25%)
- ✅ 现代Python特性

**劣势**:
- 部分老旧库可能不兼容(少见)

**使用**:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install ltp 'hanlp[full]' stanza
```

### Python 3.12 (⭐⭐⭐ 可选)

**优势**:
- 性能进一步提升
- 新特性支持

**劣势**:
- ⚠️ LTP可能有兼容性问题
- ⚠️ HanLP部分模型可能不支持
- TensorFlow支持不完整

**使用**:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install ltp  # 可能失败
```

### Python 3.13 (⭐⭐ 不推荐)

**优势**:
- 最新Python特性
- 性能最好

**劣势**:
- ❌ LTP不兼容(transformers API问题)
- ❌ HanLP不兼容(TensorFlow不支持)
- ❌ 大部分深度学习工具支持不完整
- 生态支持滞后

**适用场景**:
- 只使用Claude API(不依赖本地NLP工具)
- 使用基于PyTorch的工具(Qwen、Stanza)

**使用**:
```bash
python3.13 -m venv venv
source venv/bin/activate
# LTP和HanLP无法安装
pip install transformers torch  # Qwen可用
```

## 问题根源

### 为什么Python 3.13不兼容?

1. **TensorFlow滞后**:
   - TensorFlow最新版本(2.13)不支持Python 3.13
   - HanLP依赖TensorFlow < 2.14
   - 预计2026年中才会支持Python 3.13

2. **transformers API变更**:
   - transformers 5.x移除了batch_encode_plus
   - LTP仍使用旧API
   - 需要LTP更新代码

3. **生态滞后**:
   - Python 3.13发布于2024年10月
   - 深度学习生态通常滞后6-12个月

## 如何切换Python版本?

### 方法1: 使用系统Python (简单)

```bash
# 检查可用版本
ls /usr/bin/python3*

# 使用特定版本创建venv
python3.10 -m venv venv  # 或3.11
source venv/bin/activate
```

### 方法2: 使用pyenv (推荐,灵活)

```bash
# 安装pyenv
curl https://pyenv.run | bash

# 安装Python 3.10
pyenv install 3.10.13

# 设置项目Python版本
cd labs/hybrid-semantic-analysis
pyenv local 3.10.13

# 创建venv
python -m venv venv
source venv/bin/activate
```

### 方法3: 使用conda

```bash
# 创建Python 3.10环境
conda create -n shiji-nlp python=3.10

# 激活
conda activate shiji-nlp

# 安装依赖
pip install ltp 'hanlp[full]' stanza
```

## 当前项目状态

**当前环境**: Python 3.13.3

**问题**:
- ❌ LTP无法运行
- ❌ HanLP无法安装

**解决方案**:

### 选项1: 使用已有LTP数据 (⭐⭐⭐⭐⭐ 推荐)

不切换Python版本,直接使用已有测试结果:

```bash
# 已有完整的LTP测试数据
cat results/ltp_experiment_report.md

# 直接实现方案B和C
# 创建 methods/method_b_hybrid.py
# 创建 methods/method_c_claude.py
```

**优势**:
- 无需重新配置环境
- 数据已完整
- 可立即推进

### 选项2: 切换到Python 3.10 (⭐⭐⭐⭐)

重新创建venv:

```bash
# 1. 删除当前venv
rm -rf venv

# 2. 使用Python 3.10创建
python3.10 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
pip install ltp 'hanlp[full]'

# 4. 运行测试
python test_ltp.py --data short
python test_hanlp.py --data short
```

**优势**:
- 所有工具可用
- 可对比LTP/HanLP性能
- 可重新运行测试

## 推荐方案

### 对于当前项目

**立即执行**: 选项1 (使用已有数据)
- 已有完整LTP测试结果
- 无需切换环境
- 可立即实现方案B/C

**可选补充**: 选项2 (切换Python 3.10)
- 如果想测试HanLP
- 如果想对比不同工具
- 如果有充足时间

### 对于新项目

**强烈建议**: 从一开始就使用Python 3.10或3.11

```bash
# 创建项目
mkdir new-project
cd new-project

# 使用Python 3.10
python3.10 -m venv venv
source venv/bin/activate

# 安装所有NLP工具
pip install ltp 'hanlp[full]' stanza spacy
```

## 总结

| 场景 | 推荐Python版本 | 原因 |
|------|---------------|------|
| 新项目 | 3.10/3.11 | 兼容性最好 |
| 当前项目(已有数据) | 保持3.13 | 无需切换,使用已有数据 |
| 测试所有工具 | 3.10 | 最成熟 |
| 只用Claude | 3.13 | 可以,无依赖问题 |
| 生产环境 | 3.10/3.11 | 稳定可靠 |

## 相关文档

- [NLP_TOOLS_TEST_RESULTS.md](NLP_TOOLS_TEST_RESULTS.md) - 实测结果
- [NLP_TOOLS_COMPARISON.md](NLP_TOOLS_COMPARISON.md) - 工具对比
- [LTP_STATUS.md](LTP_STATUS.md) - LTP兼容性
