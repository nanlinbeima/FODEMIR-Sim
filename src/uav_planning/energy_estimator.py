"""
Energy Estimator

Estimates UAV energy consumption for deployment missions.
"""

import numpy as np
from typing import Dict, Tuple, Optional


class EnergyEstimator:
    """
    Estimates energy consumption for UAV flight missions.
    
    Energy model includes:
    - Horizontal flight energy
    - Vertical climb/descent energy
    - Hovering energy (for sensor deployment)
    """
    
    def __init__(self, uav_mass_kg: float = 3.5, sensor_mass_kg: float = 0.2,
                 horizontal_energy_wh_per_m: float = 0.05,
                 vertical_energy_wh_per_m_per_kg: float = 0.15,
                 hover_power_w: float = 480.0):
        """
        Initialize energy estimator.
        
        Args:
            uav_mass_kg: UAV mass in kg
            sensor_mass_kg: Mass of one sensor in kg
            horizontal_energy_wh_per_m: Horizontal flight energy per meter (Wh/m)
            vertical_energy_wh_per_m_per_kg: Vertical flight energy per meter per kg (Wh/m/kg)
            hover_power_w: Hover power consumption in watts
        """
        self.uav_mass = uav_mass_kg
        self.sensor_mass = sensor_mass_kg
        self.horizontal_energy = horizontal_energy_wh_per_m
        self.vertical_energy = vertical_energy_wh_per_m_per_kg
        self.hover_power = hover_power_w
    
    def calculate_horizontal_energy(self, horizontal_distance: float, 
                                    payload_mass: float = 0.0) -> float:
        """
        Calculate energy for horizontal flight.
        
        Args:
            horizontal_distance: Horizontal distance in meters
            payload_mass: Current payload mass in kg
        
        Returns:
            Energy consumption in Wh
        """
        # Energy increases with payload but primarily distance-dependent
        total_mass = self.uav_mass + payload_mass
        mass_factor = total_mass / self.uav_mass
        
        energy = self.horizontal_energy * horizontal_distance * mass_factor
        return energy
    
    def calculate_vertical_energy(self, altitude_change: float, 
                                  payload_mass: float = 0.0) -> float:
        """
        Calculate energy for vertical flight (climb or descent).
        
        Args:
            altitude_change: Altitude change in meters (positive for climb)
            payload_mass: Current payload mass in kg
        
        Returns:
            Energy consumption in Wh
        """
        total_mass = self.uav_mass + payload_mass
        
        # Climbing requires energy; descending can be partially regenerated
        # For simplicity, we assume descent uses minimal energy
        if altitude_change > 0:
            energy = self.vertical_energy * altitude_change * total_mass
        else:
            # Descent energy is much lower (controlled descent)
            energy = 0.1 * self.vertical_energy * abs(altitude_change) * total_mass
        
        return energy
    
    def calculate_hover_energy(self, hover_time_seconds: float) -> float:
        """
        Calculate energy for hovering.
        
        Args:
            hover_time_seconds: Hover duration in seconds
        
        Returns:
            Energy consumption in Wh
        """
        energy_wh = (self.hover_power * hover_time_seconds) / 3600.0
        return energy_wh
    
    def calculate_trajectory_energy(self, trajectory: np.ndarray, 
                                   drop_indices: Optional[np.ndarray] = None,
                                   hover_time_per_drop: float = 5.0) -> Dict:
        """
        Calculate total energy for a trajectory.
        
        Args:
            trajectory: 3D trajectory array (N, 3)
            drop_indices: Indices where sensors are dropped
            hover_time_per_drop: Hover time at each drop point in seconds
        
        Returns:
            Dictionary with energy breakdown
        """
        if drop_indices is None:
            drop_indices = []
        
        # Initialize payload (all sensors at start)
        n_sensors = len(drop_indices)
        current_payload = n_sensors * self.sensor_mass
        
        # Energy components
        horizontal_energy = 0.0
        vertical_energy = 0.0
        hover_energy = 0.0
        
        # Cumulative energy at each waypoint
        cumulative_energy = [0.0]
        
        sensors_dropped = 0
        
        for i in range(len(trajectory) - 1):
            start = trajectory[i]
            end = trajectory[i + 1]
            
            # Calculate segment distances
            segment_3d = end - start
            horizontal_dist = np.linalg.norm(segment_3d[:2])  # x-y distance
            altitude_change = segment_3d[2]  # z change
            
            # Horizontal energy
            h_energy = self.calculate_horizontal_energy(horizontal_dist, current_payload)
            horizontal_energy += h_energy
            
            # Vertical energy
            v_energy = self.calculate_vertical_energy(altitude_change, current_payload)
            vertical_energy += v_energy
            
            # Check if this is a drop point
            if i in drop_indices:
                # Hover energy for deployment
                hov_energy = self.calculate_hover_energy(hover_time_per_drop)
                hover_energy += hov_energy
                
                # Reduce payload
                current_payload -= self.sensor_mass
                sensors_dropped += 1
            
            # Update cumulative energy
            cumulative_energy.append(cumulative_energy[-1] + h_energy + v_energy + 
                                    (hov_energy if i in drop_indices else 0))
        
        total_energy = horizontal_energy + vertical_energy + hover_energy
        
        return {
            'total_energy_wh': total_energy,
            'horizontal_energy_wh': horizontal_energy,
            'vertical_energy_wh': vertical_energy,
            'hover_energy_wh': hover_energy,
            'cumulative_energy_wh': np.array(cumulative_energy),
            'energy_breakdown': {
                'horizontal_percent': 100 * horizontal_energy / total_energy if total_energy > 0 else 0,
                'vertical_percent': 100 * vertical_energy / total_energy if total_energy > 0 else 0,
                'hover_percent': 100 * hover_energy / total_energy if total_energy > 0 else 0
            }
        }
    
    def check_battery_feasibility(self, total_energy_wh: float, 
                                  battery_capacity_wh: float,
                                  safety_margin: float = 0.2) -> Tuple[bool, float]:
        """
        Check if mission is feasible with given battery capacity.
        
        Args:
            total_energy_wh: Required mission energy in Wh
            battery_capacity_wh: Battery capacity in Wh
            safety_margin: Safety margin (0.2 = 20% reserve)
        
        Returns:
            Tuple of (is_feasible, remaining_capacity_percent)
        """
        usable_capacity = battery_capacity_wh * (1 - safety_margin)
        is_feasible = total_energy_wh <= usable_capacity
        
        remaining_percent = 100 * (usable_capacity - total_energy_wh) / battery_capacity_wh
        
        return is_feasible, remaining_percent
    
    def estimate_flight_time(self, total_energy_wh: float, 
                            average_power_w: Optional[float] = None) -> float:
        """
        Estimate total flight time.
        
        Args:
            total_energy_wh: Total energy consumption in Wh
            average_power_w: Average power consumption (defaults to hover power)
        
        Returns:
            Estimated flight time in seconds
        """
        if average_power_w is None:
            average_power_w = self.hover_power
        
        flight_time_hours = total_energy_wh / average_power_w
        flight_time_seconds = flight_time_hours * 3600
        
        return flight_time_seconds
    
    def optimize_payload_distribution(self, n_sensors: int, 
                                      max_payload_kg: float) -> Tuple[int, int]:
        """
        Determine if mission requires multiple trips.
        
        Args:
            n_sensors: Total number of sensors to deploy
            max_payload_kg: Maximum payload capacity in kg
        
        Returns:
            Tuple of (n_trips, sensors_per_trip)
        """
        total_sensor_mass = n_sensors * self.sensor_mass
        
        if total_sensor_mass <= max_payload_kg:
            return 1, n_sensors
        else:
            sensors_per_trip = int(max_payload_kg / self.sensor_mass)
            n_trips = int(np.ceil(n_sensors / sensors_per_trip))
            return n_trips, sensors_per_trip

