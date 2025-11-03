"""
Link Calculator

Calculates link budgets, RSSI, SNR for wireless communication links in forest environments.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from .propagation_base import PropagationModel


class LinkCalculator:
    """
    Calculates wireless link parameters including path loss, RSSI, and SNR.
    
    Integrates propagation models with forest geometry to compute link budgets.
    """
    
    def __init__(self, propagation_model: PropagationModel,
                 tx_power_dbm: float = 14.0,
                 tx_gain_dbi: float = 2.15,
                 rx_gain_dbi: float = 2.15,
                 noise_floor_dbm: float = -120.0):
        """
        Initialize link calculator.
        
        Args:
            propagation_model: Propagation model instance
            tx_power_dbm: Transmit power in dBm
            tx_gain_dbi: Transmit antenna gain in dBi
            rx_gain_dbi: Receive antenna gain in dBi
            noise_floor_dbm: Noise floor in dBm
        """
        self.propagation_model = propagation_model
        self.tx_power_dbm = tx_power_dbm
        self.tx_gain_dbi = tx_gain_dbi
        self.rx_gain_dbi = rx_gain_dbi
        self.noise_floor_dbm = noise_floor_dbm
    
    def calculate_link_loss(self, tx_pos: np.ndarray, rx_pos: np.ndarray,
                           tree_positions: Optional[np.ndarray] = None,
                           crown_radii: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Calculate complete link loss including vegetation.
        
        Args:
            tx_pos: Transmitter position (x, y)
            rx_pos: Receiver position (x, y)
            tree_positions: Array of tree positions (N, 2)
            crown_radii: Array of crown radii (N,)
        
        Returns:
            Dictionary with link parameters
        """
        # Calculate distance
        distance = np.linalg.norm(rx_pos - tx_pos)
        
        # Calculate vegetation depth if forest data provided
        veg_depth = 0.0
        if tree_positions is not None and crown_radii is not None:
            # Simplified vegetation depth calculation
            for tree_pos, crown_radius in zip(tree_positions, crown_radii):
                dist_to_tree = np.linalg.norm(tree_pos - tx_pos)
                if dist_to_tree < crown_radius:
                    veg_depth += crown_radius
        
        # Calculate losses
        fspl = self.propagation_model.calculate_free_space_loss(distance)
        veg_loss = self.propagation_model.calculate_vegetation_loss(veg_depth)
        total_loss = fspl + veg_loss
        
        # Calculate RSSI and SNR
        rssi = self.tx_power_dbm + self.tx_gain_dbi + self.rx_gain_dbi - total_loss
        snr = rssi - self.noise_floor_dbm
        
        return {
            'distance_m': distance,
            'vegetation_depth_m': veg_depth,
            'fspl_db': fspl,
            'vegetation_loss_db': veg_loss,
            'total_loss_db': total_loss,
            'rssi_dbm': rssi,
            'snr_db': snr
        }
    
    def calculate_link_matrix(self, tx_positions: np.ndarray, rx_positions: np.ndarray,
                             tree_positions: Optional[np.ndarray] = None,
                             crown_radii: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """
        Calculate link parameters for all TX-RX pairs.
        
        Args:
            tx_positions: Array of TX positions (M, 2)
            rx_positions: Array of RX positions (N, 2)
            tree_positions: Array of tree positions (K, 2)
            crown_radii: Array of crown radii (K,)
        
        Returns:
            Dictionary with parameter matrices (M, N)
        """
        n_tx = len(tx_positions)
        n_rx = len(rx_positions)
        
        # Initialize result matrices
        distance_matrix = np.zeros((n_tx, n_rx))
        veg_depth_matrix = np.zeros((n_tx, n_rx))
        fspl_matrix = np.zeros((n_tx, n_rx))
        veg_loss_matrix = np.zeros((n_tx, n_rx))
        total_loss_matrix = np.zeros((n_tx, n_rx))
        rssi_matrix = np.zeros((n_tx, n_rx))
        snr_matrix = np.zeros((n_tx, n_rx))
        
        # Calculate for each TX-RX pair
        for i, tx_pos in enumerate(tx_positions):
            for j, rx_pos in enumerate(rx_positions):
                link_params = self.calculate_link_loss(
                    tx_pos, rx_pos, tree_positions, crown_radii
                )
                
                distance_matrix[i, j] = link_params['distance_m']
                veg_depth_matrix[i, j] = link_params['vegetation_depth_m']
                fspl_matrix[i, j] = link_params['fspl_db']
                veg_loss_matrix[i, j] = link_params['vegetation_loss_db']
                total_loss_matrix[i, j] = link_params['total_loss_db']
                rssi_matrix[i, j] = link_params['rssi_dbm']
                snr_matrix[i, j] = link_params['snr_db']
        
        return {
            'distance_m': distance_matrix,
            'vegetation_depth_m': veg_depth_matrix,
            'fspl_db': fspl_matrix,
            'vegetation_loss_db': veg_loss_matrix,
            'total_loss_db': total_loss_matrix,
            'rssi_dbm': rssi_matrix,
            'snr_db': snr_matrix
        }
    
    def find_best_gateway(self, sensor_pos: np.ndarray, gateway_positions: np.ndarray,
                         tree_positions: Optional[np.ndarray] = None,
                         crown_radii: Optional[np.ndarray] = None) -> Tuple[int, Dict[str, float]]:
        """
        Find best gateway for a sensor based on maximum SNR.
        
        Args:
            sensor_pos: Sensor position (x, y)
            gateway_positions: Array of gateway positions (N, 2)
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
        
        Returns:
            Tuple of (best_gateway_idx, link_params)
        """
        best_snr = -np.inf
        best_idx = 0
        best_params = {}
        
        for i, gw_pos in enumerate(gateway_positions):
            params = self.calculate_link_loss(
                gw_pos, sensor_pos, tree_positions, crown_radii
            )
            
            if params['snr_db'] > best_snr:
                best_snr = params['snr_db']
                best_idx = i
                best_params = params
        
        return best_idx, best_params
    
    def check_connectivity(self, sensor_positions: np.ndarray, gateway_positions: np.ndarray,
                          snr_threshold_db: float,
                          tree_positions: Optional[np.ndarray] = None,
                          crown_radii: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Check which sensors have connectivity to at least one gateway.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
            gateway_positions: Array of gateway positions (M, 2)
            snr_threshold_db: Minimum required SNR in dB
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
        
        Returns:
            Boolean array indicating connectivity for each sensor
        """
        connectivity = np.zeros(len(sensor_positions), dtype=bool)
        
        for i, sensor_pos in enumerate(sensor_positions):
            for gw_pos in gateway_positions:
                params = self.calculate_link_loss(
                    gw_pos, sensor_pos, tree_positions, crown_radii
                )
                
                if params['snr_db'] >= snr_threshold_db:
                    connectivity[i] = True
                    break
        
        return connectivity
    
    def calculate_network_topology(self, sensor_positions: np.ndarray, 
                                   gateway_positions: np.ndarray,
                                   snr_threshold_db: float,
                                   tree_positions: Optional[np.ndarray] = None,
                                   crown_radii: Optional[np.ndarray] = None) -> Dict:
        """
        Calculate complete network topology.
        
        Args:
            sensor_positions: Array of sensor positions
            gateway_positions: Array of gateway positions
            snr_threshold_db: Minimum SNR threshold
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
        
        Returns:
            Dictionary with topology information
        """
        n_sensors = len(sensor_positions)
        n_gateways = len(gateway_positions)
        
        # Find best gateway for each sensor
        sensor_gateway_map = np.zeros(n_sensors, dtype=int)
        sensor_snr = np.zeros(n_sensors)
        connectivity = np.zeros(n_sensors, dtype=bool)
        
        for i, sensor_pos in enumerate(sensor_positions):
            best_gw_idx, params = self.find_best_gateway(
                sensor_pos, gateway_positions, tree_positions, crown_radii
            )
            
            sensor_gateway_map[i] = best_gw_idx
            sensor_snr[i] = params['snr_db']
            connectivity[i] = (params['snr_db'] >= snr_threshold_db)
        
        # Calculate gateway load
        gateway_load = np.bincount(sensor_gateway_map[connectivity], 
                                   minlength=n_gateways)
        
        return {
            'sensor_gateway_map': sensor_gateway_map,
            'sensor_snr': sensor_snr,
            'connectivity': connectivity,
            'connected_sensors': np.sum(connectivity),
            'disconnected_sensors': n_sensors - np.sum(connectivity),
            'connectivity_rate': np.mean(connectivity),
            'gateway_load': gateway_load,
            'average_snr_db': np.mean(sensor_snr[connectivity]) if np.any(connectivity) else 0.0
        }

