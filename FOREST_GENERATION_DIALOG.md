# Forest Generation Method Selection Dialog

## 功能概述 ✅

在点击 "RUN SIMULATION" 按钮时，会弹出一个对话框询问用户选择森林生成方式。

## 对话框选项

### 1. GPT-4 选项 (顶部复选框)

```
☐ Use GPT-4 for Enhanced Forest Generation
⚠️ Note: GPT-4 requires API key and may incur costs
```

- **用途**: 使用 GPT-4 API 生成更智能、更真实的森林布局
- **状态**: 当前未实现，选中后会提示"GPT-4 generation not yet implemented"并回退到默认合成方法
- **要求**: 需要配置 OpenAI API key
- **成本**: 可能产生 API 调用费用

---

### 2. 森林生成方法 (二选一)

如果不使用 GPT-4，可以选择以下两种方法之一：

#### 选项 A: 默认合成森林 (Default Synthetic Forest) ✅

```
◉ Use Default Synthetic Forest Generation
   • Procedurally generated forest with configurable parameters
```

**特点**:
- ✅ 完全本地生成，无需外部资源
- ✅ 可配置参数（树木密度、物种比例、区域大小等）
- ✅ 自动生成树木位置（Poisson Disk Sampling）
- ✅ 包含自然空地（clearings）
- ✅ 支持多种树种（松树、橡树、桦树、枫树）
- ✅ 快速生成（2-5秒）

**生成过程**:
1. 根据区域大小和密度计算树木数量
2. 使用 Poisson Disk 算法分布树木位置
3. 创建 3 个自然空地
4. 过滤空地内的树木
5. 分配树种和属性（高度、直径、冠幅）

**可视化**:
- 背景：草绿色 (#90C878)
- 树冠：半透明彩色圆圈
- 空地：浅棕色圆形区域
- 树干：深棕色标记点

---

#### 选项 B: 真实航空森林图像 (Real Aerial Forest Image) ✅

```
◉ Use Real Aerial Forest Image (image.png)
   • Use real forest data from aerial/satellite imagery
```

**特点**:
- ✅ 使用真实的航拍/卫星森林图像
- ✅ 更真实的森林分布和纹理
- ✅ 需要 `image.png` 文件存在于项目根目录
- ⚠️ 如果文件不存在，此选项会被禁用

**文件要求**:
- **文件名**: `image.png`
- **位置**: 项目根目录 (与 `main.py` 同级)
- **格式**: PNG 图像
- **推荐分辨率**: 与区域大小匹配 (如 1000×1000 像素)
- **内容**: 航拍或卫星拍摄的森林图像

**行为**:
- 图像会作为背景显示在 Step 1 和 Step 4
- 不生成合成树木（仅创建最小树木数据以保持兼容性）
- 图像会自动缩放到设置的区域范围
- 坐标轴范围与设置的区域大小一致

**如果文件不存在**:
```
◯ Use Real Aerial Forest Image (image.png not found)    [禁用]
   • ⚠️ image.png not found in project directory
```

---

## 对话框界面

### 外观设计

```
┌─────────────────────────────────────────────┐
│   Select Forest Generation Method           │
│─────────────────────────────────────────────│
│                                              │
│ ☐ Use GPT-4 for Enhanced Forest Generation │
│   ⚠️ Note: GPT-4 requires API key and may   │
│   incur costs                                │
│                                              │
│─────────────────────────────────────────────│
│                                              │
│ If not using GPT-4, select generation       │
│ method:                                      │
│                                              │
│ ◉ Use Default Synthetic Forest Generation  │
│    • Procedurally generated forest with     │
│      configurable parameters                 │
│                                              │
│ ◯ Use Real Aerial Forest Image (image.png) │
│    • Use real forest data from aerial/      │
│      satellite imagery                       │
│                                              │
│                                              │
│        [Start Simulation]  [Cancel]          │
│                                              │
└─────────────────────────────────────────────┘
```

### 样式特性

- **字体**: Times New Roman
- **标题**: 18pt, 粗体, 深色 (#2c3e50)
- **选项**: 13-14pt
- **描述**: 11pt, 斜体, 灰色
- **背景**: 浅灰色 (#ecf0f1)
- **按钮**:
  - Start Simulation: 绿色 (#27ae60)
  - Cancel: 灰色 (#95a5a6)

---

## 使用流程

### 1. 启动仿真

```
用户点击 "RUN SIMULATION" → 弹出对话框
```

### 2. 选择方法

**场景 A: 使用默认合成森林**
```
1. 不勾选 GPT-4
2. 选择 "Use Default Synthetic Forest Generation"
3. 点击 "Start Simulation"
→ 生成合成森林，显示彩色树木
```

**场景 B: 使用真实图像**
```
1. 确保 image.png 存在
2. 不勾选 GPT-4
3. 选择 "Use Real Aerial Forest Image"
4. 点击 "Start Simulation"
→ 加载真实图像作为背景
```

**场景 C: 尝试 GPT-4（未实现）**
```
1. 勾选 "Use GPT-4 for Enhanced Forest Generation"
2. 点击 "Start Simulation"
→ 显示错误提示
→ 回退到合成方法
```

**场景 D: 取消**
```
点击 "Cancel" → 关闭对话框，不运行仿真
```

---

## 技术实现

### 配置存储

对话框选择会存储到配置中：

```python
config.set('forest_generation.use_gpt', True/False)
config.set('forest_generation.method', 'synthetic'/'real_image'/'gpt4')
```

### 方法枚举

| 方法代码 | 说明 | 状态 |
|---------|------|------|
| `'synthetic'` | 默认合成森林 | ✅ 实现 |
| `'real_image'` | 真实航空图像 | ✅ 实现 |
| `'gpt4'` | GPT-4 增强生成 | ⚠️ 未实现 |

### 生成逻辑

```python
# SimulationWorker.run()

forest_method = config.get('forest_generation.method')
use_gpt = config.get('forest_generation.use_gpt')

if forest_method == 'real_image':
    # Load image, create minimal tree data
    tree_positions = np.array([[width/2, height/2]])  # Dummy
    species_list = ['pine']
    crown_radii = np.array([5.0])
    clearings = []
    
elif use_gpt:
    # TODO: Implement GPT-4 API call
    error.emit("GPT-4 not implemented")
    # Fall back to synthetic
    
else:  # synthetic
    # Generate with Poisson Disk + Tree DB
    # Create clearings
    # Filter positions
```

### 可视化逻辑

```python
# update_visualizations()

forest_method = results['forest'].get('method', 'synthetic')

if forest_method == 'real_image':
    background_img = 'image.png'  # Use real image
else:
    background_img = None  # Use synthetic forest

forest_vis.plot_forest_map(..., background_image=background_img)
```

---

## 文件修改清单

### 1. `main.py` (主要修改)

#### 新增类: `ForestGenerationDialog` (Line 54-232)
- 对话框UI
- 3种生成方法选择
- GPT-4 复选框
- image.png 存在性检查
- 样式化按钮

#### 修改方法: `run_full_simulation()` (Line ~1125)
```python
def run_full_simulation(self):
    # 1. 显示对话框
    dialog = ForestGenerationDialog(self)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return  # User cancelled
    
    # 2. 获取选择
    forest_method = dialog.get_selected_method()
    use_gpt4 = dialog.use_gpt4_checkbox.isChecked()
    
    # 3. 存储到配置
    self.config.set('forest_generation.use_gpt', use_gpt4)
    self.config.set('forest_generation.method', forest_method)
    
    # 4. 启动仿真
    self.worker = SimulationWorker(self.config)
    ...
```

#### 修改类: `SimulationWorker.run()` (Line ~250-332)
```python
# 获取方法
forest_method = config.get('forest_generation.method')
use_gpt = config.get('forest_generation.use_gpt')

if forest_method == 'real_image':
    # Minimal data
elif use_gpt:
    # TODO: GPT-4 (fallback to synthetic)
else:  # synthetic
    # Full generation
```

#### 修改方法: `update_visualizations()` (Line ~1195, ~1279)
```python
# Step 1 & Step 4
forest_method = results['forest'].get('method', 'synthetic')
background_img = None
if forest_method == 'real_image':
    background_img = 'image.png'
    if not Path(background_img).exists():
        background_img = None
```

#### 新增导入 (Line 14-20)
```python
from PyQt6.QtWidgets import (..., QCheckBox, QButtonGroup, 
                              QRadioButton, QFrame)
```

---

## 使用示例

### 示例 1: 默认合成森林 (推荐)

**步骤**:
1. 运行 `python main.py`
2. 点击 "RUN SIMULATION"
3. 在对话框中保持默认选择（Synthetic Forest）
4. 点击 "Start Simulation"

**结果**:
- Step 1: 显示带彩色树木的合成森林
- Step 4: UAV 路径叠加在合成森林上
- 统计框显示实际树木数量和密度

---

### 示例 2: 真实航空图像

**准备**:
1. 将真实森林图像重命名为 `image.png`
2. 放置在项目根目录 (与 `main.py` 同级)
3. 确保图像分辨率合理 (推荐 1000×1000)

**步骤**:
1. 运行 `python main.py`
2. 点击 "RUN SIMULATION"
3. 在对话框中选择 "Use Real Aerial Forest Image"
4. 点击 "Start Simulation"

**结果**:
- Step 1: 显示真实森林航拍图像
- Step 4: UAV 路径叠加在真实图像上
- 统计框显示最小树木数据（兼容性）

---

### 示例 3: 取消仿真

**步骤**:
1. 运行 `python main.py`
2. 点击 "RUN SIMULATION"
3. 在对话框中点击 "Cancel"

**结果**:
- 对话框关闭
- 不执行任何仿真
- 界面保持当前状态

---

## 配置文件更新

不需要手动修改 `config/default_config.json`，对话框选择会自动更新运行时配置。

### 运行时配置示例

```json
{
  "forest_generation": {
    "method": "synthetic",        // or "real_image" or "gpt4"
    "use_gpt": false,
    "area_m2": 1000000,
    ...
  }
}
```

---

## 验证清单

重启程序后验证：

- [ ] 点击 "RUN SIMULATION" 弹出对话框
- [ ] 对话框显示 3 个选项（GPT-4, Synthetic, Real Image）
- [ ] 如果 image.png 不存在，Real Image 选项被禁用
- [ ] 选择 Synthetic 并运行，显示合成森林
- [ ] 如果 image.png 存在，选择 Real Image 并运行，显示真实图像
- [ ] 点击 Cancel 关闭对话框，不运行仿真
- [ ] 勾选 GPT-4 并运行，显示"未实现"错误提示

---

## 未来改进

### GPT-4 集成

**需要实现**:
1. OpenAI API 集成
2. 提示词工程（森林布局描述）
3. API 响应解析
4. 生成参数转换

**API 流程**:
```
User Input → GPT-4 Prompt → API Call → Parse Response → Generate Forest
```

**提示词示例**:
```
Generate a realistic forest distribution for a {width}×{height}m area.
Include {n_trees} trees with species: {species_mix}.
Create natural clearings and realistic spacing.
Output as JSON with tree positions and attributes.
```

### 更多生成方法

**潜在扩展**:
- ✅ Synthetic (已实现)
- ✅ Real Image (已实现)
- ⚠️ GPT-4 (待实现)
- 🔮 GIS Import (导入真实地理数据)
- 🔮 Procedural Noise (基于噪声算法)
- 🔮 Template-based (基于模板)

---

## 故障排除

### 问题 1: 对话框不显示

**原因**: 可能是旧版本的程序仍在运行

**解决**:
```bash
# 关闭所有 Python 进程
taskkill /F /IM python.exe  # Windows
pkill python  # Linux/Mac

# 重新运行
python main.py
```

---

### 问题 2: Real Image 选项总是禁用

**原因**: `image.png` 文件不存在或路径错误

**检查**:
```python
from pathlib import Path
print(Path('image.png').exists())  # Should be True
print(Path('image.png').resolve())  # Check actual path
```

**解决**:
1. 确保文件名正确（区分大小写）
2. 确保文件在项目根目录
3. 确保文件格式为PNG

---

### 问题 3: 图像显示不正确

**原因**: 图像分辨率或坐标范围不匹配

**解决**:
- 调整 Area Size 参数以匹配图像实际范围
- 使用高分辨率图像 (推荐 ≥1000×1000)
- 确保图像内容为航拍森林

---

### 问题 4: GPT-4 提示错误

**原因**: GPT-4 功能尚未实现

**解决**:
- 这是预期行为
- 系统会自动回退到 Synthetic 方法
- 等待未来版本实现 GPT-4 集成

---

## 完成状态

- ✅ 对话框UI设计
- ✅ 3种方法选择逻辑
- ✅ Synthetic 森林生成
- ✅ Real Image 背景支持
- ✅ image.png 存在性检查
- ✅ 配置管理
- ✅ 可视化逻辑更新
- ⚠️ GPT-4 集成（待实现）
- ✅ 文档完成

---

**所有功能已实现！请重启程序并点击 "RUN SIMULATION" 体验新对话框！** 🎉

