# DJI UAV Trajectory Export Guide
# 大疆无人机航迹导出使用指南

## Overview | 概述

FODEMIR-Sim now exports UAV trajectories in two formats compatible with DJI drones:

FODEMIR-Sim 现在可以导出两种与大疆无人机兼容的航迹格式：

1. **Standard CSV Format** - General waypoint data with GPS coordinates
2. **DJI Pilot Format** - Direct import into DJI Pilot app for autonomous missions

---

## Export Process | 导出流程

### Step 1: Run Simulation | 运行仿真

1. Configure your forest and sensor deployment parameters
2. Click "开始仿真" (Start Simulation)
3. Wait for all 4 steps to complete (Forest → Coverage → Optimization → UAV Path)

### Step 2: Export UAV Trajectory | 导出UAV航迹

Two methods to export:

**Method A: Complete Export (Recommended)**
- Go to "Export" tab
- Click "📦 Export Complete Report (All Data)"
- Two CSV files will be generated in `output_data/` folder:
  - `uav_trajectory.csv` - Standard format
  - `uav_trajectory_DJI_Format.csv` - DJI Pilot format

**Method B: Individual Export**
- Go to "Export" tab
- Click "🌍 Export GeoJSON (with GPS Coordinates)"
- CSV files will be generated automatically

---

## File Formats | 文件格式

### 1. Standard CSV Format (`uav_trajectory.csv`)

**Columns:**
```
Waypoint_ID, Local_X_m, Local_Y_m, Altitude_m, Latitude, Longitude, Heading_deg, Speed_m_s
```

**Example:**
```csv
Waypoint_ID,Local_X_m,Local_Y_m,Altitude_m,Latitude,Longitude,Heading_deg,Speed_m_s
0,158.00,158.00,50.00,30.001425,120.001408,45.5,5.0
1,223.45,187.32,50.00,30.001689,120.001990,32.1,5.0
2,312.67,245.89,50.00,30.002217,120.002785,58.3,5.0
...
```

**Usage:**
- Import into flight planning software (Litchi, UgCS, etc.)
- Convert to other waypoint formats
- Analyze trajectory data

---

### 2. DJI Pilot Format (`uav_trajectory_DJI_Format.csv`)

**Columns:**
```
latitude, longitude, altitude(m), heading(deg), curvesize(m), rotationdir, 
gimbalmode, gimbalpitchangle, actiontype1, actionparam1
```

**Example:**
```csv
latitude,longitude,altitude(m),heading(deg),curvesize(m),rotationdir,gimbalmode,gimbalpitchangle,actiontype1,actionparam1
30.001425,120.001408,50.0,45.5,0.2,0,0,-90,-1,0
30.001689,120.001990,50.0,32.1,0.2,0,0,-90,-1,0
30.002217,120.002785,50.0,58.3,0.2,0,0,-90,-1,0
...
```

**Parameters Explained:**
- **latitude/longitude**: GPS coordinates (WGS84)
- **altitude(m)**: Flight altitude above ground level (AGL)
- **heading(deg)**: Aircraft heading (0-360°, 0=North)
- **curvesize(m)**: Turn radius at waypoint (0.2m for smooth flight)
- **rotationdir**: Rotation direction (0=shortest path)
- **gimbalmode**: 0=Disabled, 1=FPV, 2=YawFollow
- **gimbalpitchangle**: Gimbal pitch (-90° = straight down)
- **actiontype1**: Action at waypoint (-1=none, 0=stay, 1=photo, 2=video)
- **actionparam1**: Action parameter (0=default)

---

## Import to DJI Pilot App | 导入到大疆智图

### For DJI Matrice 300 RTK, M30 Series, etc.

**Method 1: DJI Pilot 2 (Recommended for M300 RTK)**

1. Open **DJI Pilot 2** app on your remote controller
2. Navigate to: **飞行** (Flight) → **航线飞行** (Waypoint Mission)
3. Tap **+** button → **导入航线** (Import Waypoint)
4. Select `uav_trajectory_DJI_Format.csv` from your storage
5. Review the flight path on the map
6. Adjust parameters if needed:
   - Flight speed (default 5 m/s)
   - Camera actions at waypoints
   - RTH altitude
7. Save the mission and execute

**Method 2: DJI FlightHub 2 (Cloud Planning)**

1. Open **DJI FlightHub 2** web interface
2. Go to **Mission Library** → **Create New Mission**
3. Select **Waypoint Mission**
4. Click **Import CSV**
5. Upload `uav_trajectory_DJI_Format.csv`
6. Sync mission to your aircraft via cloud

---

## GPS Coordinate Reference | GPS坐标参考点

**⚠️ IMPORTANT:** The exported coordinates use a **default reference point**:
- **Latitude**: 30.0° N
- **Longitude**: 120.0° E

### Customizing Reference Point | 自定义参考点

To use your actual site coordinates, modify the reference point in `main.py`:

**Location:** Line ~2510 and ~2514

```python
# Reference point (user can modify this to their actual site location)
ref_lat = 30.0  # Change to your site latitude
ref_lon = 120.0  # Change to your site longitude
```

**How to find your coordinates:**
1. Open Google Maps or Baidu Maps
2. Find your deployment site
3. Right-click → "What's here?"
4. Copy the latitude and longitude
5. Update `ref_lat` and `ref_lon` in the code
6. Re-run simulation and export

**Example Sites in China:**
- **Beijing Forest Park**: `ref_lat = 40.0, ref_lon = 116.4`
- **Hangzhou West Lake**: `ref_lat = 30.25, ref_lon = 120.15`
- **Kunming**: `ref_lat = 25.04, ref_lon = 102.72`

---

## Flight Safety Checklist | 飞行安全检查清单

Before importing the mission to your DJI drone:

✅ **Pre-Flight Checks:**
1. Verify GPS coordinates are correct for your site
2. Check altitude values are appropriate (AGL, not MSL)
3. Ensure flight path avoids obstacles (trees, buildings, power lines)
4. Confirm battery capacity is sufficient for entire mission
5. Set appropriate flight speed (recommended: 3-7 m/s)
6. Configure RTH (Return to Home) altitude above obstacles
7. Test with a short segment first before full mission

✅ **Regulatory Compliance:**
- Obtain necessary flight permits
- Check airspace restrictions (no-fly zones)
- Follow local drone regulations
- Maintain visual line of sight (if required)
- Have a safety observer

✅ **Equipment:**
- Fully charged batteries (at least 2)
- SD card with sufficient storage
- Remote controller fully charged
- GPS signal strength > 4 satellites

---

## Coordinate System Conversion | 坐标系统转换

The simulator uses a **local Cartesian coordinate system** (meters) with origin at (0, 0).

### Local to GPS Conversion Formula:

```
Latitude = ref_lat + (Y_meters / 111,000)
Longitude = ref_lon + (X_meters / (111,000 × cos(ref_lat)))
```

Where:
- 1° latitude ≈ 111 km (constant)
- 1° longitude ≈ 111 km × cos(latitude) (varies with latitude)

This is an **approximate** conversion suitable for small areas (<10 km × 10 km).

For larger areas or high precision, use professional GIS software with proper projection transformations.

---

## Troubleshooting | 故障排除

### Issue 1: Coordinates are incorrect
**Solution:** Update `ref_lat` and `ref_lon` to your actual site location

### Issue 2: DJI Pilot cannot import CSV
**Problem:** File format not recognized
**Solution:** 
- Ensure file is saved as `.csv` (not `.xlsx`)
- Check CSV uses commas (not semicolons) as delimiters
- Verify no special characters in file path

### Issue 3: Aircraft does not follow exact path
**Cause:** DJI drones use smooth curve interpolation between waypoints
**Solution:** 
- Reduce `curvesize` parameter for sharper turns
- Increase waypoint density for more precise path

### Issue 4: Altitude too high/low
**Problem:** Confusion between AGL (Above Ground Level) and MSL (Mean Sea Level)
**Solution:**
- The simulator exports **AGL** altitudes
- Add terrain elevation if needed for MSL
- Check DJI Pilot altitude mode setting

---

## Advanced Usage | 高级用法

### Adding Camera Actions

Edit the DJI Format CSV to add photo/video capture at waypoints:

```csv
# Take photo at waypoint 5
actiontype1 = 1  (1 = take photo)
actionparam1 = 1  (1 = single shot)

# Start recording at waypoint 10
actiontype1 = 2  (2 = start recording)
actionparam1 = 1  (1 = start)
```

### Multi-Segment Missions

For large deployment areas:
1. Run simulation with smaller sub-areas
2. Export multiple trajectory files
3. Combine in DJI FlightHub 2
4. Execute as sequential missions

### Integration with RTK Base Station

For high-precision deployments:
1. Set up D-RTK 2 Mobile Station
2. Enable RTK positioning in DJI Pilot
3. Import waypoint mission
4. Achieve centimeter-level accuracy

---

## File Locations | 文件位置

After export, find files in:

```
your_project_folder/
├── output_data/
│   ├── uav_trajectory.csv              # Standard format
│   ├── uav_trajectory_DJI_Format.csv   # DJI compatible
│   └── uav_trajectory.geojson          # GIS format
└── output_figures/
    └── step4_uav_trajectory_on_forest.png  # Visualization
```

---

## Supported DJI Models | 支持的大疆机型

**Tested Compatible:**
- DJI Matrice 300 RTK ✅
- DJI Matrice 30/30T ✅
- DJI Mavic 3 Enterprise ✅
- DJI Phantom 4 RTK ✅

**Should Work (untested):**
- DJI M600 Pro
- DJI Inspire 2
- Other DJI enterprise drones with waypoint mission support

**Not Supported:**
- Consumer drones without waypoint mission feature
- Non-DJI drones (use standard CSV format instead)

---

## Contact & Support | 联系与支持

For questions or issues:
- Check project README.md
- Open GitHub issue
- Email: fodemir-sim@example.com

---

## References | 参考资料

- **DJI Pilot 2 User Manual**: https://www.dji.com/support
- **DJI FlightHub 2 Documentation**: https://www.dji.com/flighthub
- **Waypoint Mission Specifications**: DJI SDK Documentation
- **GPS Coordinate Systems**: WGS84 Standard

---

**Version:** 1.0  
**Last Updated:** November 2025  
**Compatible with:** FODEMIR-Sim v1.0+

---

## Quick Reference Card | 快速参考卡

| Item | Value |
|------|-------|
| Default Reference Latitude | 30.0° N |
| Default Reference Longitude | 120.0° E |
| Default Flight Altitude | 50 m AGL |
| Default Speed | 5 m/s |
| Gimbal Pitch | -90° (nadir) |
| CSV Format | UTF-8, Comma-delimited |
| Coordinate System | WGS84 |
| Export Location | `output_data/` folder |

---

**Happy Flying! 安全飞行！** 🚁✨

