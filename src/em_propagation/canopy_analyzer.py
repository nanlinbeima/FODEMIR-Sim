"""
Canopy Closure Analyzer

Analyzes forest canopy closure from tree positions and creates digital terrain maps.
"""

import numpy as np
from typing import Tuple, Dict
from scipy.ndimage import gaussian_filter


class CanopyAnalyzer:
    """
    Analyzes canopy closure and creates digital terrain classification maps.
    
    Converts tree vector data into rasterized canopy closure percentage maps.
    """
    
    def __init__(self, width: float, height: float, 
                 resolution: float = 5.0,
                 origin: Tuple[float, float] = (0, 0)):
        """
        Initialize canopy analyzer.
        
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
        
        # Grid dimensions
        self.grid_width = int(np.ceil(width / resolution))
        self.grid_height = int(np.ceil(height / resolution))
        
        # Create coordinate grids
        x = np.linspace(origin[0], origin[0] + width, self.grid_width)
        y = np.linspace(origin[1], origin[1] + height, self.grid_height)
        self.grid_x, self.grid_y = np.meshgrid(x, y)
    
    def calculate_canopy_closure_map(self, tree_positions: np.ndarray,
                                     crown_radii: np.ndarray,
                                     smooth_sigma: float = 1.0) -> np.ndarray:
        """
        Calculate canopy closure map as percentage (0-100%).
        
        Canopy closure is the percentage of ground area covered by tree crowns
        when viewed from directly above.
        
        Args:
            tree_positions: Array of tree positions (N, 2)
            crown_radii: Array of crown radii (N,)
            smooth_sigma: Gaussian smoothing sigma (0 = no smoothing)
        
        Returns:
            2D array of canopy closure percentages (0-100)
        """
        # Initialize coverage map
        coverage_count = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        
        # For each tree, mark covered cells
        for pos, radius in zip(tree_positions, crown_radii):
            # Calculate distance from each grid point to tree center
            dist = np.sqrt((self.grid_x - pos[0])**2 + (self.grid_y - pos[1])**2)
            
            # Add coverage (with distance-weighted contribution for smooth edges)
            coverage_weight = np.clip(1.0 - (dist - radius) / (radius * 0.2), 0, 1)
            coverage_count += coverage_weight
        
        # Convert to percentage (cap at 100%)
        canopy_closure = np.minimum(coverage_count * 100.0, 100.0)
        
        # Apply Gaussian smoothing to reduce pixelation
        if smooth_sigma > 0:
            canopy_closure = gaussian_filter(canopy_closure, sigma=smooth_sigma)
        
        return canopy_closure
    
    def classify_terrain(self, canopy_closure_map: np.ndarray,
                        clearing_threshold: float = 20.0) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Classify terrain into clearing vs forest based on canopy closure.
        
        Args:
            canopy_closure_map: Canopy closure map (0-100%)
            clearing_threshold: Threshold for clearing classification (%)
        
        Returns:
            Tuple of (terrain_map, statistics)
            - terrain_map: 0=clearing, 1=forest
            - statistics: Dictionary with area percentages
        """
        # Classify terrain
        terrain_map = (canopy_closure_map >= clearing_threshold).astype(np.uint8)
        
        # Calculate statistics
        total_cells = terrain_map.size
        clearing_cells = np.sum(terrain_map == 0)
        forest_cells = np.sum(terrain_map == 1)
        
        stats = {
            'clearing_area_pct': 100 * clearing_cells / total_cells,
            'forest_area_pct': 100 * forest_cells / total_cells,
            'clearing_area_m2': clearing_cells * self.resolution ** 2,
            'forest_area_m2': forest_cells * self.resolution ** 2,
            'total_area_m2': total_cells * self.resolution ** 2,
            'avg_canopy_closure': np.mean(canopy_closure_map),
            'clearing_threshold': clearing_threshold
        }
        
        return terrain_map, stats
    
    def identify_clearings(self, canopy_closure_map: np.ndarray,
                          clearing_threshold: float = 20.0,
                          min_clearing_size: int = 10) -> list:
        """
        Identify discrete clearing patches in the forest.
        
        Args:
            canopy_closure_map: Canopy closure map (0-100%)
            clearing_threshold: Threshold for clearing classification (%)
            min_clearing_size: Minimum clearing size in cells
        
        Returns:
            List of clearing dictionaries with center position and size
        """
        from scipy.ndimage import label, center_of_mass
        
        # Binary mask of clearings
        clearing_mask = canopy_closure_map < clearing_threshold
        
        # Label connected components
        labeled_clearings, num_clearings = label(clearing_mask)
        
        clearings = []
        for i in range(1, num_clearings + 1):
            clearing_cells = (labeled_clearings == i)
            clearing_size = np.sum(clearing_cells)
            
            if clearing_size >= min_clearing_size:
                # Calculate center of mass
                center_idx = center_of_mass(clearing_cells)
                
                # Convert to real coordinates
                center_y = self.origin[1] + center_idx[0] * self.resolution
                center_x = self.origin[0] + center_idx[1] * self.resolution
                
                # Estimate radius
                radius = np.sqrt(clearing_size * self.resolution ** 2 / np.pi)
                
                clearings.append({
                    'center': np.array([center_x, center_y]),
                    'radius': radius,
                    'size_cells': int(clearing_size),
                    'size_m2': clearing_size * self.resolution ** 2
                })
        
        return clearings
    
    def get_canopy_statistics_by_zone(self, canopy_closure_map: np.ndarray,
                                     zone_size: int = 50) -> Dict:
        """
        Calculate canopy closure statistics for different zones.
        
        Args:
            canopy_closure_map: Canopy closure map
            zone_size: Size of zones in grid cells
        
        Returns:
            Dictionary with zonal statistics
        """
        zones_y = self.grid_height // zone_size
        zones_x = self.grid_width // zone_size
        
        zone_stats = []
        
        for i in range(zones_y):
            for j in range(zones_x):
                y_start = i * zone_size
                y_end = min((i + 1) * zone_size, self.grid_height)
                x_start = j * zone_size
                x_end = min((j + 1) * zone_size, self.grid_width)
                
                zone_data = canopy_closure_map[y_start:y_end, x_start:x_end]
                
                zone_stats.append({
                    'zone_id': i * zones_x + j,
                    'center_x': (x_start + x_end) / 2 * self.resolution,
                    'center_y': (y_start + y_end) / 2 * self.resolution,
                    'avg_canopy': np.mean(zone_data),
                    'max_canopy': np.max(zone_data),
                    'min_canopy': np.min(zone_data),
                    'std_canopy': np.std(zone_data)
                })
        
        return {
            'zones': zone_stats,
            'num_zones': len(zone_stats),
            'zone_size_m': zone_size * self.resolution
        }
    
    def export_canopy_map(self, canopy_closure_map: np.ndarray, filepath: str):
        """
        Export canopy closure map to file.
        
        Args:
            canopy_closure_map: Canopy closure map
            filepath: Output file path
        """
        np.save(filepath, canopy_closure_map)
        print(f"✓ Canopy closure map saved to: {filepath}")
    
    def load_canopy_map(self, filepath: str) -> np.ndarray:
        """
        Load canopy closure map from file.
        
        Args:
            filepath: Input file path
        
        Returns:
            Canopy closure map array
        """
        return np.load(filepath)

