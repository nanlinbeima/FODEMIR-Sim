"""
Enhanced UAV Visualizer V2

Professional dual-panel UAV deployment visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Polygon
from typing import Optional, Dict, List, Tuple


class UAVVisualizerV2:
    """Enhanced UAV deployment visualization with dual-panel layout."""
    
    def __init__(self):
        self.fig = None
        self.axes = None
    
    def plot_uav_deployment(self, sensor_positions: np.ndarray,
                           gateway_position: np.ndarray,
                           trajectory: np.ndarray,
                           tree_positions: np.ndarray = None,
                           crown_radii: np.ndarray = None,
                           energy_data: Dict = None,
                           ax=None) -> plt.Figure:
        """
        Create comprehensive UAV deployment visualization.
        
        Args:
            sensor_positions: Deployed sensor coordinates
            gateway_position: Gateway/depot position
            trajectory: UAV flight path
            tree_positions: Forest tree positions
            crown_radii: Tree crown radii
            energy_data: Energy consumption data
            ax: Parent axes (optional)
        
        Returns:
            Figure object
        """
        # Create figure with dual-panel layout
        if ax is None:
            fig = plt.figure(figsize=(28, 13))
            self.fig = fig
        else:
            fig = ax.get_figure()
            self.fig = fig
        
        gs = fig.add_gridspec(1, 2, wspace=0.25,
                             left=0.05, right=0.95, top=0.92, bottom=0.08)
        
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        
        self.axes = (ax1, ax2)
        
        # Left panel: Deployment network
        self._plot_deployment_network(ax1, sensor_positions, gateway_position,
                                     tree_positions, crown_radii)
        
        # Right panel: UAV flight path
        self._plot_uav_flight_path(ax2, sensor_positions, gateway_position,
                                   trajectory, tree_positions, crown_radii,
                                   energy_data)
        
        # Overall title
        fig.suptitle('Step 4: Deployment Results & UAV Path Planning\n' +
                    '(TSP-Based Sequential Deployment)',
                    fontsize=32, fontweight='bold', y=0.98)
        
        return fig
    
    def _plot_deployment_network(self, ax, sensor_positions, gateway_position,
                                 tree_positions, crown_radii):
        """Left panel: Deployment network with coverage."""
        # Background
        ax.set_facecolor('#2d4a2b')
        
        # Determine extent
        if tree_positions is not None and len(tree_positions) > 0:
            extent = [0, np.max(tree_positions[:, 0]) + 20,
                     0, np.max(tree_positions[:, 1]) + 20]
        else:
            extent = [0, 500, 0, 500]
        
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        
        # Draw trees (sample for performance)
        if tree_positions is not None and crown_radii is not None:
            sample_indices = np.random.choice(len(tree_positions),
                                            size=min(150, len(tree_positions)),
                                            replace=False)
            for idx in sample_indices:
                x, y = tree_positions[idx]
                r = crown_radii[idx]
                crown = Circle((x, y), r, color='#3a5a3a', alpha=0.5, zorder=1)
                ax.add_patch(crown)
        
        # Draw coverage circles
        coverage_radius = 50
        for sx, sy in sensor_positions:
            coverage_circle = Circle((sx, sy), coverage_radius,
                                    color='cyan', alpha=0.12, zorder=2,
                                    edgecolor='cyan', linewidth=1.5, linestyle='--')
            ax.add_patch(coverage_circle)
        
        # Draw communication links between sensors
        for i, (sx1, sy1) in enumerate(sensor_positions):
            for sx2, sy2 in sensor_positions[i+1:]:
                dist = np.sqrt((sx1 - sx2)**2 + (sy1 - sy2)**2)
                if dist < 100:  # Communication range
                    ax.plot([sx1, sx2], [sy1, sy2], 'b-',
                           alpha=0.4, linewidth=2, zorder=3)
        
        # Connect to gateway
        for sx, sy in sensor_positions:
            dist = np.sqrt((sx - gateway_position[0])**2 +
                          (sy - gateway_position[1])**2)
            if dist < 150:  # Gateway communication range
                ax.plot([gateway_position[0], sx], [gateway_position[1], sy],
                       'r-', alpha=0.5, linewidth=2.5, zorder=4)
        
        # Draw sensors
        for sx, sy in sensor_positions:
            sensor = Circle((sx, sy), 6, color='blue', zorder=10,
                          edgecolor='white', linewidth=2.5)
            ax.add_patch(sensor)
        
        # Draw gateway
        gateway_rect = Rectangle((gateway_position[0] - 12, gateway_position[1] - 12),
                                24, 24, color='red', zorder=11,
                                edgecolor='white', linewidth=2.5)
        ax.add_patch(gateway_rect)
        
        ax.set_xlabel('X Coordinate (m)', fontsize=25, fontweight='bold')
        ax.set_ylabel('Y Coordinate (m)', fontsize=25, fontweight='bold')
        ax.set_title('Optimized Sensor Network', fontsize=26, fontweight='bold')
        ax.grid(True, alpha=0.3, color='white', linestyle='--', linewidth=1)
        ax.tick_params(labelsize=20)
        
        # Legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue',
                      markersize=16, label='Sensor Node',
                      markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red',
                      markersize=16, label='Gateway',
                      markeredgecolor='white', markeredgewidth=2.5),
            plt.Line2D([0], [0], color='cyan', linewidth=3,
                      linestyle='--', label='Coverage Range'),
            plt.Line2D([0], [0], color='blue', linewidth=2.5,
                      label='Sensor-Sensor Link'),
            plt.Line2D([0], [0], color='red', linewidth=2.5,
                      label='Sensor-Gateway Link')
        ]
        ax.legend(handles=legend_elements, fontsize=19, loc='upper left',
                 framealpha=0.95, edgecolor='white', fancybox=True)
    
    def _plot_uav_flight_path(self, ax, sensor_positions, gateway_position,
                              trajectory, tree_positions, crown_radii,
                              energy_data):
        """Right panel: UAV deployment sequence."""
        # Background
        ax.set_facecolor('#e6f2ff')
        
        # Determine extent
        if tree_positions is not None and len(tree_positions) > 0:
            extent = [0, np.max(tree_positions[:, 0]) + 20,
                     0, np.max(tree_positions[:, 1]) + 20]
        else:
            extent = [0, 500, 0, 500]
        
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        
        # Draw simplified forest (every 5th tree)
        if tree_positions is not None and crown_radii is not None:
            sample_indices = range(0, len(tree_positions), 5)
            for idx in sample_indices:
                x, y = tree_positions[idx]
                r = crown_radii[idx]
                crown = Circle((x, y), r, color='#3a5a3a', alpha=0.3, zorder=1)
                ax.add_patch(crown)
        
        # UAV flight path
        if trajectory is not None and len(trajectory) > 0:
            # Main path
            ax.plot(trajectory[:, 0], trajectory[:, 1], 'b-',
                   linewidth=3.5, alpha=0.7, zorder=5)
            ax.plot(trajectory[:, 0], trajectory[:, 1], 'bo',
                   markersize=13, zorder=6)
            
            # Draw direction arrows
            for i in range(len(trajectory) - 1):
                dx = trajectory[i+1, 0] - trajectory[i, 0]
                dy = trajectory[i+1, 1] - trajectory[i, 1]
                ax.arrow(trajectory[i, 0], trajectory[i, 1],
                        dx * 0.7, dy * 0.7,
                        head_width=10, head_length=12,
                        fc='orange', ec='orange', alpha=0.8,
                        zorder=7, linewidth=2.5)
            
            # Mark deployment points
            for i in range(len(trajectory)):
                x, y = trajectory[i, 0], trajectory[i, 1]
                if i == 0:
                    # Start point (gateway/depot)
                    start_marker = Rectangle((x - 12, y - 12), 24, 24,
                                            color='green', zorder=10,
                                            edgecolor='black', linewidth=2.5)
                    ax.add_patch(start_marker)
                    ax.text(x, y - 30, 'START', fontsize=22, ha='center',
                           fontweight='bold', color='green',
                           bbox=dict(boxstyle='round,pad=0.5',
                                   facecolor='white', alpha=0.9))
                else:
                    # Deployment point
                    deploy_circle = Circle((x, y), 8, color='red', zorder=10,
                                          edgecolor='black', linewidth=2.5)
                    ax.add_patch(deploy_circle)
                    
                    # Number label
                    label_box = FancyBboxPatch((x + 10, y + 10), 25, 25,
                                              boxstyle="circle,pad=0.1",
                                              transform=ax.transData,
                                              facecolor='white', edgecolor='black',
                                              linewidth=2, zorder=11)
                    ax.add_patch(label_box)
                    ax.text(x + 22.5, y + 22.5, f'{i}', fontsize=20,
                           ha='center', va='center', fontweight='bold',
                           zorder=12)
        
        ax.set_xlabel('X Coordinate (m)', fontsize=25, fontweight='bold')
        ax.set_ylabel('Y Coordinate (m)', fontsize=25, fontweight='bold')
        ax.set_title('UAV Deployment Sequence', fontsize=26, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
        ax.tick_params(labelsize=20)
        
        # Calculate and display flight statistics
        if trajectory is not None and len(trajectory) > 1:
            total_distance = 0
            for i in range(len(trajectory) - 1):
                total_distance += np.sqrt((trajectory[i+1, 0] - trajectory[i, 0])**2 +
                                        (trajectory[i+1, 1] - trajectory[i, 1])**2)
            
            flight_time = total_distance / 5.0  # Assume 5 m/s cruise speed
            deploy_time = (len(sensor_positions)) * 15  # 15s per deployment
            total_time = flight_time + deploy_time
            
            stats_text = f'Deployment Statistics:\n'
            stats_text += f'Total Sensors: {len(sensor_positions)}\n'
            stats_text += f'Flight Distance: {total_distance:.1f} m\n'
            stats_text += f'Flight Time: {flight_time:.1f} s\n'
            stats_text += f'Deploy Time: {deploy_time:.1f} s\n'
            stats_text += f'Total Time: {total_time:.1f} s\n'
            stats_text += f'Sequence: TSP-Optimized'
            
            props = dict(boxstyle='round,pad=0.8', facecolor='lightyellow',
                        alpha=0.95, edgecolor='black', linewidth=2.5)
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   fontsize=21, verticalalignment='top', bbox=props,
                   fontweight='bold', family='monospace')

