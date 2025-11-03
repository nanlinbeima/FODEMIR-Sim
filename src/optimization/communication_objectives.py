"""
Communication-Oriented Objective Functions

Multi-objective functions focusing on network communication performance.
"""

import numpy as np
from typing import Dict, Optional, Tuple, List


class CommunicationObjectives:
    """
    Communication-focused objective functions for sensor network optimization.
    
    Objectives:
    1. Maximize average SNR (better overall communication quality)
    2. Maximize minimum SNR (improve weakest link)
    3. Maximize average RSSI (received signal strength)
    4. Minimize average hop count (routing efficiency)
    5. Maximize network connectivity (reliability)
    """
    
    def __init__(self, domain_width: float, domain_height: float,
                 gateway_positions: np.ndarray,
                 link_calculator,
                 coverage_analyzer,
                 tree_positions: Optional[np.ndarray] = None,
                 crown_radii: Optional[np.ndarray] = None,
                 snr_threshold_db: float = 6.0,
                 enforce_snr_strict: bool = False):
        """
        Initialize communication objectives.
        
        Args:
            domain_width: Forest area width in meters
            domain_height: Forest area height in meters
            gateway_positions: Array of gateway positions
            link_calculator: LinkCalculator instance
            coverage_analyzer: CoverageAnalyzer instance
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
            snr_threshold_db: Minimum SNR for valid link
            enforce_snr_strict: If False, use relaxed threshold for routing
        """
        self.domain_width = domain_width
        self.domain_height = domain_height
        self.gateway_positions = gateway_positions
        self.link_calculator = link_calculator
        self.coverage_analyzer = coverage_analyzer
        self.tree_positions = tree_positions
        self.crown_radii = crown_radii
        self.snr_threshold_db = snr_threshold_db
        self.enforce_snr_strict = enforce_snr_strict
        # Use more relaxed threshold for routing if strict mode is off
        self.routing_snr_threshold = snr_threshold_db if enforce_snr_strict else 0.0
    
    def calculate_average_snr(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate average SNR across all sensor-gateway links.
        
        Returns negative value for minimization (higher SNR is better).
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Negative average SNR (for minimization)
        """
        if len(sensor_positions) == 0:
            return -0.0  # No sensors
        
        snr_values = []
        for sensor_pos in sensor_positions:
            # Calculate SNR to best gateway
            best_snr = -np.inf
            for gw_pos in self.gateway_positions:
                link_params = self.link_calculator.calculate_link_loss(
                    gw_pos, sensor_pos,
                    self.tree_positions, self.crown_radii
                )
                snr = link_params['snr_db']
                best_snr = max(best_snr, snr)
            snr_values.append(best_snr)
        
        avg_snr = np.mean(snr_values)
        return -avg_snr  # Negative for minimization
    
    def calculate_min_snr(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate minimum SNR (weakest link) in the network.
        
        Returns negative value for minimization (higher min SNR is better).
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Negative minimum SNR (for minimization)
        """
        if len(sensor_positions) == 0:
            return -0.0
        
        min_snr = np.inf
        for sensor_pos in sensor_positions:
            # Find best gateway SNR for this sensor
            best_snr = -np.inf
            for gw_pos in self.gateway_positions:
                link_params = self.link_calculator.calculate_link_loss(
                    gw_pos, sensor_pos,
                    self.tree_positions, self.crown_radii
                )
                snr = link_params['snr_db']
                best_snr = max(best_snr, snr)
            min_snr = min(min_snr, best_snr)
        
        return -min_snr  # Negative for minimization
    
    def calculate_average_rssi(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate average RSSI across all sensor-gateway links.
        
        Returns negative value for minimization (higher RSSI is better).
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Negative average RSSI in dBm (for minimization)
        """
        if len(sensor_positions) == 0:
            return -0.0
        
        rssi_values = []
        for sensor_pos in sensor_positions:
            # Calculate RSSI to best gateway
            best_rssi = -np.inf
            for gw_pos in self.gateway_positions:
                link_params = self.link_calculator.calculate_link_loss(
                    gw_pos, sensor_pos,
                    self.tree_positions, self.crown_radii
                )
                rssi = link_params['rssi_dbm']
                best_rssi = max(best_rssi, rssi)
            rssi_values.append(best_rssi)
        
        avg_rssi = np.mean(rssi_values)
        return -avg_rssi  # Negative for minimization
    
    def calculate_min_rssi(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate minimum RSSI (weakest signal) in the network.
        
        Returns negative value for minimization (higher min RSSI is better).
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Negative minimum RSSI in dBm (for minimization)
        """
        if len(sensor_positions) == 0:
            return -0.0
        
        min_rssi = np.inf
        for sensor_pos in sensor_positions:
            # Find best gateway RSSI for this sensor
            best_rssi = -np.inf
            for gw_pos in self.gateway_positions:
                link_params = self.link_calculator.calculate_link_loss(
                    gw_pos, sensor_pos,
                    self.tree_positions, self.crown_radii
                )
                rssi = link_params['rssi_dbm']
                best_rssi = max(best_rssi, rssi)
            min_rssi = min(min_rssi, best_rssi)
        
        return -min_rssi  # Negative for minimization
    
    def calculate_average_hop_count(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate average hop count from sensors to gateway.
        
        Uses greedy routing based on SNR (route to best neighbor closer to gateway).
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            Average hop count (lower is better)
        """
        if len(sensor_positions) == 0:
            return 0.0
        
        routing_table = self._build_routing_table(sensor_positions)
        
        hop_counts = []
        for sensor_id in range(len(sensor_positions)):
            hops = routing_table[sensor_id]['hop_count']
            hop_counts.append(hops)
        
        return np.mean(hop_counts)
    
    def calculate_connectivity_ratio(self, sensor_positions: np.ndarray) -> float:
        """
        Calculate network connectivity ratio.
        
        Returns 1 - connectivity for minimization (higher connectivity is better).
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            1 - connectivity ratio (for minimization)
        """
        if len(sensor_positions) == 0:
            return 1.0  # No sensors = no connectivity
        
        routing_table = self._build_routing_table(sensor_positions)
        
        # Count connected sensors
        connected = sum(1 for entry in routing_table if entry['next_hop'] != -1)
        connectivity = connected / len(sensor_positions)
        
        return 1.0 - connectivity  # Return disconnect ratio for minimization
    
    def _build_routing_table(self, sensor_positions: np.ndarray) -> List[Dict]:
        """
        Build routing table using SNR-based greedy routing.
        
        Each sensor routes to the neighbor (or gateway) with best SNR
        that is closer to the gateway.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            List of routing entries, one per sensor
        """
        n_sensors = len(sensor_positions)
        routing_table = []
        
        # Handle empty sensor positions
        if n_sensors == 0 or sensor_positions.shape[0] == 0:
            return routing_table
        
        # All nodes (gateway + sensors)
        all_nodes = np.vstack([self.gateway_positions, sensor_positions])
        
        for sensor_id in range(n_sensors):
            sensor_pos = sensor_positions[sensor_id]
            
            # Try direct link to gateway first
            best_snr = -np.inf
            best_rssi = -np.inf
            best_next_hop = -1  # -1 means no route
            best_hop_count = np.inf
            
            # Check direct gateway links
            for gw_id, gw_pos in enumerate(self.gateway_positions):
                link_params = self.link_calculator.calculate_link_loss(
                    sensor_pos, gw_pos,
                    self.tree_positions, self.crown_radii
                )
                snr = link_params['snr_db']
                rssi = link_params['rssi_dbm']
                
                # Use relaxed threshold for routing to support 300m coverage range
                if snr >= self.routing_snr_threshold and snr > best_snr:
                    best_snr = snr
                    best_rssi = rssi
                    best_next_hop = -(gw_id + 1)  # Negative for gateway
                    best_hop_count = 1
            
            # Check multi-hop routes through other sensors
            for other_id in range(n_sensors):
                if other_id == sensor_id:
                    continue
                
                other_pos = sensor_positions[other_id]
                
                # SNR and RSSI from current sensor to neighbor
                link_params = self.link_calculator.calculate_link_loss(
                    sensor_pos, other_pos,
                    self.tree_positions, self.crown_radii
                )
                snr_to_neighbor = link_params['snr_db']
                rssi_to_neighbor = link_params['rssi_dbm']
                
                # Use relaxed threshold for routing
                if snr_to_neighbor >= self.routing_snr_threshold:
                    # Check if neighbor is closer to gateway
                    dist_current = np.min([
                        np.linalg.norm(sensor_pos - gw_pos)
                        for gw_pos in self.gateway_positions
                    ])
                    dist_neighbor = np.min([
                        np.linalg.norm(other_pos - gw_pos)
                        for gw_pos in self.gateway_positions
                    ])
                    
                    if dist_neighbor < dist_current:
                        # Estimate hop count (1 + neighbor's hops)
                        # For first pass, use distance heuristic
                        estimated_hops = 1 + int(dist_neighbor / 200)  # Assume 200m per hop
                        
                        if snr_to_neighbor > best_snr or \
                           (snr_to_neighbor >= best_snr * 0.9 and estimated_hops < best_hop_count):
                            best_snr = snr_to_neighbor
                            best_rssi = rssi_to_neighbor
                            best_next_hop = other_id
                            best_hop_count = estimated_hops
            
            routing_table.append({
                'sensor_id': sensor_id,
                'next_hop': best_next_hop,
                'link_snr': best_snr if best_snr > -np.inf else 0.0,
                'link_rssi': best_rssi if best_rssi > -np.inf else -120.0,
                'hop_count': best_hop_count if best_hop_count < np.inf else 999
            })
        
        return routing_table
    
    def get_routing_table(self, sensor_positions: np.ndarray) -> List[Dict]:
        """
        Public method to get routing table for display.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
        
        Returns:
            List of routing entries with full information
        """
        return self._build_routing_table(sensor_positions)
    
    def evaluate_all(self, sensor_positions: np.ndarray, depot_position: np.ndarray) -> Dict:
        """
        Evaluate all communication objectives.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
            depot_position: Depot position (not used in communication objectives)
        
        Returns:
            Dictionary with all objective values
        """
        # Calculate coverage map for blind area ratio (for compatibility)
        all_tx = np.vstack([self.gateway_positions, sensor_positions])
        coverage_map = self.coverage_analyzer.calculate_coverage_map(
            all_tx, self.link_calculator,
            self.tree_positions, self.crown_radii,
            metric='snr'
        )
        stats = self.coverage_analyzer.calculate_coverage_statistics(
            coverage_map, self.snr_threshold_db, metric='snr'
        )
        
        return {
            'avg_snr': -self.calculate_average_snr(sensor_positions),  # Convert back to positive
            'min_snr': -self.calculate_min_snr(sensor_positions),
            'avg_rssi': -self.calculate_average_rssi(sensor_positions),  # Convert back to positive
            'min_rssi': -self.calculate_min_rssi(sensor_positions),
            'avg_hop_count': self.calculate_average_hop_count(sensor_positions),
            'connectivity': 1.0 - self.calculate_connectivity_ratio(sensor_positions),
            'routing_table': self.get_routing_table(sensor_positions),
            'blind_area_ratio': stats['blind_area_ratio']  # For compatibility with existing code
        }

