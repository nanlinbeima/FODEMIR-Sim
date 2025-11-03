"""
Coverage Analyzer

Analyzes wireless coverage over forest area using grid-based signal strength maps.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.spatial import Voronoi
from .propagation_base import PropagationModel
from .link_calculator import LinkCalculator


class CoverageAnalyzer:
    """
    Analyzes wireless coverage using grid-based signal strength computation.
    
    Creates coverage heatmaps and calculates coverage statistics.
    """
    
    def __init__(self, width: float, height: float, resolution: float = 5.0,
                 origin: Tuple[float, float] = (0, 0)):
        """
        Initialize coverage analyzer.
        
        Args:
            width: Domain width in meters
            height: Domain height in meters
            resolution: Grid cell size in meters
            origin: Origin coordinates (x0, y0)
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin = origin
        
        # Create grid
        self.grid_width = int(np.ceil(width / resolution))
        self.grid_height = int(np.ceil(height / resolution))
        
        # Grid coordinates
        x = np.linspace(origin[0], origin[0] + width, self.grid_width)
        y = np.linspace(origin[1], origin[1] + height, self.grid_height)
        self.grid_x, self.grid_y = np.meshgrid(x, y)
        
        # Flatten for computation
        self.grid_points = np.column_stack([self.grid_x.ravel(), self.grid_y.ravel()])
    
    def calculate_coverage_map(self, gateway_positions: np.ndarray,
                              link_calculator: LinkCalculator,
                              tree_positions: Optional[np.ndarray] = None,
                              crown_radii: Optional[np.ndarray] = None,
                              metric: str = 'snr') -> np.ndarray:
        """
        Calculate coverage map using specified metric.
        
        Args:
            gateway_positions: Array of gateway positions (N, 2)
            link_calculator: LinkCalculator instance
            tree_positions: Array of tree positions
            crown_radii: Array of crown radii
            metric: Metric to compute ('snr', 'rssi', 'path_loss')
        
        Returns:
            2D array with metric values
        """
        n_points = len(self.grid_points)
        metric_values = np.full(n_points, -np.inf if metric != 'path_loss' else np.inf)
        
        # For each grid point, find best gateway
        for i, point in enumerate(self.grid_points):
            best_value = -np.inf if metric != 'path_loss' else np.inf
            
            for gw_pos in gateway_positions:
                params = link_calculator.calculate_link_loss(
                    gw_pos, point, tree_positions, crown_radii
                )
                
                if metric == 'snr':
                    value = params['snr_db']
                    if value > best_value:
                        best_value = value
                elif metric == 'rssi':
                    value = params['rssi_dbm']
                    if value > best_value:
                        best_value = value
                elif metric == 'path_loss':
                    value = params['total_loss_db']
                    if value < best_value:
                        best_value = value
            
            metric_values[i] = best_value
        
        # Reshape to 2D grid
        coverage_map = metric_values.reshape(self.grid_height, self.grid_width)
        
        return coverage_map
    
    def calculate_coverage_statistics(self, coverage_map: np.ndarray,
                                     threshold: float,
                                     metric: str = 'snr') -> Dict[str, float]:
        """
        Calculate coverage statistics.
        
        Args:
            coverage_map: 2D coverage map
            threshold: Threshold value for coverage
            metric: Metric type ('snr', 'rssi', 'path_loss')
        
        Returns:
            Dictionary with statistics
        """
        # Determine coverage based on metric type
        if metric in ['snr', 'rssi']:
            covered = coverage_map >= threshold
        else:  # path_loss
            covered = coverage_map <= threshold
        
        total_cells = coverage_map.size
        covered_cells = np.sum(covered)
        
        coverage_percent = 100 * covered_cells / total_cells
        coverage_area_m2 = covered_cells * self.resolution ** 2
        blind_area_ratio = 1.0 - (covered_cells / total_cells)
        
        # Additional statistics
        valid_values = coverage_map[np.isfinite(coverage_map)]
        
        stats = {
            'coverage_percent': coverage_percent,
            'coverage_area_m2': coverage_area_m2,
            'blind_area_ratio': blind_area_ratio,
            'covered_cells': int(covered_cells),
            'total_cells': int(total_cells),
            'mean_value': np.mean(valid_values) if len(valid_values) > 0 else 0.0,
            'median_value': np.median(valid_values) if len(valid_values) > 0 else 0.0,
            'min_value': np.min(valid_values) if len(valid_values) > 0 else 0.0,
            'max_value': np.max(valid_values) if len(valid_values) > 0 else 0.0,
            'std_value': np.std(valid_values) if len(valid_values) > 0 else 0.0
        }
        
        return stats
    
    def identify_dead_zones(self, coverage_map: np.ndarray, threshold: float,
                           min_zone_size: int = 4) -> List[Tuple[int, int, int]]:
        """
        Identify contiguous dead zones (areas below threshold).
        
        Args:
            coverage_map: 2D coverage map
            threshold: Coverage threshold
            min_zone_size: Minimum number of cells to constitute a zone
        
        Returns:
            List of (row, col, size) tuples for dead zones
        """
        # Simple connected component analysis
        dead_cells = coverage_map < threshold
        
        # Find connected components (simplified version)
        visited = np.zeros_like(dead_cells, dtype=bool)
        zones = []
        
        def flood_fill(start_r, start_c):
            """Simple flood fill to find connected dead cells."""
            stack = [(start_r, start_c)]
            zone_cells = []
            
            while stack:
                r, c = stack.pop()
                
                if (r < 0 or r >= self.grid_height or 
                    c < 0 or c >= self.grid_width or
                    visited[r, c] or not dead_cells[r, c]):
                    continue
                
                visited[r, c] = True
                zone_cells.append((r, c))
                
                # Add neighbors
                stack.extend([(r+1, c), (r-1, c), (r, c+1), (r, c-1)])
            
            return zone_cells
        
        # Find all zones
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if dead_cells[i, j] and not visited[i, j]:
                    zone_cells = flood_fill(i, j)
                    
                    if len(zone_cells) >= min_zone_size:
                        # Calculate zone center
                        center_r = int(np.mean([r for r, c in zone_cells]))
                        center_c = int(np.mean([c for r, c in zone_cells]))
                        zones.append((center_r, center_c, len(zone_cells)))
        
        return zones
    
    def calculate_best_sensor_positions(self, coverage_map: np.ndarray,
                                       n_positions: int,
                                       threshold: float) -> np.ndarray:
        """
        Find best positions for additional sensors to improve coverage.
        
        Uses greedy approach to find positions in worst-covered areas.
        
        Args:
            coverage_map: Current coverage map
            n_positions: Number of positions to suggest
            threshold: Coverage threshold
        
        Returns:
            Array of suggested positions (n_positions, 2)
        """
        # Find cells below threshold
        poor_coverage = coverage_map < threshold
        
        # Get coordinates of poor coverage cells
        poor_indices = np.where(poor_coverage)
        
        if len(poor_indices[0]) == 0:
            # No poor coverage areas, return random positions
            return np.random.rand(n_positions, 2) * [self.width, self.height] + self.origin
        
        # Convert to real coordinates
        poor_coords = np.column_stack([
            self.grid_x[poor_indices],
            self.grid_y[poor_indices]
        ])
        
        # Greedy selection: choose most poorly covered points
        coverage_values = coverage_map[poor_indices]
        sorted_indices = np.argsort(coverage_values)[:n_positions]
        
        suggested_positions = poor_coords[sorted_indices]
        
        return suggested_positions
    
    def visualize_gateway_coverage(self, gateway_positions: np.ndarray,
                                   coverage_map: np.ndarray) -> Dict[int, np.ndarray]:
        """
        Determine which gateway serves each grid cell.
        
        Args:
            gateway_positions: Array of gateway positions
            coverage_map: Coverage map
        
        Returns:
            Dictionary mapping gateway index to coverage mask
        """
        n_gateways = len(gateway_positions)
        gateway_masks = {}
        
        # Simple Voronoi-based assignment
        # For each grid point, assign to nearest gateway
        distances = np.zeros((len(self.grid_points), n_gateways))
        
        for i, gw_pos in enumerate(gateway_positions):
            diff = self.grid_points - gw_pos
            distances[:, i] = np.sqrt(np.sum(diff**2, axis=1))
        
        nearest_gateway = np.argmin(distances, axis=1)
        
        for i in range(n_gateways):
            mask = (nearest_gateway == i).reshape(self.grid_height, self.grid_width)
            gateway_masks[i] = mask
        
        return gateway_masks
    
    def export_coverage_data(self, coverage_map: np.ndarray,
                            filepath: str) -> None:
        """
        Export coverage map to file.
        
        Args:
            coverage_map: Coverage map array
            filepath: Output file path
        """
        np.save(filepath, coverage_map)


