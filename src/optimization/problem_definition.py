"""
Deployment Problem Definition

Pymoo-compatible problem definition for sensor deployment optimization.
"""

import numpy as np
from pymoo.core.problem import Problem
from typing import Optional
from .objectives import ObjectiveFunctions
from .constraints import ConstraintHandler


class DeploymentProblem(Problem):
    """
    Multi-objective sensor deployment optimization problem.
    
    Compatible with Pymoo optimization algorithms.
    
    Decision variables: sensor positions (x, y) coordinates
    Objectives: blind area ratio, node count, energy, flight distance
    Constraints: spacing, bounds, connectivity
    """
    
    def __init__(self, objective_functions: ObjectiveFunctions,
                 constraint_handler: ConstraintHandler,
                 n_sensors: int,
                 domain_width: float,
                 domain_height: float,
                 depot_position: Optional[np.ndarray] = None,
                 use_penalties: bool = True):
        """
        Initialize deployment problem.
        
        Args:
            objective_functions: ObjectiveFunctions instance
            constraint_handler: ConstraintHandler instance
            n_sensors: Number of sensors to deploy
            domain_width: Domain width in meters
            domain_height: Domain height in meters
            depot_position: UAV depot position
            use_penalties: Whether to use penalty functions for constraints
        """
        self.objective_functions = objective_functions
        self.constraint_handler = constraint_handler
        self.n_sensors = n_sensors
        self.domain_width = domain_width
        self.domain_height = domain_height
        self.depot_position = depot_position if depot_position is not None else np.array([0, 0])
        self.use_penalties = use_penalties
        
        # Decision variables: [x1, y1, x2, y2, ..., xn, yn]
        n_var = n_sensors * 2
        
        # Variable bounds
        xl = np.zeros(n_var)  # Lower bounds
        xu = np.repeat([domain_width, domain_height], n_sensors)  # Upper bounds
        
        # Number of objectives
        n_obj = 4  # blind_area_ratio, node_count, energy, flight_distance
        
        # Number of constraints (if not using penalties)
        n_constr = 0 if use_penalties else 5
        
        # Initialize parent class
        super().__init__(n_var=n_var, n_obj=n_obj, n_constr=n_constr,
                        xl=xl, xu=xu)
    
    def _evaluate(self, X, out, *args, **kwargs):
        """
        Evaluate objectives (and constraints) for population.
        
        Args:
            X: Population array (pop_size, n_var)
            out: Output dictionary
        """
        pop_size = X.shape[0]
        
        # Initialize objective and constraint arrays
        F = np.zeros((pop_size, self.n_obj))
        
        if not self.use_penalties:
            G = np.zeros((pop_size, 5))  # 5 constraint types
        
        # Evaluate each individual
        for i in range(pop_size):
            solution = X[i]
            
            # Decode sensor positions
            sensor_positions = solution.reshape(-1, 2)
            
            # Evaluate objectives
            obj_values = self.objective_functions.evaluate_all(
                sensor_positions, self.depot_position
            )
            
            F[i, 0] = obj_values['blind_area_ratio']
            F[i, 1] = obj_values['node_count']
            F[i, 2] = obj_values['network_energy']
            F[i, 3] = obj_values['flight_distance']
            
            # Apply penalties or evaluate constraints
            if self.use_penalties:
                # Penalty approach - add violations to objectives
                violations = self.constraint_handler.evaluate_solution_constraints(sensor_positions)
                penalty = violations['total_violations'] * 1000  # Large penalty
                
                # Add penalty to first objective (blind area ratio)
                F[i, 0] += penalty
            else:
                # Constraint approach - pymoo handles constraint satisfaction
                violations = self.constraint_handler.evaluate_solution_constraints(sensor_positions)
                
                G[i, 0] = violations['bounds_violations']
                G[i, 1] = violations['spacing_violations']
                G[i, 2] = violations['gateway_spacing_violations']
                G[i, 3] = violations['no_drop_zone_violations']
                G[i, 4] = violations['connectivity_violations']
        
        # Set output
        out["F"] = F
        
        if not self.use_penalties:
            out["G"] = G
    
    def evaluate_single(self, x: np.ndarray) -> dict:
        """
        Evaluate a single solution and return detailed results.
        
        Args:
            x: Solution vector
        
        Returns:
            Dictionary with objectives, constraints, and metrics
        """
        sensor_positions = x.reshape(-1, 2)
        
        # Objectives
        objectives = self.objective_functions.evaluate_all(
            sensor_positions, self.depot_position
        )
        
        # Constraints
        constraints = self.constraint_handler.evaluate_solution_constraints(
            sensor_positions
        )
        
        return {
            'sensor_positions': sensor_positions,
            'objectives': objectives,
            'constraints': constraints,
            'is_feasible': constraints['total_violations'] == 0
        }


