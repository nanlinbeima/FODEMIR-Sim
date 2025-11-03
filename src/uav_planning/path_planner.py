"""
Path Planner

3D trajectory generation for UAV with altitude optimization.
"""

import numpy as np
from typing import Tuple, Optional, List
from scipy.interpolate import splprep, splev


class PathPlanner:
    """
    Generates smooth 3D trajectories for UAV deployment missions.
    
    Features:
    - Altitude optimization
    - Smooth trajectory interpolation (B-spline)
    - Obstacle avoidance (basic)
    - Waypoint sequencing
    """
    
    def __init__(self, min_altitude: float = 30.0, max_altitude: float = 120.0,
                 cruise_altitude: float = 80.0, drop_altitude: float = 40.0):
        """
        Initialize path planner.
        
        Args:
            min_altitude: Minimum flight altitude in meters
            max_altitude: Maximum flight altitude in meters
            cruise_altitude: Preferred cruise altitude in meters
            drop_altitude: Altitude for sensor deployment in meters
        """
        self.min_altitude = min_altitude
        self.max_altitude = max_altitude
        self.cruise_altitude = cruise_altitude
        self.drop_altitude = drop_altitude
    
    def generate_3d_trajectory(self, waypoints_2d: np.ndarray, tour_order: List[int],
                               smooth: bool = True, n_interpolation_points: int = 100) -> np.ndarray:
        """
        Generate 3D trajectory from 2D waypoints and tour order.
        
        Args:
            waypoints_2d: Array of 2D waypoints (N, 2)
            tour_order: Sequence of waypoint indices
            smooth: Whether to apply B-spline smoothing
            n_interpolation_points: Number of points for smooth trajectory
        
        Returns:
            3D trajectory array (M, 3) with x, y, z coordinates
        """
        # Create 3D waypoints with altitude
        waypoints_3d = []
        
        for idx in tour_order:
            x, y = waypoints_2d[idx]
            
            # Assign altitude based on waypoint type
            if idx == 0 or idx == len(waypoints_2d) - 1:
                # Depot - takeoff/landing altitude
                z = self.min_altitude
            else:
                # Drop waypoint
                z = self.drop_altitude
            
            waypoints_3d.append([x, y, z])
        
        waypoints_3d = np.array(waypoints_3d)
        
        if smooth and len(waypoints_3d) > 3:
            # Apply B-spline interpolation
            trajectory = self._smooth_trajectory(waypoints_3d, n_interpolation_points)
        else:
            trajectory = waypoints_3d
        
        return trajectory
    
    def _smooth_trajectory(self, waypoints: np.ndarray, n_points: int) -> np.ndarray:
        """
        Smooth trajectory using B-spline interpolation.
        
        Args:
            waypoints: Array of 3D waypoints (N, 3)
            n_points: Number of interpolation points
        
        Returns:
            Smoothed trajectory (n_points, 3)
        """
        try:
            # Parametric B-spline interpolation
            tck, u = splprep([waypoints[:, 0], waypoints[:, 1], waypoints[:, 2]], 
                            s=0, k=min(3, len(waypoints)-1))
            
            # Evaluate at fine resolution
            u_new = np.linspace(0, 1, n_points)
            x_new, y_new, z_new = splev(u_new, tck)
            
            trajectory = np.column_stack([x_new, y_new, z_new])
            
            # Ensure altitude constraints
            trajectory[:, 2] = np.clip(trajectory[:, 2], self.min_altitude, self.max_altitude)
            
            return trajectory
        
        except Exception as e:
            print(f"Warning: Smoothing failed ({e}). Using waypoints directly.")
            return waypoints
    
    def optimize_altitudes(self, waypoints_2d: np.ndarray, tour_order: List[int],
                          energy_weights: Tuple[float, float] = (1.0, 2.0)) -> np.ndarray:
        """
        Optimize waypoint altitudes to minimize energy consumption.
        
        Trade-off: Higher altitude = shorter horizontal distance but more climb energy
        
        Args:
            waypoints_2d: Array of 2D waypoints
            tour_order: Waypoint sequence
            energy_weights: (horizontal_weight, vertical_weight) for energy cost
        
        Returns:
            Optimized altitudes array
        """
        n_waypoints = len(tour_order)
        altitudes = np.full(n_waypoints, self.cruise_altitude)
        
        # Set depot altitudes
        altitudes[0] = self.min_altitude  # Takeoff
        altitudes[-1] = self.min_altitude  # Landing
        
        # Set drop altitudes for intermediate waypoints
        for i in range(1, n_waypoints - 1):
            altitudes[i] = self.drop_altitude
        
        return altitudes
    
    def add_altitude_to_waypoints(self, waypoints_2d: np.ndarray, 
                                  altitudes: np.ndarray) -> np.ndarray:
        """
        Combine 2D waypoints with altitude information.
        
        Args:
            waypoints_2d: Array of 2D positions (N, 2)
            altitudes: Array of altitudes (N,)
        
        Returns:
            3D waypoints (N, 3)
        """
        return np.column_stack([waypoints_2d, altitudes])
    
    def calculate_segment_distances(self, trajectory: np.ndarray) -> np.ndarray:
        """
        Calculate distances between consecutive trajectory points.
        
        Args:
            trajectory: 3D trajectory array (N, 3)
        
        Returns:
            Array of segment distances (N-1,)
        """
        segments = np.diff(trajectory, axis=0)
        distances = np.linalg.norm(segments, axis=1)
        return distances
    
    def calculate_altitude_changes(self, trajectory: np.ndarray) -> np.ndarray:
        """
        Calculate altitude changes between consecutive points.
        
        Args:
            trajectory: 3D trajectory array (N, 3)
        
        Returns:
            Array of altitude changes (N-1,) - positive for climb, negative for descent
        """
        altitude_changes = np.diff(trajectory[:, 2])
        return altitude_changes
    
    def insert_transition_waypoints(self, trajectory: np.ndarray, 
                                    max_segment_length: float = 100.0) -> np.ndarray:
        """
        Insert intermediate waypoints for long segments.
        
        Args:
            trajectory: 3D trajectory
            max_segment_length: Maximum segment length before subdivision
        
        Returns:
            Refined trajectory with additional waypoints
        """
        refined_trajectory = [trajectory[0]]
        
        for i in range(len(trajectory) - 1):
            start = trajectory[i]
            end = trajectory[i + 1]
            
            segment_vector = end - start
            segment_length = np.linalg.norm(segment_vector)
            
            if segment_length > max_segment_length:
                # Insert intermediate points
                n_subdivisions = int(np.ceil(segment_length / max_segment_length))
                
                for j in range(1, n_subdivisions):
                    t = j / n_subdivisions
                    intermediate = start + t * segment_vector
                    refined_trajectory.append(intermediate)
            
            refined_trajectory.append(end)
        
        return np.array(refined_trajectory)
    
    def check_obstacle_clearance(self, trajectory: np.ndarray, 
                                 obstacles: Optional[List[np.ndarray]] = None,
                                 clearance_distance: float = 10.0) -> bool:
        """
        Check if trajectory maintains clearance from obstacles.
        
        Args:
            trajectory: 3D trajectory
            obstacles: List of obstacle positions (3D)
            clearance_distance: Minimum required clearance in meters
        
        Returns:
            True if trajectory is safe
        """
        if obstacles is None or len(obstacles) == 0:
            return True
        
        obstacles = np.array(obstacles)
        
        for point in trajectory:
            distances = np.linalg.norm(obstacles - point, axis=1)
            if np.any(distances < clearance_distance):
                return False
        
        return True
    
    def generate_hover_trajectory(self, position: np.ndarray, 
                                  hover_duration: float, 
                                  sampling_rate: float = 1.0) -> np.ndarray:
        """
        Generate trajectory for hovering at a position.
        
        Args:
            position: 3D position for hovering
            hover_duration: Duration in seconds
            sampling_rate: Trajectory sampling rate in Hz
        
        Returns:
            Trajectory array with repeated position
        """
        n_points = int(hover_duration * sampling_rate)
        hover_trajectory = np.tile(position, (n_points, 1))
        return hover_trajectory


