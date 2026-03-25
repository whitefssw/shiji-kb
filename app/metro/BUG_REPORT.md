# 时间轴对齐问题 - Bug报告

**日期**: 2026-03-25
**状态**: 🔴 未解决
**优先级**: P0 - 关键功能缺陷

## 问题描述

史记地铁图的固定时间轴（顶部和底部）与SVG网格线**视觉上不对齐**，尽管代码验证显示逻辑是正确的。

### 症状

1. **主要问题**：时间轴刻度与SVG事件位置严重不对应
   - 顶部时间轴显示："前2650、前2500、前2350、前2200..."
   - 秦始皇本纪（黄色线，应该在前259到前210范围）却显示在画面右侧中间位置
   - 视觉上完全不匹配

2. **次要问题**：时间轴标记数量少
   - 预期显示10-20个时间刻度
   - 实际只显示很少的标记（具体数量未确认）

### 验证结果

控制台运行`validateTimelineAlignment()`显示：
```
✅ Timeline alignment validation passed
All 36 visible markers are correctly aligned
```

**矛盾点**：验证通过，但视觉上明显不对齐！

## 已完成的工作

### 1. 架构重构 ✅

创建了清晰的三层坐标系统架构：

- **文档**：
  - [TIMELINE_ALIGNMENT_SPEC.md](TIMELINE_ALIGNMENT_SPEC.md) - 完整的架构规范
  - [ALIGNMENT_CHECKLIST.md](ALIGNMENT_CHECKLIST.md) - 实现检查清单

- **代码重构**：
  - `yearToSvgX(year)` - Year → SVG坐标转换（纯函数）
  - `svgToScreenX(svgX)` - SVG坐标 → 屏幕坐标转换
  - `yearToScreenX(year)` - Year → 屏幕坐标（组合函数）

- **验证工具**：
  - `validateTimelineAlignment()` - 自动验证对齐状态
  - `debugYearCoordinates(year)` - 显示指定年份的坐标转换
  - `debugTimelineMarkers()` - 显示当前所有时间轴标记

### 2. 尝试的修复方案

#### 修复1: 移除adaptive timeline ✅
- **问题**：自适应时间轴在zoom/pan时不重新计算，导致不同步
- **方案**：改用简单的线性比例尺
- **结果**：简化了逻辑，但未解决对齐问题

#### 修复2: 移除SVG width/height属性 ✅
- **问题**：SVG同时设置了width/height和viewBox，导致坐标系混乱
- **方案**：只使用viewBox控制，移除width/height设置
- **代码**：`window.svgTotalW` 存储逻辑尺寸
- **结果**：未解决问题

#### 修复3: 修改preserveAspectRatio ✅
- **问题**：`preserveAspectRatio="xMidYMid meet"`可能导致缩放
- **方案**：改为`preserveAspectRatio="none"`
- **文件**：index.html:27
- **结果**：未解决问题

#### 修复4: 初始化viewBox尺寸 ✅
- **问题**：初始viewBox `{w: 2000, h: 1000}` 与实际SVG内容尺寸不匹配
- **方案**：在render()中自动初始化viewBox为正确尺寸
- **代码**：
  ```javascript
  if (viewBox.w === 2000 && viewBox.h === 1000) {
    viewBox.w = totalW;  // ~4430
    viewBox.h = totalH;
  }
  ```
- **结果**：未解决问题

#### 修复5: 调整初始化流程 ✅
- **方案**：render() → fitView() → centerViewOnYear(-221)
- **目的**：确保viewBox正确初始化后再居中
- **结果**：未解决问题

#### 修复6: 改进验证函数 ✅
- **问题**：旧验证函数期望所有年份都有marker，产生大量误报
- **方案**：改为正向检查 - 验证实际显示的marker是否对齐
- **结果**：验证通过，但仍不对齐

#### 修复7: 调整标签稀疏化 ✅
- **方案**：动态调整maxLabels（8-20个）
- **代码**：`const maxLabels = Math.min(Math.max(displayTicks.length, 8), 20);`
- **结果**：未解决问题

## 问题分析

### 关键矛盾

1. **代码验证通过**：`validateTimelineAlignment()` 检查所有显示的marker，确认：
   - 每个marker的screen-X与`yearToScreenX(year)`计算值匹配（误差<2px）
   - 每个marker对应的grid line存在且位置正确

2. **视觉上不对齐**：用户看到的时间轴与事件位置完全不匹配

### 可能的原因

#### 假设1: SVG坐标系统错位
- **描述**：SVG的viewBox映射不正确，导致整个SVG内容被错误地平移或缩放
- **证据**：秦始皇本纪（-259到-210）应该在画面中间偏左，却显示在右侧
- **待验证**：
  ```javascript
  debugYearCoordinates(-221)  // 秦始皇即位
  debugYearCoordinates(-259)  // 秦始皇出生
  ```

#### 假设2: 固定时间轴的定位错误
- **描述**：HTML的timeline-ruler容器相对于SVG容器有偏移
- **待验证**：检查CSS中`.timeline-ruler`和`svg`的定位

#### 假设3: 多个viewBox冲突
- **描述**：HTML中硬编码的viewBox与JavaScript设置的viewBox冲突
- **状态**：已移除HTML中的硬编码viewBox，但问题仍存在

#### 假设4: 坐标转换函数错误
- **描述**：yearToSvgX()或svgToScreenX()的计算有误
- **反证**：验证函数通过，说明转换逻辑自洽
- **但**：可能整体映射方向或基准点错误

## 调试信息需求

为了继续诊断，需要收集以下信息：

### 1. 当前状态快照
```javascript
// 在浏览器控制台运行
console.log('=== SVG总尺寸 ===');
console.log('svgTotalW:', window.svgTotalW);
console.log('svgTotalH:', window.svgTotalH);

console.log('\n=== ViewBox ===');
console.log('viewBox:', viewBox);

console.log('\n=== SVG元素 ===');
const svg = document.getElementById('metroSvg');
console.log('viewBox attribute:', svg.getAttribute('viewBox'));
console.log('getBoundingClientRect:', svg.getBoundingClientRect());

console.log('\n=== 数据范围 ===');
console.log('x_range:', data.meta.x_range);

console.log('\n=== 时间轴标记 ===');
debugTimelineMarkers();

console.log('\n=== 关键年份坐标 ===');
debugYearCoordinates(-2698);  // xMin
debugYearCoordinates(-221);   // 秦始皇即位
debugYearCoordinates(-29);    // xMax
```

### 2. 视觉对比检查

- 截图标注：标出顶部时间轴的"前221"位置
- 测量：秦始皇本纪的"即位"事件在屏幕上的x坐标
- 对比：两者是否在同一垂直线上

### 3. 网格线检查
```javascript
// 检查实际的SVG网格线
const gridLines = document.querySelectorAll('.year-grid');
console.log(`Total grid lines: ${gridLines.length}`);

// 找前221的grid line
const target = yearToSvgX(-221);
let found = false;
gridLines.forEach(line => {
  const x1 = parseFloat(line.getAttribute('x1'));
  if (Math.abs(x1 - target) < 1) {
    console.log(`Found grid line for -221 at SVG-X ${x1}`);
    found = true;
  }
});
if (!found) {
  console.log(`No grid line found at expected SVG-X ${target}`);
}
```

## 下一步行动计划

### 优先级1: 收集调试信息
1. 运行上述所有调试命令
2. 截图当前显示状态，标注关键年份
3. 记录所有输出到文档

### 优先级2: 根本原因诊断

基于调试信息，检查以下假设：

1. **检查SVG viewBox是否正确设置**
   - 预期：viewBox应该覆盖整个SVG内容范围
   - 验证：viewBox.x 应该=0，viewBox.w 应该≈svgTotalW

2. **检查坐标基准点**
   - yearToSvgX(-2698)应该 ≈ 120（padding.left）
   - yearToSvgX(-29)应该 ≈ svgTotalW - padding.right

3. **检查屏幕坐标映射**
   - yearToScreenX(-2698)应该在屏幕左边缘附近
   - yearToScreenX(-29)应该在屏幕右边缘附近

### 优先级3: 可能的修复方案

如果发现viewBox问题：
- 确保render()后viewBox完全覆盖SVG内容
- 检查fitView()和centerViewOnYear()的调用顺序

如果发现坐标转换问题：
- 重新审查yearToSvgX()的计算公式
- 检查是否需要考虑SVG的padding

如果发现CSS定位问题：
- 检查`.timeline-ruler`是否相对于正确的容器定位
- 确认SVG容器没有额外的margin/padding

## 临时解决方案

在问题修复前，可以考虑：

1. **禁用固定时间轴**：注释掉timeline-ruler元素，先确保SVG内容本身正确
2. **回退到简单版本**：暂时移除centerViewOnYear()，使用默认fitView()
3. **添加视觉辅助**：在SVG中绘制年份标签，验证SVG内部坐标是否正确

## 相关文件

- **核心代码**：
  - `app/metro/metro.js` - 主要逻辑
  - `app/metro/index.html` - SVG容器定义
  - `app/metro/metro.css` - 样式定义

- **文档**：
  - `app/metro/TIMELINE_ALIGNMENT_SPEC.md` - 架构规范
  - `app/metro/ALIGNMENT_CHECKLIST.md` - 检查清单
  - `app/metro/BUG_REPORT.md` - 本文档

## 已知限制

- Window resize未处理（低优先级）
- 智能稀疏化可能需要优化（中优先级）

## 联系与参考

- 项目约定：见 `CLAUDE.md`
- Git提交不使用自动commit，只提交已暂存文件
- 对话语言：中文

---

**最后更新**: 2026-03-25
**下次处理时间**: 待定
**预计工作量**: 2-4小时（需要详细调试）
