"""
Weissberger Vegetation Model

Modified Exponential Decay (MED) model for vegetation attenuation.
"""

import numpy as np
from typing import Union
from .propagation_base import PropagationModel


class WeissbergerModel(PropagationModel):
    """
    Weissberger's Modified Exponential Decay (MED) model.
    
    Widely used empirical model for vegetation attenuation.
    Valid for frequencies 230 MHz - 95 GHz and vegetation depth 14m - 400m.
    
    Formula: L_veg = 1.33 * f^0.284 * d^0.588  (dB)
    where f is frequency in MHz and d is vegetation depth in meters
    """
    
    def __init__(self, frequency_mhz: float):
        """
        Initialize Weissberger model.
        
        Args:
            frequency_mhz: Operating frequency in MHz (valid: 230-95000)
        """
        super().__init__(frequency_mhz)
        
        # Model validity ranges
        self.min_frequency_mhz = 230
        self.max_frequency_mhz = 95000
        self.min_depth_m = 14
        self.max_depth_m = 400
        
        # Warn if outside validity range
        if not (self.min_frequency_mhz <= frequency_mhz <= self.max_frequency_mhz):
            print(f"Warning: Weissberger model frequency {frequency_mhz} MHz outside "
                  f"validity range [{self.min_frequency_mhz}, {self.max_frequency_mhz}] MHz")
    
    def calculate_vegetation_loss(self, vegetation_depth_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate vegetation loss using Weissberger model.
        
        L_veg = 1.33 * f^0.284 * d^0.588  for d >= 14m
        L_veg = 0.45 * f^0.284 * d       for 0 < d < 14m (ITU-R extrapolation)
        
        Args:
            vegetation_depth_m: Vegetation depth in meters
        
        Returns:
            Vegetation-induced path loss in dB
        """
        vegetation_depth_m = np.asarray(vegetation_depth_m)
        
        # Initialize loss array
        loss = np.zeros_like(vegetation_depth_m, dtype=float)
        
        # For depth >= 14m, use standard Weissberger formula
        mask_standard = vegetation_depth_m >= self.min_depth_m
        loss[mask_standard] = (1.33 * (self.frequency_mhz ** 0.284) * 
                              (vegetation_depth_m[mask_standard] ** 0.588))
        
        # For depth < 14m, use linear approximation (ITU-R recommendation)
        mask_low = (vegetation_depth_m > 0) & (vegetation_depth_m < self.min_depth_m)
        loss[mask_low] = (0.45 * (self.frequency_mhz ** 0.284) * 
                         vegetation_depth_m[mask_low])
        
        return loss
    
    def get_specific_attenuation(self, vegetation_depth_m: float = 100) -> float:
        """
        Calculate specific attenuation (dB per meter).
        
        Args:
            vegetation_depth_m: Reference vegetation depth for calculation
        
        Returns:
            Specific attenuation in dB/m
        """
        if vegetation_depth_m <= 0:
            return 0.0
        
        total_loss = self.calculate_vegetation_loss(vegetation_depth_m)
        return total_loss / vegetation_depth_m
    
    def calculate_max_range(self, max_acceptable_loss_db: float, 
                           base_distance_m: float = 100) -> float:
        """
        Estimate maximum communication range for given acceptable loss.
        
        Args:
            max_acceptable_loss_db: Maximum acceptable total path loss in dB
            base_distance_m: Reference vegetation depth
        
        Returns:
            Estimated maximum range in meters
        """
        # Simplified estimation - actual range depends on many factors
        spec_atten = self.get_specific_attenuation(base_distance_m)
        
        if spec_atten <= 0:
            return float('inf')
        
        max_veg_depth = max_acceptable_loss_db / spec_atten
        return max_veg_depth


