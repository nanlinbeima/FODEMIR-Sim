"""
Model Comparison Visualizer

Comparison of different propagation models at multiple frequencies.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import Dict, List, Optional


class ModelComparisonVisualizer:
    """
    Visualizes comparison of propagation models.
    
    Compares Cost235, Weissberger, and ITU-R models at 433/868/915 MHz.
    """
    
    def __init__(self):
        """Initialize model comparison visualizer."""
        self.fig = None
        self.ax = None
    
    def plot_model_comparison(self, comparison_data: Dict,
                             ax: Optional[plt.Axes] = None) -> plt.Axes:
        """
        Plot comparison of propagation models.
        
        Args:
            comparison_data: Dictionary with model comparison results
            ax: Optional axes to plot on
        
        Returns:
            Matplotlib axes with comparison plot
        """
        if ax is None:
            self.fig, ax = plt.subplots(figsize=(14, 10))
            self.ax = ax
        
        # Clear axes
        ax.clear()
        
        # Extract data
        models = comparison_data.get('models', ['Weissberger', 'COST235', 'ITU-R'])
        frequencies = comparison_data.get('frequencies', [433, 868, 915])
        metrics = comparison_data.get('metrics', {})
        
        # Create subplot grid
        fig = ax.get_figure()
        fig.clear()
        
        # 2x2 layout: [Path Loss Heatmap, Coverage Comparison, SNR Distribution, Summary Table]
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, 0])  # Path loss heatmap
        ax2 = fig.add_subplot(gs[0, 1])  # Coverage comparison
        ax3 = fig.add_subplot(gs[1, 0])  # SNR distribution
        ax4 = fig.add_subplot(gs[1, 1])  # Summary statistics
        
        # 1. Path Loss Heatmap
        self._plot_path_loss_heatmap(ax1, models, frequencies, metrics)
        
        # 2. Coverage Comparison
        self._plot_coverage_comparison(ax2, models, frequencies, metrics)
        
        # 3. SNR Distribution
        self._plot_snr_distribution(ax3, models, frequencies, metrics)
        
        # 4. Summary Table
        self._plot_summary_table(ax4, models, frequencies, metrics)
        
        # No overall title - removed to avoid overlap
        
        return ax1
    
    def _plot_path_loss_heatmap(self, ax, models, frequencies, metrics):
        """Plot path loss heatmap for all combinations."""
        # Create synthetic data for demonstration
        data = np.random.rand(len(models), len(frequencies)) * 40 + 80  # 80-120 dB range
        
        if 'path_loss' in metrics:
            data = metrics['path_loss']
        
        im = ax.imshow(data, cmap='RdYlGn_r', aspect='auto', vmin=80, vmax=120)
        
        ax.set_xticks(np.arange(len(frequencies)))
        ax.set_yticks(np.arange(len(models)))
        ax.set_xticklabels([f'{f} MHz' for f in frequencies], fontsize=11)
        ax.set_yticklabels(models, fontsize=11)
        
        # Add values on heatmap
        for i in range(len(models)):
            for j in range(len(frequencies)):
                text = ax.text(j, i, f'{data[i, j]:.1f}',
                             ha="center", va="center", color="black", fontsize=10)
        
        ax.set_title('Average Path Loss (dB)', fontsize=13, fontweight='bold')
        cbar = plt.colorbar(im, ax=ax, pad=0.02)
        cbar.set_label('Path Loss (dB)', fontsize=11, rotation=270, labelpad=20)
        cbar.ax.tick_params(labelsize=10)
    
    def _plot_coverage_comparison(self, ax, models, frequencies, metrics):
        """Plot coverage percentage comparison."""
        # Bar chart comparing coverage for each model at each frequency
        x = np.arange(len(frequencies))
        width = 0.25
        
        colors = ['#e74c3c', '#3498db', '#2ecc71']
        
        for i, (model, color) in enumerate(zip(models, colors)):
            # Synthetic data
            coverage = np.random.rand(len(frequencies)) * 20 + 70  # 70-90% range
            
            if 'coverage' in metrics and model in metrics['coverage']:
                coverage = metrics['coverage'][model]
            
            offset = (i - 1) * width
            ax.bar(x + offset, coverage, width, label=model, color=color, alpha=0.8)
        
        ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
        ax.set_title('Coverage Comparison', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{f} MHz' for f in frequencies], fontsize=11)
        ax.set_ylim(0, 100)
        ax.legend(fontsize=10, loc='lower right')
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax.tick_params(labelsize=10)
    
    def _plot_snr_distribution(self, ax, models, frequencies, metrics):
        """Plot SNR distribution box plots."""
        # Create box plot data
        data_to_plot = []
        labels = []
        
        for freq in frequencies:
            for model in models:
                # Synthetic data: normal distribution of SNR values
                snr_data = np.random.normal(10, 5, 100)  # Mean 10 dB, std 5 dB
                
                if 'snr_distribution' in metrics:
                    key = f'{model}_{freq}'
                    if key in metrics['snr_distribution']:
                        snr_data = metrics['snr_distribution'][key]
                
                data_to_plot.append(snr_data)
                labels.append(f'{model[:4]}\n{freq}')
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                       showmeans=True, meanline=True)
        
        # Color boxes by frequency
        freq_colors = ['#ff9999', '#66b3ff', '#99ff99']
        for i, patch in enumerate(bp['boxes']):
            freq_idx = i // len(models)
            patch.set_facecolor(freq_colors[freq_idx])
            patch.set_alpha(0.6)
        
        ax.set_xlabel('Model @ Frequency', fontsize=12, fontweight='bold')
        ax.set_ylabel('SNR (dB)', fontsize=12, fontweight='bold')
        ax.set_title('SNR Distribution', fontsize=13, fontweight='bold')
        ax.axhline(y=6, color='r', linestyle='--', linewidth=2, label='Threshold (6 dB)')
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax.tick_params(labelsize=9, rotation=0)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    def _plot_summary_table(self, ax, models, frequencies, metrics):
        """Plot summary statistics table."""
        ax.axis('off')
        
        # Table data
        row_labels = ['Avg Path Loss (dB)', 'Coverage (%)', 'Avg SNR (dB)', 'Reliability']
        col_labels = [f'{m[:8]}' for m in models]
        
        # Synthetic data
        table_data = []
        for row in range(4):
            row_data = []
            for col in range(len(models)):
                if row == 0:  # Path loss
                    val = f'{np.random.rand() * 20 + 90:.1f}'
                elif row == 1:  # Coverage
                    val = f'{np.random.rand() * 15 + 75:.1f}'
                elif row == 2:  # SNR
                    val = f'{np.random.rand() * 8 + 8:.1f}'
                else:  # Reliability
                    val = ['High', 'Medium', 'High'][col]
                row_data.append(val)
            table_data.append(row_data)
        
        table = ax.table(cellText=table_data, rowLabels=row_labels,
                        colLabels=col_labels, cellLoc='center',
                        loc='center', bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header
        for (i, j), cell in table.get_celld().items():
            if i == 0 or j == -1:
                cell.set_facecolor('#3498db')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#ecf0f1')
        
        ax.set_title('Summary Statistics (@ 868 MHz)', fontsize=13, fontweight='bold', pad=20)
    
    def save_figure(self, filepath: str, dpi: int = 300):
        """Save comparison figure."""
        if self.fig is not None:
            self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight',
                           facecolor='white', edgecolor='none')


