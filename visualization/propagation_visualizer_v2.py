"""
Enhanced Propagation Visualizer V2

Professional multi-panel EM propagation visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from typing import Optional, Dict, List
from pathlib import Path


class PropagationVisualizerV2:
    """Enhanced EM propagation visualization with dual-panel layout."""
    
    def __init__(self):
        self.fig = None
        self.axes = None
    
    def plot_em_analysis(self, coverage_map: np.ndarray, extent: tuple,
                        gateway_positions: np.ndarray,
                        tree_positions: np.ndarray = None,
                        crown_radii: np.ndarray = None,
                        sensor_positions: np.ndarray = None,
                        link_calculator = None,
                        metric: str = 'snr',
                        ax=None) -> plt.Figure:
        """
        Create comprehensive EM propagation analysis visualization.
        
        Args:
            coverage_map: 2D array of coverage values
            extent: (xmin, xmax, ymin, ymax)
            gateway_positions: Gateway coordinates
            tree_positions: Forest tree positions
            crown_radii: Tree crown radii
            sensor_positions: Deployed sensor positions
            link_calculator: Link calculator object
            metric: 'snr', 'rssi', or 'path_loss'
            ax: Parent axes (if embedding in larger figure)
        
        Returns:
            Figure object
        """
        # Create figure with dual-panel layout
        if ax is None:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(28, 12))
            self.fig = fig
            self.axes = (ax1, ax2)
        else:
            # If ax is provided, create subplots within it
            fig = ax.get_figure()
            gs = ax.get_subplotspec().subgridspec(1, 2, wspace=0.25)
            ax.remove()
            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            self.fig = fig
            self.axes = (ax1, ax2)
        
        # Left panel: Propagation paths
        self._plot_propagation_paths(ax1, extent, gateway_positions, 
                                     tree_positions, crown_radii,
                                     sensor_positions)
        
        # Right panel: Coverage heatmap
        self._plot_coverage_heatmap(ax2, coverage_map, extent,
                                    gateway_positions, sensor_positions,
                                    metric)
        
        # No overall title - removed to avoid overlap
        if ax is None:
            plt.tight_layout()
        
        return fig
    
    def _plot_propagation_paths(self, ax, extent, gateway_positions,
                                tree_positions, crown_radii, sensor_positions):
        """Plot left panel: propagation paths through forest."""
        # Background
        ax.set_facecolor('#2d4a2b')
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        
        # Draw trees (simplified for clarity)
        if tree_positions is not None and crown_radii is not None:
            for i in range(min(len(tree_positions), 200)):  # Limit for performance
                x, y = tree_positions[i]
                r = crown_radii[i]
                crown = Circle((x, y), r, color='#3a5a3a', alpha=0.6, zorder=1)
                ax.add_patch(crown)
        
        # Draw sample propagation paths
        if gateway_positions is not None and len(gateway_positions) > 0:
            gateway_pos = gateway_positions[0]
            
            # Create test points grid
            width = extent[1] - extent[0]
            height = extent[3] - extent[2]
            test_points = [
                [width*0.2, height*0.2], [width*0.8, height*0.2],
                [width*0.2, height*0.8], [width*0.8, height*0.8],
                [width*0.5, height*0.2], [width*0.2, height*0.5],
                [width*0.8, height*0.5], [width*0.5, height*0.8]
            ]
            
            # Draw paths
            for point in test_points:
                ax.plot([gateway_pos[0], point[0]], 
                       [gateway_pos[1], point[1]],
                       'y--', linewidth=2.5, alpha=0.7, zorder=5)
                
                # Draw test point
                test_circle = Circle(point, 6, color='yellow', 
                                    edgecolor='black', linewidth=1.5, zorder=10)
                ax.add_patch(test_circle)
            
            # Draw gateway
            gateway_rect = Rectangle((gateway_pos[0] - 10, gateway_pos[1] - 10),
                                     20, 20, color='red', zorder=11,
                                     edgecolor='white', linewidth=2)
            ax.add_patch(gateway_rect)
            ax.text(gateway_pos[0], gateway_pos[1] - 30, 'Gateway',
                   fontsize=22, ha='center', color='white', 
                   fontweight='bold', zorder=12)
        
        # Draw deployed sensors if available
        if sensor_positions is not None and len(sensor_positions) > 0:
            for sx, sy in sensor_positions:
                sensor = Circle((sx, sy), 5, color='blue', zorder=10,
                              edgecolor='white', linewidth=2)
                ax.add_patch(sensor)
        
        ax.set_xlabel('X Coordinate (m)', fontsize=16, fontweight='bold', family='Times New Roman')
        ax.set_ylabel('Y Coordinate (m)', fontsize=16, fontweight='bold', family='Times New Roman')
        ax.set_title('EM Propagation Paths', fontsize=18, fontweight='bold', family='Times New Roman')
        ax.tick_params(labelsize=14)  # Increase tick label size
        ax.grid(True, alpha=0.3, color='white', linestyle='--', linewidth=1)
        
        # Legend
        legend_elements = [
            plt.Line2D([0], [0], color='y', linewidth=2.5, linestyle='--',
                      label='Sample Path'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow',
                      markersize=12, label='Test Point'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red',
                      markersize=15, label='Gateway')
        ]
        legend = ax.legend(handles=legend_elements, fontsize=14, loc='upper left',
                          framealpha=0.9, prop={'family': 'Times New Roman'})
    
    def _plot_coverage_heatmap(self, ax, coverage_map, extent,
                               gateway_positions, sensor_positions, metric):
        """Plot right panel: coverage heatmap."""
        # Select colormap and label based on metric
        if metric == 'snr':
            cmap = 'RdYlGn'
            cbar_label = 'SNR (dB)'
            vmin, vmax = -10, 30
        elif metric == 'rssi':
            cmap = 'RdYlGn'
            cbar_label = 'RSSI (dBm)'
            vmin, vmax = -120, -60
        else:  # path_loss
            cmap = 'RdYlGn_r'
            cbar_label = 'Path Loss (dB)'
            vmin, vmax = 80, 140
        
        # Plot heatmap
        im = ax.imshow(coverage_map, extent=extent, origin='lower',
                      cmap=cmap, vmin=vmin, vmax=vmax, alpha=0.9, aspect='auto')
        
        # Draw gateway
        if gateway_positions is not None and len(gateway_positions) > 0:
            for gw_pos in gateway_positions:
                gateway_marker = Rectangle((gw_pos[0] - 10, gw_pos[1] - 10),
                                          20, 20, color='red', zorder=10,
                                          edgecolor='white', linewidth=2.5)
                ax.add_patch(gateway_marker)
        
        # Draw sensors
        if sensor_positions is not None and len(sensor_positions) > 0:
            ax.scatter(sensor_positions[:, 0], sensor_positions[:, 1],
                      c='blue', s=150, marker='o', edgecolors='white',
                      linewidths=2, label='Sensor', zorder=9)
        
        ax.set_xlabel('X Coordinate (m)', fontsize=16, fontweight='bold', family='Times New Roman')
        ax.set_ylabel('Y Coordinate (m)', fontsize=16, fontweight='bold', family='Times New Roman')
        ax.set_title(f'{cbar_label} Heatmap', fontsize=18, fontweight='bold', family='Times New Roman')
        ax.tick_params(labelsize=14)  # Increase tick label size
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax, pad=0.02)
        cbar.set_label(cbar_label, fontsize=16, fontweight='bold',
                      rotation=270, labelpad=25, family='Times New Roman')
        cbar.ax.tick_params(labelsize=14)
        # Set colorbar tick labels to Times New Roman
        for label in cbar.ax.get_yticklabels():
            label.set_fontfamily('Times New Roman')
        
        ax.grid(True, alpha=0.2, color='white', linestyle='--', linewidth=1)
        
        # Add statistics box
        if metric == 'snr':
            mean_val = np.mean(coverage_map[~np.isnan(coverage_map)])
            min_val = np.min(coverage_map[~np.isnan(coverage_map)])
            max_val = np.max(coverage_map[~np.isnan(coverage_map)])
            
            stats_text = f'Statistics:\n'
            stats_text += f'Mean SNR: {mean_val:.1f} dB\n'
            stats_text += f'Min SNR: {min_val:.1f} dB\n'
            stats_text += f'Max SNR: {max_val:.1f} dB\n'
            stats_text += f'Coverage: {np.sum(coverage_map > 6) / coverage_map.size * 100:.1f}%'
            
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.9,
                        edgecolor='black', linewidth=2)
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   fontsize=14, verticalalignment='top', bbox=props,
                   fontweight='bold', family='Times New Roman')

