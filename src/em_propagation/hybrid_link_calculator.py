"""
Hybrid Link Calculator with Terrain-Aware Propagation

Calculates link budgets using different propagation models for clearings vs forested areas.
- Clearings: Free Space Path Loss (FSPL) model
- Forested areas: ITU-R P.833 vegetation model
"""

import numpy as np
from typing import Dict, Optional, Tuple
from .propagation_base import PropagationModel
from .itur_p833_model import ITURP833Model


class HybridLinkCalculator:
    """
    Hybrid link calculator that adapts propagation model based on terrain type.
    
    Uses canopy closure map to determine propagation model:
    - Low canopy closure (< 20%): Free Space Path Loss
    - Medium/High canopy closure (>= 20%): ITU-R P.833 vegetation model
    """
    
    def __init__(self, 
                 frequency_mhz: float = 868.0,
                 tx_power_dbm: float = 14.0,
                 tx_gain_dbi: float = 2.15,
                 rx_gain_dbi: float = 2.15,
                 noise_floor_dbm: float = -120.0,
                 canopy_closure_map: Optional[np.ndarray] = None,
                 grid_resolution: float = 5.0,
                 domain_size: Tuple[float, float] = (1000, 1000)):
        """
        Initialize hybrid link calculator.
        
        Args:
            frequency_mhz: Operating frequency in MHz
            tx_power_dbm: Transmit power in dBm
            tx_gain_dbi: Transmit antenna gain in dBi
            rx_gain_dbi: Receive antenna gain in dBi
            noise_floor_dbm: Noise floor in dBm
            canopy_closure_map: 2D array of canopy closure (0-100%)
            grid_resolution: Resolution of canopy map in meters
            domain_size: (width, height) of domain in meters
        """
        self.frequency_mhz = frequency_mhz
        self.tx_power_dbm = tx_power_dbm
        self.tx_gain_dbi = tx_gain_dbi
        self.rx_gain_dbi = rx_gain_dbi
        self.noise_floor_dbm = noise_floor_dbm
        
        # Canopy closure map
        self.canopy_closure_map = canopy_closure_map
        self.grid_resolution = grid_resolution
        self.domain_size = domain_size
        
        # Create ITU-R P.833 model for forested areas
        self.forest_model = ITURP833Model(frequency_mhz)
        self.forest_model.set_vegetation_category('in_leaf')  # Summer forest
        
        # Wavelength for FSPL calculation
        self.wavelength = 3e8 / (frequency_mhz * 1e6)  # meters
        
        # Canopy closure threshold for model selection
        self.clearing_threshold = 20.0  # % canopy closure
    
    def calculate_fspl(self, distance_m: float) -> float:
        """
        Calculate Free Space Path Loss.
        
        FSPL(dB) = 20*log10(d) + 20*log10(f) + 20*log10(4π/c)
        
        Args:
            distance_m: Distance in meters
        
        Returns:
            Path loss in dB
        """
        if distance_m < 1.0:
            distance_m = 1.0
        
        # FSPL formula
        fspl = 20 * np.log10(distance_m) + 20 * np.log10(self.frequency_mhz * 1e6) - 147.55
        
        return fspl
    
    def get_canopy_closure_along_path(self, pos1: np.ndarray, pos2: np.ndarray,
                                     num_samples: int = 50) -> Tuple[float, np.ndarray]:
        """
        Sample canopy closure along the path between two points.
        
        Args:
            pos1: Starting position (x, y)
            pos2: Ending position (x, y)
            num_samples: Number of sample points along path
        
        Returns:
            Tuple of (average_canopy_closure, canopy_profile_array)
        """
        if self.canopy_closure_map is None:
            return 0.0, np.zeros(num_samples)
        
        # Sample points along path
        t = np.linspace(0, 1, num_samples)
        path_x = pos1[0] + t * (pos2[0] - pos1[0])
        path_y = pos1[1] + t * (pos2[1] - pos1[1])
        
        # Convert to grid indices
        grid_height, grid_width = self.canopy_closure_map.shape
        grid_i = np.clip((path_y / self.domain_size[1] * grid_height).astype(int), 
                        0, grid_height - 1)
        grid_j = np.clip((path_x / self.domain_size[0] * grid_width).astype(int), 
                        0, grid_width - 1)
        
        # Sample canopy closure
        canopy_profile = self.canopy_closure_map[grid_i, grid_j]
        average_canopy = np.mean(canopy_profile)
        
        return average_canopy, canopy_profile
    
    def calculate_link_loss(self, tx_pos: np.ndarray, rx_pos: np.ndarray,
                           tree_positions: Optional[np.ndarray] = None,
                           crown_radii: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Calculate link loss using hybrid propagation model.
        
        Args:
            tx_pos: Transmitter position (x, y)
            rx_pos: Receiver position (x, y)
            tree_positions: Array of tree positions (N, 2) - not used, kept for compatibility
            crown_radii: Array of crown radii (N,) - not used, kept for compatibility
        
        Returns:
            Dictionary with link parameters
        """
        # Calculate distance
        distance = np.linalg.norm(rx_pos - tx_pos)
        
        if distance < 1.0:
            distance = 1.0
        
        # Get canopy closure along path
        avg_canopy_closure, canopy_profile = self.get_canopy_closure_along_path(
            tx_pos, rx_pos, num_samples=50
        )
        
        # Calculate FSPL (always needed)
        fspl = self.calculate_fspl(distance)
        
        # Determine vegetation loss based on canopy closure
        if avg_canopy_closure < self.clearing_threshold:
            # Clearing area - use FSPL only
            veg_loss = 0.0
            terrain_type = 'clearing'
        else:
            # Forested area - use ITU-R P.833 model
            # Estimate effective vegetation depth based on canopy closure
            # Higher canopy closure = more vegetation penetration
            effective_depth = distance * (avg_canopy_closure / 100.0)
            veg_loss = self.forest_model.calculate_vegetation_loss(effective_depth)
            terrain_type = 'forest'
        
        # Total path loss
        total_loss = fspl + veg_loss
        
        # Calculate RSSI and SNR
        rssi = self.tx_power_dbm + self.tx_gain_dbi + self.rx_gain_dbi - total_loss
        snr = rssi - self.noise_floor_dbm
        
        return {
            'distance_m': distance,
            'avg_canopy_closure_pct': avg_canopy_closure,
            'terrain_type': terrain_type,
            'fspl_db': fspl,
            'vegetation_loss_db': veg_loss,
            'total_loss_db': total_loss,
            'rssi_dbm': rssi,
            'snr_db': snr
        }
    
    def find_best_gateway(self, sensor_pos: np.ndarray, gateway_positions: np.ndarray,
                         tree_positions: Optional[np.ndarray] = None,
                         crown_radii: Optional[np.ndarray] = None) -> Tuple[int, Dict[str, float]]:
        """
        Find best gateway for a sensor based on maximum RSSI.
        
        Args:
            sensor_pos: Sensor position (x, y)
            gateway_positions: Array of gateway positions (N, 2)
            tree_positions: Not used, kept for compatibility
            crown_radii: Not used, kept for compatibility
        
        Returns:
            Tuple of (best_gateway_idx, link_params)
        """
        best_rssi = -np.inf
        best_idx = 0
        best_params = {}
        
        for i, gw_pos in enumerate(gateway_positions):
            params = self.calculate_link_loss(gw_pos, sensor_pos)
            
            if params['rssi_dbm'] > best_rssi:
                best_rssi = params['rssi_dbm']
                best_idx = i
                best_params = params
        
        return best_idx, best_params
    
    def check_connectivity(self, sensor_positions: np.ndarray, 
                          gateway_positions: np.ndarray,
                          rssi_threshold_dbm: float = -85.0,
                          tree_positions: Optional[np.ndarray] = None,
                          crown_radii: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Check which sensors have connectivity to at least one gateway.
        
        Args:
            sensor_positions: Array of sensor positions (N, 2)
            gateway_positions: Array of gateway positions (M, 2)
            rssi_threshold_dbm: Minimum required RSSI in dBm (default: -85)
            tree_positions: Not used, kept for compatibility
            crown_radii: Not used, kept for compatibility
        
        Returns:
            Boolean array indicating connectivity for each sensor
        """
        connectivity = np.zeros(len(sensor_positions), dtype=bool)
        
        for i, sensor_pos in enumerate(sensor_positions):
            for gw_pos in gateway_positions:
                params = self.calculate_link_loss(gw_pos, sensor_pos)
                
                if params['rssi_dbm'] >= rssi_threshold_dbm:
                    connectivity[i] = True
                    break
        
        return connectivity
    
    def get_coverage_statistics(self) -> Dict[str, float]:
        """
        Get statistics about the canopy closure map.
        
        Returns:
            Dictionary with canopy statistics
        """
        if self.canopy_closure_map is None:
            return {
                'clearing_area_pct': 0.0,
                'forest_area_pct': 0.0,
                'avg_canopy_closure': 0.0
            }
        
        clearing_mask = self.canopy_closure_map < self.clearing_threshold
        forest_mask = self.canopy_closure_map >= self.clearing_threshold
        
        total_cells = self.canopy_closure_map.size
        clearing_cells = np.sum(clearing_mask)
        forest_cells = np.sum(forest_mask)
        
        return {
            'clearing_area_pct': 100 * clearing_cells / total_cells,
            'forest_area_pct': 100 * forest_cells / total_cells,
            'avg_canopy_closure': np.mean(self.canopy_closure_map),
            'max_canopy_closure': np.max(self.canopy_closure_map),
            'min_canopy_closure': np.min(self.canopy_closure_map)
        }
    
    def __repr__(self) -> str:
        return (f"HybridLinkCalculator(frequency={self.frequency_mhz} MHz, "
                f"tx_power={self.tx_power_dbm} dBm, "
                f"clearing_threshold={self.clearing_threshold}%)")

