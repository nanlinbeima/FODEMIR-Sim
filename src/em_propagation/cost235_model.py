"""
COST235 Vegetation Model

European model for vegetation attenuation with density factor.
"""

import numpy as np
from typing import Union
from .propagation_base import PropagationModel


class COST235Model(PropagationModel):
    """
    COST235 vegetation attenuation model.
    
    European COST (Cooperation in Science and Technology) model.
    Accounts for vegetation type and density.
    
    Formula: L_veg = A * f^(-B) * d^C * ρ
    where A, B, C are empirical constants and ρ is vegetation density factor
    """
    
    def __init__(self, frequency_mhz: float, vegetation_density_factor: float = 1.0):
        """
        Initialize COST235 model.
        
        Args:
            frequency_mhz: Operating frequency in MHz
            vegetation_density_factor: Vegetation density factor (0.5-2.0)
                1.0 = normal forest density
                <1.0 = sparse vegetation
                >1.0 = dense vegetation
        """
        super().__init__(frequency_mhz)
        
        self.vegetation_density_factor = vegetation_density_factor
        
        # Model coefficients (standard values for mixed forest)
        self.coeff_A = 26.6
        self.coeff_B = 0.2
        self.coeff_C = 0.5
        
        # Validity range
        self.min_frequency_mhz = 200
        self.max_frequency_mhz = 95000
        
        if not (self.min_frequency_mhz <= frequency_mhz <= self.max_frequency_mhz):
            print(f"Warning: COST235 model frequency {frequency_mhz} MHz outside "
                  f"typical range [{self.min_frequency_mhz}, {self.max_frequency_mhz}] MHz")
    
    def calculate_vegetation_loss(self, vegetation_depth_m: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate vegetation loss using COST235 model.
        
        L_veg = A * f^(-B) * d^C * ρ
        
        Args:
            vegetation_depth_m: Vegetation depth in meters
        
        Returns:
            Vegetation-induced path loss in dB
        """
        vegetation_depth_m = np.asarray(vegetation_depth_m)
        
        # Apply model formula
        frequency_factor = self.frequency_mhz ** (-self.coeff_B)
        depth_factor = np.power(np.maximum(vegetation_depth_m, 0), self.coeff_C)
        
        loss = (self.coeff_A * frequency_factor * depth_factor * 
                self.vegetation_density_factor)
        
        return loss
    
    def set_vegetation_type(self, vegetation_type: str) -> None:
        """
        Set model coefficients based on vegetation type.
        
        Args:
            vegetation_type: Type of vegetation ('sparse', 'normal', 'dense', 'very_dense')
        """
        vegetation_params = {
            'sparse': {
                'density': 0.5,
                'A': 20.0,
                'B': 0.2,
                'C': 0.5
            },
            'normal': {
                'density': 1.0,
                'A': 26.6,
                'B': 0.2,
                'C': 0.5
            },
            'dense': {
                'density': 1.5,
                'A': 30.0,
                'B': 0.2,
                'C': 0.5
            },
            'very_dense': {
                'density': 2.0,
                'A': 35.0,
                'B': 0.2,
                'C': 0.5
            }
        }
        
        if vegetation_type in vegetation_params:
            params = vegetation_params[vegetation_type]
            self.vegetation_density_factor = params['density']
            self.coeff_A = params['A']
            self.coeff_B = params['B']
            self.coeff_C = params['C']
        else:
            print(f"Warning: Unknown vegetation type '{vegetation_type}'. Using default.")
    
    def calculate_multi_layer_loss(self, layer_depths: np.ndarray, 
                                   layer_densities: np.ndarray) -> float:
        """
        Calculate loss through multiple vegetation layers.
        
        Args:
            layer_depths: Array of depths for each layer in meters
            layer_densities: Array of density factors for each layer
        
        Returns:
            Total vegetation loss in dB
        """
        total_loss = 0.0
        
        for depth, density in zip(layer_depths, layer_densities):
            if depth > 0:
                # Temporarily set density
                original_density = self.vegetation_density_factor
                self.vegetation_density_factor = density
                
                # Calculate loss for this layer
                layer_loss = self.calculate_vegetation_loss(depth)
                total_loss += layer_loss
                
                # Restore original density
                self.vegetation_density_factor = original_density
        
        return total_loss
    
    def get_specific_attenuation(self) -> float:
        """
        Calculate specific attenuation per meter.
        
        Returns:
            Specific attenuation in dB/m at 1 meter depth
        """
        return self.calculate_vegetation_loss(1.0)
    
    def __repr__(self) -> str:
        return (f"COST235Model(frequency_mhz={self.frequency_mhz}, "
                f"density_factor={self.vegetation_density_factor})")


