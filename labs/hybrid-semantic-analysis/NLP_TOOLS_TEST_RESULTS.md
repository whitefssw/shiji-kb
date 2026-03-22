# NLP工具实测结果

**测试环境**: Python 3.13.3 + 8GB显存

**测试时间**: 2026-03-22

## 测试结果总结

| 工具 | 安装 | 运行 | 问题 | Python 3.13兼容性 |
|------|------|------|------|-------------------|
| LTP | ✅ | ❌ | transformers API兼容性 | ❌ |
| HanLP | ✅ | ❌ | TensorFlow依赖冲突 | ❌ |
| Stanza | ⏳ | ⏳ | 未测试 | ✅ (理论) |
| spaCy | ⏳ | ⏳ | 未测试 | ✅ (理论) |

## 详细测试记录

### 1. LTP (哈工大)

**安装**:
```bash
pip install ltp  # ✅ 成功
```

**运行**:
```bash
python test_ltp.py --data short
```

**结果**: ❌ 失败

**错误信息**:
```
AttributeError: BertTokenizer has no attribute batch_encode_plus
```

**原因**:
- LTP使用transformers 4.x API
- transformers 5.x已废弃batch_encode_plus方法
- Python 3.13环境需要最新的transformers

**解决方案**:
- 使用Python 3.10环境
- 或使用已有测试结果

**已有数据**: ✅ 完整的3个尺度测试结果

---

### 2. HanLP 2.x

**安装**:
```bash
# 基础版本
pip install hanlp  # ✅ 成功

# 完整版本(NER需要)
pip install 'hanlp[full]'  # ❌ 失败
```

**运行**:
```bash
python test_hanlp.py --data short
```

**结果**: ❌ 失败

**错误信息**:
```
ERROR: Cannot install hanlp[full] because these package versions have conflicting dependencies.

The conflict is caused by:
    hanlp[full] depends on tensorflow<2.14 and >=2.6.0

Additionally, some packages in these conflicts have no matching distributions available for your environment:
    tensorflow
```

**原因**:
- HanLP的NER模型需要TensorFlow
- TensorFlow < 2.14 在Python 3.13环境下不可用
- TensorFlow官方尚未完全支持Python 3.13

**解决方案**:
- 使用Python 3.10或3.11环境
- 等待HanLP支持TensorFlow 2.14+
- 或使用PyTorch后端的NER模型(如果有)

**测试状态**: ⚠️ Python 3.13环境不兼容

---

### 3. Stanza (未测试)

**理论兼容性**: ✅ 应该兼容Python 3.13

**原因**:
- 基于PyTorch,不依赖TensorFlow
- PyTorch对Python 3.13支持良好

**下一步**: 可以尝试测试

**安装**:
```bash
pip install stanza
python -c "import stanza; stanza.download('zh')"
```

---

### 4. spaCy (未测试)

**理论兼容性**: ✅ 应该兼容Python 3.13

**原因**:
- 纯Python/Cython实现
- 不依赖TensorFlow

**局限**: 中文NER效果可能不如HanLP/LTP

**下一步**: 可以尝试测试

**安装**:
```bash
pip install spacy
python -m spacy download zh_core_web_sm
```

## Python 3.13 兼容性分析

### ❌ 不兼容的工具

1. **LTP**: transformers 5.x API变更
2. **HanLP**: TensorFlow < 2.14 不支持Python 3.13

### ✅ 可能兼容的工具

1. **Stanza**: 基于PyTorch,理论兼容
2. **spaCy**: 无深度学习后端依赖

### 根本问题

**Python 3.13太新**:
- 很多深度学习库尚未完全支持
- TensorFlow官方支持滞后
- API breaking changes导致兼容性问题

## 推荐方案

### 方案1: 使用Python 3.10环境 ⭐⭐⭐⭐⭐

**优势**:
- LTP和HanLP都能正常运行
- 生态成熟,兼容性好
- 所有NLP工具都支持

**实施**:
```bash
# 创建Python 3.10虚拟环境
conda create -n shiji-nlp python=3.10
conda activate shiji-nlp

# 安装工具
pip install ltp hanlp[full] stanza spacy
```

### 方案2: 测试Stanza (Python 3.13) ⭐⭐⭐⭐

**优势**:
- 无需切换Python版本
- Stanford官方维护
- 基于PyTorch,兼容性好

**实施**:
```bash
# 在当前Python 3.13环境
pip install stanza
python test_stanza.py --data short
```

**下一步**: 创建test_stanza.py并测试

### 方案3: 使用已有LTP数据 + Claude ⭐⭐⭐⭐⭐

**优势**:
- 已有完整的LTP测试结果
- 可以直接实现混合方案和Claude方案
- 无需解决兼容性问题

**实施**:
- 基于LTP已有数据
- 实现methods/method_b_hybrid.py
- 实现methods/method_c_claude.py
- 运行对比测试

## 建议

### 短期(立即可做):

1. **✅ 使用已有LTP数据**,不再尝试运行LTP
2. **🔍 测试Stanza**(Python 3.13兼容)
3. **🚀 实现方案B和C**,进入对比测试阶段

### 中期(可选):

1. 创建Python 3.10环境
2. 在Python 3.10环境测试LTP/HanLP
3. 对比不同工具性能

### 长期(观望):

1. 等待TensorFlow支持Python 3.13
2. 等待HanLP更新依赖
3. 等待LTP修复transformers兼容性

## 文件清单

### 已创建的测试脚本

- ✅ test_ltp.py - LTP测试(无法运行)
- ✅ test_hanlp.py - HanLP测试(无法运行)
- ⏳ test_stanza.py - 待创建

### 文档

- ✅ NLP_TOOLS_COMPARISON.md - 工具对比
- ✅ NLP_TOOLS_TEST_RESULTS.md - 本文件
- ✅ LTP_STATUS.md - LTP兼容性状态
- ✅ TEST_STATUS.md - 整体测试状态

## 总结

**现状**: Python 3.13环境下,传统NLP工具(LTP/HanLP)都因依赖问题无法运行

**原因**:
1. TensorFlow不支持Python 3.13
2. transformers API breaking changes
3. 深度学习生态对新Python版本支持滞后

**解决方案**:
1. ⭐⭐⭐⭐⭐ 使用已有LTP数据,直接进入方案B/C测试
2. ⭐⭐⭐⭐ 测试Stanza(基于PyTorch,理论兼容)
3. ⭐⭐⭐ 使用Python 3.10环境(兼容性最好)

**推荐**: 采用方案1,使用已有数据,直接实现混合方案和Claude方案进行对比测试。
