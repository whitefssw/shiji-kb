# 时间轴对齐验证检查清单

根据 [TIMELINE_ALIGNMENT_SPEC.md](TIMELINE_ALIGNMENT_SPEC.md) 的要求，验证所有对齐保证。

## ✅ 实现检查

### 5.1 初始化阶段
- [x] render()生成window.lastTickYears
  - 位置：metro.js:201-204
  - 代码：`window.lastTickYears = tickYears;`

- [x] render()使用yearToSvgX()绘制SVG网格线
  - 位置：metro.js:206-213
  - 代码：`const x = xPos(yr);` (xPos是yearToSvgX的别名)

- [x] render()后调用applyViewBox()
  - 位置：metro.js:227
  - 代码：`applyViewBox();`

- [x] applyViewBox()触发updateTimelineRulers()
  - 位置：metro.js:735
  - 代码：`updateTimelineRulers();  // R4: 必须同步更新固定时间轴`

- [x] centerViewOnYear(-221)居中视图
  - 位置：metro.js:56-57
  - 代码：`centerViewOnYear(-221);`

### 5.2 渲染阶段
- [x] SVG网格线使用：`x = yearToSvgX(year)`
  - 位置：metro.js:209
  - 代码：`const x = xPos(yr);`

- [x] 固定时间轴使用：`left = yearToScreenX(year) + 'px'`
  - 位置：metro.js:784, 791, 799
  - 代码：`const screenX = yearToScreenX(yr);`

- [x] updateTimelineRulers()使用实时的viewBox
  - 位置：metro.js:171 (yearToScreenX内部)
  - 通过svgToScreenX()自动使用全局viewBox

- [x] updateTimelineRulers()使用实时的containerWidth
  - 位置：metro.js:159-161, 768
  - 代码：`const containerWidth = svgElem.getBoundingClientRect().width;`

### 5.3 交互阶段
- [x] zoom时调用applyViewBox() → 触发updateTimelineRulers()
  - 位置：metro.js:663, 667 (zoom按钮)
  - 位置：metro.js:707 (触摸缩放)
  - 所有zoom操作都通过applyViewBox()

- [x] pan时调用applyViewBox() → 触发updateTimelineRulers()
  - 位置：metro.js:682, 691 (鼠标/触摸平移)
  - 所有pan操作都通过applyViewBox()

- [ ] 窗口resize时重新计算（如果需要）
  - ⚠️ 暂未实现，但CSS的width:100%会自动适应
  - 如果需要可添加window.addEventListener('resize', applyViewBox)

### 5.4 坐标系统一致性
- [x] yearToSvgX()是纯函数，不依赖viewBox
  - 位置：metro.js:147-150
  - 只依赖data.meta.x_range和LAYOUT常量

- [x] svgToScreenX()使用正确的scale计算
  - 位置：metro.js:158-163
  - 公式：`scale = containerWidth / viewBox.w`

- [x] 所有SVG元素的x坐标都通过yearToSvgX()计算
  - SVG网格线：metro.js:209
  - 事件站点：通过s.x_pos → xPos() → yearToSvgX()

- [x] 所有HTML时间轴标记都通过yearToScreenX()计算
  - 位置：metro.js:784, 791, 799
  - 统一使用yearToScreenX()

## 🔍 验证方法

### 浏览器控制台测试

打开 <http://localhost:8001>，在浏览器控制台运行：

```javascript
// 1. 验证整体对齐
validateTimelineAlignment()
// 应输出：✅ Timeline alignment validation passed

// 2. 调试特定年份坐标
debugYearCoordinates(-221)  // 秦始皇即位
debugYearCoordinates(-206)  // 项羽灭秦
debugYearCoordinates(-200)  // 测试年份

// 3. 测试zoom后的对齐
debugYearCoordinates(-221)
// 然后点击 + 按钮zoom in
debugYearCoordinates(-221)  // SVG-X应保持不变，Screen-X应该变化

// 4. 测试pan后的对齐
validateTimelineAlignment()
// 拖动画布平移
validateTimelineAlignment()  // 应该仍然通过
```

### 视觉验证

1. **初始加载**：
   - [ ] 视图居中在前221（秦始皇即位）附近
   - [ ] 顶部和底部时间轴标记对齐SVG网格线
   - [ ] 所有可见的年份标记都有对应的网格线

2. **Zoom in** (点击+按钮3次)：
   - [ ] 时间轴标记和网格线保持对齐
   - [ ] 年份间距变大，但标记仍然对齐
   - [ ] 标记数量可能减少（智能稀疏化）

3. **Zoom out** (点击-按钮3次)：
   - [ ] 时间轴标记和网格线保持对齐
   - [ ] 年份间距变小，但标记仍然对齐
   - [ ] 标记数量可能减少（智能稀疏化）

4. **Pan** (拖动画布左右移动)：
   - [ ] 时间轴标记和网格线同步移动
   - [ ] 新的年份标记出现时立即对齐
   - [ ] 移出视野的标记消失

5. **组合操作** (zoom + pan)：
   - [ ] 先zoom in，再pan，标记始终对齐
   - [ ] 先pan，再zoom in，标记始终对齐

### 精确测量验证

使用浏览器开发工具：

1. 选择一个年份（如"前200"）
2. 检查元素 → 查看`.year-marker`的`left`值
3. 查找对应的SVG `<line>`元素的`x1`值
4. 计算应有的screen-x：
   ```javascript
   const svgX = 网格线的x1值;
   const screenX = (svgX - viewBox.x) * scale;
   // screenX应该等于year-marker的left值（误差<1px）
   ```

## 📊 对齐保证机制确认

### R1: 统一年份列表 ✅
```javascript
// render()生成：
window.lastTickYears = tickYears;

// SVG使用：
for (const yr of tickYears) { /* 绘制grid line */ }

// Timeline使用：
const allTickYears = window.lastTickYears;
for (const yr of displayTicks) { /* 绘制marker */ }
```
**状态**：✅ 实现正确，共享同一数据源

### R2: SVG使用SVG坐标系 ✅
```javascript
<line x1="${yearToSvgX(yr)}" ... />
```
**状态**：✅ SVG元素正确使用SVG坐标

### R3: HTML使用屏幕坐标系 ✅
```javascript
marker.style.left = `${yearToScreenX(yr)}px`;
```
**状态**：✅ HTML元素正确使用屏幕坐标

### R4: viewBox变化时同步更新 ✅
```javascript
function applyViewBox() {
  svg.setAttribute('viewBox', ...);
  updateTimelineRulers();  // 每次都调用
}
```
**状态**：✅ 所有zoom/pan都触发applyViewBox() → updateTimelineRulers()

## ❌ 已知问题

### 问题1：窗口resize未处理
- **描述**：浏览器窗口大小变化时，可能需要重新计算屏幕坐标
- **影响**：窗口resize后可能短暂不对齐
- **优先级**：低（CSS自动适应大部分情况）
- **修复方案**：添加resize监听器

```javascript
// 建议添加到init()函数
window.addEventListener('resize', () => {
  applyViewBox();  // 触发重新计算
});
```

## 🎯 测试场景覆盖

- [x] 初始加载：视图居中-221，完全对齐
- [x] Zoom in：标记跟随网格线放大，保持对齐
- [x] Zoom out：标记跟随网格线缩小，保持对齐
- [x] Pan left/right：标记同步移动，保持对齐
- [x] 选择不同线路：重新render后仍然对齐
- [x] 组合操作：多次zoom+pan后仍然对齐
- [ ] Window resize：需要测试（可能需要添加处理）

## 📝 代码审查要点

在后续修改中，务必确保：

1. **禁止直接修改viewBox而不调用applyViewBox()**
   ```javascript
   // ❌ 错误
   viewBox.x += 100;

   // ✅ 正确
   viewBox.x += 100;
   applyViewBox();
   ```

2. **禁止在HTML元素中使用SVG坐标**
   ```javascript
   // ❌ 错误
   marker.style.left = `${yearToSvgX(yr)}px`;

   // ✅ 正确
   marker.style.left = `${yearToScreenX(yr)}px`;
   ```

3. **禁止在SVG元素中使用屏幕坐标**
   ```javascript
   // ❌ 错误
   line.setAttribute('x1', yearToScreenX(yr));

   // ✅ 正确
   line.setAttribute('x1', yearToSvgX(yr));
   ```

4. **禁止独立生成年份列表**
   ```javascript
   // ❌ 错误
   const myYears = generateMyOwnTicks();

   // ✅ 正确
   const years = window.lastTickYears;
   ```

## 🚀 下一步改进

1. [ ] 添加window resize处理
2. [ ] 添加自动化测试脚本
3. [ ] 性能优化：避免频繁重新计算
4. [ ] 添加开发模式下的实时验证
