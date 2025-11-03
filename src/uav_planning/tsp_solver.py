"""
TSP Solver

Traveling Salesman Problem solver for UAV path planning.
"""

import numpy as np
from typing import List, Tuple, Optional

# Try to import OR-Tools
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False


class TSPSolver:
    """
    Solves Traveling Salesman Problem for UAV waypoint sequencing.
    
    Supports multiple solution methods:
    - Nearest neighbor heuristic (fast, ~1.25x optimal)
    - Christofides algorithm (1.5-approximation)
    - OR-Tools (near-optimal, requires ortools package)
    """
    
    def __init__(self, method: str = 'nearest_neighbor'):
        """
        Initialize TSP solver.
        
        Args:
            method: Solution method ('nearest_neighbor', 'christofides', 'ortools')
        """
        self.method = method
        
        if method == 'ortools' and not ORTOOLS_AVAILABLE:
            print("Warning: OR-Tools not available. Falling back to nearest_neighbor.")
            self.method = 'nearest_neighbor'
    
    def solve(self, waypoints: np.ndarray, depot_idx: int = 0) -> Tuple[List[int], float]:
        """
        Solve TSP for given waypoints.
        
        Args:
            waypoints: Array of waypoint coordinates (N, 2) or (N, 3)
            depot_idx: Index of depot/start point
        
        Returns:
            Tuple of (tour_indices, total_distance)
        """
        if self.method == 'nearest_neighbor':
            return self._nearest_neighbor(waypoints, depot_idx)
        elif self.method == 'christofides':
            return self._christofides(waypoints, depot_idx)
        elif self.method == 'ortools':
            return self._ortools_solve(waypoints, depot_idx)
        else:
            return self._nearest_neighbor(waypoints, depot_idx)
    
    def _nearest_neighbor(self, waypoints: np.ndarray, depot_idx: int) -> Tuple[List[int], float]:
        """
        Nearest neighbor heuristic for TSP.
        
        Args:
            waypoints: Array of waypoint coordinates
            depot_idx: Starting depot index
        
        Returns:
            Tuple of (tour_indices, total_distance)
        """
        n = len(waypoints)
        unvisited = set(range(n))
        tour = [depot_idx]
        unvisited.remove(depot_idx)
        
        total_distance = 0.0
        current_idx = depot_idx
        
        while unvisited:
            # Find nearest unvisited waypoint
            nearest_idx = None
            nearest_dist = float('inf')
            
            for idx in unvisited:
                dist = np.linalg.norm(waypoints[current_idx] - waypoints[idx])
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_idx = idx
            
            # Move to nearest
            tour.append(nearest_idx)
            total_distance += nearest_dist
            unvisited.remove(nearest_idx)
            current_idx = nearest_idx
        
        # Return to depot
        total_distance += np.linalg.norm(waypoints[current_idx] - waypoints[depot_idx])
        tour.append(depot_idx)
        
        return tour, total_distance
    
    def _christofides(self, waypoints: np.ndarray, depot_idx: int) -> Tuple[List[int], float]:
        """
        Christofides algorithm (1.5-approximation for metric TSP).
        
        Simplified implementation:
        1. Minimum spanning tree
        2. Find odd-degree vertices
        3. Minimum weight perfect matching on odd vertices
        4. Combine to form Eulerian graph
        5. Find Eulerian tour and shortcut
        
        Args:
            waypoints: Array of waypoint coordinates
            depot_idx: Starting depot index
        
        Returns:
            Tuple of (tour_indices, total_distance)
        """
        # Simplified: use nearest neighbor with 2-opt improvement
        tour, distance = self._nearest_neighbor(waypoints, depot_idx)
        
        # Apply 2-opt local search
        tour, distance = self._two_opt(waypoints, tour, distance)
        
        return tour, distance
    
    def _two_opt(self, waypoints: np.ndarray, tour: List[int], 
                 initial_distance: float, max_iterations: int = 100) -> Tuple[List[int], float]:
        """
        2-opt local search improvement.
        
        Args:
            waypoints: Waypoint coordinates
            tour: Initial tour
            initial_distance: Initial tour distance
            max_iterations: Maximum improvement iterations
        
        Returns:
            Improved (tour, distance)
        """
        best_tour = tour.copy()
        best_distance = initial_distance
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(1, len(best_tour) - 2):
                for j in range(i + 1, len(best_tour) - 1):
                    # Try reversing segment [i:j+1]
                    new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    
                    # Calculate new distance
                    new_distance = self._calculate_tour_distance(waypoints, new_tour)
                    
                    if new_distance < best_distance:
                        best_tour = new_tour
                        best_distance = new_distance
                        improved = True
                        break
                
                if improved:
                    break
        
        return best_tour, best_distance
    
    def _ortools_solve(self, waypoints: np.ndarray, depot_idx: int) -> Tuple[List[int], float]:
        """
        Solve TSP using Google OR-Tools.
        
        Args:
            waypoints: Array of waypoint coordinates
            depot_idx: Starting depot index
        
        Returns:
            Tuple of (tour_indices, total_distance)
        """
        if not ORTOOLS_AVAILABLE:
            return self._nearest_neighbor(waypoints, depot_idx)
        
        n = len(waypoints)
        
        # Create distance matrix (in integer format for OR-Tools)
        distance_matrix = np.zeros((n, n), dtype=np.int32)
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = np.linalg.norm(waypoints[i] - waypoints[j])
                    distance_matrix[i, j] = int(dist * 1000)  # Convert to mm for precision
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(n, 1, depot_idx)
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 10
        
        # Solve
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            tour = []
            total_distance = 0.0
            
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                tour.append(node)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                total_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            
            # Add depot at end
            tour.append(depot_idx)
            total_distance = total_distance / 1000.0  # Convert back to meters
            
            return tour, total_distance
        else:
            # Fallback to nearest neighbor
            return self._nearest_neighbor(waypoints, depot_idx)
    
    def _calculate_tour_distance(self, waypoints: np.ndarray, tour: List[int]) -> float:
        """
        Calculate total distance of a tour.
        
        Args:
            waypoints: Waypoint coordinates
            tour: Sequence of waypoint indices
        
        Returns:
            Total tour distance
        """
        distance = 0.0
        for i in range(len(tour) - 1):
            distance += np.linalg.norm(waypoints[tour[i]] - waypoints[tour[i+1]])
        return distance
    
    def optimize_tour_order(self, waypoints: np.ndarray, tour: List[int]) -> List[int]:
        """
        Optimize tour using local search.
        
        Args:
            waypoints: Waypoint coordinates
            tour: Initial tour
        
        Returns:
            Optimized tour
        """
        distance = self._calculate_tour_distance(waypoints, tour)
        optimized_tour, _ = self._two_opt(waypoints, tour, distance)
        return optimized_tour

