# RSSI Network Visualization Update
# RSSI网络可视化更新

**Date:** November 2, 2025  
**Version:** 1.2

---

## Summary | 更新摘要

Step 2 visualization has been completely redesigned to show **RSSI (Received Signal Strength Indicator)** instead of SNR, with **sensor network communication links** visualized to demonstrate inter-sensor connectivity.

Step 2 的可视化已完全重新设计，显示 **RSSI（接收信号强度指示）** 而不是 SNR，并可视化**传感器网络通信链路**以展示传感器间的连接性。

---

## Key Changes | 主要变更

### 1. ✅ RSSI Coverage Map (替代 SNR)

**Previous:** Signal-to-Noise Ratio (SNR) in dB  
**Now:** Received Signal Strength Indicator (RSSI) in dBm

**Why RSSI?**
- **直接测量值**: RSSI is the actual received power measurement
- **实际通信参数**: Used by real sensor networks (LoRa, Zigbee, Wi-Fi)
- **工程标准**: Industry standard for wireless communication quality
- **可操作性**: Easier to compare with real-world deployments

**RSSI Range:**
- `-60 to -70 dBm`: Excellent signal (绿色)
- `-70 to -80 dBm`: Good signal (黄绿色)
- `-80 to -90 dBm`: Fair signal (黄色)
- `-90 to -100 dBm`: Weak signal (橙色)
- `-100 to -120 dBm`: Very weak signal (红色)

---

### 2. ✅ Sensor Network Communication Links
**传感器网络通信链路可视化**

**New Feature:** Visualizes actual communication links between sensors based on RSSI values.

**Link Types:**

#### Strong Links (强连接) - Green/Lime
- **RSSI > -80 dBm**
- **Line Style:** Solid, thick (2.5pt)
- **Color:** Lime green
- **Transparency:** 80%
- **Meaning:** Excellent communication quality, high data rate

#### Good Links (良好连接) - Yellow
- **-90 dBm < RSSI < -80 dBm**
- **Line Style:** Solid, medium (2.0pt)
- **Color:** Yellow
- **Transparency:** 60%
- **Meaning:** Good communication quality, reliable

#### Weak Links (弱连接) - Orange
- **-95 dBm < RSSI < -90 dBm**
- **Line Style:** Solid, thin (1.5pt)
- **Color:** Orange
- **Transparency:** 40%
- **Meaning:** Usable but marginal, may have packet loss

#### Gateway Links (网关连接) - Cyan
- **Sensor ↔ Gateway connections**
- **Line Style:** Dashed (2.5pt)
- **Color:** Cyan/Blue gradient
- **Transparency:** 50-70%
- **Meaning:** Direct connection to central gateway

---

### 3. ✅ Communication Range Constraints
**通信范围约束**

**Parameters:**
- **Maximum Communication Range:** 300 meters
- **Minimum RSSI Threshold:** -95 dBm
- **Link Calculation:** Accounts for forest vegetation attenuation

**Algorithm:**
```python
# For each sensor pair (i, j):
distance = sqrt((x_i - x_j)² + (y_i - y_j)²)

if distance <= 300m:
    RSSI = calculate_link_with_vegetation_loss(pos_i, pos_j, trees)
    
    if RSSI >= -95 dBm:
        draw_communication_link(color_based_on_RSSI)
```

---

### 4. ✅ Enhanced Statistics Box
**增强统计信息框**

**Now Displays:**
```
Network Statistics
───────────────
Mean RSSI: -82.5 dBm
Min RSSI: -110.2 dBm
Max RSSI: -65.3 dBm
Coverage: 94.2%
```

**Previous (SNR):**
```
Network Statistics
───────────────
Mean SNR: 15.2 dB
Min SNR: -5.8 dB
Max SNR: 28.4 dB
Coverage: 94.2%
```

---

### 5. ✅ Times New Roman Font (No Garbled Characters)
**Times New Roman 字体（无乱码）**

**All text elements now use Times New Roman:**
- Axis labels
- Title
- Colorbar label
- Statistics box
- Legend
- Colorbar tick labels

**No more Chinese character display issues!**

---

## Technical Implementation | 技术实现

### Code Changes in `main.py`

#### Change 1: Coverage Calculation (Line ~843)
```python
# Before:
coverage_map = coverage.calculate_coverage_map(
    gateway_positions, link_calc,
    tree_positions, crown_radii, metric='snr'
)

# After:
coverage_map = coverage.calculate_coverage_map(
    gateway_positions, link_calc,
    tree_positions, crown_radii, metric='rssi'  # Changed to RSSI
)
```

#### Change 2: Store Link Calculator (Line ~851)
```python
results['propagation'] = {
    'coverage_map': coverage_map,
    'gateway_positions': gateway_positions,
    'extent': (0, width, 0, height),
    'metric': 'rssi',  # Store metric type
    'link_calculator': link_calc  # Store for visualization
}
```

#### Change 3: RSSI Heatmap Range (Line ~2019)
```python
# Before: vmin=-10, vmax=30 (SNR in dB)
# After: vmin=-120, vmax=-60 (RSSI in dBm)

im = ax.imshow(coverage_map, extent=extent, origin='lower',
             cmap='RdYlGn', vmin=-120, vmax=-60, alpha=0.85, aspect='auto')
```

#### Change 4: Communication Link Drawing (Lines ~2032-2113)

**Pseudo-code:**
```python
for each sensor pair (i, j):
    distance = calculate_distance(sensor_i, sensor_j)
    
    if distance <= 300m:
        rssi = calculate_RSSI_through_forest(sensor_i, sensor_j)
        
        if rssi >= -95 dBm:
            # Determine link quality color
            if rssi > -80: color = 'lime'      # Strong
            elif rssi > -90: color = 'yellow'  # Good
            else: color = 'orange'             # Weak
            
            draw_line(sensor_i, sensor_j, color)

# Also draw gateway links
for each sensor:
    distance = calculate_distance(sensor, gateway)
    if distance <= 300m:
        rssi = calculate_RSSI_through_forest(sensor, gateway)
        if rssi >= -95 dBm:
            draw_dashed_line(sensor, gateway, cyan)
```

#### Change 5: Legend for Communication Links (Lines ~2172-2187)
```python
legend_elements = [
    Line2D([0], [0], color='lime', linewidth=2.5, 
           label='Strong Link (RSSI > -80 dBm)'),
    Line2D([0], [0], color='yellow', linewidth=2.0, 
           label='Good Link (-90 < RSSI < -80 dBm)'),
    Line2D([0], [0], color='orange', linewidth=1.5, 
           label='Weak Link (RSSI < -90 dBm)'),
    Line2D([0], [0], color='cyan', linewidth=2.5, linestyle='--',
           label='Gateway Link')
]
```

---

## Visualization Features | 可视化特性

### Layer Order (Z-Order)
1. **Background**: Forest aerial image or grass color (z=0)
2. **Coverage Heatmap**: RSSI spatial distribution (z=1)
3. **Tree Crowns**: Semi-transparent circles (z=2)
4. **Communication Links**: Colored lines between sensors (z=7)
5. **Sensors**: Glow effect + markers (z=8-9)
6. **Gateway**: Highlighted red square (z=10-11)
7. **Labels & Text**: Statistics box, titles (z=12-15)

### Color Scheme
- **RSSI Heatmap**: Red-Yellow-Green gradient
  - Red: Weak signal (-120 to -100 dBm)
  - Yellow: Medium signal (-100 to -80 dBm)
  - Green: Strong signal (-80 to -60 dBm)

- **Communication Links**:
  - Lime: RSSI > -80 dBm (excellent)
  - Yellow: -90 < RSSI < -80 dBm (good)
  - Orange: RSSI < -90 dBm (weak)
  - Cyan: Gateway links

- **Nodes**:
  - Blue sensors with white edges
  - Red gateway with white glow

---

## Interpretation Guide | 解读指南

### Understanding RSSI Values

| RSSI Range (dBm) | Quality | Description | Color |
|------------------|---------|-------------|-------|
| -30 to -50 | Amazing | Maximum signal | Dark Green |
| -50 to -60 | Excellent | Very strong | Green |
| -60 to -70 | Very Good | Strong signal | Yellow-Green |
| -70 to -80 | Good | Reliable | Yellow |
| -80 to -90 | Fair | Usable | Orange |
| -90 to -100 | Weak | Marginal | Red-Orange |
| < -100 | Very Weak | Unreliable | Red |

### Network Connectivity Analysis

**What to Look For:**

1. **Network Density**
   - **Many Links**: Well-connected network, redundant paths
   - **Few Links**: Sparse network, risk of disconnection

2. **Link Quality Distribution**
   - **Mostly Green/Yellow**: Healthy network
   - **Many Orange Links**: Network at risk, consider adding nodes

3. **Gateway Connectivity**
   - **All Sensors → Gateway (Cyan)**: Good coverage
   - **Missing Gateway Links**: Sensors out of range, need relays

4. **Isolated Nodes**
   - **Sensors without Links**: Disconnected, cannot communicate
   - **Solution**: Add relay nodes or reposition sensors

5. **Coverage Gaps**
   - **Red Areas in Heatmap**: Blind spots
   - **Solution**: Deploy additional sensors

---

## Comparison: RSSI vs SNR | 对比

### RSSI (Received Signal Strength Indicator)
- **Unit:** dBm (absolute power)
- **Range:** -120 to -30 dBm (typical)
- **Meaning:** Actual received power at antenna
- **Advantages:**
  - Direct hardware measurement
  - Used by all commercial devices
  - Easy to interpret
  - Includes path loss and fading
- **Use Case:** Network planning, deployment, coverage

### SNR (Signal-to-Noise Ratio)
- **Unit:** dB (relative)
- **Range:** -10 to +30 dB (typical)
- **Meaning:** Signal power vs noise power ratio
- **Advantages:**
  - Better for data rate prediction
  - Independent of absolute power
  - Better for modulation analysis
- **Use Case:** Link budget analysis, modulation selection

**Our Choice: RSSI**  
More relevant for sensor network deployment and matches industry practice.

---

## Real-World Application | 实际应用

### LoRa Sensor Networks

**RSSI Guidelines for LoRa (868 MHz):**
- **-120 dBm**: Sensitivity limit (SF12, BW125)
- **-95 dBm**: Practical minimum for reliable communication
- **-80 dBm**: Recommended for good performance
- **-60 dBm**: Excellent signal, high data rate possible

**Spreading Factor (SF) Selection:**
| RSSI Range | Recommended SF | Data Rate |
|------------|----------------|-----------|
| > -80 dBm | SF7 | 5.5 kbps |
| -80 to -90 | SF8-SF9 | 3.1 kbps |
| -90 to -100 | SF10-SF11 | 1.1 kbps |
| < -100 dBm | SF12 | 250 bps |

---

## File Changes Summary | 文件修改摘要

| File | Lines | Changes |
|------|-------|---------|
| `main.py` | 843 | Changed metric from 'snr' to 'rssi' |
| `main.py` | 851 | Added link_calculator to results |
| `main.py` | 2014 | Retrieve link_calculator for visualization |
| `main.py` | 2019 | Updated colormap range for RSSI (-120 to -60) |
| `main.py` | 2032-2113 | Added communication link drawing algorithm |
| `main.py` | 2135-2151 | Updated labels and statistics for RSSI |
| `main.py` | 2172-2187 | Added communication link legend |

**New Files:**
- `RSSI_NETWORK_VISUALIZATION_UPDATE.md` (this file)

---

## Testing Checklist | 测试清单

- [x] RSSI coverage map displays correctly
- [x] Communication links drawn between sensors
- [x] Link colors match RSSI quality
- [x] Gateway links shown in cyan/dashed
- [x] Legend displays all link types
- [x] Statistics box shows RSSI values
- [x] Times New Roman font, no garbled text
- [x] Colorbar range appropriate (-120 to -60 dBm)
- [ ] **User Testing**: Verify with real forest scenario

---

## Future Enhancements | 未来改进

**Potential Features:**

1. **Dynamic Link Quality**
   - [ ] Animate link quality over time
   - [ ] Show packet loss statistics per link

2. **Network Topology Analysis**
   - [ ] Calculate network connectivity metrics
   - [ ] Identify critical nodes (bridges)
   - [ ] Show shortest paths to gateway

3. **Multi-Hop Routing**
   - [ ] Visualize routing tables
   - [ ] Show data flow paths
   - [ ] Highlight congestion points

4. **Interference Modeling**
   - [ ] Add co-channel interference
   - [ ] Model adjacent network effects

5. **Energy Considerations**
   - [ ] Color links by energy cost
   - [ ] Show battery drain per link

---

## FAQ | 常见问题

### Q1: Why use RSSI instead of SNR?
**A:** RSSI is the actual measurement available in real sensors. It's more practical for deployment planning.

### Q2: What if sensors have no communication links?
**A:** Either they're too far apart (>300m) or vegetation attenuation is too severe. Add relay nodes.

### Q3: Can I adjust the communication range?
**A:** Yes, modify `comm_range = 300.0` in line ~2035 of `main.py`.

### Q4: What if all links are orange (weak)?
**A:** Consider: (1) Add more sensors for redundancy, (2) Use higher transmit power, (3) Deploy sensors in clearings.

### Q5: How to export RSSI data?
**A:** Use "Export Complete Report" button. RSSI map and link quality will be saved in CSV format.

---

## Contact & Support | 联系与支持

- **GitHub Issues**: Report bugs or request features
- **Documentation**: See README.md and other guides
- **Email**: fodemir-sim@example.com

---

**Version History:**

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2025-11-02 | RSSI visualization + network links |
| 1.1 | 2025-11-02 | DJI export + UI improvements |
| 1.0 | 2025-10-01 | Initial release |

---

**Enjoy the Enhanced Network Visualization! 享受增强的网络可视化！** 📡🌲✨

