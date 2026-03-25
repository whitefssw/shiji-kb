# 史记地铁图 - 已知问题

## 🔴 严重问题

### Bug #1: 时间轴与SVG内容不对齐

**症状**：
- 顶部和底部的固定时间轴刻度（如"前2650、前2500、前2350"）与SVG中的事件位置不匹配
- 验证函数`validateTimelineAlignment()`显示通过（✅），但视觉上明显不对齐
- 秦始皇本纪（黄色线）应该在前221附近，但实际显示位置与时间轴刻度不对应

**复现步骤**：
1. 访问 <http://localhost:8001>
2. 默认显示秦始皇本纪、项羽本纪、高祖本纪
3. 观察顶部时间轴与黄色线路的位置关系
4. 在控制台运行 `validateTimelineAlignment()` → 显示通过
5. 但视觉上时间轴和事件位置完全不匹配

**技术细节**：
- 验证代码逻辑上是对齐的：
  - `yearToSvgX()` 计算SVG坐标正确
  - `yearToScreenX()` 计算屏幕坐标正确
  - 验证函数确认每个marker都在预期位置
- 但实际渲染结果不对齐，说明问题在于：
  - **SVG的viewBox设置与实际内容不匹配**
  - **SVG的渲染坐标系统与计算的坐标系统脱节**

**相关代码位置**：
- [metro.js:147-177](metro.js#L147-L177) - 坐标转换函数
- [metro.js:754-811](metro.js#L754-L811) - updateTimelineRulers()
- [metro.js:188-201](metro.js#L188-L201) - render()中的viewBox初始化
- [index.html:27](index.html#L27) - SVG元素定义

**已尝试的修复**：
1. ✅ 设置 `preserveAspectRatio="none"` - 无效
2. ✅ 移除HTML中硬编码的viewBox - 无效
3. ✅ 在render()中初始化viewBox尺寸匹配SVG内容 - 无效
4. ✅ 在init()中先调用fitView()再调用centerViewOnYear() - 无效
5. ✅ 重构坐标转换函数为三层架构 - 逻辑正确但渲染仍不对齐

**调试信息**（上次测试）：
```javascript
// debugYearCoordinates(-250) 输出：
SVG-X: 4036.08
Screen-X: 826.11
ViewBox: x=80, w=4815.65
Container width: 905.58
Scale: 0.2046

// 实际SVG总尺寸：
svgTotalW: ~4430 (计算值: 120 + 40 + (2669) * 1.6)
svgTotalH: ~300+

// 初始viewBox：
{ x: 0, y: 0, w: 2000, h: 1000 } → 后被更新为 { x: 80, y: 0, w: 4815.65, h: xxx }
```

**可能的根本原因**：
1. **SVG内部坐标系统与viewBox映射不一致**
   - SVG元素使用yearToSvgX()计算位置（如4036.08）
   - 但viewBox可能不是从0开始，或者尺寸不匹配
   - 导致SVG内容被平移/缩放到错误位置

2. **CSS width:100% 与viewBox的交互问题**
   - SVG CSS设置为`width: 100%; height: 100%`
   - 可能导致viewBox坐标系统被扭曲

3. **坐标转换的scale计算可能有误**
   - `scale = containerWidth / viewBox.w`
   - 这个公式假设viewBox.x=0，但实际可能不是

**下一步调试方向**：
1. 在浏览器控制台运行以下命令收集信息：
   ```javascript
   debugTimelineMarkers()  // 查看显示了多少个标记，年份范围
   debugYearCoordinates(-221)  // 查看秦始皇即位年份的坐标
   console.log('viewBox:', viewBox)
   console.log('svgTotalW:', window.svgTotalW)
   console.log('data.meta.x_range:', data.meta.x_range)

   // 检查SVG实际的viewBox属性
   document.getElementById('metroSvg').getAttribute('viewBox')
   ```

2. 检查SVG grid line的实际位置：
   ```javascript
   // 找到年份-221的grid line
   const lines = document.querySelectorAll('.year-grid');
   Array.from(lines).forEach(line => {
     const x1 = parseFloat(line.getAttribute('x1'));
     console.log('Grid line at x1:', x1);
   });
   ```

3. 可能需要的修复方向：
   - 确保viewBox始终从(0, 0)开始
   - 或者修改坐标转换函数，考虑viewBox.x的偏移
   - 彻底检查SVG渲染流程

**优先级**：🔴 高（核心功能不可用）

---

## ⚠️ 次要问题

### Bug #2: 时间轴标记数量不符合预期

**症状**：
- 用户期望显示约10个时间刻度
- 实际显示的标记数量不确定（可能很少）

**相关代码**：
- [metro.js:780-788](metro.js#L780-L788) - 智能稀疏化逻辑

**当前实现**：
```javascript
const maxLabels = Math.min(Math.max(displayTicks.length, 8), 20);
```

**预期行为**：
- zoom out（显示整个时间轴）：显示8-12个标记
- zoom in（显示局部）：显示15-20个标记
- 智能调整，避免过密或过疏

**优先级**：⚠️ 中（影响用户体验）

---

## 📝 架构改进

### 已完成的重构

✅ **三层坐标系统架构** ([TIMELINE_ALIGNMENT_SPEC.md](TIMELINE_ALIGNMENT_SPEC.md))
- Layer 1→2: `yearToSvgX(year)` - 年份→SVG坐标
- Layer 2→3: `svgToScreenX(svgX)` - SVG坐标→屏幕坐标
- Layer 1→3: `yearToScreenX(year)` - 年份→屏幕坐标（组合）

✅ **验证和调试工具**
- `validateTimelineAlignment()` - 自动验证对齐状态
- `debugYearCoordinates(year)` - 显示坐标转换详情
- `debugTimelineMarkers()` - 显示当前标记信息

✅ **文档**
- [TIMELINE_ALIGNMENT_SPEC.md](TIMELINE_ALIGNMENT_SPEC.md) - 完整的架构规范
- [ALIGNMENT_CHECKLIST.md](ALIGNMENT_CHECKLIST.md) - 实现检查清单

### 待优化

❌ **SVG viewBox初始化流程**
- 当前：初始viewBox硬编码为{x:0, y:0, w:2000, h:1000}，与实际内容不匹配
- 理想：render()时立即设置正确的viewBox尺寸

❌ **坐标系统一致性**
- 需要确保SVG内容坐标系统与viewBox完全匹配
- 可能需要强制viewBox.x=0, viewBox.y=0

---

## 🔧 开发工具

### 浏览器控制台命令

```javascript
// 验证对齐
validateTimelineAlignment()

// 查看特定年份坐标
debugYearCoordinates(-221)  // 秦始皇即位
debugYearCoordinates(-206)  // 项羽灭秦
debugYearCoordinates(-202)  // 刘邦称帝

// 查看当前标记
debugTimelineMarkers()

// 查看全局状态
console.log('viewBox:', viewBox)
console.log('svgTotalW:', window.svgTotalW)
console.log('svgTotalH:', window.svgTotalH)
console.log('data.meta.x_range:', data.meta.x_range)

// 检查SVG元素
const svg = document.getElementById('metroSvg');
console.log('SVG viewBox attr:', svg.getAttribute('viewBox'));
console.log('SVG rect:', svg.getBoundingClientRect());
```

---

## 📊 测试场景

### 需要验证的场景

1. **初始加载**
   - [ ] 视图居中在-221 BC
   - [ ] 时间轴与事件完全对齐
   - [ ] 显示8-12个时间刻度

2. **Zoom in**
   - [ ] 时间轴标记跟随网格线同步放大
   - [ ] 保持完全对齐
   - [ ] 标记数量增加（更详细）

3. **Zoom out**
   - [ ] 时间轴标记跟随网格线同步缩小
   - [ ] 保持完全对齐
   - [ ] 标记数量减少（智能稀疏化）

4. **Pan**
   - [ ] 时间轴和网格线同步移动
   - [ ] 新标记出现时立即对齐

5. **选择不同线路**
   - [ ] render()后仍然对齐
   - [ ] 时间刻度适应新的事件分布

---

## 📅 工作日志

### 2026-03-25

**目标**：修复时间轴对齐问题

**完成**：
1. ✅ 编写完整的架构规范文档
2. ✅ 重构坐标转换函数为三层架构
3. ✅ 实现验证和调试工具
4. ✅ 创建检查清单文档

**发现的问题**：
- 代码逻辑上对齐（验证通过）
- 但实际渲染不对齐
- 根本原因可能在SVG viewBox设置

**待解决**：
- 需要深入调试SVG渲染流程
- 可能需要重新设计viewBox初始化逻辑
- 确保SVG坐标系统与viewBox完全一致

**下次继续**：
1. 收集详细调试信息（debugTimelineMarkers, debugYearCoordinates）
2. 检查SVG grid line实际位置
3. 验证viewBox映射关系
4. 找到根本原因并修复
