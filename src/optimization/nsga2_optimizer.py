"""
NSGA-II Optimizer

Non-dominated Sorting Genetic Algorithm II for multi-objective optimization.
"""

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.core.sampling import Sampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from typing import Dict, Optional
from .problem_definition import DeploymentProblem


class ClusterBasedSampling(Sampling):
    """
    Custom sampling strategy for cluster-based sensor deployment.
    
    Sensors are initialized in a radial pattern around the gateway center,
    with controlled spacing to promote efficient coverage while minimizing
    the number of sensors needed.
    """
    
    def __init__(self, gateway_center: np.ndarray, domain_bounds: tuple):
        """
        Initialize cluster-based sampling.
        
        Args:
            gateway_center: [x, y] coordinates of gateway (forest center)
            domain_bounds: (width, height) of deployment domain
        """
        super().__init__()
        self.gateway_center = gateway_center
        self.width, self.height = domain_bounds
    
    def _do(self, problem, n_samples, **kwargs):
        """
        Generate initial population with cluster-based layout and boundary coverage.
        
        Args:
            problem: Optimization problem instance
            n_samples: Number of samples to generate (population size)
        
        Returns:
            Array of shape (n_samples, n_var) with sensor positions
        """
        n_var = problem.n_var  # Total variables (n_sensors * 2 for x,y)
        n_sensors = n_var // 2
        
        # Initialize population array
        X = np.zeros((n_samples, n_var))
        
        # Gateway center
        cx, cy = self.gateway_center
        
        for i in range(n_samples):
            # Create a radial cluster pattern with some variation per individual
            positions = []
            
            # Strategy: Mix of grid layout and boundary emphasis for 100% coverage
            # For 100% coverage with 300m radius, need strategic placement
            
            # Calculate optimal grid size for base coverage
            grid_cols = max(2, int(np.ceil(self.width / 600)))  # 600m spacing (2×300m radius)
            grid_rows = max(2, int(np.ceil(self.height / 600)))
            n_grid = grid_cols * grid_rows
            
            # Allocate: 60% grid-based, 40% boundary-focused
            n_grid_sensors = min(n_sensors, int(n_sensors * 0.6))
            n_boundary = n_sensors - n_grid_sensors
            
            # Calculate max radius to cover entire area including boundaries
            # Distance from center to corner
            max_radius_needed = np.sqrt((self.width - cx)**2 + (self.height - cy)**2)
            
            sensor_idx = 0
            
            # STEP 1: Place boundary sensors along all four edges
            if n_boundary > 0:
                # Generate boundary points distributed along all four edges
                boundary_points = []
                
                # Calculate how many sensors per edge (distribute evenly)
                sensors_per_edge = n_boundary // 4
                extra_sensors = n_boundary % 4
                
                # Bottom edge (y ≈ 5% of height)
                for k in range(sensors_per_edge + (1 if extra_sensors > 0 else 0)):
                    x = (k + 1) * self.width / (sensors_per_edge + 2) + np.random.uniform(-30, 30)
                    y = 0.05 * self.height + np.random.uniform(-20, 20)
                    boundary_points.append((x, y))
                
                # Top edge (y ≈ 95% of height)
                for k in range(sensors_per_edge + (1 if extra_sensors > 1 else 0)):
                    x = (k + 1) * self.width / (sensors_per_edge + 2) + np.random.uniform(-30, 30)
                    y = 0.95 * self.height + np.random.uniform(-20, 20)
                    boundary_points.append((x, y))
                
                # Left edge (x ≈ 5% of width)
                for k in range(sensors_per_edge + (1 if extra_sensors > 2 else 0)):
                    x = 0.05 * self.width + np.random.uniform(-20, 20)
                    y = (k + 1) * self.height / (sensors_per_edge + 2) + np.random.uniform(-30, 30)
                    boundary_points.append((x, y))
                
                # Right edge (x ≈ 95% of width)
                for k in range(sensors_per_edge):
                    x = 0.95 * self.width + np.random.uniform(-20, 20)
                    y = (k + 1) * self.height / (sensors_per_edge + 2) + np.random.uniform(-30, 30)
                    boundary_points.append((x, y))
                
                # Place all boundary sensors
                for j in range(min(n_boundary, len(boundary_points))):
                    x, y = boundary_points[j]
                    x = np.clip(x, 0, self.width)
                    y = np.clip(y, 0, self.height)
                    positions.extend([x, y])
                    sensor_idx += 1
            
            # STEP 2: Place grid-based sensors for systematic coverage
            if n_grid_sensors > 0:
                # Create grid with some randomization for diversity
                spacing_x = self.width / (grid_cols + 1)
                spacing_y = self.height / (grid_rows + 1)
                
                grid_idx = 0
                for row in range(grid_rows):
                    for col in range(grid_cols):
                        if grid_idx >= n_grid_sensors:
                            break
                        
                        # Base grid position (evenly spaced)
                        x = (col + 1) * spacing_x
                        y = (row + 1) * spacing_y
                        
                        # Add randomization for population diversity
                        x += np.random.uniform(-80, 80)
                        y += np.random.uniform(-80, 80)
                        
                        x = np.clip(x, 0, self.width)
                        y = np.clip(y, 0, self.height)
                        
                        positions.extend([x, y])
                        sensor_idx += 1
                        grid_idx += 1
                    
                    if grid_idx >= n_grid_sensors:
                        break
            
            # STEP 3: Place remaining sensors using radial pattern
            n_remaining = n_sensors - sensor_idx
            n_rings = max(1, int(np.sqrt(n_remaining)))
            sensors_per_ring = max(1, n_remaining // n_rings) if n_rings > 0 else 0
            
            # Add randomization factor for diversity (50-150% of base radius)
            radius_variation = np.random.uniform(0.5, 1.5)
            
            for ring in range(n_rings):
                # Base radius for this ring (covering forest efficiently)
                # Distribute sensors from center to boundary
                # Scale radius to ensure outer ring reaches boundaries
                ring_fraction = (ring + 1) / n_rings
                base_radius = max_radius_needed * ring_fraction * radius_variation
                
                # Number of sensors in this ring (more sensors in outer rings)
                n_in_ring = min(sensors_per_ring * (ring + 1), n_sensors - sensor_idx)
                
                # Angular distribution
                for j in range(n_in_ring):
                    if sensor_idx >= n_sensors:
                        break
                    
                    # Angle with some randomization for diversity
                    angle = 2 * np.pi * j / n_in_ring + np.random.uniform(-0.2, 0.2)
                    
                    # Add radial jitter (±30m) for diversity
                    r = base_radius + np.random.uniform(-30, 30)
                    
                    # Calculate position
                    x = cx + r * np.cos(angle)
                    y = cy + r * np.sin(angle)
                    
                    # Clamp to domain bounds
                    x = np.clip(x, 0, self.width)
                    y = np.clip(y, 0, self.height)
                    
                    positions.extend([x, y])
                    sensor_idx += 1
            
            # STEP 4: Fill any remaining sensors randomly across entire area
            while sensor_idx < n_sensors:
                angle = np.random.uniform(0, 2 * np.pi)
                # Use full range from center to max boundary
                r = np.random.uniform(0, max_radius_needed)
                x = cx + r * np.cos(angle)
                y = cy + r * np.sin(angle)
                x = np.clip(x, 0, self.width)
                y = np.clip(y, 0, self.height)
                positions.extend([x, y])
                sensor_idx += 1
            
            X[i, :] = positions[:n_var]
        
        return X


class NSGA2Optimizer:
    """
    NSGA-II optimizer for sensor deployment.
    
    Features:
    - Non-dominated sorting
    - Crowding distance for diversity
    - Simulated binary crossover (SBX)
    - Polynomial mutation (PM)
    """
    
    def __init__(self, problem: DeploymentProblem,
                 population_size: int = 100,
                 n_generations: int = 200,
                 crossover_prob: float = 0.9,
                 crossover_eta: float = 15,
                 mutation_prob: Optional[float] = None,
                 mutation_eta: float = 20,
                 seed: Optional[int] = None,
                 use_cluster_sampling: bool = True,
                 gateway_center: Optional[np.ndarray] = None,
                 domain_bounds: Optional[tuple] = None):
        """
        Initialize NSGA-II optimizer.
        
        Args:
            problem: DeploymentProblem instance
            population_size: Population size
            n_generations: Maximum number of generations
            crossover_prob: Crossover probability
            crossover_eta: Crossover distribution index
            mutation_prob: Mutation probability (default: 1/n_var)
            mutation_eta: Mutation distribution index
            seed: Random seed
            use_cluster_sampling: Whether to use cluster-based sampling (default: True)
            gateway_center: Gateway center coordinates [x, y] for cluster sampling
            domain_bounds: Domain bounds (width, height) for cluster sampling
        """
        self.problem = problem
        self.population_size = population_size
        self.n_generations = n_generations
        self.seed = seed
        
        # Set mutation probability
        if mutation_prob is None:
            mutation_prob = 1.0 / problem.n_var
        
        # Select sampling strategy
        if use_cluster_sampling and gateway_center is not None and domain_bounds is not None:
            # Use cluster-based sampling for efficient radial deployment
            sampling = ClusterBasedSampling(gateway_center, domain_bounds)
        else:
            # Fall back to random sampling
            sampling = FloatRandomSampling()
        
        # Initialize NSGA-II algorithm
        self.algorithm = NSGA2(
            pop_size=population_size,
            sampling=sampling,
            crossover=SBX(prob=crossover_prob, eta=crossover_eta),
            mutation=PM(prob=mutation_prob, eta=mutation_eta),
            eliminate_duplicates=True
        )
        
        # Termination criterion
        self.termination = get_termination("n_gen", n_generations)
        
        # Results storage
        self.result = None
        self.history = []
    
    def optimize(self, verbose: bool = True, save_history: bool = True) -> Dict:
        """
        Run NSGA-II optimization.
        
        Args:
            verbose: Whether to print progress
            save_history: Whether to save generation history
        
        Returns:
            Dictionary with optimization results
        """
        # Run optimization
        self.result = minimize(
            self.problem,
            self.algorithm,
            self.termination,
            seed=self.seed,
            save_history=save_history,
            verbose=verbose
        )
        
        # Extract results
        results = self._process_results()
        
        return results
    
    def _process_results(self) -> Dict:
        """
        Process optimization results.
        
        Returns:
            Dictionary with Pareto front and solutions
        """
        if self.result is None:
            return {}
        
        # Get Pareto front
        pareto_front = self.result.F
        pareto_solutions = self.result.X
        
        # Decode solutions
        n_solutions = len(pareto_solutions)
        decoded_solutions = []
        
        for i in range(n_solutions):
            sensor_positions = pareto_solutions[i].reshape(-1, 2)
            decoded_solutions.append({
                'solution_id': i,
                'sensor_positions': sensor_positions,
                'objectives': {
                    'blind_area_ratio': pareto_front[i, 0],
                    'node_count': pareto_front[i, 1],
                    'network_energy': pareto_front[i, 2],
                    'flight_distance': pareto_front[i, 3]
                }
            })
        
        results = {
            'pareto_front': pareto_front,
            'pareto_solutions': pareto_solutions,
            'decoded_solutions': decoded_solutions,
            'n_solutions': n_solutions,
            'n_generations': self.result.algorithm.n_gen,
            'n_evaluations': self.result.algorithm.evaluator.n_eval,
            'execution_time': self.result.exec_time if hasattr(self.result, 'exec_time') else None
        }
        
        # Add history if available
        if self.result.history is not None and len(self.result.history) > 0:
            results['history'] = self._process_history()
        
        return results
    
    def _process_history(self) -> Dict:
        """
        Process optimization history.
        
        Returns:
            Dictionary with generation-wise metrics
        """
        history = {
            'generations': [],
            'n_solutions': [],
            'hypervolume': [],
            'best_objectives': []
        }
        
        for gen_idx, entry in enumerate(self.result.history):
            history['generations'].append(gen_idx)
            history['n_solutions'].append(len(entry.opt))
            
            # Best values in each objective
            if len(entry.opt) > 0:
                opt_f = entry.opt.get("F")
                best_obj = np.min(opt_f, axis=0)
                history['best_objectives'].append(best_obj)
        
        return history
    
    def get_pareto_front(self) -> np.ndarray:
        """
        Get Pareto front objective values.
        
        Returns:
            Array of shape (n_solutions, n_objectives)
        """
        if self.result is None:
            return np.array([])
        
        return self.result.F
    
    def get_pareto_solutions(self) -> np.ndarray:
        """
        Get Pareto optimal solution vectors.
        
        Returns:
            Array of shape (n_solutions, n_variables)
        """
        if self.result is None:
            return np.array([])
        
        return self.result.X
    
    def select_solution_by_criteria(self, criterion: str = 'balanced') -> Optional[np.ndarray]:
        """
        Select a single solution from Pareto front based on criterion.
        
        Args:
            criterion: Selection criterion
                'balanced' - closest to ideal point
                'max_coverage' - minimum blind area ratio
                'min_nodes' - minimum node count
                'min_energy' - minimum energy
                'min_distance' - minimum flight distance
                'quality_priority' - prioritize communication quality and coverage with minimum sensors
        
        Returns:
            Selected solution vector
        """
        if self.result is None or len(self.result.F) == 0:
            return None
        
        pareto_front = self.result.F
        pareto_solutions = self.result.X
        
        if criterion == 'balanced':
            # Normalize objectives and find closest to ideal point (0,0,0,0)
            f_min = np.min(pareto_front, axis=0)
            f_max = np.max(pareto_front, axis=0)
            f_range = f_max - f_min
            f_range[f_range == 0] = 1  # Avoid division by zero
            
            f_norm = (pareto_front - f_min) / f_range
            distances = np.sqrt(np.sum(f_norm**2, axis=1))
            idx = np.argmin(distances)
        
        elif criterion == 'max_coverage':
            idx = np.argmin(pareto_front[:, 0])  # Min blind area ratio
        
        elif criterion == 'min_nodes':
            idx = np.argmin(pareto_front[:, 1])  # Min node count
        
        elif criterion == 'min_energy':
            idx = np.argmin(pareto_front[:, 2])  # Min energy
        
        elif criterion == 'min_distance':
            idx = np.argmin(pareto_front[:, 3])  # Min flight distance
        
        elif criterion == 'quality_priority':
            # Prioritize: low blind area (high coverage) + low node count
            # Weighted score: 70% coverage quality + 30% sensor count efficiency
            f_min = np.min(pareto_front, axis=0)
            f_max = np.max(pareto_front, axis=0)
            f_range = f_max - f_min
            f_range[f_range == 0] = 1
            
            # Normalize first two objectives
            f_norm = (pareto_front - f_min) / f_range
            
            # Combined score: prioritize coverage (blind area) and minimize sensors
            scores = 0.7 * f_norm[:, 0] + 0.3 * f_norm[:, 1]
            idx = np.argmin(scores)
        
        else:
            idx = 0  # Default to first solution
        
        return pareto_solutions[idx]


