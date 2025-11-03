# Communication Metrics Update

## Overview

Optimization objectives changed from **deployment metrics** (blind area, energy, flight distance) to **communication performance metrics** with **routing table** display, better reflecting wireless sensor network applications.

---

## New Optimization Objectives

| Metric | Description | Optimization | Quality Threshold |
|--------|-------------|--------------|-------------------|
| **Average SNR** | Network avg signal-to-noise ratio | Maximize | >15dB excellent, 10-15dB good, <10dB poor |
| **Minimum SNR** | Network bottleneck link | Maximize | >10dB excellent, 6-10dB good, <6dB poor |
| **Average Hops** | Routing efficiency | Minimize | ≤1.5 excellent, ≤3.0 good, >3.0 poor |
| **Connectivity** | Network reachability | Maximize | 100% excellent, ≥95% good, <95% poor |

---

## Routing Table

### Display Location
Results tab, below Pareto table

### Columns
1. **Sensor ID** - Sensor node number
2. **Next Hop** - Next hop node
   - "Gateway" - Direct connection (green)
   - "Sensor X" - Relay via sensor (yellow)
   - "No Route" - No route available (red)
3. **Link SNR (dB)** - SNR to next hop
4. **Hops to Gateway** - Hop count to gateway

### Routing Algorithm
**SNR-Based Greedy Routing**:
- Prefer direct gateway link (1 hop)
- Select neighbor closer to gateway
- Choose highest SNR link
- Ensure SNR > threshold (6dB)

---

## Results Table Example

### Pareto Optimal Solutions
| Solution ID | Avg SNR (dB) | Min SNR (dB) | Avg Hops | Connectivity (%) |
|-------------|--------------|--------------|----------|------------------|
| 1 | 18.5 🟢 | 12.3 🟢 | 1.2 🟢 | 100.0% 🟢 |
| 2 | 16.2 🟢 | 10.8 🟡 | 1.5 🟢 | 100.0% 🟢 |
| 3 | 14.7 🟡 | 8.9 🟡 | 2.1 🟡 | 100.0% 🟢 |

### Network Routing Table
| Sensor ID | Next Hop | Link SNR (dB) | Hops to Gateway |
|-----------|----------|---------------|-----------------|
| Sensor 1 | Gateway 🟢 | 18.5 🟢 | 1 🟢 |
| Sensor 2 | Gateway 🟢 | 16.2 🟢 | 1 🟢 |
| Sensor 3 | Sensor 1 🟡 | 12.4 🟡 | 2 🟡 |

---

## Technical Implementation

### New Files
1. **src/optimization/communication_objectives.py** - Communication objective functions
2. **src/optimization/communication_problem.py** - Pymoo-compatible problem definition

### Modified Files
1. **main.py** - Multiple updates:
   - Import communication classes
   - Use `CommunicationObjectives` and `CommunicationProblem`
   - Update Results table headers
   - Add routing table widget
   - Implement `update_routing_table()` method

### Key Changes
```python
# New objectives
objectives = CommunicationObjectives(...)

# New problem
problem = CommunicationProblem(objectives, constraints, ...)

# New table columns
["Solution ID", "Avg SNR (dB)", "Min SNR (dB)", "Avg Hops", "Connectivity (%)"]

# Routing table
routing_table = objectives.get_routing_table(sensor_positions)
```

---

## What Was Removed ❌

- **Energy consumption** (per user request)
- **Flight distance** (per user request)
- **Blind area ratio** (moved to auxiliary metric, not primary objective)

---

## Usage

1. **Run simulation**: `python main.py`
2. **View Results tab**:
   - Pareto table shows communication metrics
   - Routing table shows network paths
3. **Interpret metrics**:
   - Green = Excellent
   - Yellow = Good
   - Red = Needs improvement

---

## FAQ

**Q: Where did energy and flight distance go?**  
A: Removed per user request. Focus shifted to communication performance.

**Q: What does "No Route" mean?**  
A: Sensor's SNR is below threshold, cannot establish link to gateway.

**Q: Why some sensors have 3+ hops?**  
A: Heavy forest attenuation requires multi-hop relay. Add sensors or increase power to improve.

**Q: Is 95% connectivity enough?**  
A: Depends on application. Critical: need 100%. Monitoring: 95% acceptable. System aims for 100%.

---

## Changelog

### Version 1.7.0 (2025-01-30)

**Added**:
- ✨ Communication-oriented objectives (4 new metrics)
- ✨ Routing table generation and display
- ✨ SNR-based greedy routing algorithm
- ✨ Color-coded routing table

**Removed**:
- ❌ Energy consumption objective (user request)
- ❌ Flight distance objective (user request)
- ❌ Blind area as primary objective

**Modified**:
- 📝 Results table changed to communication metrics
- 📝 Added Network Routing Table section
- 📝 Redesigned color coding system

---

**Last Updated**: 2025-01-30  
**Version**: v1.7.0  
**System**: FODEMIR-Sim v1.0.0

---

Run `python main.py` to see professional communication network optimization! 🎉

