"""
UAV Visualizer

Step 4 visualization: 3D UAV flight trajectory with energy consumption.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec
from typing import Optional
from .plot_config import TRAJECTORY_COLORMAP, CHINESE_LABELS


class UAVVisualizer:
    """
    Visualizes UAV flight trajectories and energy consumption.
    
    Creates Figure 4: 3D flight trajectory with drop points and energy curve,
    with Times New Roman 25pt and Chinese labels.
    """
    
    def __init__(self):
        """Initialize UAV visualizer."""
        self.fig = None
        self.ax = None
    
    def plot_3d_trajectory(self, trajectory: np.ndarray,
                          drop_indices: Optional[np.ndarray] = None,
                          depot_idx: int = 0,
                          ax: Optional[Axes3D] = None) -> Axes3D:
        """
        Plot 3D UAV flight trajectory.
        
        Args:
            trajectory: 3D trajectory array (N, 3) with x, y, z
            drop_indices: Indices of sensor drop waypoints
            depot_idx: Index of depot/launch point
            ax: Optional 3D axes
        
        Returns:
            3D matplotlib axes
        """
        if ax is None:
            self.fig = plt.figure(figsize=(14, 12))
            ax = self.fig.add_subplot(111, projection='3d')
            self.ax = ax
        
        labels = CHINESE_LABELS['uav_planning']
        
        # Color trajectory by altitude
        colors = trajectory[:, 2]  # z-coordinate
        
        # Plot trajectory line with color gradient
        for i in range(len(trajectory) - 1):
            ax.plot(trajectory[i:i+2, 0], trajectory[i:i+2, 1], trajectory[i:i+2, 2],
                   c=plt.cm.plasma(colors[i] / np.max(colors)),
                   linewidth=3, alpha=0.8)
        
        # Plot waypoints
        ax.scatter(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
                  c=colors, cmap=TRAJECTORY_COLORMAP, s=80,
                  edgecolors='black', linewidths=1, alpha=0.8,
                  label=labels['waypoint'])
        
        # Highlight depot
        ax.scatter([trajectory[depot_idx, 0]], 
                  [trajectory[depot_idx, 1]],
                  [trajectory[depot_idx, 2]],
                  c='green', s=500, marker='s', edgecolors='black',
                  linewidths=2.5, label=labels['depot'], zorder=10)
        
        # Highlight drop points
        if drop_indices is not None and len(drop_indices) > 0:
            drop_points = trajectory[drop_indices]
            ax.scatter(drop_points[:, 0], drop_points[:, 1], drop_points[:, 2],
                      c='red', s=300, marker='v', edgecolors='black',
                      linewidths=2, label=labels['drop_point'], zorder=9)
            
            # Draw vertical lines from drop points to ground
            for drop_point in drop_points:
                ax.plot([drop_point[0], drop_point[0]],
                       [drop_point[1], drop_point[1]],
                       [0, drop_point[2]],
                       'r--', linewidth=2, alpha=0.5)
        
        # Labels
        ax.set_xlabel(labels['xlabel'], fontsize=22, labelpad=15, fontweight='bold')
        ax.set_ylabel(labels['ylabel'], fontsize=22, labelpad=15, fontweight='bold')
        ax.set_zlabel(labels['zlabel'], fontsize=22, labelpad=15, fontweight='bold')
        ax.set_title(labels['title'], fontsize=26, fontweight='bold', pad=25)
        
        # Legend
        ax.legend(fontsize=18, loc='upper left', framealpha=0.9)
        
        # Set viewing angle
        ax.view_init(elev=25, azim=135)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Set z-axis to start from 0
        ax.set_zlim(0, np.max(trajectory[:, 2]) * 1.1)
        
        return ax
    
    def plot_energy_consumption(self, cumulative_energy: np.ndarray,
                               waypoint_labels: Optional[np.ndarray] = None,
                               ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot cumulative energy consumption vs waypoint.
        
        Args:
            cumulative_energy: Cumulative energy at each waypoint (Wh)
            waypoint_labels: Optional waypoint labels
            ax: Optional axes
        
        Returns:
            Matplotlib axes
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(12, 6))
            self.ax = ax
        
        labels = CHINESE_LABELS['uav_planning']
        
        waypoints = np.arange(len(cumulative_energy))
        
        # Plot cumulative energy
        ax.plot(waypoints, cumulative_energy, 'b-', linewidth=3,
               marker='o', markersize=8, markerfacecolor='blue',
               markeredgecolor='white', markeredgewidth=2)
        
        # Fill area under curve
        ax.fill_between(waypoints, 0, cumulative_energy, alpha=0.3, color='blue')
        
        # Labels
        ax.set_xlabel(labels['waypoint_index'], fontsize=25, fontweight='bold')
        ax.set_ylabel(labels['energy'], fontsize=25, fontweight='bold')
        ax.set_title('飞行能量消耗曲线', fontsize=28, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add final energy value annotation
        final_energy = cumulative_energy[-1]
        ax.text(waypoints[-1], final_energy, f'{final_energy:.1f} Wh',
               ha='right', va='bottom', fontsize=18, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        return ax
    
    def plot_trajectory_with_energy(self, trajectory: np.ndarray,
                                   cumulative_energy: np.ndarray,
                                   drop_indices: Optional[np.ndarray] = None) -> tuple:
        """
        Create combined plot with 3D trajectory and energy subplot.
        
        Args:
            trajectory: 3D trajectory array
            cumulative_energy: Cumulative energy array
            drop_indices: Drop point indices
        
        Returns:
            Tuple of (fig, ax3d, ax_energy)
        """
        self.fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(2, 1, height_ratios=[2, 1], hspace=0.3)
        
        # 3D trajectory subplot
        ax3d = self.fig.add_subplot(gs[0], projection='3d')
        self.plot_3d_trajectory(trajectory, drop_indices, ax=ax3d)
        
        # Energy subplot
        ax_energy = self.fig.add_subplot(gs[1])
        self.plot_energy_consumption(cumulative_energy, ax=ax_energy)
        
        return self.fig, ax3d, ax_energy
    
    def plot_energy_breakdown(self, energy_dict: dict,
                             ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot energy consumption breakdown pie chart.
        
        Args:
            energy_dict: Dictionary with energy breakdown
            ax: Optional axes
        
        Returns:
            Matplotlib axes
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(10, 10))
            self.ax = ax
        
        breakdown = energy_dict['energy_breakdown']
        
        labels = ['水平飞行', '垂直爬升', '悬停投放']
        sizes = [
            breakdown['horizontal_percent'],
            breakdown['vertical_percent'],
            breakdown['hover_percent']
        ]
        colors = ['#3498db', '#e74c3c', '#f39c12']
        explode = (0.05, 0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
                                          colors=colors, autopct='%1.1f%%',
                                          shadow=True, startangle=90,
                                          textprops={'fontsize': 22, 'fontweight': 'bold'})
        
        # Make percentage text white and bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(24)
            autotext.set_fontweight('bold')
        
        ax.set_title('能量消耗组成', fontsize=28, fontweight='bold', pad=20)
        
        return ax
    
    def plot_altitude_profile(self, trajectory: np.ndarray,
                             segment_distances: Optional[np.ndarray] = None,
                             ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot altitude profile along trajectory.
        
        Args:
            trajectory: 3D trajectory array
            segment_distances: Cumulative distances along trajectory
            ax: Optional axes
        
        Returns:
            Matplotlib axes
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(14, 6))
            self.ax = ax
        
        if segment_distances is None:
            # Calculate cumulative distance
            segments = np.diff(trajectory, axis=0)
            distances = np.sqrt(np.sum(segments**2, axis=1))
            segment_distances = np.concatenate([[0], np.cumsum(distances)])
        
        altitudes = trajectory[:, 2]
        
        # Plot altitude profile
        ax.plot(segment_distances, altitudes, 'b-', linewidth=3,
               marker='o', markersize=6)
        
        # Fill to ground
        ax.fill_between(segment_distances, 0, altitudes, alpha=0.3, color='skyblue')
        
        # Labels
        ax.set_xlabel('累计飞行距离 (m)', fontsize=25, fontweight='bold')
        ax.set_ylabel('飞行高度 (m)', fontsize=25, fontweight='bold')
        ax.set_title('飞行高度剖面图', fontsize=28, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, np.max(altitudes) * 1.1)
        
        return ax
    
    def save_figure(self, filepath: str, dpi: int = 300):
        """
        Save UAV visualization figure.
        
        Args:
            filepath: Output file path
            dpi: Resolution in DPI
        """
        if self.fig is not None:
            self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                           facecolor='white', edgecolor='none')


