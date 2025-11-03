"""
Poisson Disk Sampler

Fast Poisson disk sampling for generating spatially distributed tree positions
with minimum distance constraints.
"""

import numpy as np
from typing import Tuple, List, Optional


class PoissonDiskSampler:
    """
    Generates 2D points with minimum distance constraint using Poisson disk sampling.
    
    Implements Bridson's algorithm for fast Poisson disk sampling.
    """
    
    def __init__(self, width: float, height: float, min_distance: float, 
                 max_attempts: int = 30, seed: Optional[int] = None):
        """
        Initialize Poisson disk sampler.
        
        Args:
            width: Domain width
            height: Domain height
            min_distance: Minimum distance between points
            max_attempts: Maximum attempts to find new point around existing point
            seed: Random seed for reproducibility
        """
        self.width = width
        self.height = height
        self.min_distance = min_distance
        self.max_attempts = max_attempts
        
        if seed is not None:
            np.random.seed(seed)
        
        # Cell size for spatial grid (r / sqrt(2) for 2D)
        self.cell_size = min_distance / np.sqrt(2)
        
        # Grid dimensions
        self.grid_width = int(np.ceil(width / self.cell_size))
        self.grid_height = int(np.ceil(height / self.cell_size))
        
        # Initialize grid (-1 means empty)
        self.grid = np.full((self.grid_height, self.grid_width), -1, dtype=int)
        
        # List of sample points
        self.points = []
        
        # Active list for processing
        self.active = []
    
    def _get_grid_coords(self, point: np.ndarray) -> Tuple[int, int]:
        """
        Get grid cell coordinates for a point.
        
        Args:
            point: Point coordinates (x, y)
        
        Returns:
            Grid cell coordinates (row, col)
        """
        col = int(point[0] / self.cell_size)
        row = int(point[1] / self.cell_size)
        return (row, col)
    
    def _is_valid_point(self, point: np.ndarray) -> bool:
        """
        Check if point satisfies minimum distance constraint.
        
        Args:
            point: Point to check
        
        Returns:
            True if point is valid
        """
        # Check bounds
        if point[0] < 0 or point[0] >= self.width or point[1] < 0 or point[1] >= self.height:
            return False
        
        # Get grid cell
        row, col = self._get_grid_coords(point)
        
        # Check neighboring cells
        search_radius = int(np.ceil(self.min_distance / self.cell_size))
        
        for i in range(max(0, row - search_radius), min(self.grid_height, row + search_radius + 1)):
            for j in range(max(0, col - search_radius), min(self.grid_width, col + search_radius + 1)):
                if self.grid[i, j] != -1:
                    existing_point = self.points[self.grid[i, j]]
                    distance = np.linalg.norm(point - existing_point)
                    if distance < self.min_distance:
                        return False
        
        return True
    
    def _add_point(self, point: np.ndarray) -> None:
        """
        Add point to samples and update grid.
        
        Args:
            point: Point to add
        """
        self.points.append(point)
        point_idx = len(self.points) - 1
        
        row, col = self._get_grid_coords(point)
        self.grid[row, col] = point_idx
        
        self.active.append(point_idx)
    
    def _generate_around_point(self, point_idx: int) -> Optional[np.ndarray]:
        """
        Generate new point around an existing point.
        
        Args:
            point_idx: Index of existing point
        
        Returns:
            New valid point or None if no valid point found
        """
        point = self.points[point_idx]
        
        for _ in range(self.max_attempts):
            # Random angle
            angle = np.random.uniform(0, 2 * np.pi)
            
            # Random radius between min_distance and 2 * min_distance
            radius = np.random.uniform(self.min_distance, 2 * self.min_distance)
            
            # Generate candidate point
            candidate = point + radius * np.array([np.cos(angle), np.sin(angle)])
            
            if self._is_valid_point(candidate):
                return candidate
        
        return None
    
    def sample(self, target_count: Optional[int] = None) -> np.ndarray:
        """
        Generate Poisson disk samples.
        
        Args:
            target_count: Optional target number of points (stops when reached)
        
        Returns:
            Array of sampled points (N, 2)
        """
        # Reset state
        self.grid.fill(-1)
        self.points = []
        self.active = []
        
        # Add initial random point
        initial_point = np.array([
            np.random.uniform(0, self.width),
            np.random.uniform(0, self.height)
        ])
        self._add_point(initial_point)
        
        # Process active list
        while self.active:
            # Check target count
            if target_count is not None and len(self.points) >= target_count:
                break
            
            # Random index from active list
            active_idx = np.random.randint(0, len(self.active))
            point_idx = self.active[active_idx]
            
            # Try to generate new point
            new_point = self._generate_around_point(point_idx)
            
            if new_point is not None:
                self._add_point(new_point)
            else:
                # Remove from active list if no valid point found
                self.active.pop(active_idx)
        
        return np.array(self.points)
    
    def sample_with_variable_radii(self, radii: np.ndarray) -> np.ndarray:
        """
        Generate points with variable exclusion radii (e.g., for different crown sizes).
        
        Args:
            radii: Array of exclusion radii for each point to generate
        
        Returns:
            Array of sampled points (N, 2) where N <= len(radii)
        """
        # This is a simplified version - more complex implementation would
        # dynamically adjust min_distance for each point
        # For now, use maximum radius as global min_distance
        
        max_radius = np.max(radii)
        original_min_dist = self.min_distance
        
        self.min_distance = max_radius
        self.cell_size = max_radius / np.sqrt(2)
        
        # Regenerate grid with new cell size
        self.grid_width = int(np.ceil(self.width / self.cell_size))
        self.grid_height = int(np.ceil(self.height / self.cell_size))
        self.grid = np.full((self.grid_height, self.grid_width), -1, dtype=int)
        
        points = self.sample(target_count=len(radii))
        
        # Restore original parameters
        self.min_distance = original_min_dist
        
        return points


