# 🚀 FODEMIR-Sim Quick Start Guide

## Installation & Launch

```bash
# 1. Install dependencies (if not already done)
pip install -r requirements.txt

# 2. Run the application
python main.py
```

---

## 📋 Step-by-Step Usage

### 1️⃣ Configure Parameters

In the **"Parameters"** tab, adjust settings:

#### Forest Generation
- **Forest Area**: Size in m² (default: 100,000)
- **Tree Density**: Trees per hectare (default: 500)
- **Min Spacing**: Minimum distance between trees (default: 3m)

#### EM Propagation
- **Frequency**: Communication frequency in MHz (default: 868)
- **TX Power**: Transmission power in dBm (default: 14)
- **SNR Threshold**: Minimum SNR in dB (default: 6)

#### UAV Planning
- **Cruise Speed**: Flight speed in m/s (default: 15)
- **Battery Capacity**: Battery in Wh (default: 300)

---

### 2️⃣ Run Simulation

1. Click **"Run Full Simulation"** button
2. Watch progress bar (1% → 100%)
3. Status messages show each step:
   - 1-25%: Generating forest
   - 25-50%: Calculating EM propagation
   - 50-75%: Running optimization
   - 75-100%: Planning UAV trajectory

**⏱️ Estimated Time**: 10-20 seconds (demo mode)

---

### 3️⃣ View Results

The **"Visualization"** tab automatically opens with **4 sub-tabs**:

#### 📊 Tab 1: Step 1: Forest
- **Shows**: Forest distribution map
- **Elements**: Tree positions, crown circles, species legend
- **Colors**: Species-specific greens

#### 📊 Tab 2: Step 2: Coverage
- **Shows**: EM coverage heatmap
- **Elements**: Signal strength, gateways (red triangles)
- **Colormap**: Green (good) to Red (poor)

#### 📊 Tab 3: Step 3: Optimization
- **Shows**: Pareto front (multi-objective solutions)
- **Axes**: Blind Area vs. Number of Nodes
- **Points**: Blue = all solutions, Red star = selected

#### 📊 Tab 4: Step 4: UAV Path
- **Shows**: UAV flight trajectory
- **Elements**: Depot (green square), drop points (red triangles), path (blue line)

---

### 4️⃣ Save Figures

Each tab has a **blue "Save" button** at the bottom:

1. Click the tab you want to save
2. Click **"Save [Step Name]"** button
3. Choose format:
   - **PNG**: Best for presentations (recommended)
   - **PDF**: Vector graphics for LaTeX papers
   - **SVG**: Editable vector format
4. Select location and filename
5. Click **"Save"**
6. ✅ Confirmation message appears

**Default Names**:
- `step1_forest_distribution.png`
- `step2_em_coverage.png`
- `step3_pareto_front.png`
- `step4_uav_trajectory.png`

---

## 🎯 Common Tasks

### Change Forest Size
1. Go to **Parameters** → Forest Generation
2. Adjust **"Forest Area"** slider
3. Run simulation again

### Adjust Signal Quality
1. Go to **Parameters** → EM Propagation
2. Change **"SNR Threshold"** (higher = stricter)
3. Run simulation

### Save All Figures
1. After simulation completes
2. Visit each visualization tab (1-4)
3. Click save button on each
4. Choose same folder for all

---

## 💡 Tips & Tricks

### 🎨 For Publication-Quality Figures
- Use **PDF** or **SVG** format (vector graphics)
- Figures are 300 DPI by default
- All text is **Times New Roman** (standard academic font)
- No post-processing needed!

### ⚡ For Faster Testing
- Reduce **Forest Area** to 50,000 m²
- Lower **Tree Density** to 300/ha
- Current settings already optimized for speed

### 📊 For Presentations
- Save as **PNG** at 300 DPI
- Figures have clean, minimal design
- Professional color schemes
- No Chinese text issues

### 🔍 Zoom & Pan
- Click and drag to pan
- Scroll to zoom (if matplotlib toolbar enabled)
- Double-click to reset view

---

## 🐛 Troubleshooting

### Simulation Stuck?
- Check status bar for current step
- Optimization (50-75%) takes longest
- Wait up to 30 seconds

### Can't Save Figure?
- Make sure simulation completed (100%)
- Check write permissions in save folder
- Try different location

### Garbled Text?
- ✅ **Fixed!** All text now in English
- If still seeing issues, restart application

### Font Too Small/Large?
- ✅ **Standardized!** All fonts 12-14pt
- Consistent across all figures

---

## 📁 Output Files

### Visualization Saves
- Location: **Your choice** (via save dialog)
- Format: PNG (300 DPI), PDF, or SVG
- Naming: Customizable with smart defaults

### Data Exports
- Go to **"Export"** tab
- Export GeoJSON, CSV, or JSON
- Batch export all results

---

## ⌨️ Keyboard Shortcuts

*Future feature - coming soon*

---

## 📚 Next Steps

1. **Read Full Documentation**: See `README.md`
2. **Understand Parameters**: See `docs/PARAMETERS.md`
3. **Learn Algorithms**: See `docs/ALGORITHMS.md`
4. **View Examples**: See `examples/` folder

---

## ❓ FAQ

**Q: How long does simulation take?**  
A: 10-20 seconds in demo mode (5 sensors, 5 population, 3 generations)

**Q: Can I save figures programmatically?**  
A: Yes! Use the Export tab or modify `export_results()` method

**Q: Are figures publication-ready?**  
A: Yes! 300 DPI, Times New Roman, vector formats supported

**Q: Can I change color schemes?**  
A: Edit `visualization/plot_config.py` → `FOREST_COLORS`, etc.

**Q: How do I cite this software?**  
A: See `CITATION.cff` file

---

## 🎉 You're Ready!

Start exploring your forest sensor network deployments!

```bash
python main.py
```

**Happy Simulating! 🌲📡🚁**


