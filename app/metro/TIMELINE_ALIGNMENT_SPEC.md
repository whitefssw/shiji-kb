# 史记地铁图 - 时间轴对齐架构规范

## 1. 核心需求

### 1.1 对齐要求
1. **SVG网格线和固定时间轴必须完全对齐**
   - SVG中的垂直年份网格线（year-grid）
   - 顶部固定时间轴（timeline-top）
   - 底部固定时间轴（timeline-bottom）
   - 三者在任何缩放/平移状态下，相同年份的标记必须在屏幕上的同一x坐标

2. **缩放时保持对齐**
   - zoom in/out时，时间轴标记必须跟随SVG网格线同步移动
   - 无论viewBox如何变化，年份→屏幕x坐标的映射必须一致

3. **平移时保持对齐**
   - pan时，时间轴标记必须跟随SVG网格线同步移动
   - 固定时间轴只显示当前可见区域内的年份标记

### 1.2 视图居中要求
- 初始加载时，视图应居中在-221 BC（秦始皇即位）
- 居中计算应基于年份→SVG坐标的映射

## 2. 坐标系统设计

### 2.1 三层坐标系

```
逻辑年份 → SVG坐标 → 屏幕坐标
  (Year)    (SVG-X)    (Screen-X)
```

#### Layer 1: 逻辑年份 (Year)
- 表示：公元前年份（负数），如 -221, -206
- 范围：data.meta.x_range = [-2698, -29]

#### Layer 2: SVG坐标 (SVG-X)
- SVG的内部逻辑坐标系统
- 由viewBox定义：viewBox = "x y width height"
- 转换公式：`svgX = PADDING_LEFT + (year - xMin) * xScale`
- 独立于屏幕显示尺寸

#### Layer 3: 屏幕坐标 (Screen-X)
- 浏览器窗口中的实际像素坐标
- 受viewBox和容器尺寸共同影响
- 转换公式：`screenX = (svgX - viewBox.x) * scale`
- 其中：`scale = containerWidth / viewBox.w`

### 2.2 关键参数

```javascript
// 常量
const LAYOUT = {
  padding: { left: 120, right: 40, top: 40 },  // SVG边距
  xScale: 1.6,                                  // 年份到SVG单位的比例
  lineSpacing: 28                               // 线路间距
};

// 数据范围
const [xMin, xMax] = data.meta.x_range;  // [-2698, -29]

// SVG总尺寸（逻辑尺寸）
const svgTotalW = LAYOUT.padding.left + LAYOUT.padding.right + (xMax - xMin) * LAYOUT.xScale;
const svgTotalH = LAYOUT.padding.top + lines.length * LAYOUT.lineSpacing + 60;

// 当前视口（viewBox）
let viewBox = {
  x: 0,      // 当前视口左边缘的SVG x坐标
  y: 0,      // 当前视口顶部的SVG y坐标
  w: 2000,   // 视口宽度（SVG单位）
  h: 1000    // 视口高度（SVG单位）
};
```

## 3. 核心转换函数

### 3.1 年份 → SVG坐标

```javascript
/**
 * 将年份转换为SVG x坐标
 * @param {number} year - 年份（负数表示公元前）
 * @returns {number} SVG x坐标
 */
function yearToSvgX(year) {
  const [xMin] = data.meta.x_range;
  return LAYOUT.padding.left + (year - xMin) * LAYOUT.xScale;
}
```

**要求**：
- 必须是纯函数，只依赖输入参数和常量
- 不受viewBox影响
- 线性映射，确保年份间距比例一致

### 3.2 SVG坐标 → 屏幕坐标

```javascript
/**
 * 将SVG坐标转换为屏幕坐标
 * @param {number} svgX - SVG x坐标
 * @param {Object} options - 转换参数
 * @returns {number} 屏幕x坐标（相对于SVG容器左边缘）
 */
function svgToScreenX(svgX, { viewBox, containerWidth }) {
  const scale = containerWidth / viewBox.w;
  return (svgX - viewBox.x) * scale;
}
```

**要求**：
- 必须使用当前viewBox和实际容器宽度
- zoom时scale会变化，但映射关系必须一致
- pan时viewBox.x会变化，屏幕坐标相应调整

### 3.3 年份 → 屏幕坐标（组合）

```javascript
/**
 * 将年份直接转换为屏幕坐标
 * @param {number} year - 年份
 * @returns {number} 屏幕x坐标
 */
function yearToScreenX(year) {
  const svgX = yearToSvgX(year);
  const svgElem = document.getElementById('metroSvg');
  const containerWidth = svgElem.getBoundingClientRect().width;
  return svgToScreenX(svgX, { viewBox, containerWidth });
}
```

## 4. 对齐保证机制

### 4.1 数据层保证

**R1: 使用统一的年份列表**
```javascript
// 在render()中生成，全局共享
window.lastTickYears = [年份列表];

// SVG网格线使用
for (const yr of window.lastTickYears) {
  drawGridLine(yearToSvgX(yr));
}

// 固定时间轴使用
for (const yr of window.lastTickYears) {
  drawTimelineMarker(yearToScreenX(yr));
}
```

**要求**：
- ✅ SVG网格线和固定时间轴必须使用相同的年份列表
- ✅ 确保不会出现"SVG有这条线，但时间轴没有标记"的情况

### 4.2 转换层保证

**R2: SVG网格线使用SVG坐标系**
```javascript
// 正确：SVG元素使用SVG坐标
<line x1="${yearToSvgX(yr)}" ... />
```

**R3: 固定时间轴使用屏幕坐标系**
```javascript
// 正确：HTML div使用屏幕坐标
marker.style.left = `${yearToScreenX(yr)}px`;
```

**要求**：
- ✅ 不能混用坐标系统
- ✅ 转换函数必须使用实时的viewBox和containerWidth

### 4.3 更新层保证

**R4: viewBox变化时必须更新固定时间轴**
```javascript
function applyViewBox() {
  svg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
  updateTimelineRulers();  // 关键！必须同步更新
}
```

**要求**：
- ✅ 每次viewBox变化（zoom/pan）都必须调用updateTimelineRulers()
- ✅ updateTimelineRulers()必须重新计算所有标记的屏幕坐标

## 5. 实现检查清单

### 5.1 初始化阶段
- [ ] render()生成window.lastTickYears
- [ ] render()使用yearToSvgX()绘制SVG网格线
- [ ] render()后调用applyViewBox()
- [ ] applyViewBox()触发updateTimelineRulers()
- [ ] centerViewOnYear(-221)居中视图

### 5.2 渲染阶段
- [ ] SVG网格线使用：`x = yearToSvgX(year)`
- [ ] 固定时间轴使用：`left = yearToScreenX(year) + 'px'`
- [ ] updateTimelineRulers()使用实时的viewBox
- [ ] updateTimelineRulers()使用实时的containerWidth

### 5.3 交互阶段
- [ ] zoom时调用applyViewBox() → 触发updateTimelineRulers()
- [ ] pan时调用applyViewBox() → 触发updateTimelineRulers()
- [ ] 窗口resize时重新计算（如果需要）

### 5.4 坐标系统一致性
- [ ] yearToSvgX()是纯函数，不依赖viewBox
- [ ] svgToScreenX()使用正确的scale计算
- [ ] 所有SVG元素的x坐标都通过yearToSvgX()计算
- [ ] 所有HTML时间轴标记都通过yearToScreenX()计算

## 6. 常见错误模式

### ❌ 错误1：混用坐标系统
```javascript
// 错误：HTML div使用SVG坐标
marker.style.left = `${yearToSvgX(yr)}px`;  // 不对齐！
```

### ❌ 错误2：使用过时的viewBox
```javascript
// 错误：在zoom之后，使用zoom之前的viewBox计算
const scale = oldContainerWidth / oldViewBox.w;
```

### ❌ 错误3：不同的年份列表
```javascript
// 错误：SVG和时间轴使用不同的年份列表
const svgYears = generateTicks1();
const rulerYears = generateTicks2();  // 可能不一致！
```

### ❌ 错误4：忘记更新
```javascript
// 错误：viewBox变化后没有更新固定时间轴
function zoom() {
  viewBox.w *= 0.8;
  applyViewBox();  // 如果这里面不调用updateTimelineRulers()，就不对齐了
}
```

## 7. 测试验证

### 7.1 视觉验证
1. 在浏览器中打开，用尺子（或屏幕截图工具）测量：
   - 选择一个年份标记（如"前200"）
   - 测量其在顶部时间轴的x坐标
   - 测量其对应的SVG网格线的x坐标
   - 两者必须完全重合（误差<1px）

2. Zoom in，再次测量相同年份
   - 位置应该同步移动
   - 仍然完全对齐

3. Pan，再次测量
   - 位置应该同步移动
   - 仍然完全对齐

### 7.2 代码验证
```javascript
// 在控制台运行
const testYear = -200;
const svgX = yearToSvgX(testYear);
const screenX = yearToScreenX(testYear);

console.log(`Year ${testYear}:`);
console.log(`  SVG-X: ${svgX}`);
console.log(`  Screen-X: ${screenX}`);
console.log(`  ViewBox: x=${viewBox.x}, w=${viewBox.w}`);

// 手动检查SVG中是否有x=${svgX}的grid line
// 手动检查HTML中是否有left=${screenX}px的marker
```

### 7.3 自动化验证
```javascript
function validateAlignment() {
  const years = window.lastTickYears;

  for (const yr of years) {
    const svgX = yearToSvgX(yr);
    const screenX = yearToScreenX(yr);

    // 检查SVG网格线
    const gridLine = document.querySelector(`line[x1="${svgX}"]`);
    if (!gridLine) {
      console.error(`Missing grid line for year ${yr} at SVG-X ${svgX}`);
    }

    // 检查时间轴标记
    const marker = Array.from(document.querySelectorAll('.year-marker'))
      .find(m => Math.abs(parseFloat(m.style.left) - screenX) < 1);
    if (!marker) {
      console.error(`Missing timeline marker for year ${yr} at Screen-X ${screenX}`);
    }
  }

  console.log('Alignment validation complete');
}
```

## 8. 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     数据层 (Data Layer)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ data.meta.x_range = [-2698, -29]                     │   │
│  │ window.lastTickYears = [-2650, -2600, ..., -50]      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   转换层 (Transform Layer)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ yearToSvgX(year) → svgX                              │   │
│  │   = PADDING_LEFT + (year - xMin) * xScale            │   │
│  │                                                       │   │
│  │ svgToScreenX(svgX, {viewBox, containerWidth})        │   │
│  │   = (svgX - viewBox.x) * (containerWidth / viewBox.w)│   │
│  │                                                       │   │
│  │ yearToScreenX(year) = svgToScreenX(yearToSvgX(year)) │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    渲染层 (Render Layer)                     │
│  ┌─────────────────────┐         ┌──────────────────────┐   │
│  │   SVG网格线          │         │  固定时间轴 (HTML)    │   │
│  │ ────────────────── │         │ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼    │   │
│  │ <line x1="{svgX}"/> │         │ <div left="{screenX}">│   │
│  │                     │         │                      │   │
│  │ 使用SVG坐标         │         │ 使用屏幕坐标          │   │
│  └─────────────────────┘         └──────────────────────┘   │
│            ↓                                ↓                │
│       applyViewBox() ─────────→ updateTimelineRulers()      │
│       (viewBox变化时)            (同步更新屏幕坐标)           │
└─────────────────────────────────────────────────────────────┘
```

## 9. 下一步行动

1. 重构现有代码，明确分离三层坐标转换函数
2. 确保所有对齐要求都有对应的代码检查点
3. 添加验证函数，在开发模式下自动检查对齐
4. 测试所有交互场景（zoom/pan/resize）
