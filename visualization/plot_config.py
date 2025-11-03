"""
Plot Configuration

Global matplotlib configuration for Times New Roman 25pt with Chinese support.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import platform


def setup_plot_style():
    """
    Setup global matplotlib style with unified Times New Roman font.
    All text elements use larger, professional sizing.
    """
    # Font configuration - LARGER SIZES for better visibility
    mpl.rcParams['font.family'] = 'Times New Roman'
    mpl.rcParams['font.size'] = 12
    mpl.rcParams['axes.labelsize'] = 14
    mpl.rcParams['axes.titlesize'] = 16
    mpl.rcParams['xtick.labelsize'] = 13
    mpl.rcParams['ytick.labelsize'] = 13
    mpl.rcParams['legend.fontsize'] = 12
    mpl.rcParams['figure.titlesize'] = 18
    
    # Ensure Times New Roman is used (no Chinese fallback needed)
    mpl.rcParams['font.sans-serif'] = ['Times New Roman']
    
    # Fix minus sign display
    mpl.rcParams['axes.unicode_minus'] = False
    
    # Figure settings - Unified size (10x8)
    mpl.rcParams['figure.dpi'] = 100
    mpl.rcParams['savefig.dpi'] = 300
    mpl.rcParams['savefig.bbox'] = 'tight'
    mpl.rcParams['savefig.facecolor'] = 'white'
    mpl.rcParams['figure.figsize'] = (10, 8)
    mpl.rcParams['figure.autolayout'] = True
    mpl.rcParams['figure.facecolor'] = 'white'
    
    # Line and marker settings - Professional
    mpl.rcParams['lines.linewidth'] = 2.0
    mpl.rcParams['lines.markersize'] = 8
    
    # Grid settings - Subtle
    mpl.rcParams['grid.alpha'] = 0.3
    mpl.rcParams['grid.linestyle'] = '--'
    mpl.rcParams['grid.linewidth'] = 0.8
    
    # Axes settings - Clean professional look
    mpl.rcParams['axes.grid'] = False  # Enable per-plot as needed
    mpl.rcParams['axes.axisbelow'] = True
    mpl.rcParams['axes.edgecolor'] = '0.3'
    mpl.rcParams['axes.linewidth'] = 1.2
    mpl.rcParams['axes.facecolor'] = '#f8f9fa'
    
    # Color cycle (professional colors)
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=[
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf'
    ])
    
    # Tight layout
    mpl.rcParams['figure.constrained_layout.use'] = True


def get_chinese_font(size=14):
    """
    Get available Chinese font for matplotlib.
    
    Args:
        size: Font size (default 14 to match axis labels)
    
    Returns:
        Font properties for Chinese text
    """
    system = platform.system()
    
    if system == 'Windows':
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun']
    elif system == 'Darwin':
        chinese_fonts = ['Arial Unicode MS', 'STHeiti']
    else:
        chinese_fonts = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC']
    
    # Try to find an available font
    available_fonts = [f.name for f in font_manager.fontManager.ttflist]
    
    for font in chinese_fonts:
        if font in available_fonts:
            return font_manager.FontProperties(family=font, size=size)
    
    # Fallback
    return font_manager.FontProperties(size=size)


def create_figure_with_subplots(nrows: int = 2, ncols: int = 2, 
                                figsize: tuple = (20, 16)) -> tuple:
    """
    Create figure with subplots using configured style.
    
    Args:
        nrows: Number of subplot rows
        ncols: Number of subplot columns
        figsize: Figure size in inches
    
    Returns:
        Tuple of (fig, axes)
    """
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    return fig, axes


def save_figure(fig, filepath: str, dpi: int = 300, bbox_inches: str = 'tight'):
    """
    Save figure with high quality settings.
    
    Args:
        fig: Matplotlib figure
        filepath: Output file path
        dpi: Resolution in dots per inch
        bbox_inches: Bounding box setting
    """
    fig.savefig(filepath, dpi=dpi, bbox_inches=bbox_inches, 
                facecolor='white', edgecolor='none')


# Color schemes for different visualizations
FOREST_COLORS = {
    'pine': '#2E7D32',
    'oak': '#558B2F',
    'birch': '#7CB342',
    'maple': '#9CCC65',
    'spruce': '#1B5E20',
    'beech': '#689F38'
}

HEATMAP_COLORMAP = 'RdYlGn_r'  # Red (bad) to Green (good)
COVERAGE_COLORMAP = 'viridis'
TRAJECTORY_COLORMAP = 'plasma'


# Chinese labels dictionary
CHINESE_LABELS = {
    'forest_map': {
        'title': '森林分布图',
        'xlabel': '东-西方向 (m)',
        'ylabel': '南-北方向 (m)',
        'species': '树种',
        'distance': '距离 (m)',
        'position': '位置坐标'
    },
    'em_propagation': {
        'title': '信号覆盖热力图',
        'xlabel': '东-西方向 (m)',
        'ylabel': '南-北方向 (m)',
        'path_loss': '路径损耗 (dB)',
        'rssi': '接收信号强度 (dBm)',
        'snr': '信噪比 (dB)',
        'coverage': '覆盖率',
        'gateway': '网关',
        'sensor': '传感器'
    },
    'optimization': {
        'title': 'Pareto前沿与传感器部署',
        'xlabel_obj1': '盲区比例',
        'xlabel_obj2': '节点数量',
        'xlabel_obj3': '能量消耗',
        'pareto_front': 'Pareto前沿',
        'selected': '选中方案',
        'deployment': '传感器部署图',
        'objectives': '目标函数'
    },
    'uav_planning': {
        'title': 'UAV飞行轨迹规划',
        'xlabel': '东-西方向 (m)',
        'ylabel': '南-北方向 (m)',
        'zlabel': '高度 (m)',
        'trajectory': '飞行轨迹',
        'waypoint': '航点',
        'depot': '起降点',
        'drop_point': '投放点',
        'energy': '累计能量消耗 (Wh)',
        'waypoint_index': '航点序号'
    }
}


# Apply configuration on import
setup_plot_style()

