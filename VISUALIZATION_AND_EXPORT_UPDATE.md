# 可视化与导出功能优化更新

**更新日期**: 2025-10-29

## 📊 本次更新内容

本次更新主要优化了三个方面：
1. **图表字号优化** - 提升标题和坐标轴文字的可读性
2. **Results界面美化** - 改善数据显示格式，增加单位和专业样式
3. **完整导出功能** - 实现一键导出所有仿真结果，包括带GPS坐标的无人机轨迹

---

## 🎨 1. 图表字号优化

### 修改文件
- `visualization/plot_config.py`

### 主要改进
调整了全局matplotlib字体大小，确保在不重叠的情况下提升可读性：

| 元素 | 原始大小 | 新大小 | 改进 |
|------|---------|--------|------|
| 一般文字 | 9pt | 12pt | +33% |
| 坐标轴标签 | 10pt | 14pt | +40% |
| 图表标题 | 11pt | 16pt | +45% |
| 坐标轴刻度 | 8pt | 13pt | +62% |
| 图例文字 | 9pt | 12pt | +33% |
| 整体标题 | 12pt | 18pt | +50% |

### 效果
- ✅ 所有图表的标题和坐标轴数字更清晰
- ✅ 字号大小更加协调统一
- ✅ 保持专业的Times New Roman字体
- ✅ 支持中文标签显示（通过`get_chinese_font()`函数）

---

## 💎 2. Results界面优化

### 修改文件
- `main.py` - `create_results_tab()` 和 `update_results_table()` 函数

### 主要改进

#### 界面美化
1. **标题区域增强**
   - 主标题：22pt粗体，居中显示
   - 副标题："Multi-Objective Optimization Results"
   - 专业的颜色配色（#2c3e50主色，#7f8c8d副色）

2. **表格样式提升**
   - 蓝色表头（#3498db）配白色文字
   - 交替行颜色显示（白色/#f8f9fa）
   - 选中行高亮（#5dade2）
   - Times New Roman字体，11-12pt大小

#### 数据格式优化

| 列名 | 原始显示 | 新显示 | 说明 |
|------|---------|--------|------|
| Solution ID | "1" | "#01" | 添加#前缀，两位数格式，粗体 |
| Blind Area | "0.1234" | "12.3" | 转换为百分比，1位小数 |
| Sensor Nodes | "15.0000" | "15" | 整数显示 |
| Energy | "234.5678" | "234.57" | 添加单位(Wh)，2位小数 |
| Flight Distance | "1234.5678" | "1234.6" | 添加单位(m)，1位小数 |

#### 表头更新
- "Solution ID" → "Solution ID"
- "Blind Area" → "Blind Area (%)"
- "Nodes" → "Sensor Nodes"
- "Energy" → "Energy (Wh)"
- "Distance" → "Flight Distance (m)"

### 效果
- ✅ 数据显示更简洁专业
- ✅ 单位明确，易于理解
- ✅ 视觉效果更高级
- ✅ 所有数据居中对齐

---

## 📦 3. 完整导出功能实现

### 修改文件
- `main.py` - 新增和完善多个导出函数
- `utils/data_export.py` - 使用现有的导出工具函数

### 新增功能：一键完整导出

#### 新增函数
1. **`export_complete_report()`** - 主导出函数
2. **`_export_uav_trajectory_geojson()`** - 带GPS坐标的轨迹导出
3. 完善 **`export_figures()`**, **`export_data()`**, **`export_geojson()`**

#### Export界面优化

新的导出界面包含：

1. **完整报告导出按钮**（绿色大按钮）
   - 📦 Export Complete Report (All Data)
   - 一键导出所有内容到带时间戳的文件夹

2. **单独导出选项**（蓝色按钮）
   - 🖼️ Export Figures (PNG)
   - 📊 Export Data (CSV)
   - 🌍 Export GeoJSON (with GPS Coordinates)

3. **提示信息**
   - 蓝色边框信息框
   - 列出所有导出内容类型

### 导出内容详细说明

#### 一键完整导出包含：

**输出文件夹结构**：
```
FODEMIR_Export_YYYYMMDD_HHMMSS/
├── figures/
│   ├── forest.png
│   ├── coverage.png
│   ├── optimization.png
│   ├── uav.png
│   ├── convergence.png
│   └── comparison.png
├── forest_trees.csv
├── forest_trees.geojson
├── sensor_positions.csv
├── sensor_positions.geojson
├── pareto_solutions.csv
├── uav_trajectory.csv
├── uav_trajectory.geojson (带GPS坐标！)
└── simulation_summary.json
```

#### 详细内容

**1. 图表导出 (figures/)** 
- 所有6个可视化图表
- PNG格式，300 DPI高分辨率
- 适合论文发表和报告使用

**2. 森林数据**
- `forest_trees.csv`: 包含所有树木的坐标、种类、树冠半径
- `forest_trees.geojson`: GeoJSON格式，可在GIS软件中查看

**3. 传感器数据**
- `sensor_positions.csv`: 所有传感器节点的坐标
- `sensor_positions.geojson`: GeoJSON格式

**4. Pareto解集**
- `pareto_solutions.csv`: 包含所有Pareto最优解
  - blind_area_ratio: 盲区比例
  - num_nodes: 节点数量
  - energy_wh: 能量消耗(Wh)
  - distance_m: 飞行距离(m)

**5. 无人机轨迹（重点功能！）**

##### CSV格式 (`uav_trajectory.csv`)
包含字段：
- `waypoint_id`: 航点序号
- `x`: 本地坐标X (米)
- `y`: 本地坐标Y (米)
- `z`: 高度 (米)
- `cumulative_energy_wh`: 累计能量消耗 (Wh)

##### GeoJSON格式 (`uav_trajectory.geojson`) - 带GPS坐标！
包含两种几何对象：

**Point Features** (每个航点)：
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [longitude, latitude, altitude]
  },
  "properties": {
    "waypoint_id": 0,
    "x_local_m": 100.0,
    "y_local_m": 150.0,
    "altitude_m": 50.0,
    "latitude": 39.9042,
    "longitude": 116.4074,
    "cumulative_energy_wh": 45.6
  }
}
```

**LineString Feature** (完整轨迹路径)：
```json
{
  "type": "Feature",
  "geometry": {
    "type": "LineString",
    "coordinates": [[lon1, lat1, alt1], [lon2, lat2, alt2], ...]
  },
  "properties": {
    "type": "trajectory_path",
    "num_waypoints": 25
  }
}
```

##### GPS坐标转换说明
- 使用参考GPS点：北京 (39.9042°N, 116.4074°E)
- 本地米坐标 → GPS度坐标的转换：
  - 纬度：1度 ≈ 111 km
  - 经度：1度 ≈ 111 km × cos(纬度)
- 可在QGIS、Google Earth等GIS软件中直接打开
- 支持3D可视化（包含高度信息）

**6. 仿真摘要**
- `simulation_summary.json`: 包含所有关键统计信息
  - 元数据（时间戳、版本）
  - 森林信息（树木数量、面积、生成方法）
  - 优化结果（Pareto解数量、传感器数量）
  - 无人机信息（总距离、总能耗、航点数量）

### 使用方法

#### 方法1：完整导出（推荐）
1. 运行仿真直到完成
2. 切换到 "Export & Reports" 标签
3. 点击绿色的 "📦 Export Complete Report (All Data)" 按钮
4. 选择输出文件夹
5. 等待导出完成，会显示详细的导出清单

#### 方法2：单独导出
- **仅导出图表**: 点击 "🖼️ Export Figures (PNG)"
- **仅导出数据**: 点击 "📊 Export Data (CSV)"
- **仅导出GeoJSON**: 点击 "🌍 Export GeoJSON (with GPS Coordinates)"

### GeoJSON文件使用建议

#### 推荐软件
1. **QGIS** (免费开源)
   - 完整的GIS分析功能
   - 支持多图层叠加显示
   - 可导出为各种格式

2. **Google Earth Pro** (免费)
   - 3D地球可视化
   - 直接查看GPS轨迹
   - 需先转换为KML格式

3. **ArcGIS / MapBox / Leaflet**
   - 专业GIS软件
   - 网页地图展示

#### 在QGIS中查看的步骤
1. 打开QGIS
2. 图层 → 添加图层 → 添加矢量图层
3. 选择 `.geojson` 文件
4. 森林、传感器、轨迹将显示在地图上
5. 可以查看每个点的详细属性

---

## ✅ 验证测试

### 测试清单
- [x] 图表字号增大且不重叠
- [x] Results表格显示格式正确
- [x] Results表格包含单位
- [x] 完整导出功能正常工作
- [x] 所有CSV文件包含正确的列和数据
- [x] GeoJSON文件格式正确
- [x] UAV轨迹包含GPS坐标
- [x] 导出的文件夹结构清晰
- [x] 导出完成后显示成功消息

### 运行测试
```bash
# 启动程序
python main.py

# 测试步骤：
# 1. 运行完整仿真
# 2. 查看Results标签，确认格式
# 3. 切换到Export & Reports标签
# 4. 点击"Export Complete Report"
# 5. 检查输出文件夹中的所有文件
# 6. 在QGIS中打开GeoJSON文件验证
```

---

## 🎯 主要优势

### 1. 可读性提升
- 更大的字号让图表在演示和打印时更清晰
- 坐标轴数字和标题大小协调一致
- 专业的Times New Roman字体统一风格

### 2. 数据展示专业化
- Results表格格式规范
- 单位明确，避免混淆
- 适当的小数位数，简洁不冗余
- 美观的配色和布局

### 3. 导出功能完整
- 一键导出所有结果，节省时间
- 多种格式支持（PNG, CSV, JSON, GeoJSON）
- **独特优势**: 无人机轨迹带GPS坐标
- 可在专业GIS软件中进一步分析
- 完整的元数据和摘要信息

### 4. 实用性强
- 适合论文发表（高分辨率图表）
- 适合数据分析（CSV格式）
- 适合GIS应用（GeoJSON + GPS）
- 适合存档和分享（完整报告包）

---

## 📝 技术细节

### GPS坐标转换算法
```python
# 参考点
ref_lat = 39.9042  # 北京纬度
ref_lon = 116.4074  # 北京经度

# 转换系数
lat_per_m = 1.0 / 111000.0  # 1米对应的纬度变化
lon_per_m = 1.0 / (111000.0 * cos(ref_lat))  # 1米对应的经度变化

# 本地坐标 → GPS坐标
latitude = ref_lat + y_local * lat_per_m
longitude = ref_lon + x_local * lon_per_m
```

### 文件命名规范
- 时间戳格式：`YYYYMMDD_HHMMSS`
- 导出文件夹：`FODEMIR_Export_{timestamp}`
- 清晰的文件命名，易于识别和管理

---

## 🔧 后续可能的改进

1. **GPS参考点配置**
   - 添加UI选项让用户设置参考GPS坐标
   - 支持从配置文件读取

2. **更多导出格式**
   - KML格式（Google Earth）
   - Shapefile格式（传统GIS）
   - Excel格式（XLSX）

3. **导出预览**
   - 导出前显示文件列表
   - 估算文件大小

4. **批量处理**
   - 支持多个仿真结果的批量导出
   - 对比分析功能

---

## 📞 使用支持

如有问题或建议，请参考：
- `README.md` - 项目总体说明
- `QUICK_START.md` - 快速入门指南
- `HOW_TO_SEE_CHANGES.md` - 功能展示指南

---

**更新完成！现在可以享受更清晰的可视化和强大的导出功能了！** 🎉

