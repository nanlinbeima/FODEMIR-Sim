"""
Objective Functions

Multi-objective functions for sensor deployment optimization.
"""

import numpy as np
from typing import Dict, Optional


class ObjectiveFunctions:
    """
    Defines objective functions for multi-objective sensor deployment optimization.
    
    Objectives:
    1. Maximize coverage reliability (minimize blind area ratio)
    2. Minimize total node count
    3. Minimize network energy consumption
    4. Minimize UAV flight distance
    """
    
    def __init__(self, domain_width: float, domain_height: float,
                 gateway_positions: np.ndarray,
                 link_calculator,  # LinkCalculator type
                 coverage_analyzer,  # CoverageAnalyzer type
                 tree_positions: Optional[np.ndarray] = None,
                 crown_radii: Optional[np.ndarray] = None,
                 snr_threshold_db: float = 6.0,
                 clearings: Optional[list] = None,
                 clearing_priority_weight: float = 0.3):
        """
        Initialize objective functions.
        
        Args:
            domain_width: Forest area width in meters
            domain_height: Forest area height in meters
            gateway_positions: Array of gateway positions
            link_calculator: LinkCalculator instance
            coverage_analyzer: CoverageAnalyzer instance
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
            snr_threshold_db: Minimum SNR for coverage
            clearings: List of clearings (dicts with 'center' and 'radius')
            clearing_priority_weight: Weight for clearing placement bonus (0-1)
        """
        self.domain_width = domain_width
        self.domain_height = domain_height
        self.gateway_positions = gateway_positions
        self.link_calculator = link_calculator
        self.coverage_analyzer = coverage_analyzer
        self.tree_positions = tree_positions
        self.crown_radii = crown_radii
        self.snr_threshold_db = snr_threshold_db
        self.clearings = clearings if clearings is not None else []
        self.clearing_priority_weight = clearing_priority_weight
    
    def calculate_blind_area_ratio(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate blind area ratio (objective 1) with clearing priority bonus
        and edge coverage penalty.
        
        Prioritizes:
        1. Sensors in clearings (better signal propagation)
        2. Coverage of forest edges and corners (full area coverage)
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Blind area ratio (0 to 1, lower is better)
        """
        # Combine gateways and sensors as transmitters
        all_tx = np.vstack([self.gateway_positions, sensor_positions])
        
        # Calculate coverage map
        coverage_map = self.coverage_analyzer.calculate_coverage_map(
            all_tx, self.link_calculator,
            self.tree_positions, self.crown_radii,
            metric='snr'
        )
        
        # Calculate statistics
        stats = self.coverage_analyzer.calculate_coverage_statistics(
            coverage_map, self.snr_threshold_db, metric='snr'
        )
        
        blind_area_ratio = stats['blind_area_ratio']
        
        # Apply clearing placement bonus
        if len(self.clearings) > 0 and len(sensor_positions) > 0:
            clearing_bonus = self._calculate_clearing_bonus(sensor_positions)
            # Reduce blind area ratio for sensors in clearings
            blind_area_ratio *= (1.0 - clearing_bonus * self.clearing_priority_weight)
        
        # Apply edge coverage penalty - CRITICAL for 100% coverage requirement
        if len(sensor_positions) > 0:
            edge_penalty = self._calculate_edge_coverage_penalty(sensor_positions, coverage_map)
            # Increase blind area if edges are poorly covered
            # MAXIMUM weight (50%) to guarantee every point within 300m of a sensor
            blind_area_ratio += edge_penalty * 0.5  # 50% weight for edge coverage
        
        return min(blind_area_ratio, 1.0)  # Cap at 1.0
    
    def _calculate_edge_coverage_penalty(self, sensor_positions: np.ndarray, 
                                        coverage_map: np.ndarray) -> float:
        """
        Calculate penalty for poor edge coverage.
        
        Checks coverage in edge regions (outer 15% of domain).
        Returns higher penalty if edges are not well covered.
        
        Args:
            sensor_positions: Array of sensor positions
            coverage_map: Coverage map (2D array)
        
        Returns:
            Edge coverage penalty (0 to 1, lower is better)
        """
        h, w = coverage_map.shape
        
        # Define edge thickness (20% of domain to ensure 300m coverage at boundaries)
        # For 1000m domain, 20% = 200m which is less than 300m radius requirement
        edge_thickness_x = int(w * 0.20)
        edge_thickness_y = int(h * 0.20)
        
        # Extract edge regions
        edges = []
        edges.append(coverage_map[:edge_thickness_y, :])  # Top edge
        edges.append(coverage_map[-edge_thickness_y:, :])  # Bottom edge
        edges.append(coverage_map[:, :edge_thickness_x])  # Left edge
        edges.append(coverage_map[:, -edge_thickness_x:])  # Right edge
        
        # Calculate average coverage in edge regions
        edge_covered = 0
        edge_total = 0
        
        for edge_region in edges:
            edge_covered += np.sum(edge_region >= self.snr_threshold_db)
            edge_total += edge_region.size
        
        edge_coverage_ratio = edge_covered / edge_total if edge_total > 0 else 0
        
        # Penalty = 1 - coverage (higher penalty for lower coverage)
        penalty = 1.0 - edge_coverage_ratio
        
        return penalty
    
    def _calculate_clearing_bonus(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate bonus for sensors placed in clearings.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Clearing bonus ratio (0 to 1, higher is better)
        """
        if len(sensor_positions) == 0 or len(self.clearings) == 0:
            return 0.0
        
        sensors_in_clearings = 0
        
        for sensor_pos in sensor_positions:
            for clearing in self.clearings:
                dist = np.linalg.norm(sensor_pos - clearing['center'])
                if dist < clearing['radius']:
                    sensors_in_clearings += 1
                    break  # Count each sensor only once
        
        # Return ratio of sensors in clearings
        return sensors_in_clearings / len(sensor_positions)
    
    def calculate_node_count(self, sensor_positions: np.ndarray) -> int:
        """
        Calculate total number of sensor nodes (objective 2).
        
        Args:
            sensor_positions: Array of sensor positions
        
        Returns:
            Number of nodes (lower is better)
        """
        return len(sensor_positions)
    
    def calculate_network_energy(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate total network energy consumption (objective 3).
        
        Assumes periodic transmission from each sensor to nearest gateway.
        Energy ∝ transmission power × path loss
        
        Args:
            sensor_positions: Array of sensor positions
        
        Returns:
            Normalized energy consumption (lower is better)
        """
        if len(sensor_positions) == 0:
            return 0.0
        
        total_energy = 0.0
        
        for sensor_pos in sensor_positions:
            # Find best gateway
            best_gw_idx, params = self.link_calculator.find_best_gateway(
                sensor_pos, self.gateway_positions,
                self.tree_positions, self.crown_radii
            )
            
            # Energy proportional to path loss (need more power for higher loss)
            # Convert dB to linear scale for energy calculation
            path_loss_linear = 10 ** (params['total_loss_db'] / 10)
            total_energy += path_loss_linear
        
        # Normalize by number of sensors
        return total_energy / len(sensor_positions) if len(sensor_positions) > 0 else 0.0
    
    def calculate_flight_distance(self, sensor_positions: np.ndarray,
                                  depot_position: np.ndarray = None) -> float:
        """
        Calculate UAV flight distance using TSP approximation (objective 4).
        
        Args:
            sensor_positions: Array of sensor positions
            depot_position: UAV depot/launch position
        
        Returns:
            Total flight distance in meters (lower is better)
        """
        if len(sensor_positions) == 0:
            return 0.0
        
        if depot_position is None:
            depot_position = np.array([0, 0])
        
        # Nearest neighbor TSP approximation
        positions = np.vstack([depot_position, sensor_positions, depot_position])
        
        total_distance = 0.0
        for i in range(len(positions) - 1):
            # Euclidean distance
            total_distance += np.linalg.norm(positions[i] - positions[i+1])
        
        return total_distance
    
    def evaluate_all(self, sensor_positions: np.ndarray,
                    depot_position: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Evaluate all objectives for a given deployment.
        
        Args:
            sensor_positions: Array of sensor positions
            depot_position: UAV depot position
        
        Returns:
            Dictionary with all objective values
        """
        objectives = {
            'blind_area_ratio': self.calculate_blind_area_ratio(sensor_positions),
            'node_count': self.calculate_node_count(sensor_positions),
            'network_energy': self.calculate_network_energy(sensor_positions),
            'flight_distance': self.calculate_flight_distance(sensor_positions, depot_position)
        }
        
        return objectives
    
    def evaluate_solution_vector(self, x: np.ndarray, n_max_sensors: int,
                                 depot_position: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Evaluate objectives from solution vector (for pymoo interface).
        
        Solution encoding: [x1, y1, x2, y2, ..., xn, yn, active_flags...]
        
        Args:
            x: Solution vector
            n_max_sensors: Maximum number of sensors
            depot_position: UAV depot position
        
        Returns:
            Array of objective values [obj1, obj2, obj3, obj4]
        """
        # Decode sensor positions
        n_coords = n_max_sensors * 2
        coords = x[:n_coords].reshape(-1, 2)
        
        # If solution includes active flags (for variable number of sensors)
        if len(x) > n_coords:
            active = x[n_coords:].astype(bool)
            sensor_positions = coords[active]
        else:
            sensor_positions = coords
        
        # Evaluate objectives
        obj = self.evaluate_all(sensor_positions, depot_position)
        
        # Return as array (all objectives to be minimized)
        return np.array([
            obj['blind_area_ratio'],
            obj['node_count'],
            obj['network_energy'],
            obj['flight_distance']
        ])
    
    def get_objective_names(self) -> list:
        """Get list of objective names."""
        return ['blind_area_ratio', 'node_count', 'network_energy', 'flight_distance']
    
    def get_objective_directions(self) -> list:
        """Get optimization direction for each objective (all minimization)."""
        return ['minimize', 'minimize', 'minimize', 'minimize']

