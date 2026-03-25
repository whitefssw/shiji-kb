# Ontology 目录

本目录包含《史记》知识本体的不同版本。

## 目录结构

```
ontology/
├── ontology-v1/     # 稳定版本（当前生产使用）
└── ontology-v2/     # 实验版本（知识覆盖度转化实验中）
```

## 版本说明

### ontology-v1（稳定版本）

- **状态**：已完成，稳定版本
- **用途**：生产环境使用的知识本体
- **内容**：
  - 434 项事实性标准知识单元（Factual SKUs - Standard Knowledge Units）
  - 241 项技能标准知识单元（Procedural SKUs - Standard Knowledge Units）
  - 1 项关系标准知识单元（标签体系、术语表、实体关系）
  - 实体标注（7,497 个实体标注，覆盖 17 类命名实体）
- **详细说明**：见 [ontology-v1/README.md](ontology-v1/README.md)

### ontology-v2（实验版本）

- **状态**：实验中
- **用途**：知识覆盖度转化相关实验
- **说明**：用于测试新的知识组织方式和覆盖度分析方法
- **详细说明**：见 [ontology-v2/README.md](ontology-v2/README.md)

## 使用建议

- **应用开发**：使用 `ontology-v1`，保证稳定性
- **实验研究**：使用 `ontology-v2`，探索新方法
- **版本迁移**：待 v2 实验成熟后，评估是否升级到 v1
