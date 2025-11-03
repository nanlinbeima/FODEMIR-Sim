"""
Communication-Oriented Problem Definition

Pymoo-compatible problem definition for communication-focused optimization.
"""

import numpy as np
from pymoo.core.problem import Problem
from typing import Optional
from .communication_objectives import CommunicationObjectives
from .constraints import ConstraintHandler


class CommunicationProblem(Problem):
    """
    Communication-focused sensor deployment optimization problem.
    
    Compatible with Pymoo optimization algorithms.
    
    Decision variables: sensor positions (x, y) coordinates
    Objectives: avg_snr, min_snr, avg_rssi, min_rssi, avg_hop_count, connectivity
    Constraints: spacing, bounds, connectivity
    """
    
    def __init__(self, communication_objectives: CommunicationObjectives,
                 constraint_handler: ConstraintHandler,
                 n_sensors: int,
                 domain_width: float,
                 domain_height: float,
                 depot_position: Optional[np.ndarray] = None,
                 use_penalties: bool = True):
        """
        Initialize communication problem.
        
        Args:
            communication_objectives: CommunicationObjectives instance
            constraint_handler: ConstraintHandler instance
            n_sensors: Number of sensors to deploy
            domain_width: Domain width in meters
            domain_height: Domain height in meters
            depot_position: UAV depot position (not used in objectives)
            use_penalties: Whether to use penalty functions for constraints
        """
        self.communication_objectives = communication_objectives
        self.constraint_handler = constraint_handler
        self.n_sensors = n_sensors
        self.domain_width = domain_width
        self.domain_height = domain_height
        self.depot_position = depot_position if depot_position is not None else np.array([0, 0])
        self.use_penalties = use_penalties
        
        # Decision variables: [x1, y1, x2, y2, ..., xn, yn]
        n_var = n_sensors * 2
        
        # Variable bounds
        xl = np.zeros(n_var)
        xu = np.repeat([domain_width, domain_height], n_sensors)
        
        # Number of objectives: avg_snr, min_snr, avg_rssi, min_rssi, avg_hop_count, connectivity
        n_obj = 6
        
        # Number of constraints
        n_constr = 0 if use_penalties else 5
        
        # Initialize parent class
        super().__init__(n_var=n_var, n_obj=n_obj, n_constr=n_constr,
                        xl=xl, xu=xu)
    
    def _evaluate(self, X, out, *args, **kwargs):
        """
        Evaluate communication objectives for population.
        
        Args:
            X: Population array (pop_size, n_var)
            out: Output dictionary
        """
        pop_size = X.shape[0]
        
        # Initialize objective array
        F = np.zeros((pop_size, self.n_obj))
        
        for i in range(pop_size):
            # Extract sensor positions
            positions_flat = X[i, :]
            sensor_positions = positions_flat.reshape(-1, 2)
            
            # Apply penalties for constraint violations if enabled
            penalty = 0.0
            if self.use_penalties:
                penalty = self._calculate_penalty(sensor_positions)
            
            # Evaluate communication objectives
            f1 = self.communication_objectives.calculate_average_snr(sensor_positions)    # Minimize negative avg SNR
            f2 = self.communication_objectives.calculate_min_snr(sensor_positions)        # Minimize negative min SNR
            f3 = self.communication_objectives.calculate_average_rssi(sensor_positions)   # Minimize negative avg RSSI
            f4 = self.communication_objectives.calculate_min_rssi(sensor_positions)       # Minimize negative min RSSI
            f5 = self.communication_objectives.calculate_average_hop_count(sensor_positions)  # Minimize hop count
            f6 = self.communication_objectives.calculate_connectivity_ratio(sensor_positions) # Minimize disconnect ratio
            
            # Add penalties (if any violations)
            F[i, 0] = f1 + penalty
            F[i, 1] = f2 + penalty
            F[i, 2] = f3 + penalty
            F[i, 3] = f4 + penalty
            F[i, 4] = f5 + penalty * 0.1  # Smaller penalty weight for hop count
            F[i, 5] = f6 + penalty
        
        out["F"] = F
    
    def _calculate_penalty(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate penalty for constraint violations including communication quality.
        
        Constraints:
        - Spatial constraints (spacing, bounds)
        - Communication quality: avg RSSI > -90 dBm
        - Communication quality: avg SNR > 10 dB
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Penalty value (0 if no violations)
        """
        penalty = 0.0
        violation_weight = 1000.0  # Large penalty
        
        # Spatial constraint checks
        for i, pos in enumerate(sensor_positions):
            # Check constraints
            if not self.constraint_handler.check_all_constraints(pos):
                penalty += violation_weight
            
            # Check spacing with other sensors
            for j in range(i + 1, len(sensor_positions)):
                dist = np.linalg.norm(pos - sensor_positions[j])
                min_spacing = self.constraint_handler.min_sensor_spacing
                if dist < min_spacing:
                    penalty += violation_weight * (1.0 - dist / min_spacing)
        
        # Communication quality constraints (relaxed for feasibility)
        if len(sensor_positions) > 0:
            # Calculate average RSSI (returns negative value for minimization)
            avg_rssi = -self.communication_objectives.calculate_average_rssi(sensor_positions)
            # Require: avg RSSI > -95 dBm (relaxed from -90 for large areas)
            if avg_rssi < -95:
                # Penalty proportional to violation
                rssi_violation = (-95 - avg_rssi) / 15.0  # Normalize by 15 dB
                penalty += violation_weight * 0.3 * rssi_violation  # Reduced weight
            
            # Calculate average SNR (returns negative value for minimization)
            avg_snr = -self.communication_objectives.calculate_average_snr(sensor_positions)
            # Require: avg SNR > 8 dB (relaxed from 10 for large areas)
            if avg_snr < 8:
                # Penalty proportional to violation
                snr_violation = (8 - avg_snr) / 6.0  # Normalize by 6 dB
                penalty += violation_weight * 0.3 * snr_violation  # Reduced weight
        
        return penalty

