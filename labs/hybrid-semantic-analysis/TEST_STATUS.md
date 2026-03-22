# 测试脚本状态

**更新时间**: 2026-03-22

## 测试脚本清单

### ✅ test_ltp.py - LTP统一测试脚本

**功能**: 使用真实LTP模型进行实体标注

**命令**:
```bash
python test_ltp.py --data short   # 138字
python test_ltp.py --data medium  # 631字
python test_ltp.py --data long    # 3000字
```

**当前状态**: ❌ 因兼容性问题无法运行

**错误信息**:
```
AttributeError: BertTokenizer has no attribute batch_encode_plus
```

**原因**: LTP使用的transformers API在新版本中已废弃

**解决方案**:
1. 使用Python 3.10环境
2. 查看已有测试结果: [results/ltp_experiment_report.md](results/ltp_experiment_report.md)
3. 详见: [LTP_STATUS.md](LTP_STATUS.md)

### ✅ test_qwen_actual.py - Qwen2.5-7B测试

**功能**: 使用真实Qwen2.5-7B模型进行标注

**命令**:
```bash
python test_qwen_actual.py
```

**当前状态**: ❌ 因显存不足无法运行

**原因**: 需要14-16GB显存(FP16模式),当前环境只有8GB

**解决方案**:
1. 使用Qwen2.5-3B (6GB显存)
2. 使用云端GPU (16GB+显存)
3. 详见: [QWEN_TEST_SUMMARY.md](QWEN_TEST_SUMMARY.md)

### ✅ test_qwen_int8.py - Qwen INT8量化测试

**功能**: 使用INT8量化的Qwen2.5-7B

**命令**:
```bash
pip install bitsandbytes accelerate
python test_qwen_int8.py
```

**当前状态**: ❌ CUDA兼容性问题

**错误**: CUDA initialization error

**解决方案**: 详见 [QWEN_MEMORY_ISSUE.md](QWEN_MEMORY_ISSUE.md)

### ⚠️ demo_qwen_result.py - Qwen格式演示

**功能**: 展示标注格式,**不用于性能测试**

**警告**:
- 标注结果基于ground truth生成
- 性能数据为示例值,无实际意义
- 仅用于理解标注格式

**何时使用**: 理解工作流程,不用于性能评估

## 集成测试脚本

### ✅ run_tests.sh - 一键测试

**功能**: 自动运行所有可用测试

**命令**:
```bash
./run_tests.sh
```

**流程**:
1. 检查并激活虚拟环境
2. 检查测试数据
3. 运行test_ltp.py (3个尺度)
4. 运行test_qwen_actual.py (如果模型已下载)
5. 运行混合方案 (如果已实现)
6. 运行Claude方案 (如果已实现)
7. 显示结果汇总

**错误处理**: 优雅地处理失败,提供有用的错误信息和解决方案链接

## 已删除的废弃脚本

以下模拟脚本已删除:
- ~~demo_ltp_result.py~~ ✅ 已删除
- ~~demo_ltp_long.py~~ ✅ 已删除
- ~~demo_ltp_chapter.py~~ ✅ 已删除

**删除原因**: 使用模拟数据,误导性强

**替代**: 使用真实的test_ltp.py

## 工具脚本

### download_qwen.py
下载Qwen2.5-7B模型 (~15GB)

### extract_chapter_text.py
从标注文件提取纯文本

### patch_ltp.py
修复LTP的use_auth_token问题

## 当前可运行的测试

在当前环境(Python 3.13 + 8GB显存)下:

❌ **无法运行**:
- test_ltp.py (transformers兼容性)
- test_qwen_actual.py (显存不足)
- test_qwen_int8.py (CUDA问题)

✅ **可以运行**:
- run_tests.sh (会优雅地处理失败)
- demo_qwen_result.py (仅用于格式演示)

📊 **已有数据**:
- LTP完整测试结果: [results/ltp_experiment_report.md](results/ltp_experiment_report.md)
- 测试数据说明: [results/test_data_summary.md](results/test_data_summary.md)

## 推荐下一步

1. **使用已有数据**: LTP测试结果已完整,无需重新运行
2. **实现方案B和C**:
   - methods/method_b_hybrid.py (LTP + Claude)
   - methods/method_c_claude.py (纯Claude)
3. **运行对比测试**: 基于LTP已有数据 + 新的Claude测试
4. **(可选)补充Qwen测试**: 使用Qwen2.5-3B或云端环境

## 相关文档

- [LTP_STATUS.md](LTP_STATUS.md) - LTP兼容性详情
- [QWEN_TEST_SUMMARY.md](QWEN_TEST_SUMMARY.md) - Qwen测试总结
- [SCRIPTS_README.md](SCRIPTS_README.md) - 脚本使用指南
- [STATUS.md](STATUS.md) - 项目整体状态
