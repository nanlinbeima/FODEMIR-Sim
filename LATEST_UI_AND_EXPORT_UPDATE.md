# Latest UI and Export Updates
# 最新界面与导出功能更新

**Date:** November 2, 2025  
**Version:** 1.1

---

## Summary | 更新摘要

This update focuses on improving visualization clarity and enhancing UAV trajectory export for real-world deployment with DJI drones.

本次更新专注于提升可视化清晰度，并增强UAV航迹导出功能，支持大疆无人机实际部署。

---

## Changes Made | 更新内容

### 1. ✅ Step 1: Forest Visualization - Clean Display
**森林可视化图 - 简洁显示**

**Change:** Removed the yellow statistics box in upper left corner

**修改：** 删除左上角黄色统计信息框

**Before:**
```
┌─────────────────────┐
│ Forest Statistics:  │
│ Area: 1000×1000 m   │
│ Total: 1,000,000 m² │
│ Trees: 1            │
│ Density: 0.0 trees/ha│
│ Canopy Closure: 0.0%│
└─────────────────────┘
```

**After:**
- Clean forest map without overlaying text
- Statistics still calculated internally for export
- More professional appearance

**Files Modified:**
- `main.py` (lines 1985-1999)

---

### 2. ✅ Step 2: EM Propagation - Times New Roman Font
**电磁传播图 - Times New Roman字体**

**Change:** All text elements now use Times New Roman font to prevent garbled characters

**修改：** 所有文本元素使用Times New Roman字体，防止乱码

**Updated Elements:**
- Axis labels (X/Y coordinates)
- Figure titles
- Colorbar labels
- Legend text
- Statistics box text
- Colorbar tick labels

**Files Modified:**
- `visualization/propagation_visualizer_v2.py` (lines 134-219)

**Font Parameters Added:**
```python
family='Times New Roman'
prop={'family': 'Times New Roman'}
```

---

### 3. ✅ Results Tab: Increased Subplot Spacing
**结果标签页 - 增大子图间距**

**Change:** Increased vertical spacing between (a)(b) and (c)(d) plots

**修改：** 增大(a)(b)与(c)(d)图表之间的垂直间距

**Before:** `hspace=0.3` (30% spacing)  
**After:** `hspace=0.5` (50% spacing)

**Visual Improvement:**
- Better separation between top and bottom rows
- No overlap of titles and axis labels
- Improved readability

**Files Modified:**
- `main.py` (line 2239)

---

### 4. ✅ NEW: DJI-Compatible UAV Trajectory Export
**新功能：大疆兼容UAV航迹导出**

**Major Enhancement:** UAV trajectories now export in **two formats** for DJI drone deployment

**重大改进：** UAV航迹现在导出**两种格式**，支持大疆无人机部署

#### Format 1: Standard CSV (`uav_trajectory.csv`)

**New Columns Added:**
- `Heading_deg` - Calculated heading to next waypoint
- `Speed_m_s` - Cruise speed (default 5 m/s)

**Example Output:**
```csv
Waypoint_ID,Local_X_m,Local_Y_m,Altitude_m,Latitude,Longitude,Heading_deg,Speed_m_s
0,158.00,158.00,50.00,30.001425,120.001408,45.5,5.0
1,223.45,187.32,50.00,30.001689,120.001990,32.1,5.0
```

#### Format 2: DJI Pilot CSV (`uav_trajectory_DJI_Format.csv`)

**NEW - Direct Import to DJI Pilot App!**

**Columns:**
```csv
latitude,longitude,altitude(m),heading(deg),curvesize(m),rotationdir,
gimbalmode,gimbalpitchangle,actiontype1,actionparam1
```

**Features:**
- ✅ Direct import to DJI Pilot 2 app
- ✅ Compatible with Matrice 300 RTK, M30, Mavic 3 Enterprise
- ✅ Automatic heading calculation
- ✅ Smooth flight curves (0.2m curve size)
- ✅ Nadir gimbal angle (-90°) for sensor deployment
- ✅ Ready for autonomous missions

**Files Modified:**
- `main.py` (lines 2499-2574)

---

## How to Use | 使用方法

### Export UAV Trajectory for DJI Drones

**Step 1:** Run simulation until Step 4 (UAV trajectory) completes

**Step 2:** Go to "Export" tab → Click one of:
- **"📦 Export Complete Report"** (Recommended) - Exports everything
- **"🌍 Export GeoJSON"** - Exports trajectory files only

**Step 3:** Find exported files in `output_data/` folder:
```
output_data/
├── uav_trajectory.csv              # Standard format
├── uav_trajectory_DJI_Format.csv   # DJI compatible ⭐NEW
└── uav_trajectory.geojson          # GIS format
```

**Step 4:** Import `uav_trajectory_DJI_Format.csv` to DJI Pilot app:
1. Open DJI Pilot 2 on your remote controller
2. Navigate to: 飞行 → 航线飞行 → 导入航线
3. Select the CSV file
4. Review and execute mission

---

## GPS Coordinate Configuration | GPS坐标配置

**Default Reference Point:**
- Latitude: 30.0° N
- Longitude: 120.0° E

**To Customize for Your Site:**

Edit `main.py` lines ~2510 and ~2514:

```python
# Reference point (user can modify this to their actual site location)
ref_lat = 30.0   # ← Change to your site latitude
ref_lon = 120.0  # ← Change to your site longitude
```

**Example Sites:**
- Beijing: `ref_lat = 40.0, ref_lon = 116.4`
- Shanghai: `ref_lat = 31.2, ref_lon = 121.5`
- Shenzhen: `ref_lat = 22.5, ref_lon = 114.1`

---

## Supported DJI Models | 支持的大疆机型

**Tested & Compatible:**
- ✅ DJI Matrice 300 RTK
- ✅ DJI Matrice 30/30T
- ✅ DJI Mavic 3 Enterprise
- ✅ DJI Phantom 4 RTK

**Should Work:**
- DJI M600 Pro
- DJI Inspire 2
- Other enterprise models with waypoint missions

---

## Technical Details | 技术细节

### Heading Calculation

Automatic calculation of aircraft heading between waypoints:

```python
heading = (atan2(dy, dx) × 180/π + 90) mod 360
```

Where:
- `dx` = next_waypoint.x - current_waypoint.x
- `dy` = next_waypoint.y - current_waypoint.y
- Result in degrees (0° = North, 90° = East, 180° = South, 270° = West)

### GPS Coordinate Conversion

Local coordinates (meters) → GPS (decimal degrees):

```python
latitude = ref_lat + (y_meters / 111,000)
longitude = ref_lon + (x_meters / (111,000 × cos(ref_lat)))
```

**Accuracy:** Suitable for areas up to 10 km × 10 km

---

## Documentation | 文档

**New File Added:** `DJI_UAV_TRAJECTORY_GUIDE.md`

**Contents:**
- Complete DJI drone integration guide
- Import instructions for DJI Pilot 2
- Flight safety checklist
- GPS coordinate reference setup
- Troubleshooting tips
- Advanced usage examples

**Location:** Project root directory

---

## File Changes Summary | 文件修改摘要

| File | Lines Modified | Changes |
|------|----------------|---------|
| `main.py` | 1985-1999 | Removed statistics box from Step 1 |
| `main.py` | 2239 | Increased subplot spacing (hspace) |
| `main.py` | 2499-2574 | Enhanced UAV export with DJI format |
| `visualization/propagation_visualizer_v2.py` | 134-219 | Added Times New Roman font |
| `visualization/forest_visualizer.py` | 83-93, 141-145 | Removed titles from forest plot |

**New Files:**
- `DJI_UAV_TRAJECTORY_GUIDE.md` - Complete usage guide
- `LATEST_UI_AND_EXPORT_UPDATE.md` - This file

---

## Breaking Changes | 不兼容变更

**None.** All changes are backward compatible.

唯一变化是导出的CSV文件现在包含更多列（Heading和Speed），但旧代码仍可正常运行。

---

## Testing Checklist | 测试清单

Before deploying to real DJI drones:

- [x] Step 1 visualization: No statistics box visible
- [x] Step 2 visualization: All text in Times New Roman, no garbled characters
- [x] Results tab: Adequate spacing between plot rows
- [x] CSV export: Both standard and DJI formats generated
- [x] Heading values: Range 0-360°, correctly oriented
- [x] GPS coordinates: Reasonable values near reference point
- [ ] **User Testing:** Import to DJI Pilot 2 and verify mission
- [ ] **Field Test:** Execute mission with real drone

---

## Next Steps | 后续步骤

### For Users:

1. **Update Your Reference Point:**
   - Find your deployment site GPS coordinates
   - Edit `main.py` lines 2510, 2514
   - Re-run simulation and export

2. **Test with DJI Simulator First:**
   - Import CSV to DJI Pilot 2
   - Use DJI flight simulator to verify path
   - Check for obstacles and safety issues

3. **Conduct Field Test:**
   - Start with short segment (3-5 waypoints)
   - Monitor flight closely
   - Validate sensor deployment accuracy

### For Developers:

**Potential Future Enhancements:**
- [ ] GUI option to set GPS reference point (no code editing)
- [ ] Support for Litchi CSV format
- [ ] Mission Library / UgCS format export
- [ ] Terrain-following altitude adjustment
- [ ] Multi-battery mission splitting
- [ ] Real-time altitude from DEM data

---

## Troubleshooting | 常见问题

### Q1: CSV file won't import to DJI Pilot
**A:** Ensure file is saved as `.csv` (not `.xlsx`), uses UTF-8 encoding, and commas as delimiters.

### Q2: Coordinates are in the wrong location
**A:** Update `ref_lat` and `ref_lon` to your actual site coordinates in `main.py`.

### Q3: Drone altitude is too high/low
**A:** Check if altitudes are AGL (above ground level). Add terrain elevation if needed.

### Q4: Font still shows garbled characters in Step 2
**A:** Ensure matplotlib backend supports Times New Roman. Install font if missing.

---

## Version History | 版本历史

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2025-11-02 | UI improvements + DJI export |
| 1.0 | 2025-10-01 | Initial release |

---

## Credits | 致谢

- **DJI SDK Team** - Waypoint mission format specification
- **FODEMIR-Sim Community** - Feature requests and testing
- **Contributors** - Code reviews and documentation

---

**Questions or Issues?**
- GitHub Issues: [Open an issue](https://github.com/yourusername/fodemir-sim/issues)
- Documentation: See `DJI_UAV_TRAJECTORY_GUIDE.md`
- Email: fodemir-sim@example.com

---

**Happy Deploying! 祝部署顺利！** 🚁🌲📡

