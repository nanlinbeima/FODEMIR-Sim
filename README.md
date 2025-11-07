# FODEMIR-Sim: Forest Deployment Optimization via EM & Multi-objective Integrated Research Simulator

**森林传感器网络部署优化仿真系统**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt-6.4+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Overview

FODEMIR-Sim is a comprehensive simulation framework for optimizing wireless sensor network deployment in forest environments. It integrates four key components:

1. **GPT-Based Forest Map Generation** - AI-generated realistic forest structures with species diversity
2. **EM Propagation Modeling** - Three vegetation attenuation models (Weissberger, COST235, ITU-R P.833)
3. **Multi-Objective Optimization** - NSGA-II/SMPSO algorithms for Pareto-optimal sensor placement
4. **UAV Path Planning** - TSP-based trajectory optimization with energy consumption modeling

## ✨ Key Features

### 🌲 Forest Generation Module
- **GPT-4 Integration**: Natural language forest specification
- **Poisson-Disk Sampling**: Spatially-constrained tree positioning
- **Allometric Modeling**: Species-specific DBH, height, and crown diameter relationships
- **GeoJSON Export**: Standard geospatial data formats

### 📡 EM Propagation Module
- **Three Propagation Models**:
  - Weissberger (Modified Exponential Decay)
  - COST235 (European vegetation model)
  - ITU-R P.833 (ITU recommendation)
- **Link Budget Calculator**: FSPL + vegetation loss + ground reflection
- **Coverage Analyzer**: Grid-based SNR/RSSI heatmaps
- **Blind Spot Detection**: Automatic identification of coverage gaps

### 🎯 Multi-Objective Optimization
- **Algorithms**: NSGA-II, SMS-EMOA (Pymoo framework)
- **Four Objectives**:
  1. Minimize blind area ratio (maximize coverage)
  2. Minimize sensor node count
  3. Minimize network energy consumption
  4. Minimize UAV flight distance
- **Constraints**:
  - Minimum sensor spacing
  - No-drop zones (water bodies, cliffs)
  - Communication reachability (SNR threshold)
  - UAV payload and range limits

### 🚁 UAV Path Planning
- **TSP Solvers**: Nearest neighbor, Christofides, OR-Tools
- **3D Trajectory Generation**: B-spline smoothing with altitude optimization
- **Energy Model**: Horizontal flight + vertical climb + hovering energy
- **Battery Feasibility**: Automated mission viability checking

### 🖥️ Professional GUI
- **PyQt6 Interface**: Modern, responsive desktop application
- **Times New Roman 25pt**: Publication-quality typography
- **Chinese Labels**: Full bilingual support (English code, Chinese UI)
- **Four-Panel Visualization**: Integrated matplotlib canvas
- **Real-Time Progress**: Multi-threaded simulation with live updates

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- 8GB+ RAM recommended
- Optional: OpenAI API key for GPT-based forest generation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/fodemir-sim.git
cd fodemir-sim
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure (Optional)

If using GPT-4 forest generation:

```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## 🚀 Quick Start

### Launch GUI Application

```bash
python main.py
```

### Basic Workflow

1. **Configure Parameters** 
   - Forest area: 100,000 m²
   - Tree density: 500 trees/ha
   - EM model: Weissberger
   - Frequency: 868 MHz (LoRa)
   - Algorithm: NSGA-II
   - Population: 100
   - Generations: 200

2. **Run Simulation** 
   - Step 1: Forest generation (25%)
   - Step 2: EM propagation (50%)
   - Step 3: Optimization (75%)
   - Step 4: UAV planning (90%)

3. **View Results** 
   - **Figure 1**: Forest map with tree species
   - **Figure 2**: Signal coverage heatmap
   - **Figure 3**: Pareto front & deployment
   - **Figure 4**: UAV 3D trajectory

4. **Analyze Solutions** 
   - Browse Pareto-optimal solutions
   - Select solution by criterion
   - View objective trade-offs

5. **Export Data** 
   - PNG/PDF figures (300 DPI)
   - CSV data tables
   - GeoJSON spatial data

## 📊 Example Output

### Figure 1: Forest Distribution Map 
- 2D scatter plot with crown circles
- Species color-coded (pine=green, oak=yellow, etc.)
- Chinese axis labels: "东-西方向 (m)", "南-北方向 (m)"

### Figure 2: EM Coverage Heatmap 
- SNR/RSSI spatial distribution
- Coverage threshold contour lines
- Gateway (triangle) and sensor (circle) markers

### Figure 3: Pareto Front & Deployment 
- 3D scatter of objective space
- Interactive solution selection
- Sensor deployment overlay on coverage map

### Figure 4: UAV Flight Trajectory 
- 3D trajectory with altitude color gradient
- Vertical drop lines at sensor positions
- Inset: Cumulative energy vs. waypoint

## 🛠️ Advanced Configuration

### Custom Configuration File

```json
{
  "forest_generation": {
    "area_m2": 100000,
    "tree_density_per_ha": 500,
    "species_mix": {
      "pine": 40,
      "oak": 30,
      "birch": 20,
      "maple": 10
    }
  },
  "em_propagation": {
    "model": "weissberger",
    "frequency_mhz": 868,
    "tx_power_dbm": 14,
    "snr_threshold_db": 6
  },
  "optimization": {
    "algorithm": "nsga2",
    "nsga2": {
      "population_size": 100,
      "n_generations": 200
    }
  }
}
```

Load custom configuration: `File → Open configuration`

## 📐 Technical Specifications

### Forest Generation
- **Spatial Algorithm**: Poisson-disk sampling (O(n) complexity)
- **Minimum Spacing**: Species-dependent crown diameter
- **Allometric Equations**: Height = a × DBH^b, Crown = c × DBH^d
- **Output Format**: GeoJSON FeatureCollection with Point geometries

### EM Propagation Models

**Weissberger Model**:
```
L_veg = 1.33 × f^0.284 × d^0.588  (dB)
Valid: 14m < d < 400m, 230MHz < f < 95GHz
```

**COST235 Model**:
```
L_veg = 26.6 × f^(-0.2) × d^0.5 × ρ  (dB)
ρ = vegetation density factor (0.5-2.0)
```

**ITU-R P.833 Model**:
```
A = A_m × [1 - exp(-d/d_s)]  (dB)
A_m = max specific attenuation
d_s = characteristic distance
```

### Optimization Algorithms

**NSGA-II**:
- Non-dominated sorting: O(MN²) per generation
- Crowding distance: Euclidean distance in objective space
- Operators: SBX crossover (η=15), Polynomial mutation (η=20)

**SMS-EMOA** (Alternative):
- S-metric (hypervolume) selection
- Steady-state evolution (single offspring per iteration)

### UAV Energy Model

```
E_total = E_horizontal + E_vertical + E_hover

E_horizontal = k_h × distance × mass_factor
E_vertical = k_v × |Δz| × (m_UAV + m_payload)
E_hover = P_hover × time
```

Default parameters:
- k_h = 0.05 Wh/m
- k_v = 0.15 Wh/m/kg
- P_hover = 480 W

## 📚 Module Documentation

### Python API Usage

```python
from src.forest_generation import TreeAttributesDB, PoissonDiskSampler
from src.em_propagation import WeissbergerModel, LinkCalculator
from src.optimization import NSGA2Optimizer, DeploymentProblem
from visualization import ForestVisualizer, OptimizationVisualizer

# Generate forest
tree_db = TreeAttributesDB()
sampler = PoissonDiskSampler(width=500, height=500, min_distance=5)
positions = sampler.sample()

# Calculate propagation
model = WeissbergerModel(frequency_mhz=868)
calculator = LinkCalculator(model, tx_power_dbm=14)
link_params = calculator.calculate_link_loss(tx_pos, rx_pos, tree_positions, crown_radii)

# Optimize deployment
problem = DeploymentProblem(objectives, constraints, n_sensors=20, ...)
optimizer = NSGA2Optimizer(problem, population_size=100, n_generations=200)
results = optimizer.optimize()

# Visualize
vis = OptimizationVisualizer()
vis.plot_pareto_front_3d(results['pareto_front'], objective_names)
```

## 🔬 Research Applications

FODEMIR-Sim is designed for:

- **Forest Monitoring Networks**: Optimal IoT sensor placement for environmental monitoring
- **Wildfire Detection Systems**: Early warning sensor network deployment
- **Ecological Research**: Biodiversity monitoring with minimal infrastructure
- **Telecommunications**: Rural 5G/LoRa network planning in forested areas
- **UAV-Assisted Deployment**: Autonomous sensor delivery optimization

## 📖 Citation

If you use FODEMIR-Sim in your research, please cite:

```bibtex
@software{fodemir_sim_2025,
  title={FODEMIR-Sim: Forest Deployment Optimization via EM and Multi-objective Integrated Research Simulator},
  author={FODEMIR-Sim Development Team},
  year={2025},
  version={1.0.0},
  url={https://github.com/yourusername/fodemir-sim}
}
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Pymoo**: Multi-objective optimization framework
- **PyQt6**: Cross-platform GUI toolkit
- **Matplotlib**: Scientific visualization library
- **OpenAI**: GPT-4 API for intelligent forest generation
- **Google OR-Tools**: Advanced TSP solvers

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/fodemir-sim/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fodemir-sim/discussions)
- **Email**: fodemir-sim@example.com

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Real-world terrain integration (DEM support)
- [ ] Multi-hop routing optimization
- [ ] Battery degradation modeling
- [ ] Weather impact on propagation

### Version 1.2 (Future)
- [ ] 3D forest canopy modeling
- [ ] Ray-tracing propagation simulation
- [ ] Machine learning-based coverage prediction
- [ ] Multi-UAV coordination

---

**Built with ❤️ for forest ecology and wireless sensor networks research**

*Last updated: October 2025*

This project is licensed under the MIT License - see the [LICENSE](https://github.com/nanlinbeima/FODEMIR-Sim/blob/main/LICENSE) file for details.
