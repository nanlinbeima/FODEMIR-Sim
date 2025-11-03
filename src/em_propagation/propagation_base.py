"""
Propagation Model Base Class

Abstract base class for electromagnetic propagation models in forest environments.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Union


class PropagationModel(ABC):
    """
    Abstract base class for vegetation propagation models.
    
    All propagation models should inherit from this class and implement
    the calculate_vegetation_loss method.
    """
    
    def __init__(self, frequency_mhz: float):
        """
        Initialize propagation model.
        
        Args:
            frequency_mhz: Operating frequency in MHz
        """
        self.frequency_mhz = frequency_mhz
        self.speed_of_light = 3e8  # m/s
        self.wavelength = self.speed_of_light / (frequency_mhz * 1e6)  # meters
    
    @abstractmethod
    def calculate_vegetation_loss(self, vegetation_depth_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate vegetation-induced path loss.
        
        Args:
            vegetation_depth_m: Depth of vegetation along path in meters
        
        Returns:
            Vegetation loss in dB
        """
        pass
    
    def calculate_free_space_loss(self, distance_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate free-space path loss (FSPL).
        
        FSPL (dB) = 20*log10(d) + 20*log10(f) + 32.45
        
        Args:
            distance_m: Distance in meters
        
        Returns:
            Free-space path loss in dB
        """
        # Avoid log of zero
        distance_m = np.maximum(distance_m, 1e-3)
        
        fspl = 20 * np.log10(distance_m) + 20 * np.log10(self.frequency_mhz) + 32.45
        return fspl
    
    def calculate_total_loss(self, distance_m: Union[float, np.ndarray],
                            vegetation_depth_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate total path loss including free space and vegetation.
        
        Args:
            distance_m: Total link distance in meters
            vegetation_depth_m: Vegetation depth along path in meters
        
        Returns:
            Total path loss in dB
        """
        fspl = self.calculate_free_space_loss(distance_m)
        veg_loss = self.calculate_vegetation_loss(vegetation_depth_m)
        
        return fspl + veg_loss
    
    def calculate_ground_reflection_loss(self, distance_m: Union[float, np.ndarray],
                                        tx_height_m: float, rx_height_m: float,
                                        reflection_coefficient: float = 0.3) -> Union[float, np.ndarray]:
        """
        Calculate ground reflection loss using simplified two-ray model.
        
        Args:
            distance_m: Horizontal distance in meters
            tx_height_m: Transmitter height in meters
            rx_height_m: Receiver height in meters
            reflection_coefficient: Ground reflection coefficient (0-1)
        
        Returns:
            Additional loss due to ground reflection in dB
        """
        # Simplified model - full two-ray model is more complex
        # This approximates multipath interference
        
        if np.any(distance_m < 1):
            return 0
        
        # Critical distance (where direct and reflected rays have equal strength)
        critical_distance = 4 * tx_height_m * rx_height_m / self.wavelength
        
        # Beyond critical distance, use simplified formula
        mask = distance_m > critical_distance
        
        loss = np.zeros_like(distance_m)
        loss[mask] = 40 * np.log10(distance_m[mask]) - 20 * np.log10(tx_height_m) - 20 * np.log10(rx_height_m)
        
        # Apply reflection coefficient
        loss = loss * reflection_coefficient
        
        return loss
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(frequency_mhz={self.frequency_mhz})"


