"""
ITU-R P.833 Vegetation Model

International Telecommunication Union model for vegetation attenuation.
"""

import numpy as np
from typing import Union
from .propagation_base import PropagationModel


class ITURP833Model(PropagationModel):
    """
    ITU-R P.833 vegetation attenuation model.
    
    Recommendation ITU-R P.833 for attenuation in vegetation.
    Uses exponential model with maximum specific attenuation.
    
    Formula: A = A_m * [1 - exp(-d/d_s)]
    where:
        A = total attenuation (dB)
        A_m = maximum attenuation (dB)
        d = path length through vegetation (m)
        d_s = characteristic distance (m)
    """
    
    def __init__(self, frequency_mhz: float, 
                 max_specific_attenuation_db_per_m: float = 0.3,
                 characteristic_distance_m: float = 20.0):
        """
        Initialize ITU-R P.833 model.
        
        Args:
            frequency_mhz: Operating frequency in MHz
            max_specific_attenuation_db_per_m: Maximum specific attenuation γ_m (dB/m)
            characteristic_distance_m: Characteristic distance d_s (m)
        """
        super().__init__(frequency_mhz)
        
        self.max_specific_attenuation = max_specific_attenuation_db_per_m
        self.characteristic_distance = characteristic_distance_m
        
        # Calculate maximum attenuation based on model
        self._calculate_parameters()
    
    def _calculate_parameters(self) -> None:
        """
        Calculate model parameters based on frequency.
        
        ITU-R P.833 provides frequency-dependent specific attenuation values.
        This is a simplified implementation.
        """
        # Frequency-dependent specific attenuation (simplified)
        # Actual values should be from ITU-R P.833 tables
        
        if self.frequency_mhz < 400:
            # VHF range
            self.max_specific_attenuation = 0.1
            self.characteristic_distance = 30.0
        elif self.frequency_mhz < 2000:
            # UHF range (including LoRa ISM bands 868/915 MHz)
            self.max_specific_attenuation = 0.3
            self.characteristic_distance = 20.0
        elif self.frequency_mhz < 10000:
            # Low microwave
            self.max_specific_attenuation = 0.6
            self.characteristic_distance = 15.0
        else:
            # Higher frequencies
            self.max_specific_attenuation = 1.0
            self.characteristic_distance = 10.0
    
    def calculate_vegetation_loss(self, vegetation_depth_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate vegetation loss using ITU-R P.833 exponential model.
        
        A = A_m * [1 - exp(-d/d_s)]
        where A_m = γ_m * d_s
        
        Args:
            vegetation_depth_m: Vegetation depth in meters
        
        Returns:
            Vegetation-induced path loss in dB
        """
        vegetation_depth_m = np.asarray(vegetation_depth_m)
        
        # Maximum attenuation
        A_m = self.max_specific_attenuation * self.characteristic_distance
        
        # Exponential model
        loss = A_m * (1 - np.exp(-vegetation_depth_m / self.characteristic_distance))
        
        return loss
    
    def calculate_linear_loss(self, vegetation_depth_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate vegetation loss using simplified linear model.
        
        For short paths where d << d_s, the exponential can be approximated linearly:
        A ≈ γ_m * d
        
        Args:
            vegetation_depth_m: Vegetation depth in meters
        
        Returns:
            Vegetation-induced path loss in dB
        """
        vegetation_depth_m = np.asarray(vegetation_depth_m)
        
        # Linear approximation
        loss = self.max_specific_attenuation * vegetation_depth_m
        
        return loss
    
    def set_vegetation_category(self, category: str) -> None:
        """
        Set attenuation parameters based on ITU-R vegetation categories.
        
        Args:
            category: Vegetation category
                'in_leaf' - Trees/vegetation in leaf (summer)
                'out_of_leaf' - Trees/vegetation out of leaf (winter)
                'short_veg' - Short vegetation (grass, crops)
                'tropical' - Tropical vegetation
        """
        categories = {
            'in_leaf': {
                'max_atten': 0.35,
                'char_dist': 20.0
            },
            'out_of_leaf': {
                'max_atten': 0.15,
                'char_dist': 25.0
            },
            'short_veg': {
                'max_atten': 0.1,
                'char_dist': 10.0
            },
            'tropical': {
                'max_atten': 0.5,
                'char_dist': 15.0
            }
        }
        
        if category in categories:
            params = categories[category]
            self.max_specific_attenuation = params['max_atten']
            self.characteristic_distance = params['char_dist']
        else:
            print(f"Warning: Unknown vegetation category '{category}'. Using default.")
    
    def get_effective_depth(self, loss_db: float) -> float:
        """
        Calculate effective vegetation depth for given loss.
        
        Inverse calculation: d = -d_s * ln(1 - A/A_m)
        
        Args:
            loss_db: Desired attenuation in dB
        
        Returns:
            Effective vegetation depth in meters
        """
        A_m = self.max_specific_attenuation * self.characteristic_distance
        
        if loss_db >= A_m:
            # Loss exceeds maximum - return very large depth
            return float('inf')
        
        depth = -self.characteristic_distance * np.log(1 - loss_db / A_m)
        return depth
    
    def compare_models(self, vegetation_depth_m: Union[float, np.ndarray]) -> dict:
        """
        Compare exponential and linear approximations.
        
        Args:
            vegetation_depth_m: Vegetation depth in meters
        
        Returns:
            Dictionary with results from both models
        """
        exponential_loss = self.calculate_vegetation_loss(vegetation_depth_m)
        linear_loss = self.calculate_linear_loss(vegetation_depth_m)
        
        return {
            'exponential_db': exponential_loss,
            'linear_db': linear_loss,
            'difference_db': exponential_loss - linear_loss,
            'relative_error_percent': 100 * (linear_loss - exponential_loss) / np.maximum(exponential_loss, 1e-10)
        }
    
    def __repr__(self) -> str:
        return (f"ITURP833Model(frequency_mhz={self.frequency_mhz}, "
                f"γ_m={self.max_specific_attenuation} dB/m, "
                f"d_s={self.characteristic_distance} m)")


