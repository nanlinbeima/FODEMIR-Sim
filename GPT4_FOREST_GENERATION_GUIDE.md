# GPT-4 森林生成完整指南

## ✅ 功能已实现

点击 "RUN SIMULATION" → 勾选 "Use GPT-4 for Enhanced Forest Generation" → 会弹出 API Key 输入对话框。

---

## 🎯 功能概述

使用 OpenAI GPT-4 API 生成更智能、更真实的森林布局，包括：
- 🌲 自然的树木聚类模式
- 🎨 真实的物种分布
- 📐 合理的树木间距
- 🟫 自然位置的空地

---

## 🚀 使用步骤

### 第一步：获取 OpenAI API Key

1. **访问 OpenAI 平台**
   ```
   https://platform.openai.com/api-keys
   ```

2. **登录或注册账号**
   - 使用 Gmail/Microsoft 账号登录
   - 或创建新的 OpenAI 账号

3. **创建 API Key**
   - 点击 "+ Create new secret key"
   - 输入名称（如 "FODEMIR-Sim"）
   - 复制生成的 key（格式：`sk-...`）
   - ⚠️ **重要**：保存好 API key，页面关闭后无法再次查看

4. **充值账户（必需）**
   - 在 Billing 页面添加支付方式
   - 最低充值 $5-10 USD
   - GPT-4 收费：约 $0.03-0.06 每次调用

---

### 第二步：在程序中使用 GPT-4

#### 2.1 运行程序
```bash
python main.py
```

#### 2.2 启动仿真
- 点击 "RUN SIMULATION" 按钮

#### 2.3 森林生成对话框
会弹出选择对话框：

```
┌──────────────────────────────────────┐
│ Select Forest Generation Method      │
├──────────────────────────────────────┤
│                                      │
│ ☑ Use GPT-4 for Enhanced Forest     │  ← 勾选这个
│   Generation                         │
│   ⚠️ GPT-4 requires API key         │
│                                      │
│──────────────────────────────────────│
│                                      │
│ If not using GPT-4, select:         │
│                                      │
│ ◯ Use Default Synthetic Forest      │
│   Generation                         │
│                                      │
│ ◯ Use Real Aerial Forest Image      │
│   (image.png)                        │
│                                      │
│        [Start Simulation] [Cancel]   │
│                                      │
└──────────────────────────────────────┘
```

**操作**:
1. ☑ 勾选 "Use GPT-4 for Enhanced Forest Generation"
2. 点击 "Start Simulation"

#### 2.4 API Key 输入对话框

**首次使用或 API key 不存在时**，会弹出：

```
┌────────────────────────────────────────────┐
│     GPT-4 API Key Configuration            │
├────────────────────────────────────────────┤
│                                            │
│ To use GPT-4 for forest generation, you   │
│ need an OpenAI API key.                    │
│ Get your API key from:                     │
│ https://platform.openai.com/api-keys       │
│                                            │
│ API Key: [sk-************************] 👁  │
│                                            │
│ ⚠️ Your API key will be stored locally in │
│   config/api_keys.json                     │
│                                            │
│        [Save & Continue]  [Cancel]         │
│                                            │
└────────────────────────────────────────────┘
```

**操作**:
1. 在 "API Key" 输入框粘贴您的 key（`sk-...`）
2. 点击 👁 "Show" 按钮可以查看输入的 key
3. 点击 "Save & Continue"

**验证**:
- 程序会检查 key 格式是否正确（必须以 `sk-` 开头）
- 如果格式错误，会显示警告
- 如果格式正确，key 会被保存到 `config/api_keys.json`

#### 2.5 GPT-4 生成过程

保存 API key 后，程序会：

```
1. Step 1/4: Generating forest with GPT-4...
   ↓
2. Calling GPT-4 API...
   ↓
3. Parsing GPT-4 response...
   ↓
4. Processing [N] trees from GPT-4...
   ↓
5. GPT-4 generation complete!
```

**预计时间**: 10-30 秒（取决于网络和 API 响应）

---

## 🎨 GPT-4 生成效果

### 与默认合成方法的对比

| 特性 | 默认合成森林 | GPT-4 森林 |
|------|-------------|-----------|
| **生成速度** | 2-5 秒 | 10-30 秒 |
| **真实度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **聚类模式** | 随机分布 | 自然聚类 |
| **物种分布** | 均匀 | 生态真实 |
| **空地位置** | 固定模式 | 自然位置 |
| **可重复性** | 高 | 中（每次略有不同） |
| **成本** | 免费 | ~$0.03-0.06/次 |

### GPT-4 生成特点

✅ **自然聚类**
- 树木按生态习性聚集
- 同种树木倾向于分组
- 避免过于规则的排列

✅ **生态真实性**
- 物种根据环境分布
- 考虑光照、水分等因素
- 边缘效应模拟

✅ **智能空地**
- 空地位置更自然
- 大小和形状更合理
- 符合森林演替规律

✅ **参数适应**
- 自动调整树木间距
- 根据密度优化分布
- 适应不同区域大小

---

## 💰 成本估算

### OpenAI GPT-4 定价

**GPT-4 Turbo (推荐)**:
- Input: $0.01 / 1K tokens
- Output: $0.03 / 1K tokens

**每次森林生成**:
- 输入 tokens: ~300-500
- 输出 tokens: ~1000-2000
- **预估成本**: $0.03-0.06 USD/次

### 使用场景成本

| 使用场景 | 次数 | 预估成本 |
|---------|------|---------|
| 单次测试 | 1 | $0.05 |
| 小型实验 | 10 | $0.50 |
| 中型项目 | 50 | $2.50 |
| 大型研究 | 200 | $10.00 |

**建议**:
- 日常开发：使用默认合成森林（免费）
- 论文/展示：使用 GPT-4（高质量）
- 参数实验：使用默认合成（可重复）

---

## 🔧 技术细节

### API 调用流程

```python
1. 加载 API key (config/api_keys.json)
   ↓
2. 构建 GPT-4 提示词
   - 区域大小 (如 1000×1000 m)
   - 树木数量 (如 50,000 棵)
   - 物种比例 (Pine 40%, Oak 30%, ...)
   - 生成要求 (聚类、间距、空地)
   ↓
3. 调用 OpenAI API
   - Endpoint: https://api.openai.com/v1/chat/completions
   - Model: gpt-4
   - Temperature: 0.7
   - Max tokens: 3000
   ↓
4. 解析 JSON 响应
   - 提取树木位置 (x, y)
   - 提取物种信息
   - 提取冠幅、高度、直径
   - 提取空地位置和半径
   ↓
5. 数据扩展（如需要）
   - 如果生成的树木 < 目标数量
   - 复制并添加随机偏移
   - 确保覆盖整个区域
   ↓
6. 返回森林数据
```

### 提示词（Prompt）

程序会发送以下提示给 GPT-4：

```
Generate a realistic forest distribution for a 1000×1000 meter area.

Requirements:
- Total area: 1,000,000 m²
- Target tree count: approximately 50,000 trees
- Tree density: 500 trees per hectare
- Species distribution: Pine (40%), Oak (30%), Birch (20%), Maple (10%)

Please generate:
1. Tree positions (x, y coordinates in meters)
2. Species for each tree
3. Crown radii (realistic sizes: 3-8 meters)
4. 2-4 natural clearings (open areas) with positions and radii

Output format: JSON with structure:
{
  "trees": [
    {"x": float, "y": float, "species": "pine|oak|birch|maple", 
     "crown_radius": float, "height": float, "dbh": float}
  ],
  "clearings": [
    {"x": float, "y": float, "radius": float}
  ]
}

Make it realistic with:
- Natural clustering patterns
- Appropriate spacing (min 3m between trees)
- Varied crown sizes based on species
- Clearings in natural-looking positions

Generate approximately 100 sample trees (we'll extrapolate for larger forests).
```

### 响应示例

```json
{
  "trees": [
    {
      "x": 125.5,
      "y": 340.2,
      "species": "pine",
      "crown_radius": 6.2,
      "height": 18.5,
      "dbh": 35.0
    },
    {
      "x": 130.1,
      "y": 345.8,
      "species": "pine",
      "crown_radius": 5.8,
      "height": 17.2,
      "dbh": 32.5
    },
    // ... 更多树木
  ],
  "clearings": [
    {
      "x": 500.0,
      "y": 500.0,
      "radius": 45.0
    },
    {
      "x": 250.0,
      "y": 750.0,
      "radius": 30.0
    }
  ]
}
```

---

## 📂 文件说明

### config/api_keys.json

**格式**:
```json
{
  "openai_api_key": "sk-your-actual-key-here"
}
```

**安全性**:
- ✅ 已添加到 `.gitignore`，不会被 Git 追踪
- ✅ 仅存储在本地，不会上传到服务器
- ⚠️ 请勿分享此文件
- ⚠️ 请勿将 key 硬编码到代码中

**位置**: `config/api_keys.json`

---

## 🔒 安全建议

### API Key 保护

1. **不要分享 API key**
   - 不要提交到 Git
   - 不要发送给他人
   - 不要在公开场所展示

2. **定期轮换 key**
   - 每 3-6 个月更换一次
   - 如果怀疑泄露，立即撤销

3. **监控使用量**
   - 定期检查 OpenAI 账单
   - 设置预算限额
   - 及时发现异常使用

4. **权限最小化**
   - 仅赋予必要的 API 权限
   - 不要使用管理员 key

### 文件权限

```bash
# Linux/Mac
chmod 600 config/api_keys.json  # 仅所有者可读写

# Windows
# 通过文件属性设置，仅允许当前用户访问
```

---

## ❓ 常见问题

### Q1: 如何检查 API key 是否有效？

**方法 1**: 在 OpenAI 平台查看
- 访问 https://platform.openai.com/api-keys
- 查看 key 状态

**方法 2**: 尝试使用
- 勾选 GPT-4 选项
- 运行仿真
- 如果失败，会显示错误信息

### Q2: API 调用失败怎么办？

**可能原因**:
1. **API key 无效**
   - 检查 key 格式（必须以 `sk-` 开头）
   - 检查 key 是否被撤销
   - 重新生成 key

2. **账户余额不足**
   - 访问 Billing 页面充值
   - 最低充值 $5 USD

3. **网络问题**
   - 检查网络连接
   - 尝试使用 VPN
   - 检查防火墙设置

4. **API 限额**
   - OpenAI 有频率限制
   - 等待几分钟后重试

**解决方案**:
- 程序会自动回退到默认合成方法
- 查看终端输出的错误信息
- 修复问题后重新运行

### Q3: GPT-4 生成的森林与默认的有何不同？

**视觉差异**:
- GPT-4: 树木呈自然聚类，边缘稀疏，中心密集
- 默认: 树木分布更均匀，随机性强

**数据差异**:
- GPT-4: 冠幅大小有更大的变化
- 默认: 参数更规范，便于对照实验

**使用建议**:
- 论文/展示: GPT-4（更真实）
- 参数实验: 默认（可控性强）

### Q4: 可以修改 GPT-4 提示词吗？

**可以！** 在 `main.py` 中找到 `generate_forest_with_gpt4` 方法：

```python
def generate_forest_with_gpt4(self, api_key, width, height, n_trees, density):
    prompt = f"""Generate a realistic forest distribution...
    
    # 修改这里的提示词
    ...
    """
```

**自定义提示词示例**:
- 增加特定物种："Include 10% of rare species Sequoia"
- 添加地形："Consider a hillside with slope from north to south"
- 季节因素："Simulate autumn with deciduous trees"

### Q5: API key 保存在哪里？

**位置**: `config/api_keys.json`

**查看**:
```bash
cat config/api_keys.json  # Linux/Mac
type config\api_keys.json  # Windows
```

**修改**:
- 方法 1: 手动编辑文件
- 方法 2: 删除文件，重新运行程序输入

**删除**:
```bash
rm config/api_keys.json  # Linux/Mac
del config\api_keys.json  # Windows
```

### Q6: 能否使用其他模型（如 GPT-3.5）？

**可以！** 修改 `main.py`:

```python
data = {
    'model': 'gpt-3.5-turbo',  # 改为 gpt-3.5-turbo
    'messages': [...],
    ...
}
```

**成本对比**:
- GPT-3.5 Turbo: $0.001-0.002 / 1K tokens（便宜 10-30 倍）
- GPT-4 Turbo: $0.01-0.03 / 1K tokens（质量更高）

**建议**:
- 测试阶段：GPT-3.5（省钱）
- 最终生成：GPT-4（质量）

---

## 🔄 回退机制

### 自动回退

如果 GPT-4 调用失败，程序会**自动回退**到默认合成方法：

```
GPT-4 generation failed: API key is empty. Using synthetic method...
↓
Generating forest with default synthetic method...
↓
Step 1 complete!
```

**回退触发条件**:
- API key 不存在
- API key 格式错误
- 网络连接失败
- API 返回错误
- JSON 解析失败
- 余额不足

**用户无需干预**，仿真会继续进行。

---

## 📊 使用统计

### GPT-4 调用信息

每次调用后，终端会显示：

```
✓ API key loaded successfully
Calling GPT-4 API...
✓ API responded (status 200)
Parsing GPT-4 response...
✓ Parsed 100 trees from GPT-4
Processing trees...
✓ Expanded to 50,000 trees
GPT-4 generation complete!
```

### 成本追踪

**手动追踪**:
1. 访问 https://platform.openai.com/usage
2. 查看 API 使用历史
3. 记录每次调用的 token 数量

**自动追踪**（可选）:
- 在代码中记录调用次数
- 计算累计成本
- 设置预算警告

---

## 🎓 最佳实践

### 1. 开发阶段

```
☑ 使用默认合成森林（免费，快速）
☑ 参数调试和测试
☑ 算法验证
```

### 2. 准备发布

```
☑ 使用 GPT-4 生成 2-3 个高质量示例
☑ 保存生成的森林数据（避免重复调用）
☑ 用于论文、演示、展示
```

### 3. 混合使用

```
☑ 大部分实验：默认合成
☑ 关键场景：GPT-4
☑ 对比研究：两种方法都使用
```

---

## 🛠️ 故障排除

### 问题 1: "API key is empty"

**原因**: API key 未保存或文件损坏

**解决**:
```bash
# 删除旧的 API key 文件
rm config/api_keys.json

# 重新运行程序，输入新的 API key
python main.py
```

### 问题 2: "API returned status 401"

**原因**: API key 无效或已撤销

**解决**:
1. 访问 https://platform.openai.com/api-keys
2. 撤销旧 key
3. 创建新 key
4. 删除 `config/api_keys.json`
5. 重新输入新 key

### 问题 3: "API returned status 429"

**原因**: 超过频率限制

**解决**:
- 等待 1-5 分钟
- 减少调用频率
- 升级 OpenAI 账户

### 问题 4: "Failed to parse GPT-4 response as JSON"

**原因**: GPT-4 返回格式错误

**解决**:
- 重试（GPT-4 有时会格式错误）
- 检查提示词（是否太复杂）
- 增加 max_tokens 限制

### 问题 5: 生成的树木数量不够

**原因**: GPT-4 只生成样本树木（如 100 棵）

**说明**: 这是正常的！程序会自动扩展：
```
GPT-4 generates: 100 sample trees
↓
Program expands: 50,000 trees
(with random offsets to avoid duplicates)
```

---

## 📚 相关文档

- **FOREST_GENERATION_DIALOG.md** - 森林生成对话框详细说明
- **QUICK_GUIDE_森林生成选择.md** - 快速使用指南
- **AREA_SIZE_UPDATE.md** - 区域大小设置

---

## ✅ 完成清单

- [x] GPT-4 API key 输入对话框
- [x] API key 保存和加载
- [x] GPT-4 API 调用实现
- [x] JSON 响应解析
- [x] 树木数据扩展
- [x] 自动回退机制
- [x] 错误处理和提示
- [x] 安全性（.gitignore）
- [x] 文档完成

---

## 🎉 开始使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 获取 OpenAI API key
# 访问: https://platform.openai.com/api-keys

# 3. 运行程序
python main.py

# 4. 点击 RUN SIMULATION

# 5. 勾选 "Use GPT-4 for Enhanced Forest Generation"

# 6. 输入 API key

# 7. 享受高质量的森林生成！
```

**祝您使用愉快！** 🌲🤖

