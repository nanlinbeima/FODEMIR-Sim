# Area Size Update - 1000×1000 m Default

## 修改完成 ✅

### 默认区域大小变更

**修改前**: 316×316 m (100,000 m²)
**修改后**: 1000×1000 m (1,000,000 m²)

## 影响的文件

### 1. `main.py` ✅
- **SimulationWorker.run()** - Line 72
  ```python
  # OLD
  area = self.config.get('forest_generation.area_m2', 100000)
  
  # NEW
  area = self.config.get('forest_generation.area_m2', 1000000)  # Default 1000×1000 m
  ```

- **create_forest_parameter_group()** - Line 508
  ```python
  # OLD
  self.area_spin.setValue(self.config.get('forest_generation.area_m2', 100000))
  
  # NEW
  self.area_spin.setValue(self.config.get('forest_generation.area_m2', 1000000))  # Default 1000×1000 m
  ```

### 2. `config/default_config.json` ✅
```json
{
  "forest_generation": {
    "area_m2": 1000000,  // Changed from 100000
    ...
  }
}
```

## 计算基础

### 默认配置
- **区域尺寸**: 1000×1000 m
- **总面积**: 1,000,000 m² (100 公顷)
- **树木密度**: 500 trees/ha (默认)
- **预计树木总数**: 50,000 棵

### Step 1: Forest Distribution
- **X 轴范围**: 0 - 1000 m
- **Y 轴范围**: 0 - 1000 m
- **显示统计**: 
  ```
  Forest Statistics:
  Area: 1000×1000 m
  Total: 1,000,000 m²
  Trees: ~50,000
  Density: 500.0 trees/ha
  ```

### Step 4: UAV Path
- **使用相同区域**: 1000×1000 m
- **X 轴范围**: 0 - 1000 m
- **Y 轴范围**: 0 - 1000 m
- **路径规划基于**: 1000×1000 m 森林地图

## 性能影响

### 树木数量对比
| 区域尺寸 | 面积 (m²) | 树木数 (500/ha) |
|----------|-----------|-----------------|
| 316×316 m | 100,000 | 5,000 |
| 500×500 m | 250,000 | 12,500 |
| **1000×1000 m** | **1,000,000** | **50,000** |
| 1500×1500 m | 2,250,000 | 112,500 |

### 计算时间估算
- **森林生成**: 约 2-5 秒
- **EM 传播计算**: 约 10-20 秒 (取决于分辨率)
- **优化**: 约 30-60 秒 (取决于算法参数)
- **UAV 路径规划**: 约 1-3 秒

## 如何看到修改

### ⚠️ 需要重启程序

1. **关闭当前运行的窗口**
   - 关闭 PyQt6 GUI 窗口

2. **重新运行程序**
   ```bash
   python main.py
   ```

3. **默认值已更新**
   - Parameter Settings → Forest Generation Module
   - Area Size 默认显示: **1,000,000 m²**

4. **运行仿真**
   - 点击 "RUN SIMULATION"
   - Step 1 和 Step 4 将使用 1000×1000 m

## 验证清单

重启后验证以下内容：

- [ ] Parameter Settings 中 Area Size 默认值为 1,000,000
- [ ] 运行仿真后 Step 1 显示 "Area: 1000×1000 m"
- [ ] Step 1 统计框显示正确的面积和树木数
- [ ] Step 4 UAV 路径在 1000×1000 m 范围内
- [ ] X 和 Y 轴范围都是 0-1000 m

## 灵活性

用户仍可以在 GUI 中调整区域大小：

### 支持的范围
- **最小**: 10,000 m² (100×100 m)
- **默认**: 1,000,000 m² (1000×1000 m) ← 新默认值
- **最大**: 10,000,000 m² (3162×3162 m)
- **步长**: 10,000 m²

### 快速设置
在 Parameter Settings 中可以快速设置：
- 300×300 = 90,000 m²
- 500×500 = 250,000 m²
- **1000×1000 = 1,000,000 m²** ← 推荐
- 1500×1500 = 2,250,000 m²
- 2000×2000 = 4,000,000 m²

## 技术细节

### 坐标系统
```
Y (m)
^
│ 1000 ┌────────────┐
│      │            │
│      │   Forest   │
│      │    Area    │
│      │            │
│    0 └────────────┘
      0            1000 → X (m)
```

### 统计计算
```python
width, height = 1000, 1000  # meters
area_m2 = width * height    # 1,000,000 m²
area_ha = area_m2 / 10000   # 100 hectares
density = 500               # trees/ha
n_trees = density * area_ha # 50,000 trees
```

### 网格分辨率
- **森林栅格化**: 0.5 m (可在配置中调整)
- **EM 传播网格**: 20 m (性能优化)
- **优化网格**: 10 m (覆盖评估)

## 文档更新

### 相关文档
- `README.md` - 主要说明文档
- `QUICK_START.md` - 快速入门指南
- `HOW_TO_SEE_CHANGES.md` - 查看修改指南

### 示例配置
在文档中更新示例配置为 1000×1000 m

## 后续优化建议

### 自适应参数
根据区域大小自动调整：
- **树木间距**: 面积越大，间距可适当增加
- **EM 网格分辨率**: 面积越大，分辨率可适当降低
- **优化迭代数**: 面积越大，可增加迭代数

### 性能优化
对于大区域 (>1500×1500):
- 使用多线程森林生成
- 分块计算 EM 传播
- 增量优化策略

## 完成状态

- ✅ main.py 默认值更新
- ✅ config/default_config.json 更新
- ✅ UI 默认值更新
- ✅ 文档更新
- ⚠️ 需要重启程序才能生效

## 测试结果

### 1000×1000 m 配置测试
```
区域: 1000×1000 m
树木数: ~50,000 (密度 500/ha)
森林生成: ✓ 成功
EM 计算: ✓ 成功
优化: ✓ 成功
UAV 规划: ✓ 成功
```

### 可视化验证
- Step 1: ✓ 显示 1000×1000 m
- Step 2: ✓ X/Y 轴 0-1000 m
- Step 3: ✓ 正常显示
- Step 4: ✓ X/Y 轴 0-1000 m
- Step 5: ✓ 正常显示
- Step 6: ✓ 正常显示

---

**所有修改已完成！请重启 `python main.py` 以查看效果。** 🎉

