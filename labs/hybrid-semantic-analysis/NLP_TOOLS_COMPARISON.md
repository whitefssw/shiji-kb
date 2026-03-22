# NLP工具对比与选择

## 当前问题

LTP在Python 3.13环境下存在兼容性问题,无法正常运行。

## 替代方案调研

### 1. HanLP

**官网**: https://github.com/hankcs/HanLP

**版本**:
- HanLP 2.x (推荐,基于深度学习)
- HanLP 1.x (传统NLP,Java实现)

**功能**:
- ✅ 中文分词
- ✅ 词性标注
- ✅ 命名实体识别(NER)
- ✅ 依存句法分析
- ✅ 语义角色标注

**Python 3.13兼容性**: ✅ 应该兼容

**安装**:
```bash
# 基础版本(不包含深度学习后端)
pip install hanlp

# 完整版本(包含tensorflow,推荐)
pip install 'hanlp[full]'
```

**注意**: NER模型需要tensorflow,必须安装完整版本

**示例代码**:
```python
import hanlp

# 加载预训练模型
recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)

# 识别实体
text = "项籍者,下相人也"
entities = recognizer(text)
print(entities)
```

**优势**:
- 活跃维护,社区活跃
- 支持多种预训练模型
- API设计现代,易用
- 支持CPU和GPU

**劣势**:
- 首次加载模型较慢
- 模型文件较大(~1GB)
- 对古文支持可能不如现代汉语

**适用场景**: ⭐⭐⭐⭐⭐ 强烈推荐

---

### 2. Stanford CoreNLP

**官网**: https://stanfordnlp.github.io/CoreNLP/

**中文支持**: stanford-corenlp-zh

**功能**:
- ✅ 中文分词
- ✅ 词性标注
- ✅ 命名实体识别
- ✅ 依存句法分析
- ✅ 共指消解

**Python 3.13兼容性**: ⚠️ 需要Java环境

**安装**:
```bash
# 需要Java 8+
pip install stanfordcorenlp

# 下载中文模型
wget http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
```

**示例代码**:
```python
from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('/path/to/stanford-corenlp', lang='zh')

text = '项籍者,下相人也'
entities = nlp.ner(text)
print(entities)

nlp.close()
```

**优势**:
- 学术界广泛使用
- 稳定可靠
- 文档完善

**劣势**:
- 需要Java环境
- 启动较慢(JVM)
- 模型较大(~3GB)
- 对古文支持一般

**适用场景**: ⭐⭐⭐ 可选,但不如HanLP方便

---

### 3. Stanza (Stanford NLP的Python实现)

**官网**: https://stanfordnlp.github.io/stanza/

**功能**:
- ✅ 中文分词
- ✅ 词性标注
- ✅ 命名实体识别
- ✅ 依存句法分析

**Python 3.13兼容性**: ✅ 应该兼容

**安装**:
```bash
pip install stanza
```

**示例代码**:
```python
import stanza

# 下载中文模型
stanza.download('zh')

# 初始化pipeline
nlp = stanza.Pipeline('zh', processors='tokenize,ner')

# 处理文本
doc = nlp('项籍者,下相人也')
for ent in doc.ents:
    print(f'{ent.text}\t{ent.type}')
```

**优势**:
- 纯Python实现,无需Java
- Stanford官方维护
- 性能较好

**劣势**:
- 模型下载较大(~500MB)
- 对古文支持未知

**适用场景**: ⭐⭐⭐⭐ 推荐

---

### 4. spaCy (中文支持)

**官网**: https://spacy.io/

**中文模型**: zh_core_web_sm, zh_core_web_md, zh_core_web_lg

**功能**:
- ✅ 中文分词
- ✅ 词性标注
- ✅ 命名实体识别
- ✅ 依存句法分析

**Python 3.13兼容性**: ✅ 兼容

**安装**:
```bash
pip install spacy
python -m spacy download zh_core_web_sm
```

**示例代码**:
```python
import spacy

nlp = spacy.load("zh_core_web_sm")

doc = nlp("项籍者,下相人也")
for ent in doc.ents:
    print(f'{ent.text}\t{ent.label_}')
```

**优势**:
- 速度快,性能优秀
- API设计优雅
- 社区活跃,生态丰富

**劣势**:
- 中文模型相对较弱
- 对古文支持很差
- 训练数据主要是现代汉语

**适用场景**: ⭐⭐ 不推荐(古文效果差)

---

### 5. jieba (结巴分词)

**官网**: https://github.com/fxsjy/jieba

**功能**:
- ✅ 中文分词
- ⚠️ 词性标注(基础)
- ❌ 命名实体识别(需额外配置)

**Python 3.13兼容性**: ✅ 兼容

**安装**:
```bash
pip install jieba
```

**示例代码**:
```python
import jieba
import jieba.posseg as pseg

# 分词+词性
words = pseg.cut("项籍者,下相人也")
for word, flag in words:
    print(f'{word}\t{flag}')
```

**优势**:
- 轻量级,速度快
- 安装简单,无依赖
- 支持自定义词典

**劣势**:
- 仅分词,NER需要额外工具
- 对古文支持一般

**适用场景**: ⭐⭐ 只用于分词,不适合实体识别

---

## 推荐方案

### 方案1: HanLP 2.x (⭐⭐⭐⭐⭐ 强烈推荐)

**理由**:
1. ✅ Python 3.13兼容性好
2. ✅ 功能完整(NER + 依存分析)
3. ✅ 性能优秀
4. ✅ 活跃维护
5. ✅ 中文NLP专用工具

**实施步骤**:
```bash
# 1. 安装
pip install hanlp

# 2. 测试
python test_hanlp.py --data short
```

### 方案2: Stanza (⭐⭐⭐⭐ 推荐)

**理由**:
1. ✅ Stanford官方维护
2. ✅ 纯Python,无需Java
3. ✅ 性能不错
4. ✅ 文档完善

**实施步骤**:
```bash
# 1. 安装
pip install stanza

# 2. 下载中文模型
python -c "import stanza; stanza.download('zh')"

# 3. 测试
python test_stanza.py --data short
```

### 方案3: HanLP + jieba 组合

**理由**:
- jieba快速分词
- HanLP精确NER
- 结合优势

## 实施计划

### 第一步: 创建HanLP测试脚本

创建 `test_hanlp.py`:
```python
#!/usr/bin/env python3
import hanlp

# 加载NER模型
recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)

# 处理文本
text = "项籍者,下相人也"
entities = recognizer(text)

# 输出结果
for entity in entities:
    print(f'{entity[0]}\t{entity[1]}')
```

### 第二步: 测试兼容性

```bash
python test_hanlp.py --data short
```

### 第三步: 性能对比

| 工具 | 召回率 | 精确率 | 速度 | 兼容性 |
|------|-------|-------|-----|--------|
| LTP | 83.3% | 100% | 1.5秒 | ❌ |
| HanLP | ? | ? | ? | ✅ |
| Stanza | ? | ? | ? | ✅ |

### 第四步: 更新run_tests.sh

添加HanLP测试:
```bash
# 4.1 HanLP测试
if command -v python test_hanlp.py &> /dev/null; then
    python test_hanlp.py --data short
fi
```

## 古文NLP的特殊考虑

### 问题:
1. 现代NLP工具主要训练于现代汉语
2. 古文语法、词汇与现代汉语差异大
3. 需要古文专用模型或词典

### 解决方案:

#### 方案A: 使用通用工具 + 自定义词典
```python
import hanlp

# 加载模型
recognizer = hanlp.load(...)

# 添加古文词典
custom_dict = {
    '项籍': 'PERSON',
    '项梁': 'PERSON',
    '下相': 'PLACE',
    # ...
}

# 后处理修正
```

#### 方案B: 微调预训练模型
- 使用已标注的《史记》数据
- 微调HanLP或Stanza模型
- 提升古文识别准确度

#### 方案C: 规则 + 模型混合
- 规则提取高置信度实体(如"XXX者"模式)
- 模型处理复杂情况
- 结合优势

## 下一步行动

1. **安装HanLP**: `pip install hanlp`
2. **创建test_hanlp.py**: 仿照test_ltp.py结构
3. **运行测试**: 验证Python 3.13兼容性
4. **性能评估**: 对比LTP结果
5. **决策**: 选择最佳工具

## 参考资料

- [HanLP文档](https://hanlp.hankcs.com/)
- [Stanza文档](https://stanfordnlp.github.io/stanza/)
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/)
- [spaCy中文模型](https://spacy.io/models/zh)
