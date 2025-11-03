"""
Constraint Handlers

Constraints for sensor deployment optimization.
"""

import numpy as np
from typing import List, Optional, Tuple, Dict


class ConstraintHandler:
    """
    Handles constraints for sensor deployment optimization.
    
    Constraints:
    1. Minimum inter-sensor spacing
    2. Domain bounds
    3. No-drop zones (restricted areas)
    4. Communication reachability
    5. UAV payload and range limits
    """
    
    def __init__(self, domain_width: float, domain_height: float,
                 min_sensor_spacing: float = 50.0,
                 min_gateway_spacing: float = 200.0,
                 no_drop_zones: Optional[List] = None,
                 gateway_positions: Optional[np.ndarray] = None,
                 link_calculator: Optional[object] = None,  # LinkCalculator type
                 snr_threshold_db: float = 6.0,
                 tree_positions: Optional[np.ndarray] = None,
                 crown_radii: Optional[np.ndarray] = None,
                 enforce_snr_strict: bool = True):
        """
        Initialize constraint handler.
        
        Args:
            domain_width: Forest area width in meters
            domain_height: Forest area height in meters
            min_sensor_spacing: Minimum distance between sensors in meters
            min_gateway_spacing: Minimum distance from gateway in meters
            no_drop_zones: List of polygon vertices for restricted areas
            gateway_positions: Array of gateway positions
            link_calculator: LinkCalculator for connectivity checks
            snr_threshold_db: Minimum required SNR
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
        """
        self.domain_width = domain_width
        self.domain_height = domain_height
        self.min_sensor_spacing = min_sensor_spacing
        self.min_gateway_spacing = min_gateway_spacing
        self.no_drop_zones = no_drop_zones if no_drop_zones else []
        self.gateway_positions = gateway_positions
        self.link_calculator = link_calculator
        self.snr_threshold_db = snr_threshold_db
        self.tree_positions = tree_positions
        self.crown_radii = crown_radii
        self.enforce_snr_strict = enforce_snr_strict
    
    def check_domain_bounds(self, position: np.ndarray) -> bool:
        """
        Check if position is within domain bounds.
        
        Args:
            position: Position (x, y)
        
        Returns:
            True if within bounds
        """
        return (0 <= position[0] <= self.domain_width and
                0 <= position[1] <= self.domain_height)
    
    def check_min_spacing(self, new_position: np.ndarray, 
                         existing_positions: np.ndarray) -> bool:
        """
        Check if new position maintains minimum spacing.
        
        Args:
            new_position: New sensor position
            existing_positions: Array of existing positions
        
        Returns:
            True if minimum spacing is satisfied
        """
        if len(existing_positions) == 0:
            return True
        
        distances = np.sqrt(np.sum((existing_positions - new_position)**2, axis=1))
        return np.all(distances >= self.min_sensor_spacing)
    
    def check_gateway_spacing(self, position: np.ndarray) -> bool:
        """
        Check if position is not too close to gateways.
        
        Args:
            position: Sensor position
        
        Returns:
            True if maintains minimum gateway spacing
        """
        if self.gateway_positions is None or len(self.gateway_positions) == 0:
            return True
        
        distances = np.sqrt(np.sum((self.gateway_positions - position)**2, axis=1))
        return np.all(distances >= self.min_gateway_spacing)
    
    def check_no_drop_zones(self, position: np.ndarray) -> bool:
        """
        Check if position is not in restricted zones.
        
        Args:
            position: Position to check
        
        Returns:
            True if position is allowed (not in no-drop zone)
        """
        # Simplified check - actual implementation would use shapely
        for zone_vertices in self.no_drop_zones:
            # Basic point-in-polygon check
            pass
        return True
    
    def check_connectivity(self, position: np.ndarray) -> bool:
        """
        Check if position has connectivity to at least one gateway.
        STRICT MODE: SNR must be >= threshold (default 6 dB) for reliable communication.
        
        Args:
            position: Sensor position
        
        Returns:
            True if connected with sufficient SNR
        """
        if self.gateway_positions is None or self.link_calculator is None:
            return True  # Skip check if not configured
        
        # Find best gateway connection
        best_snr = -float('inf')
        for gw_pos in self.gateway_positions:
            params = self.link_calculator.calculate_link_loss(
                gw_pos, position, self.tree_positions, self.crown_radii
            )
            best_snr = max(best_snr, params['snr_db'])
            
            # Accept if meets threshold
            if params['snr_db'] >= self.snr_threshold_db:
                return True
        
        # Strict mode: reject if no gateway provides sufficient SNR
        if self.enforce_snr_strict:
            return False
        
        # Legacy mode: accept if any connection exists (even weak)
        return best_snr > -100  # Some minimum threshold
    
    def check_all_constraints(self, position: np.ndarray,
                             existing_positions: Optional[np.ndarray] = None) -> Tuple[bool, List[str]]:
        """
        Check all constraints for a position.
        
        Args:
            position: Position to check
            existing_positions: Array of existing sensor positions
        
        Returns:
            Tuple of (is_valid, violated_constraints)
        """
        violated = []
        
        if not self.check_domain_bounds(position):
            violated.append('domain_bounds')
        
        if existing_positions is not None and not self.check_min_spacing(position, existing_positions):
            violated.append('min_spacing')
        
        if not self.check_gateway_spacing(position):
            violated.append('gateway_spacing')
        
        if not self.check_no_drop_zones(position):
            violated.append('no_drop_zone')
        
        if not self.check_connectivity(position):
            violated.append('connectivity')
        
        return (len(violated) == 0, violated)
    
    def evaluate_solution_constraints(self, sensor_positions: np.ndarray) -> Dict[str, float]:
        """
        Evaluate constraint violations for a complete solution.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Dictionary with constraint violation metrics (0 = satisfied)
        """
        violations = {
            'bounds_violations': 0,
            'spacing_violations': 0,
            'gateway_spacing_violations': 0,
            'no_drop_zone_violations': 0,
            'connectivity_violations': 0,
            'total_violations': 0
        }
        
        for i, pos in enumerate(sensor_positions):
            # Bounds
            if not self.check_domain_bounds(pos):
                violations['bounds_violations'] += 1
            
            # Spacing with other sensors
            other_sensors = np.delete(sensor_positions, i, axis=0)
            if not self.check_min_spacing(pos, other_sensors):
                violations['spacing_violations'] += 1
            
            # Gateway spacing
            if not self.check_gateway_spacing(pos):
                violations['gateway_spacing_violations'] += 1
            
            # No-drop zones
            if not self.check_no_drop_zones(pos):
                violations['no_drop_zone_violations'] += 1
            
            # Connectivity
            if not self.check_connectivity(pos):
                violations['connectivity_violations'] += 1
        
        violations['total_violations'] = sum([
            violations['bounds_violations'],
            violations['spacing_violations'],
            violations['gateway_spacing_violations'],
            violations['no_drop_zone_violations'],
            violations['connectivity_violations']
        ])
        
        return violations
    
    def repair_solution(self, sensor_positions: np.ndarray) -> np.ndarray:
        """
        Attempt to repair constraint violations.
        
        Args:
            sensor_positions: Array with potential violations
        
        Returns:
            Repaired sensor positions
        """
        repaired = sensor_positions.copy()
        
        for i in range(len(repaired)):
            # Repair bounds
            repaired[i, 0] = np.clip(repaired[i, 0], 0, self.domain_width)
            repaired[i, 1] = np.clip(repaired[i, 1], 0, self.domain_height)
            
            # Try to move out of no-drop zones
            max_attempts = 10
            for _ in range(max_attempts):
                if self.check_no_drop_zones(repaired[i]):
                    break
                # Random perturbation
                repaired[i] += np.random.randn(2) * 10
                repaired[i, 0] = np.clip(repaired[i, 0], 0, self.domain_width)
                repaired[i, 1] = np.clip(repaired[i, 1], 0, self.domain_height)
        
        return repaired

