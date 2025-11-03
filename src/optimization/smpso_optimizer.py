"""
SMPSO Optimizer

Speed-constrained Multi-objective Particle Swarm Optimization.
"""

import numpy as np
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from typing import Dict, Optional
from .problem_definition import DeploymentProblem


class SMPSOOptimizer:
    """
    SMPSO optimizer for sensor deployment.
    
    Note: Pymoo doesn't have native SMPSO, so we use SMS-EMOA as an alternative
    multi-objective PSO-like algorithm. For true SMPSO, would need to implement
    from scratch or use other libraries.
    
    Features:
    - Multi-objective particle swarm optimization
    - Archive-based approach
    - S-metric (hypervolume) selection
    """
    
    def __init__(self, problem: DeploymentProblem,
                 swarm_size: int = 100,
                 n_iterations: int = 200,
                 seed: Optional[int] = None):
        """
        Initialize SMPSO optimizer.
        
        Args:
            problem: DeploymentProblem instance
            swarm_size: Swarm population size
            n_iterations: Maximum number of iterations
            seed: Random seed
        """
        self.problem = problem
        self.swarm_size = swarm_size
        self.n_iterations = n_iterations
        self.seed = seed
        
        # Use SMS-EMOA as PSO alternative in pymoo
        # SMS-EMOA is a state-of-the-art multi-objective algorithm
        self.algorithm = SMSEMOA(
            pop_size=swarm_size,
            sampling=FloatRandomSampling()
        )
        
        # Termination
        self.termination = get_termination("n_gen", n_iterations)
        
        # Results storage
        self.result = None
        self.history = []
    
    def optimize(self, verbose: bool = True, save_history: bool = True) -> Dict:
        """
        Run SMPSO optimization.
        
        Args:
            verbose: Whether to print progress
            save_history: Whether to save iteration history
        
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
        
        # Process results
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
            'n_iterations': self.result.algorithm.n_gen,
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
            Dictionary with iteration-wise metrics
        """
        history = {
            'iterations': [],
            'n_solutions': [],
            'best_objectives': []
        }
        
        for iter_idx, entry in enumerate(self.result.history):
            history['iterations'].append(iter_idx)
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
        
        Returns:
            Selected solution vector
        """
        if self.result is None or len(self.result.F) == 0:
            return None
        
        pareto_front = self.result.F
        pareto_solutions = self.result.X
        
        if criterion == 'balanced':
            # Normalize and find closest to ideal
            f_min = np.min(pareto_front, axis=0)
            f_max = np.max(pareto_front, axis=0)
            f_range = f_max - f_min
            f_range[f_range == 0] = 1
            
            f_norm = (pareto_front - f_min) / f_range
            distances = np.sqrt(np.sum(f_norm**2, axis=1))
            idx = np.argmin(distances)
        
        elif criterion == 'max_coverage':
            idx = np.argmin(pareto_front[:, 0])
        
        elif criterion == 'min_nodes':
            idx = np.argmin(pareto_front[:, 1])
        
        elif criterion == 'min_energy':
            idx = np.argmin(pareto_front[:, 2])
        
        elif criterion == 'min_distance':
            idx = np.argmin(pareto_front[:, 3])
        
        else:
            idx = 0
        
        return pareto_solutions[idx]


