# 史记地铁图 - 自适应时间轴解决方案

## 问题描述

当前使用线性时间轴，导致：
- 公元前206年（项羽灭秦）在视觉上离公元前50年很近
- 事件密集的时期（战国、秦汉）被压缩
- 事件稀疏的时期（上古）占据大量空间

## 解决方案：事件密度自适应时间轴

### 核心思想

根据事件密度动态调整时间刻度：
- **事件多的年份** → 时间轴拉长
- **事件少的年份** → 时间轴压缩
- **保持对齐** → 同年事件在所有线路上对齐

### 实现步骤

#### 1. 统计事件密度

```javascript
// 统计每个时间窗口的事件数量
function computeEventDensity(data) {
  const WINDOW_SIZE = 10; // 10年为一个窗口
  const densityMap = new Map();

  for (const line of data.lines) {
    for (const station of line.stations) {
      if (station.year === null) continue;

      const bucket = Math.floor(station.year / WINDOW_SIZE) * WINDOW_SIZE;
      densityMap.set(bucket, (densityMap.get(bucket) || 0) + 1);
    }
  }

  return densityMap;
}
```

#### 2. 计算自适应宽度

```javascript
// 根据密度计算每个时间段的显示宽度
function computeAdaptiveWidths(densityMap) {
  const MIN_WIDTH = 0.3;  // 最小宽度（SVG单位/年）
  const MAX_WIDTH = 3.0;  // 最大宽度
  const BASE_WIDTH = 1.0; // 基准宽度

  // 找到最大密度
  const maxDensity = Math.max(...densityMap.values());

  const widthMap = new Map();

  for (const [bucket, count] of densityMap.entries()) {
    // 密度越高，宽度越大
    const densityRatio = count / maxDensity;
    const width = BASE_WIDTH + (MAX_WIDTH - BASE_WIDTH) * Math.sqrt(densityRatio);
    widthMap.set(bucket, Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, width)));
  }

  // 为没有事件的时间段设置最小宽度
  const [minYear, maxYear] = data.meta.x_range;
  for (let year = minYear; year <= maxYear; year += WINDOW_SIZE) {
    const bucket = Math.floor(year / WINDOW_SIZE) * WINDOW_SIZE;
    if (!widthMap.has(bucket)) {
      widthMap.set(bucket, MIN_WIDTH);
    }
  }

  return widthMap;
}
```

#### 3. 累积位置映射

```javascript
// 建立年份 → x位置的映射
function buildPositionMapping(widthMap) {
  const WINDOW_SIZE = 10;
  const [minYear] = data.meta.x_range;

  const positionMap = new Map();
  let currentX = 0;

  // 按年份顺序累积
  const buckets = Array.from(widthMap.keys()).sort((a, b) => a - b);

  for (const bucket of buckets) {
    const width = widthMap.get(bucket);

    // 该时间窗口内的每一年
    for (let year = bucket; year < bucket + WINDOW_SIZE; year++) {
      positionMap.set(year, currentX);
      currentX += width;
    }
  }

  return positionMap;
}
```

#### 4. 替换原有的 xPos 函数

```javascript
// 原来的线性映射
function xPos_old(val) {
  const [xMin] = data.meta.x_range;
  return LAYOUT.padding.left + (val - xMin) * LAYOUT.xScale;
}

// 新的自适应映射
function xPos(val) {
  if (!window.positionMapping) {
    // 首次调用时初始化
    const density = computeEventDensity(data);
    const widths = computeAdaptiveWidths(density);
    window.positionMapping = buildPositionMapping(widths);
  }

  // 查找最近的映射点
  let mappedX = 0;

  if (window.positionMapping.has(val)) {
    mappedX = window.positionMapping.get(val);
  } else {
    // 线性插值
    const floorYear = Math.floor(val / 10) * 10;
    const ceilYear = floorYear + 10;
    const x1 = window.positionMapping.get(floorYear) || 0;
    const x2 = window.positionMapping.get(ceilYear) || x1;
    const ratio = (val - floorYear) / 10;
    mappedX = x1 + (x2 - x1) * ratio;
  }

  return LAYOUT.padding.left + mappedX;
}
```

#### 5. 更新年份刻度渲染

年份刻度需要显示不均匀的间隔：

```javascript
// 修改 render() 中的年份刻度生成
const tickG = svgEl('g', { class: 'year-ticks' });

// 不再使用固定间隔，而是根据重要性选择年份
const importantYears = selectImportantYears(data, densityMap);

for (const yr of importantYears) {
  const x = xPos(yr);

  // 垂直网格线
  tickG.appendChild(svgEl('line', {
    x1: x, y1: 0, x2: x, y2: totalH,
    stroke: '#e8e4de', 'stroke-width': 0.5,
    class: 'year-grid', opacity: 0.6
  }));
}

// 辅助函数：选择重要年份显示刻度
function selectImportantYears(data, densityMap) {
  const years = [];
  const [minYear, maxYear] = data.meta.x_range;

  // 标准刻度年份（50年间隔）
  for (let yr = Math.ceil(minYear / 50) * 50; yr <= maxYear; yr += 50) {
    years.push(yr);
  }

  // 添加高密度时期的额外刻度（10年间隔）
  const highDensityThreshold = Math.max(...densityMap.values()) * 0.3;

  for (const [bucket, density] of densityMap.entries()) {
    if (density > highDensityThreshold) {
      // 在高密度区域添加更密集的刻度
      for (let yr = bucket; yr < bucket + 50; yr += 10) {
        if (!years.includes(yr)) {
          years.push(yr);
        }
      }
    }
  }

  return years.sort((a, b) => a - b);
}
```

### 视觉优化

#### 1. 时间刻度标注

在固定时间条中显示刻度间隔：

```javascript
// 更新 updateTimelineRulers()
function updateTimelineRulers() {
  // ... 现有代码 ...

  for (let i = 0; i < importantYears.length - 1; i++) {
    const yr = importantYears[i];
    const nextYr = importantYears[i + 1];
    const interval = nextYr - yr;

    const svgX = xPos(yr);
    const screenX = (svgX - viewBox.x) * scale;

    const marker = document.createElement('div');
    marker.className = 'year-marker';

    // 显示年份和间隔
    const label = yr < 0 ? `前${-yr}` : `${yr}`;
    const intervalLabel = interval !== 50 ? ` (+${interval})` : '';
    marker.textContent = label + intervalLabel;

    // ... 现有代码 ...
  }
}
```

#### 2. 视觉提示

用颜色区分不同密度的时期：

```css
/* 高密度时期的背景 */
.timeline-dense-period {
  fill: rgba(255, 240, 200, 0.1);
}

/* 低密度时期的背景 */
.timeline-sparse-period {
  fill: rgba(220, 220, 220, 0.05);
}
```

### 预期效果

#### 调整前（线性）
```
前2698 ────────────────────────────────── 前206 ── 前50 ── 220
        ↑ 压缩，难以区分                    ↑ 稀疏
```

#### 调整后（自适应）
```
前2698 ─── 前1600 ──── 前770 ────────────── 前206 ────── 前50 ─ 220
    ↑ 压缩   ↑ 适中     ↑ 展开（战国）  ↑ 展开（秦汉）  ↑ 压缩
```

### 参数调优

```javascript
const CONFIG = {
  WINDOW_SIZE: 10,      // 时间窗口大小（年）
  MIN_WIDTH: 0.3,       // 最小宽度（SVG单位/年）
  MAX_WIDTH: 3.0,       // 最大宽度
  BASE_WIDTH: 1.0,      // 基准宽度
  DENSITY_EXPONENT: 0.5 // 密度影响系数（0.5 = 平方根）
};
```

调整这些参数可以控制：
- `WINDOW_SIZE` 越小 → 更精细的密度控制
- `MAX_WIDTH / MIN_WIDTH` 比值越大 → 密度差异越明显
- `DENSITY_EXPONENT` 越小 → 密度影响越平缓

### 兼容性保证

保持对齐的关键：
```javascript
// ✅ 正确：所有线路使用相同的 xPos() 函数
for (const line of lines) {
  for (const station of line.stations) {
    const x = xPos(station.year);  // 同年份 → 同x坐标
  }
}

// ❌ 错误：每条线路独立计算位置
// 这会导致同年事件在不同线路上的x坐标不同
```

### 实施计划

1. **第一阶段**：添加密度统计代码
2. **第二阶段**：实现自适应宽度计算
3. **第三阶段**：替换 xPos() 函数
4. **第四阶段**：调优参数
5. **第五阶段**：更新时间刻度显示

### 测试用例

验证以下场景：
1. ✅ 项羽灭秦（-206）与汉初（-200~-190）事件间距合理
2. ✅ 战国七雄事件（-475~-221）展开显示
3. ✅ 上古时期（-2698~-1600）压缩但可读
4. ✅ 同年事件在所有线路上垂直对齐
5. ✅ 时间刻度清晰标注间隔变化

---

## 备选方案

如果自适应时间轴太复杂，可以先尝试：

### 简化方案：三段式比例尺

```javascript
function xPos_simple(year) {
  let offset = 0;

  if (year < -1600) {
    // 上古（前2698-前1600）：压缩 0.3倍
    offset = (year + 2698) * 0.3;
  } else if (year < -221) {
    // 商周（前1600-前221）：正常 1倍
    offset = (year + 1600) * 1.0 + ((-1600) + 2698) * 0.3;
  } else {
    // 秦汉（前221-220）：展开 2.5倍
    offset = (year + 221) * 2.5 + ((-221) + 1600) * 1.0 + ((-1600) + 2698) * 0.3;
  }

  return LAYOUT.padding.left + offset;
}
```

这样：
- 上古压缩到原来的30%
- 商周保持不变
- 秦汉展开到250%

---

**最终建议**：先实现简化方案（三段式），测试效果；如果效果好，再考虑完整的自适应方案。
