"""
Forest Visualizer

Step 1 visualization: Forest map with tree positions and crown circles.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from typing import Dict, List, Optional
from pathlib import Path
from PIL import Image
from .plot_config import FOREST_COLORS, CHINESE_LABELS


class ForestVisualizer:
    """
    Visualizes forest maps with tree positions, species, and crown circles.
    
    Creates Figure 1: 2D forest map with tree positions, crown circles, 
    species color-coded with Times New Roman 25pt and Chinese labels.
    """
    
    def __init__(self):
        """Initialize forest visualizer."""
        self.fig = None
        self.ax = None
    
    def plot_forest_map(self, tree_positions: np.ndarray, crown_radii: np.ndarray,
                       species_list: List[str], tree_attributes: Optional[Dict] = None,
                       show_crowns: bool = True, show_trunks: bool = True,
                       ax: Optional[plt.Axes] = None, clearings: List = None,
                       domain: tuple = None, background_image: str = None) -> plt.Axes:
        """
        Plot forest map with trees, crowns, and clearings.
        
        Args:
            tree_positions: Array of tree trunk positions (N, 2)
            crown_radii: Array of crown radii (N,)
            species_list: List of species for each tree
            tree_attributes: Optional dictionary with additional attributes
            show_crowns: Whether to show crown circles
            show_trunks: Whether to show trunk markers
            ax: Optional axes to plot on
            clearings: List of clearings (dicts with 'center' and 'radius')
            domain: Tuple of (width, height) for plot limits
        
        Returns:
            Matplotlib axes with forest plot
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(12, 10))
            self.ax = ax
        
        # Check if we should use real background image
        use_real_background = False
        if background_image and Path(background_image).exists():
            try:
                img = Image.open(background_image)
                # Set extent based on domain
                if domain:
                    extent = [0, domain[0], 0, domain[1]]
                else:
                    extent = [0, 316, 0, 316]  # Default domain
                ax.imshow(img, extent=extent, aspect='auto', zorder=0, alpha=1.0)
                use_real_background = True
                print("✓ Using real aerial forest image as background")
            except Exception as e:
                print(f"Could not load background image: {e}")
                ax.set_facecolor('#90C878')  # Fallback to grass color
        else:
            # Set background to grass-like color
            ax.set_facecolor('#90C878')  # Light green grass
        
        labels = CHINESE_LABELS['forest_map']
        
        # Get unique species
        unique_species = sorted(set(species_list))
        
        # If using real background image, skip drawing trees and clearings
        if use_real_background:
            # Just set up the plot with labels (NO TITLE)
            ax.set_xlabel('X (m)', fontsize=16, fontweight='bold')
            ax.set_ylabel('Y (m)', fontsize=16, fontweight='bold')
            # Removed title to avoid clutter in upper left
            ax.tick_params(labelsize=14)  # Increase tick label size
            ax.set_aspect('equal', adjustable='box')
            if domain:
                ax.set_xlim(-10, domain[0] + 10)
                ax.set_ylim(-10, domain[1] + 10)
            ax.grid(True, alpha=0.2, linestyle='--', color='white', linewidth=0.5)
            return ax
        
        # Otherwise, plot synthetic forest with crowns and clearings
        # Plot crowns as circles
        if show_crowns:
            for species in unique_species:
                # Get trees of this species
                species_mask = np.array([s == species for s in species_list])
                species_positions = tree_positions[species_mask]
                species_radii = crown_radii[species_mask]
                
                if len(species_positions) == 0:
                    continue
                
                # Create circle patches
                circles = [Circle((pos[0], pos[1]), radius=r, alpha=0.4) 
                          for pos, r in zip(species_positions, species_radii)]
                
                collection = PatchCollection(circles, 
                                            facecolors=FOREST_COLORS.get(species, '#666666'),
                                            edgecolors='none',
                                            alpha=0.4,
                                            label=species)
                ax.add_collection(collection)
        
        # Plot clearings (light brown open areas)
        if clearings:
            for idx, clearing in enumerate(clearings):
                clearing_circle = Circle(clearing['center'], clearing['radius'],
                                       facecolor='#D4A574', edgecolor='#8B6F47',
                                       alpha=0.6, linewidth=2, linestyle='--',
                                       label='Clearing' if idx == 0 else None,
                                       zorder=1)
                ax.add_patch(clearing_circle)
        
        # Plot trunk positions
        if show_trunks:
            for species in unique_species:
                species_mask = np.array([s == species for s in species_list])
                species_positions = tree_positions[species_mask]
                
                if len(species_positions) == 0:
                    continue
                
                ax.scatter(species_positions[:, 0], species_positions[:, 1],
                          c='#3d2817', s=30, marker='o', edgecolors='black', linewidths=0.5,
                          zorder=6)  # Brown trunks
        
        # Set labels - all English (NO TITLE)
        ax.set_xlabel('X (m)', fontsize=16, fontweight='bold')
        ax.set_ylabel('Y (m)', fontsize=16, fontweight='bold')
        # Removed title to avoid clutter in upper left
        ax.tick_params(labelsize=14)  # Increase tick label size
        
        # Legend - use English with better positioning
        handles, labels_list = ax.get_legend_handles_labels()
        ax.legend(handles, labels_list, title='Tree Species', loc='upper right', 
                 framealpha=0.95, fontsize=12, title_fontsize=13, 
                 edgecolor='black', fancybox=True)
        
        # Equal aspect ratio for proper circle display
        ax.set_aspect('equal', adjustable='box')
        
        # Set limits based on domain if provided
        if domain:
            ax.set_xlim(-10, domain[0] + 10)
            ax.set_ylim(-10, domain[1] + 10)
        
        # Grid
        ax.grid(True, alpha=0.2, linestyle='--', color='white', linewidth=0.5)
        
        return ax
    
    def plot_forest_density_heatmap(self, density_map: np.ndarray, extent: tuple,
                                    ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot forest density heatmap.
        
        Args:
            density_map: 2D array of tree density
            extent: Map extent (xmin, xmax, ymin, ymax)
            ax: Optional axes
        
        Returns:
            Matplotlib axes
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(12, 10))
            self.ax = ax
        
        labels = CHINESE_LABELS['forest_map']
        
        # Plot heatmap
        im = ax.imshow(density_map, extent=extent, origin='lower',
                      cmap='YlGn', alpha=0.7, aspect='auto')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('树木密度', fontsize=22, rotation=270, labelpad=30)
        
        ax.set_xlabel(labels['xlabel'], fontsize=25, fontweight='bold')
        ax.set_ylabel(labels['ylabel'], fontsize=25, fontweight='bold')
        ax.set_title('森林密度分布图', fontsize=28, fontweight='bold', pad=20)
        
        return ax
    
    def add_scale_bar(self, ax: plt.Axes, length: float = 100.0, 
                     location: str = 'lower right') -> None:
        """
        Add scale bar to forest map.
        
        Args:
            ax: Axes to add scale bar to
            length: Length of scale bar in meters
            location: Position of scale bar
        """
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Position scale bar
        if location == 'lower right':
            x0 = xlim[1] - length - 20
            y0 = ylim[0] + 20
        elif location == 'lower left':
            x0 = xlim[0] + 20
            y0 = ylim[0] + 20
        else:
            x0 = (xlim[0] + xlim[1]) / 2 - length / 2
            y0 = ylim[0] + 20
        
        # Draw scale bar
        ax.plot([x0, x0 + length], [y0, y0], 'k-', linewidth=3, solid_capstyle='butt')
        
        # Add text
        ax.text(x0 + length / 2, y0 + 10, f'{int(length)} m',
               ha='center', va='bottom', fontsize=18, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    def plot_species_distribution(self, species_counts: Dict[str, int],
                                  ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot species composition as bar chart.
        
        Args:
            species_counts: Dictionary of species to count
            ax: Optional axes
        
        Returns:
            Matplotlib axes
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(10, 8))
            self.ax = ax
        
        species = list(species_counts.keys())
        counts = list(species_counts.values())
        colors = [FOREST_COLORS.get(sp, '#666666') for sp in species]
        
        bars = ax.bar(species, counts, color=colors, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('树种', fontsize=25, fontweight='bold')
        ax.set_ylabel('树木数量', fontsize=25, fontweight='bold')
        ax.set_title('树种分布统计', fontsize=28, fontweight='bold', pad=20)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=18, fontweight='bold')
        
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        return ax
    
    def save_figure(self, filepath: str, dpi: int = 300):
        """
        Save forest visualization figure.
        
        Args:
            filepath: Output file path
            dpi: Resolution in DPI
        """
        if self.fig is not None:
            self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                           facecolor='white', edgecolor='none')

