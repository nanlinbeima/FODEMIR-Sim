"""
Standalone script to generate Step 2 and Step 3 visualizations using V2 visualizers
"""

import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.forest_generation.poisson_disk_sampler import PoissonDiskSampler
from src.forest_generation.tree_attributes import TreeAttributesDB
from src.em_propagation.weissberger_model import WeissbergerModel
from src.em_propagation.link_calculator import LinkCalculator
from src.em_propagation.coverage_analyzer import CoverageAnalyzer
from src.optimization.objectives import ObjectiveFunctions
from src.optimization.constraints import ConstraintHandler
from src.optimization.problem_definition import DeploymentProblem
from src.optimization.nsga2_optimizer import NSGA2Optimizer

from visualization.plot_config import setup_plot_style
from visualization.propagation_visualizer_v2 import PropagationVisualizerV2
from visualization.optimization_visualizer_v2 import OptimizationVisualizerV2

import matplotlib.pyplot as plt


def main():
    """Generate Step 2 and Step 3 visualizations"""
    
    print("="*70)
    print("Generating New Step 2 and Step 3 Visualizations")
    print("="*70)
    
    # Setup plot style
    setup_plot_style()
    
    # Parameters
    area = 100000  # 100,000 m²
    width = height = np.sqrt(area)
    density = 500  # trees/ha
    n_trees = int(area / 10000 * density)
    
    print(f"\nStep 1: Generating forest ({n_trees} trees)...")
    
    # Generate forest
    tree_db = TreeAttributesDB()
    species_mix = {'pine': 40, 'oak': 30, 'birch': 20, 'maple': 10}
    
    species_list, attributes = tree_db.generate_forest_attributes(
        species_mix, n_trees, dbh_range=(15, 60)
    )
    
    # Sample positions
    min_spacing = 3.0
    sampler = PoissonDiskSampler(width, height, min_spacing)
    positions = sampler.sample(target_count=n_trees)
    
    # Create clearings
    clearings = [
        {'center': np.array([width*0.25, height*0.25]), 'radius': 40},
        {'center': np.array([width*0.75, height*0.75]), 'radius': 35},
        {'center': np.array([width*0.5, height*0.6]), 'radius': 25},
    ]
    
    # Filter out trees in clearings
    filtered_positions = []
    for pos in positions:
        in_clearing = False
        for clearing in clearings:
            dist = np.linalg.norm(pos - clearing['center'])
            if dist < clearing['radius']:
                in_clearing = True
                break
        if not in_clearing:
            filtered_positions.append(pos)
    
    # Trim to actual generated count
    actual_count = min(len(filtered_positions), len(species_list))
    tree_positions = np.array(filtered_positions[:actual_count])
    species_list = species_list[:actual_count]
    crown_radii = attributes['crown_diameter'][:actual_count] / 2
    
    print(f"Generated {actual_count} trees")
    
    # Step 2: EM Propagation
    print("\nStep 2: Calculating EM propagation...")
    
    frequency = 868  # MHz
    model = WeissbergerModel(frequency)
    
    # Place gateway
    gateway_positions = np.array([
        [width*0.5 + np.random.uniform(-50, 50), 
         height*0.5 + np.random.uniform(-50, 50)]
    ])
    
    link_calc = LinkCalculator(
        model,
        tx_power_dbm=14,
        tx_gain_dbi=2.15,
        rx_gain_dbi=2.15
    )
    
    coverage = CoverageAnalyzer(width, height, resolution=20)
    coverage_map = coverage.calculate_coverage_map(
        gateway_positions, link_calc,
        tree_positions, crown_radii, metric='snr'
    )
    
    print("Generating Step 2 visualization...")
    
    # Create Step 2 visualization
    prop_vis = PropagationVisualizerV2()
    fig = prop_vis.plot_em_analysis(
        coverage_map,
        (0, width, 0, height),
        gateway_positions,
        tree_positions,
        crown_radii,
        sensor_positions=None,
        metric='snr'
    )
    
    fig.savefig('output_figures/step2_coverage.png', dpi=300, bbox_inches='tight')
    print("Saved: output_figures/step2_coverage.png")
    plt.close(fig)
    
    # Step 3: Optimization
    print("\nStep 3: Running optimization (this may take 10-20s)...")
    
    objectives = ObjectiveFunctions(
        width, height, gateway_positions,
        link_calc, coverage,
        tree_positions, crown_radii,
        snr_threshold_db=6
    )
    
    constraints = ConstraintHandler(
        width, height,
        min_sensor_spacing=50,
        gateway_positions=gateway_positions,
        link_calculator=link_calc,
        tree_positions=tree_positions,
        crown_radii=crown_radii
    )
    
    # Fast demo mode
    n_sensors = 5
    problem = DeploymentProblem(
        objectives, constraints, n_sensors,
        width, height, depot_position=np.array([0, 0])
    )
    
    optimizer = NSGA2Optimizer(
        problem,
        population_size=20,
        n_generations=10
    )
    
    opt_results = optimizer.optimize(verbose=True)
    
    print("Generating Step 3 visualization...")
    
    # Create Step 3 visualization
    opt_vis = OptimizationVisualizerV2()
    optimization_results = {
        'pareto_front': opt_results.get('pareto_front', np.array([])),
        'history': opt_results.get('history', {})
    }
    
    fig = opt_vis.plot_optimization_analysis(optimization_results)
    fig.savefig('output_figures/step3_pareto.png', dpi=300, bbox_inches='tight')
    print("Saved: output_figures/step3_pareto.png")
    plt.close(fig)
    
    print("\n" + "="*70)
    print("Successfully generated new visualizations!")
    print("Files:")
    print("  - output_figures/step2_coverage.png (V2: dual-panel EM analysis)")
    print("  - output_figures/step3_pareto.png (V2: 6-panel optimization)")
    print("="*70)


if __name__ == "__main__":
    main()

