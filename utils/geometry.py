"""
Geometry Utility Functions

Spatial calculations for forest map generation and sensor deployment.
"""

import numpy as np
from typing import Tuple, List
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two 2D points.
    
    Args:
        p1: First point (x, y)
        p2: Second point (x, y)
    
    Returns:
        Distance in same units as input
    """
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def distance_matrix(points1: np.ndarray, points2: np.ndarray) -> np.ndarray:
    """
    Calculate pairwise distance matrix between two sets of points.
    
    Args:
        points1: Array of shape (N, 2) with N points
        points2: Array of shape (M, 2) with M points
    
    Returns:
        Distance matrix of shape (N, M)
    """
    # Use broadcasting for efficient computation
    diff = points1[:, np.newaxis, :] - points2[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=2))
    return distances


def point_in_polygon(point: Tuple[float, float], polygon_vertices: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.
    
    Args:
        point: Point coordinates (x, y)
        polygon_vertices: List of polygon vertex coordinates
    
    Returns:
        True if point is inside polygon
    """
    poly = Polygon(polygon_vertices)
    pt = Point(point)
    return poly.contains(pt)


def line_intersects_circle(line_start: np.ndarray, line_end: np.ndarray, 
                          circle_center: np.ndarray, circle_radius: float) -> bool:
    """
    Check if a line segment intersects with a circle.
    
    Args:
        line_start: Start point of line (x, y)
        line_end: End point of line (x, y)
        circle_center: Center of circle (x, y)
        circle_radius: Radius of circle
    
    Returns:
        True if line intersects circle
    """
    # Vector from line start to end
    d = line_end - line_start
    # Vector from line start to circle center
    f = line_start - circle_center
    
    # Quadratic equation coefficients
    a = np.dot(d, d)
    b = 2 * np.dot(f, d)
    c = np.dot(f, f) - circle_radius**2
    
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        return False
    
    # Check if intersection points are within line segment
    discriminant = np.sqrt(discriminant)
    t1 = (-b - discriminant) / (2*a)
    t2 = (-b + discriminant) / (2*a)
    
    return (0 <= t1 <= 1) or (0 <= t2 <= 1) or (t1 < 0 and t2 > 1)


def line_vegetation_intersection_length(line_start: np.ndarray, line_end: np.ndarray,
                                        tree_positions: np.ndarray, crown_radii: np.ndarray) -> float:
    """
    Calculate total vegetation depth along a line through forest.
    
    Args:
        line_start: Start point (x, y)
        line_end: End point (x, y)
        tree_positions: Array of tree positions (N, 2)
        crown_radii: Array of crown radii (N,)
    
    Returns:
        Total vegetation depth in meters
    """
    total_depth = 0.0
    
    for tree_pos, crown_radius in zip(tree_positions, crown_radii):
        if line_intersects_circle(line_start, line_end, tree_pos, crown_radius):
            # Calculate intersection chord length
            # Distance from circle center to line
            line_vec = line_end - line_start
            line_len = np.linalg.norm(line_vec)
            
            if line_len < 1e-6:
                continue
                
            line_unit = line_vec / line_len
            center_to_start = tree_pos - line_start
            
            # Project center onto line
            projection_length = np.dot(center_to_start, line_unit)
            projection_point = line_start + projection_length * line_unit
            
            # Distance from center to line
            dist_to_line = np.linalg.norm(tree_pos - projection_point)
            
            if dist_to_line < crown_radius:
                # Chord length through circle
                chord_half = np.sqrt(crown_radius**2 - dist_to_line**2)
                chord_length = 2 * chord_half
                
                # Ensure chord is within line segment
                chord_start = projection_length - chord_half
                chord_end = projection_length + chord_half
                
                chord_start = max(0, chord_start)
                chord_end = min(line_len, chord_end)
                
                if chord_end > chord_start:
                    total_depth += (chord_end - chord_start)
    
    return total_depth


def grid_to_coordinates(grid_indices: Tuple[int, int], grid_origin: Tuple[float, float],
                       resolution: float) -> Tuple[float, float]:
    """
    Convert grid indices to real-world coordinates.
    
    Args:
        grid_indices: Grid cell indices (row, col)
        grid_origin: Origin coordinates (x, y) of grid
        resolution: Grid cell size in meters
    
    Returns:
        Real-world coordinates (x, y)
    """
    row, col = grid_indices
    x = grid_origin[0] + col * resolution
    y = grid_origin[1] + row * resolution
    return (x, y)


def coordinates_to_grid(coords: Tuple[float, float], grid_origin: Tuple[float, float],
                       resolution: float) -> Tuple[int, int]:
    """
    Convert real-world coordinates to grid indices.
    
    Args:
        coords: Real-world coordinates (x, y)
        grid_origin: Origin coordinates (x, y) of grid
        resolution: Grid cell size in meters
    
    Returns:
        Grid cell indices (row, col)
    """
    x, y = coords
    col = int((x - grid_origin[0]) / resolution)
    row = int((y - grid_origin[1]) / resolution)
    return (row, col)


def generate_circle_polygon(center: Tuple[float, float], radius: float, 
                           num_points: int = 32) -> List[Tuple[float, float]]:
    """
    Generate polygon vertices approximating a circle.
    
    Args:
        center: Circle center (x, y)
        radius: Circle radius
        num_points: Number of polygon vertices
    
    Returns:
        List of vertex coordinates
    """
    angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    vertices = [(center[0] + radius * np.cos(a), center[1] + radius * np.sin(a)) 
                for a in angles]
    return vertices


def minimum_spanning_distance(points: np.ndarray) -> float:
    """
    Calculate approximate minimum spanning tree length using nearest neighbor heuristic.
    
    Args:
        points: Array of points (N, 2)
    
    Returns:
        Approximate MST length
    """
    if len(points) <= 1:
        return 0.0
    
    # Simple nearest neighbor approximation
    visited = [False] * len(points)
    visited[0] = True
    total_distance = 0.0
    current_idx = 0
    
    for _ in range(len(points) - 1):
        min_dist = float('inf')
        next_idx = -1
        
        for i, point in enumerate(points):
            if not visited[i]:
                dist = euclidean_distance(points[current_idx], point)
                if dist < min_dist:
                    min_dist = dist
                    next_idx = i
        
        visited[next_idx] = True
        total_distance += min_dist
        current_idx = next_idx
    
    return total_distance


def check_minimum_spacing(new_point: np.ndarray, existing_points: np.ndarray, 
                         min_distance: float) -> bool:
    """
    Check if a new point maintains minimum spacing from existing points.
    
    Args:
        new_point: New point coordinates (x, y)
        existing_points: Array of existing points (N, 2)
        min_distance: Minimum required distance
    
    Returns:
        True if minimum spacing is satisfied
    """
    if len(existing_points) == 0:
        return True
    
    distances = np.sqrt(np.sum((existing_points - new_point)**2, axis=1))
    return np.all(distances >= min_distance)


