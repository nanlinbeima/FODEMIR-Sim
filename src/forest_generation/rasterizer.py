"""
Forest Rasterizer

Converts vector forest data (tree positions, crown radii) into rasterized
crown coverage masks and GeoJSON export.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json


class ForestRasterizer:
    """
    Rasterizes forest map from vector tree data.
    
    Creates binary crown coverage masks and handles GeoJSON export.
    """
    
    def __init__(self, width: float, height: float, resolution: float = 0.5,
                 origin: Tuple[float, float] = (0, 0)):
        """
        Initialize forest rasterizer.
        
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
    
    def rasterize_crowns(self, tree_positions: np.ndarray, 
                        crown_radii: np.ndarray) -> np.ndarray:
        """
        Create binary mask of crown coverage.
        
        Args:
            tree_positions: Array of tree positions (N, 2)
            crown_radii: Array of crown radii (N,)
        
        Returns:
            Binary mask where 1 indicates crown coverage
        """
        mask = np.zeros((self.grid_height, self.grid_width), dtype=np.uint8)
        
        for pos, radius in zip(tree_positions, crown_radii):
            # Calculate distance from each grid point to tree center
            dist = np.sqrt((self.grid_x - pos[0])**2 + (self.grid_y - pos[1])**2)
            
            # Mark grid cells within crown radius
            mask[dist <= radius] = 1
        
        return mask
    
    def rasterize_density(self, tree_positions: np.ndarray,
                         crown_radii: np.ndarray) -> np.ndarray:
        """
        Create vegetation density map (count of overlapping crowns).
        
        Args:
            tree_positions: Array of tree positions (N, 2)
            crown_radii: Array of crown radii (N,)
        
        Returns:
            Density map with count of overlapping crowns per cell
        """
        density = np.zeros((self.grid_height, self.grid_width), dtype=np.int32)
        
        for pos, radius in zip(tree_positions, crown_radii):
            dist = np.sqrt((self.grid_x - pos[0])**2 + (self.grid_y - pos[1])**2)
            density[dist <= radius] += 1
        
        return density
    
    def export_to_geojson(self, tree_positions: np.ndarray, tree_attributes: List[Dict],
                         filepath: Path) -> None:
        """
        Export forest to GeoJSON format.
        
        Args:
            tree_positions: Array of tree positions (N, 2)
            tree_attributes: List of attribute dictionaries for each tree
            filepath: Output file path
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        features = []
        
        for i, (pos, attrs) in enumerate(zip(tree_positions, tree_attributes)):
            # Create point geometry for trunk
            point_geom = {
                'type': 'Point',
                'coordinates': [float(pos[0]), float(pos[1])]
            }
            
            # Convert attributes to JSON-serializable types
            properties = {'tree_id': i}
            for key, value in attrs.items():
                if isinstance(value, (np.integer, np.int64, np.int32)):
                    properties[key] = int(value)
                elif isinstance(value, (np.floating, np.float64, np.float32)):
                    properties[key] = float(value)
                else:
                    properties[key] = value
            
            feature = {
                'type': 'Feature',
                'geometry': point_geom,
                'properties': properties
            }
            
            features.append(feature)
        
        geojson_data = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2)
    
    def export_crown_polygons(self, tree_positions: np.ndarray, 
                             crown_radii: np.ndarray,
                             tree_attributes: List[Dict],
                             filepath: Path,
                             num_vertices: int = 32) -> None:
        """
        Export crown polygons to GeoJSON.
        
        Args:
            tree_positions: Array of tree positions (N, 2)
            crown_radii: Array of crown radii (N,)
            tree_attributes: List of attribute dictionaries
            filepath: Output file path
            num_vertices: Number of vertices for crown polygon approximation
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        features = []
        
        for i, (pos, radius, attrs) in enumerate(zip(tree_positions, crown_radii, tree_attributes)):
            # Generate circle vertices
            angles = np.linspace(0, 2*np.pi, num_vertices, endpoint=False)
            vertices = [[float(pos[0] + radius * np.cos(a)), 
                        float(pos[1] + radius * np.sin(a))] 
                       for a in angles]
            
            # Close the polygon
            vertices.append(vertices[0])
            
            polygon_geom = {
                'type': 'Polygon',
                'coordinates': [vertices]
            }
            
            # Convert attributes
            properties = {'tree_id': i}
            for key, value in attrs.items():
                if isinstance(value, (np.integer, np.int64, np.int32)):
                    properties[key] = int(value)
                elif isinstance(value, (np.floating, np.float64, np.float32)):
                    properties[key] = float(value)
                else:
                    properties[key] = value
            
            feature = {
                'type': 'Feature',
                'geometry': polygon_geom,
                'properties': properties
            }
            
            features.append(feature)
        
        geojson_data = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2)
    
    def get_coverage_statistics(self, crown_mask: np.ndarray) -> Dict[str, float]:
        """
        Calculate coverage statistics from crown mask.
        
        Args:
            crown_mask: Binary crown coverage mask
        
        Returns:
            Dictionary with coverage statistics
        """
        total_cells = crown_mask.size
        covered_cells = np.sum(crown_mask)
        
        coverage_percent = 100 * covered_cells / total_cells
        coverage_area_m2 = covered_cells * self.resolution ** 2
        
        return {
            'coverage_percent': coverage_percent,
            'coverage_area_m2': coverage_area_m2,
            'total_area_m2': self.width * self.height,
            'resolution_m': self.resolution,
            'grid_dimensions': (self.grid_height, self.grid_width)
        }
    
    def save_mask(self, mask: np.ndarray, filepath: Path) -> None:
        """
        Save binary mask to file.
        
        Args:
            mask: Binary mask array
            filepath: Output file path
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        np.save(filepath, mask)
    
    def load_mask(self, filepath: Path) -> np.ndarray:
        """
        Load binary mask from file.
        
        Args:
            filepath: Input file path
        
        Returns:
            Binary mask array
        """
        return np.load(filepath)


