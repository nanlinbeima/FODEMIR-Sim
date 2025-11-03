"""
Tree Attributes Database

Manages tree species parameters and allometric equations.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class TreeAttributesDB:
    """
    Database of tree species with allometric relationships.
    
    Provides methods to sample tree attributes (DBH, height, crown diameter)
    based on species-specific distributions and allometric equations.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize tree attributes database.
        
        Args:
            db_path: Path to tree species JSON database
        """
        if db_path is None:
            # Default database path
            db_path = Path(__file__).parent.parent.parent / 'data' / 'tree_species_db.json'
        
        self.db_path = Path(db_path)
        self.species_data = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load tree species database from JSON."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['species']
        except Exception as e:
            raise RuntimeError(f"Failed to load tree species database: {e}")
    
    def get_species_list(self) -> List[str]:
        """Get list of available species."""
        return list(self.species_data.keys())
    
    def get_species_color(self, species: str) -> str:
        """
        Get color for species visualization.
        
        Args:
            species: Species name
        
        Returns:
            Hex color code
        """
        return self.species_data.get(species, {}).get('color', '#000000')
    
    def sample_dbh(self, species: str, n_samples: int = 1, 
                   dbh_range: Optional[Tuple[float, float]] = None) -> np.ndarray:
        """
        Sample diameter at breast height (DBH) for a species.
        
        Args:
            species: Species name
            n_samples: Number of samples
            dbh_range: Optional (min, max) DBH range in cm
        
        Returns:
            Array of DBH values in cm
        """
        species_data = self.species_data.get(species, {})
        mean = species_data.get('dbh_mean_cm', 30)
        std = species_data.get('dbh_std_cm', 10)
        
        # Sample from truncated normal distribution
        dbh_samples = np.random.normal(mean, std, n_samples)
        
        # Apply range constraints
        if dbh_range is not None:
            dbh_samples = np.clip(dbh_samples, dbh_range[0], dbh_range[1])
        else:
            # Minimum realistic DBH
            dbh_samples = np.maximum(dbh_samples, 10.0)
        
        return dbh_samples
    
    def calculate_height(self, species: str, dbh: np.ndarray) -> np.ndarray:
        """
        Calculate tree height from DBH using allometric equation.
        
        Height = a * DBH^b
        
        Args:
            species: Species name
            dbh: Diameter at breast height in cm
        
        Returns:
            Tree height in meters
        """
        species_data = self.species_data.get(species, {})
        allometry = species_data.get('height_allometry', {'a': 1.3, 'b': 0.65})
        
        a = allometry['a']
        b = allometry['b']
        
        height = a * (dbh ** b)
        return height
    
    def calculate_crown_diameter(self, species: str, dbh: np.ndarray) -> np.ndarray:
        """
        Calculate crown diameter from DBH using allometric equation.
        
        Crown diameter = a * DBH^b
        
        Args:
            species: Species name
            dbh: Diameter at breast height in cm
        
        Returns:
            Crown diameter in meters
        """
        species_data = self.species_data.get(species, {})
        allometry = species_data.get('crown_diameter_allometry', {'a': 0.15, 'b': 0.8})
        
        a = allometry['a']
        b = allometry['b']
        
        crown_diameter = a * (dbh ** b)
        return crown_diameter
    
    def generate_tree_attributes(self, species: str, n_trees: int,
                                 dbh_range: Optional[Tuple[float, float]] = None) -> Dict[str, np.ndarray]:
        """
        Generate complete tree attributes for a species.
        
        Args:
            species: Species name
            n_trees: Number of trees
            dbh_range: Optional (min, max) DBH range in cm
        
        Returns:
            Dictionary with 'dbh', 'height', 'crown_diameter' arrays
        """
        dbh = self.sample_dbh(species, n_trees, dbh_range)
        height = self.calculate_height(species, dbh)
        crown_diameter = self.calculate_crown_diameter(species, dbh)
        
        return {
            'dbh': dbh,
            'height': height,
            'crown_diameter': crown_diameter
        }
    
    def generate_forest_attributes(self, species_mix: Dict[str, float], total_trees: int,
                                   dbh_range: Optional[Tuple[float, float]] = None) -> Tuple[List[str], Dict[str, np.ndarray]]:
        """
        Generate tree attributes for mixed forest.
        
        Args:
            species_mix: Dictionary of species names to percentages (e.g., {'pine': 40, 'oak': 60})
            total_trees: Total number of trees
            dbh_range: Optional (min, max) DBH range in cm
        
        Returns:
            Tuple of (species_list, attributes_dict)
            species_list: List of species for each tree
            attributes_dict: Dictionary with 'dbh', 'height', 'crown_diameter' arrays
        """
        # Normalize percentages
        total_percent = sum(species_mix.values())
        normalized_mix = {sp: pct / total_percent for sp, pct in species_mix.items()}
        
        # Calculate number of trees per species
        species_counts = {}
        assigned_trees = 0
        
        for species, percent in normalized_mix.items():
            count = int(np.round(total_trees * percent))
            species_counts[species] = count
            assigned_trees += count
        
        # Adjust for rounding errors
        if assigned_trees < total_trees:
            # Add remaining trees to most abundant species
            most_abundant = max(species_counts.keys(), key=lambda k: species_counts[k])
            species_counts[most_abundant] += (total_trees - assigned_trees)
        elif assigned_trees > total_trees:
            # Remove excess from most abundant
            most_abundant = max(species_counts.keys(), key=lambda k: species_counts[k])
            species_counts[most_abundant] -= (assigned_trees - total_trees)
        
        # Generate attributes for each species
        all_species = []
        all_dbh = []
        all_height = []
        all_crown_diameter = []
        
        for species, count in species_counts.items():
            if count <= 0:
                continue
            
            attrs = self.generate_tree_attributes(species, count, dbh_range)
            
            all_species.extend([species] * count)
            all_dbh.append(attrs['dbh'])
            all_height.append(attrs['height'])
            all_crown_diameter.append(attrs['crown_diameter'])
        
        # Concatenate arrays
        attributes = {
            'dbh': np.concatenate(all_dbh),
            'height': np.concatenate(all_height),
            'crown_diameter': np.concatenate(all_crown_diameter)
        }
        
        return all_species, attributes
    
    def get_typical_density(self, species: str) -> float:
        """
        Get typical planting density for species.
        
        Args:
            species: Species name
        
        Returns:
            Typical density in trees per hectare
        """
        species_data = self.species_data.get(species, {})
        return species_data.get('typical_density_per_ha', 400)


