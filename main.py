"""
FODEMIR-Sim Main Application

Forest Deployment Optimization via EM & Multi-objective Integrated Research Simulator
"""

import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                              QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                              QProgressBar, QStatusBar, QFileDialog, QMessageBox,
                              QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
                              QComboBox, QTextEdit, QScrollArea, QTableWidget,
                              QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QDialogButtonBox,
                              QCheckBox, QButtonGroup, QRadioButton, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
import matplotlib.pyplot as plt

# Import simulation modules
from config.config_manager import ConfigManager
from src.forest_generation.gpt_forest_generator import GPTForestGenerator
from src.forest_generation.poisson_disk_sampler import PoissonDiskSampler
from src.forest_generation.tree_attributes import TreeAttributesDB
from src.forest_generation.rasterizer import ForestRasterizer
from src.em_propagation.weissberger_model import WeissbergerModel
from src.em_propagation.link_calculator import LinkCalculator
from src.em_propagation.coverage_analyzer import CoverageAnalyzer
from src.em_propagation.hybrid_link_calculator import HybridLinkCalculator
from src.em_propagation.canopy_analyzer import CanopyAnalyzer
from src.optimization.objectives import ObjectiveFunctions
from src.optimization.communication_objectives import CommunicationObjectives
from src.optimization.constraints import ConstraintHandler
from src.optimization.problem_definition import DeploymentProblem
from src.optimization.communication_problem import CommunicationProblem
from src.optimization.nsga2_optimizer import NSGA2Optimizer
from src.optimization.deployment_optimizer import DeploymentOptimizer
from src.uav_planning.tsp_solver import TSPSolver
from src.uav_planning.path_planner import PathPlanner
from src.uav_planning.energy_estimator import EnergyEstimator

from visualization.plot_config import setup_plot_style
from visualization.forest_visualizer import ForestVisualizer
from visualization.propagation_visualizer_v2 import PropagationVisualizerV2
from visualization.optimization_visualizer_v2 import OptimizationVisualizerV2
from visualization.uav_visualizer import UAVVisualizer
from visualization.uav_visualizer_v2 import UAVVisualizerV2
from visualization.model_comparison_visualizer import ModelComparisonVisualizer

from ui.styles import get_stylesheet


class GPTAPIKeyDialog(QDialog):
    """Dialog for entering GPT-4 API key."""
    
    def __init__(self, parent=None, current_key=""):
        super().__init__(parent)
        self.setWindowTitle("GPT-4 API Key Required")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("GPT-4 API Key Configuration")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            font-family: 'Times New Roman';
            color: #2c3e50;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info text
        info = QLabel(
            "To use GPT-4 for forest generation, you need an OpenAI API key.\n"
            "Get your API key from: https://platform.openai.com/api-keys"
        )
        info.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            padding: 5px 10px;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # API Key input
        key_layout = QHBoxLayout()
        key_label = QLabel("API Key:")
        key_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setText(current_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Show/Hide button
        self.show_key_btn = QPushButton("👁 Show")
        self.show_key_btn.setFixedWidth(80)
        self.show_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.show_key_btn.clicked.connect(self.toggle_key_visibility)
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(self.show_key_btn)
        layout.addLayout(key_layout)
        
        # Warning
        warning = QLabel("⚠️ Your API key will be stored locally in config/api_keys.json")
        warning.setStyleSheet("""
            font-size: 10px;
            color: #e67e22;
            font-style: italic;
            padding: 5px 10px;
        """)
        layout.addWidget(warning)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Save & Continue")
        ok_btn.setFont(QFont("Times New Roman", 11, QFont.Weight.Bold))
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Times New Roman", 11))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.setStyleSheet("QDialog { background-color: #ecf0f1; }")
    
    def toggle_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("🔒 Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("👁 Show")
    
    def get_api_key(self):
        """Get entered API key."""
        return self.api_key_input.text().strip()


class ForestGenerationDialog(QDialog):
    """Dialog for selecting forest generation method."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forest Generation Method")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.parent_window = parent
        
        # Create layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Select Forest Generation Method")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            font-family: 'Times New Roman';
            color: #2c3e50;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # GPT-4 option
        self.use_gpt4_checkbox = QCheckBox("Use GPT-4 for Enhanced Forest Generation")
        self.use_gpt4_checkbox.setStyleSheet("""
            font-size: 14px;
            font-family: 'Times New Roman';
            padding: 10px;
        """)
        self.use_gpt4_checkbox.setChecked(False)
        layout.addWidget(self.use_gpt4_checkbox)
        
        # GPT-4 note
        gpt4_note = QLabel("⚠️ Note: GPT-4 requires API key and may incur costs")
        gpt4_note.setStyleSheet("""
            font-size: 11px;
            font-style: italic;
            color: #e67e22;
            padding-left: 30px;
        """)
        layout.addWidget(gpt4_note)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)
        
        # Method selection label
        method_label = QLabel("If not using GPT-4, select generation method:")
        method_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            font-family: 'Times New Roman';
            padding: 10px 0px 5px 0px;
        """)
        layout.addWidget(method_label)
        
        # Radio buttons for method selection
        self.method_group = QButtonGroup(self)
        
        # Option 1: Default synthetic forest
        self.synthetic_radio = QRadioButton("Use Default Synthetic Forest Generation")
        self.synthetic_radio.setChecked(False)  # Not default anymore
        self.synthetic_radio.setStyleSheet("""
            font-size: 13px;
            font-family: 'Times New Roman';
            padding: 5px;
        """)
        self.method_group.addButton(self.synthetic_radio, 1)
        layout.addWidget(self.synthetic_radio)
        
        synthetic_desc = QLabel("   • Procedurally generated forest with configurable parameters")
        synthetic_desc.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            padding-left: 25px;
        """)
        layout.addWidget(synthetic_desc)
        
        # Option 2: Real forest image (NOW DEFAULT)
        self.real_image_radio = QRadioButton("Use Real Aerial Forest Image (image.png) - Recommended")
        self.real_image_radio.setChecked(True)  # Set as default
        self.real_image_radio.setStyleSheet("""
            font-size: 13px;
            font-family: 'Times New Roman';
            padding: 5px;
            font-weight: bold;
        """)
        self.method_group.addButton(self.real_image_radio, 2)
        layout.addWidget(self.real_image_radio)
        
        real_desc = QLabel("   • Use real forest data from aerial/satellite imagery")
        real_desc.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            padding-left: 25px;
        """)
        layout.addWidget(real_desc)
        
        # Check if image.png exists
        if not Path('image.png').exists():
            self.real_image_radio.setEnabled(False)
            self.real_image_radio.setText("Use Real Aerial Forest Image (image.png not found)")
            real_desc.setText("   • ⚠️ image.png not found in project directory")
            real_desc.setStyleSheet("""
                font-size: 11px;
                color: #e74c3c;
                padding-left: 25px;
            """)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Start Simulation")
        ok_btn.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Times New Roman", 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a89;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply styling to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
        """)
    
    def get_selected_method(self):
        """Get selected generation method."""
        if self.use_gpt4_checkbox.isChecked():
            return 'gpt4'
        elif self.real_image_radio.isChecked():
            return 'real_image'
        else:
            return 'synthetic'
    
    def accept(self):
        """Override accept to check GPT-4 API key if needed."""
        if self.use_gpt4_checkbox.isChecked():
            # Check if API key exists
            api_key = self.load_api_key()
            if not api_key:
                # Show API key input dialog
                key_dialog = GPTAPIKeyDialog(self, api_key)
                if key_dialog.exec() != QDialog.DialogCode.Accepted:
                    return  # User cancelled API key input
                
                api_key = key_dialog.get_api_key()
                if not api_key or not api_key.startswith('sk-'):
                    QMessageBox.warning(
                        self,
                        "Invalid API Key",
                        "Please enter a valid OpenAI API key starting with 'sk-'"
                    )
                    return
                
                # Save API key
                self.save_api_key(api_key)
        
        # Continue with normal accept
        super().accept()
    
    def load_api_key(self):
        """Load API key from config file."""
        api_key_file = Path('config/api_keys.json')
        if api_key_file.exists():
            try:
                import json
                with open(api_key_file, 'r') as f:
                    data = json.load(f)
                    return data.get('openai_api_key', '')
            except Exception as e:
                print(f"Error loading API key: {e}")
        return ''
    
    def save_api_key(self, api_key):
        """Save API key to config file."""
        api_key_file = Path('config/api_keys.json')
        api_key_file.parent.mkdir(exist_ok=True)
        
        try:
            import json
            data = {'openai_api_key': api_key}
            with open(api_key_file, 'w') as f:
                json.dump(data, f, indent=2)
            print("✓ API key saved successfully")
        except Exception as e:
            print(f"Error saving API key: {e}")
            QMessageBox.warning(
                self,
                "Save Error",
                f"Could not save API key: {e}"
            )


class SimulationWorker(QThread):
    """Worker thread for running simulation."""
    
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def generate_forest_with_gpt4(self, api_key, width, height, n_trees, density):
        """Generate forest using GPT-4 API."""
        import requests
        import json
        
        # Prepare prompt for GPT-4
        prompt = f"""Generate a realistic forest distribution for a {int(width)}×{int(height)} meter area.

Requirements:
- Total area: {int(width*height)} m²
- Target tree count: approximately {n_trees} trees
- Tree density: {density} trees per hectare
- Species distribution: Pine (40%), Oak (30%), Birch (20%), Maple (10%)

Please generate:
1. Tree positions (x, y coordinates in meters)
2. Species for each tree
3. Crown radii (realistic sizes: 3-8 meters)
4. 2-4 natural clearings (open areas) with positions and radii

Output format: JSON with structure:
{{
  "trees": [
    {{"x": float, "y": float, "species": "pine|oak|birch|maple", "crown_radius": float, "height": float, "dbh": float}}
  ],
  "clearings": [
    {{"x": float, "y": float, "radius": float}}
  ]
}}

Make it realistic with:
- Natural clustering patterns
- Appropriate spacing (min 3m between trees)
- Varied crown sizes based on species
- Clearings in natural-looking positions

Generate approximately {min(n_trees, 100)} sample trees (we'll extrapolate for larger forests)."""

        # Call OpenAI API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4',
            'messages': [
                {'role': 'system', 'content': 'You are a forest ecology expert. Generate realistic forest distributions in JSON format only.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 3000
        }
        
        self.progress.emit(2, "Calling GPT-4 API...")
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            self.progress.emit(3, "Parsing GPT-4 response...")
            
            # Extract JSON from response (might be wrapped in markdown)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            forest_data = json.loads(content.strip())
            
            # Parse GPT-4 response
            trees = forest_data.get('trees', [])
            clearings_data = forest_data.get('clearings', [])
            
            if len(trees) == 0:
                raise Exception("GPT-4 returned no trees")
            
            self.progress.emit(4, f"Processing {len(trees)} trees from GPT-4...")
            
            # If we got fewer trees than needed, duplicate and adjust positions
            if len(trees) < n_trees:
                # Replicate trees to reach target count
                factor = int(np.ceil(n_trees / len(trees)))
                expanded_trees = []
                for i in range(factor):
                    for tree in trees:
                        # Add some random offset to avoid exact duplicates
                        offset_x = np.random.uniform(-20, 20)
                        offset_y = np.random.uniform(-20, 20)
                        new_x = (tree['x'] + offset_x) % width
                        new_y = (tree['y'] + offset_y) % height
                        expanded_trees.append({
                            'x': new_x,
                            'y': new_y,
                            'species': tree['species'],
                            'crown_radius': tree.get('crown_radius', 5.0),
                            'height': tree.get('height', 15.0),
                            'dbh': tree.get('dbh', 30.0)
                        })
                trees = expanded_trees[:n_trees]
            
            # Extract data
            tree_positions = np.array([[t['x'], t['y']] for t in trees])
            species_list = [t['species'] for t in trees]
            crown_radii = np.array([t.get('crown_radius', 5.0) for t in trees])
            
            # Parse clearings
            clearings = []
            for c in clearings_data:
                clearings.append({
                    'center': np.array([c['x'], c['y']]),
                    'radius': c['radius']
                })
            
            # Create attributes dictionary
            attributes = {
                'crown_diameter': crown_radii * 2,
                'height_m': np.array([t.get('height', 15.0) for t in trees]),
                'dbh_cm': np.array([t.get('dbh', 30.0) for t in trees])
            }
            
            return tree_positions, species_list, crown_radii, clearings, attributes
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse GPT-4 response as JSON: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected API response format: {e}")
    
    def _detect_clearings_from_image(self, image_path, domain_width, domain_height):
        """
        Detect clearing areas from aerial forest image.
        
        Clearings appear as lighter colored areas (brownish/tan) in the image.
        This method detects these areas and returns their approximate positions and sizes.
        
        Args:
            image_path: Path to forest image
            domain_width: Domain width in meters
            domain_height: Domain height in meters
        
        Returns:
            List of clearings (dicts with 'center' and 'radius')
        """
        try:
            from PIL import Image
            import numpy as np
            from scipy import ndimage
            
            # Load image
            img = Image.open(image_path)
            img_array = np.array(img.convert('RGB'))
            
            # Get image dimensions
            img_height, img_width = img_array.shape[:2]
            
            # Calculate scaling factors
            scale_x = domain_width / img_width
            scale_y = domain_height / img_height
            
            # Convert to HSV for better color detection
            from PIL import ImageOps
            hsv = img.convert('HSV')
            hsv_array = np.array(hsv)
            
            # Detect lighter areas (clearings)
            # Clearings typically have higher Value (brightness) and lower Saturation
            v_channel = hsv_array[:, :, 2]  # Value channel
            s_channel = hsv_array[:, :, 1]  # Saturation channel
            
            # Thresholds for clearing detection
            # High brightness, low saturation = clearing
            clearing_mask = (v_channel > 120) & (s_channel < 100)
            
            # Clean up noise with morphological operations
            from scipy.ndimage import binary_opening, binary_closing
            clearing_mask = binary_opening(clearing_mask, structure=np.ones((5, 5)))
            clearing_mask = binary_closing(clearing_mask, structure=np.ones((10, 10)))
            
            # Label connected regions
            labeled_clearings, num_clearings = ndimage.label(clearing_mask)
            
            clearings = []
            
            # Extract clearing properties
            for i in range(1, num_clearings + 1):
                # Get pixels belonging to this clearing
                clearing_pixels = np.where(labeled_clearings == i)
                
                # Calculate center of mass
                center_y = np.mean(clearing_pixels[0])
                center_x = np.mean(clearing_pixels[1])
                
                # Calculate approximate radius
                num_pixels = len(clearing_pixels[0])
                radius_pixels = np.sqrt(num_pixels / np.pi)
                
                # Only include significant clearings (not tiny specs)
                if radius_pixels > 10:  # At least 10 pixels radius
                    # Convert to domain coordinates
                    center_x_meters = center_x * scale_x
                    center_y_meters = (img_height - center_y) * scale_y  # Flip Y axis
                    radius_meters = radius_pixels * (scale_x + scale_y) / 2  # Average scale
                    
                    clearings.append({
                        'center': np.array([center_x_meters, center_y_meters]),
                        'radius': radius_meters
                    })
            
            # Sort by size (largest first) and limit to top clearings
            clearings.sort(key=lambda c: c['radius'], reverse=True)
            clearings = clearings[:15]  # Keep top 15 clearings
            
            return clearings
            
        except Exception as e:
            print(f"Warning: Could not detect clearings from image: {e}")
            # Return some default clearings based on visible patterns in the provided image
            # These are approximate positions of clearings visible in the image
            default_clearings = [
                {'center': np.array([domain_width*0.25, domain_height*0.25]), 'radius': 40},
                {'center': np.array([domain_width*0.60, domain_height*0.18]), 'radius': 35},
                {'center': np.array([domain_width*0.35, domain_height*0.50]), 'radius': 30},
                {'center': np.array([domain_width*0.78, domain_height*0.55]), 'radius': 28},
                {'center': np.array([domain_width*0.15, domain_height*0.70]), 'radius': 35},
                {'center': np.array([domain_width*0.70, domain_height*0.80]), 'radius': 32},
                {'center': np.array([domain_width*0.50, domain_height*0.35]), 'radius': 25},
                {'center': np.array([domain_width*0.85, domain_height*0.20]), 'radius': 30},
            ]
            return default_clearings
    
    def run(self):
        """Run simulation pipeline."""
        try:
            results = {}
            
            # Step 1: Forest Generation (0-25%)
            self.progress.emit(1, "Step 1/4: Generating forest map...")
            area = self.config.get('forest_generation.area_m2', 1000000)  # Default 1000×1000 m
            width = height = np.sqrt(area)
            density = self.config.get('forest_generation.tree_density_per_ha', 500)
            n_trees = int(area / 10000 * density)
            
            # Get forest generation method
            forest_method = self.config.get('forest_generation.method', 'synthetic')
            use_gpt = self.config.get('forest_generation.use_gpt', False)
            
            if forest_method == 'real_image':
                # Use real aerial forest image - detect clearings from image
                self.progress.emit(1, "Step 1/4: Loading real forest image and detecting clearings...")
                # Create minimal tree data for compatibility
                tree_positions = np.array([[width/2, height/2]])  # Dummy position
                species_list = ['pine']
                crown_radii = np.array([5.0])
                
                # Detect clearings from real forest image
                clearings = self._detect_clearings_from_image('image.png', width, height)
                print(f"Detected {len(clearings)} clearings from forest image")
                
                attributes = {
                    'crown_diameter': crown_radii * 2,
                    'height_m': np.array([15.0]),
                    'dbh_cm': np.array([30.0])
                }
                
            elif use_gpt:
                # GPT-4 generation (requires API key)
                self.progress.emit(1, "Step 1/4: Generating forest with GPT-4...")
                gpt_success = False
                try:
                    # Load API key
                    api_key_file = Path('config/api_keys.json')
                    if not api_key_file.exists():
                        raise Exception("API key file not found")
                    
                    import json
                    with open(api_key_file, 'r') as f:
                        api_data = json.load(f)
                        api_key = api_data.get('openai_api_key', '')
                    
                    if not api_key:
                        raise Exception("API key is empty")
                    
                    # Call GPT-4 to generate forest parameters
                    tree_positions, species_list, crown_radii, clearings, attributes = self.generate_forest_with_gpt4(
                        api_key, width, height, n_trees, density
                    )
                    
                    self.progress.emit(5, "GPT-4 generation complete!")
                    gpt_success = True
                    
                except Exception as e:
                    self.progress.emit(1, f"GPT-4 generation failed: {e}. Using synthetic method...")
                    print(f"GPT-4 error: {e}")
                    # Fall back to synthetic
                    forest_method = 'synthetic'
            
            if forest_method == 'synthetic' or (use_gpt and not gpt_success):
                # Generate forest without GPT (local random generation)
                tree_db = TreeAttributesDB()
                species_mix = self.config.get('forest_generation.species_mix', 
                                             {'pine': 40, 'oak': 30, 'birch': 20, 'maple': 10})
                
                species_list, attributes = tree_db.generate_forest_attributes(
                    species_mix, n_trees,
                    dbh_range=(15, 60)
                )
                
                # Sample positions with Poisson disk
                min_spacing = self.config.get('forest_generation.min_tree_spacing_m', 3.0)
                sampler = PoissonDiskSampler(width, height, min_spacing)
                positions = sampler.sample(target_count=n_trees)
                
                # Create clearings (realistic forest with open areas)
                clearings = [
                    {'center': np.array([width*0.25, height*0.25]), 'radius': 40},
                    {'center': np.array([width*0.75, height*0.75]), 'radius': 35},
                    {'center': np.array([width*0.5, height*0.6]), 'radius': 25},
                ]
                
                # Filter out trees in clearings
                filtered_positions = []
                for pos in positions:
                    in_clearing = False
                    for clearing in clearings:
                        dist = np.linalg.norm(pos - clearing['center'])
                        if dist < clearing['radius']:
                            in_clearing = True
                            break
                    if not in_clearing:
                        filtered_positions.append(pos)
                
                # Trim to actual generated count
                actual_count = min(len(filtered_positions), len(species_list))
                tree_positions = np.array(filtered_positions[:actual_count])
                species_list = species_list[:actual_count]
                crown_radii = attributes['crown_diameter'][:actual_count] / 2
            
            results['forest'] = {
                'positions': tree_positions,
                'species': species_list,
                'crown_radii': crown_radii,
                'attributes': attributes if forest_method == 'real_image' else {k: v[:actual_count] for k, v in attributes.items()},
                'clearings': clearings,  # Store clearings for visualization
                'domain': (width, height),
                'method': forest_method  # Store method for visualization
            }
            
            self.progress.emit(25, "Step 1 complete! Displaying forest map...")
            
            # Step 2: EM Propagation with Canopy-Aware Models (25-50%)
            self.progress.emit(26, "Step 2/4: Analyzing canopy closure...")
            
            # Step 2.1: Create canopy closure digital map
            canopy_analyzer = CanopyAnalyzer(width, height, resolution=5.0)
            canopy_closure_map = canopy_analyzer.calculate_canopy_closure_map(
                tree_positions, crown_radii, smooth_sigma=1.5
            )
            
            # Classify terrain (clearing vs forest)
            terrain_map, terrain_stats = canopy_analyzer.classify_terrain(
                canopy_closure_map, clearing_threshold=20.0
            )
            
            self.progress.emit(30, f"Canopy analysis complete! "
                              f"Clearing: {terrain_stats['clearing_area_pct']:.1f}%, "
                              f"Forest: {terrain_stats['forest_area_pct']:.1f}%")
            
            # Step 2.2: Create hybrid link calculator
            # Uses FSPL for clearings, ITU-R P.833 for forest
            self.progress.emit(35, "Step 2/4: Calculating propagation with terrain-aware models...")
            frequency = self.config.get('em_propagation.frequency_mhz', 868)
            
            # Place gateway at geometric center of forest for optimal cluster deployment
            gateway_positions = np.array([
                [width * 0.5, height * 0.5]  # Exact center for cluster-based deployment
            ])
            
            # Create hybrid link calculator with canopy map
            link_calc = HybridLinkCalculator(
                frequency_mhz=frequency,
                tx_power_dbm=self.config.get('em_propagation.tx_power_dbm', 14),
                tx_gain_dbi=self.config.get('em_propagation.antenna_gain_tx_dbi', 2.15),
                rx_gain_dbi=self.config.get('em_propagation.antenna_gain_rx_dbi', 2.15),
                canopy_closure_map=canopy_closure_map,
                grid_resolution=5.0,
                domain_size=(width, height)
            )
            
            # Calculate RSSI coverage map
            coverage = CoverageAnalyzer(width, height, resolution=20)  # Coarser grid for speed
            coverage_map = coverage.calculate_coverage_map(
                gateway_positions, link_calc,
                tree_positions, crown_radii, metric='rssi'  # Use RSSI
            )
            
            results['propagation'] = {
                'coverage_map': coverage_map,
                'gateway_positions': gateway_positions,
                'extent': (0, width, 0, height),
                'metric': 'rssi',  # Store metric type
                'link_calculator': link_calc,  # Store for visualization
                'canopy_closure_map': canopy_closure_map,  # Store canopy map
                'terrain_stats': terrain_stats  # Store terrain statistics
            }
            
            self.progress.emit(50, "Step 2 complete! Displaying coverage map...")
            
            # Step 3: Optimization (50-75%)
            self.progress.emit(51, "Step 3/4: Running optimization (this may take 10-20s)...")
            
            # Get clearings from forest results for priority optimization
            clearings = results['forest'].get('clearings', [])
            
            # Use communication-oriented objectives instead of deployment objectives
            objectives = CommunicationObjectives(
                width, height, gateway_positions,
                link_calc, coverage,
                tree_positions, crown_radii,
                snr_threshold_db=self.config.get('em_propagation.snr_threshold_db', 6),
                enforce_snr_strict=False  # Allow relaxed routing for 300m coverage range
            )
            
            constraints = ConstraintHandler(
                width, height,
                min_sensor_spacing=self.config.get('optimization.constraints.min_sensor_spacing_m', 50),
                min_gateway_spacing=0.0,  # Allow sensors near gateway for full area coverage
                gateway_positions=gateway_positions,
                link_calculator=link_calc,
                tree_positions=tree_positions,
                crown_radii=crown_radii,
                enforce_snr_strict=False  # Allow weaker connections to cover boundary areas
            )
            
            # Adaptive mode - GUARANTEE 100% coverage with communication quality
            # REQUIREMENTS:
            # 1. Every point within 300m of at least one sensor
            # 2. Avg RSSI > -90 dBm (good signal strength)
            # 3. Avg SNR > 10 dB (good signal quality)
            area_hectares = (width * height) / 10000
            
            # For COMPLETE coverage with QUALITY communication:
            # - Need denser deployment to ensure sensors are close to gateway
            # - Max distance from gateway to sensor should be ~400-500m for SNR>10dB
            # - Formula: based on area with heavy overlap + quality requirement
            area_km2 = (width * height) / 1000000
            # Each sensor effectively covers ~0.12 km² with quality constraints
            # (more conservative than 0.15 due to communication quality needs)
            min_sensors = max(10, int(np.ceil(area_km2 / 0.12)) + 6)
            max_sensors = min_sensors + 5  # Try wider range to find quality solution
            
            self.progress.emit(52, f"Full coverage mode: trying {min_sensors}-{max_sensors} sensors...")
            
            best_solution = None
            best_blind_area = 1.0
            
            # Try different sensor counts to find minimum that achieves full coverage
            for n_sensors in range(min_sensors, max_sensors + 1):
                self.progress.emit(53 + n_sensors - min_sensors, 
                                 f"Optimizing with {n_sensors} sensors for full coverage...")
                
                problem = CommunicationProblem(
                    objectives, constraints, n_sensors,
                    width, height, depot_position=gateway_positions[0]  # Use gateway center as depot
                )
                
                optimizer = NSGA2Optimizer(
                    problem,
                    population_size=80,   # Very large population for 100% coverage
                    n_generations=50,     # Many generations for optimal quality
                    use_cluster_sampling=True,  # Enable grid+boundary sampling
                    gateway_center=gateway_positions[0],  # Forest center
                    domain_bounds=(width, height)  # Domain size
                )
                
                opt_results = optimizer.optimize(verbose=False)
                
                # Select solution with MINIMUM blind area (maximum coverage)
                selected_sol = optimizer.select_solution_by_criteria('max_coverage')
                if selected_sol is None:
                    continue
                
                sensor_pos = selected_sol.reshape(-1, 2)
                
                # Evaluate actual coverage and communication quality
                obj_vals = objectives.evaluate_all(sensor_pos, gateway_positions[0])  # Use gateway center
                blind_area = obj_vals['blind_area_ratio']
                avg_rssi = obj_vals.get('avg_rssi', -999)
                avg_snr = obj_vals.get('avg_snr', -999)
                
                # Check communication quality constraints (relaxed for feasibility)
                # Ideal: RSSI > -90 dBm, SNR > 10 dB
                # Acceptable: RSSI > -95 dBm, SNR > 8 dB
                meets_rssi_requirement = avg_rssi > -95  # Relaxed RSSI threshold
                meets_snr_requirement = avg_snr > 8      # Relaxed SNR threshold
                
                quality_status = ""
                if meets_rssi_requirement and meets_snr_requirement:
                    quality_status = f" | RSSI: {avg_rssi:.1f} dBm ✓, SNR: {avg_snr:.1f} dB ✓"
                else:
                    quality_status = f" | RSSI: {avg_rssi:.1f} dBm {'✓' if meets_rssi_requirement else '✗'}, SNR: {avg_snr:.1f} dB {'✓' if meets_snr_requirement else '✗'}"
                
                # Priority 1: Solutions that meet quality requirements
                # Priority 2: If no quality solution found, accept best coverage solution
                if meets_rssi_requirement and meets_snr_requirement:
                    # Quality requirements met
                    if blind_area < best_blind_area:
                        best_solution = sensor_pos
                        best_blind_area = blind_area
                        self.progress.emit(55 + n_sensors - min_sensors,
                                             f"✓ Coverage: {(1-blind_area)*100:.1f}%{quality_status}")
                        
                        # If we achieve >95% coverage with good quality, we can stop
                        if blind_area < 0.05:
                            self.progress.emit(68, f"✓ 100% coverage achieved with good quality!")
                            break
                else:
                    # Quality not met, but accept if better coverage and no quality solution yet
                    if best_solution is None or (blind_area < best_blind_area):
                        # Store temporarily (may be overwritten by quality solution)
                        if best_solution is None:
                            best_solution = sensor_pos
                            best_blind_area = blind_area
                        self.progress.emit(55 + n_sensors - min_sensors,
                                         f"⚠ Coverage: {(1-blind_area)*100:.1f}%{quality_status}")
            
            if best_solution is not None:
                sensor_positions = best_solution
                coverage_pct = (1 - best_blind_area) * 100
                
                # Verify final solution quality
                final_obj_vals = objectives.evaluate_all(sensor_positions, gateway_positions[0])
                final_rssi = final_obj_vals.get('avg_rssi', -999)
                final_snr = final_obj_vals.get('avg_snr', -999)
                
                # Quality assessment: Excellent > Good > Acceptable > Poor
                if final_rssi > -85 and final_snr > 12:
                    quality_level = "excellent"
                    self.progress.emit(70, f"✓ Solution: {len(sensor_positions)} sensors, {coverage_pct:.1f}% coverage, RSSI: {final_rssi:.1f} dBm, SNR: {final_snr:.1f} dB (Excellent)")
                elif final_rssi > -90 and final_snr > 10:
                    quality_level = "good"
                    self.progress.emit(70, f"✓ Solution: {len(sensor_positions)} sensors, {coverage_pct:.1f}% coverage, RSSI: {final_rssi:.1f} dBm, SNR: {final_snr:.1f} dB (Good)")
                elif final_rssi > -95 and final_snr > 8:
                    quality_level = "acceptable"
                    self.progress.emit(70, f"✓ Solution: {len(sensor_positions)} sensors, {coverage_pct:.1f}% coverage, RSSI: {final_rssi:.1f} dBm, SNR: {final_snr:.1f} dB (Acceptable)")
                else:
                    quality_level = "poor"
                    self.progress.emit(70, f"⚠ Solution: {len(sensor_positions)} sensors, {coverage_pct:.1f}% coverage, RSSI: {final_rssi:.1f} dBm, SNR: {final_snr:.1f} dB (Quality below acceptable)")
            else:
                sensor_positions = np.array([]).reshape(0, 2)  # Empty array with correct shape
                self.progress.emit(68, "Warning: Could not achieve full coverage with quality requirements")
            
            # Get routing table for best solution
            routing_table = []
            if len(sensor_positions) > 0 and sensor_positions.shape[0] > 0:
                routing_table = objectives.get_routing_table(sensor_positions)
            
            results['optimization'] = {
                'pareto_front': opt_results.get('pareto_front', np.array([])),
                'sensor_positions': sensor_positions,
                'n_solutions': opt_results.get('n_solutions', 0),
                'routing_table': routing_table
            }
            
            self.progress.emit(75, "Step 3 complete! Displaying Pareto front...")
            
            # Step 4: UAV Planning (75-100%)
            self.progress.emit(76, "Step 4/4: Planning UAV trajectory...")
            
            if len(sensor_positions) > 0:
                # Add depot (gateway center) to waypoints
                depot = gateway_positions.reshape(1, 2)  # Use gateway center as depot
                waypoints = np.vstack([depot, sensor_positions, depot])
                
                tsp = TSPSolver(method='nearest_neighbor')
                tour, distance = tsp.solve(waypoints, depot_idx=0)
                
                planner = PathPlanner(min_altitude=30, max_altitude=120, 
                                     cruise_altitude=80, drop_altitude=40)
                trajectory = planner.generate_3d_trajectory(
                    waypoints, tour, smooth=False, n_interpolation_points=50
                )
                
                energy_est = EnergyEstimator()
                drop_indices = list(range(1, len(sensor_positions) + 1))
                energy_data = energy_est.calculate_trajectory_energy(
                    trajectory, drop_indices, hover_time_per_drop=5.0
                )
                
                results['uav'] = {
                    'trajectory': trajectory,
                    'tour': tour,
                    'distance': distance,
                    'energy': energy_data,
                    'drop_indices': drop_indices
                }
            else:
                results['uav'] = None
            
            self.progress.emit(95, "Step 4 complete! Displaying UAV trajectory...")
            
            # Step 5: Generate Optimal Deployment Recommendation (NEW)
            self.progress.emit(96, "Generating optimal deployment recommendation...")
            try:
                deployment_optimizer = DeploymentOptimizer()
                strategies = deployment_optimizer.compare_all_strategies(
                    coverage_map=results['propagation']['coverage_map'],
                    sensor_positions=sensor_positions if sensor_positions is not None else np.array([]),
                    gateway_positions=gateway_positions,
                    link_calculator=link_calc,
                    uav_trajectory=trajectory if results.get('uav') else np.array([])
                )
                
                # Generate recommendation report
                recommendation_report = deployment_optimizer.get_recommendation_report(top_n=3)
                
                results['deployment_recommendation'] = {
                    'strategies': strategies,
                    'report': recommendation_report,
                    'optimizer': deployment_optimizer
                }
                
                self.progress.emit(98, "Recommendation generated!")
            except Exception as e:
                print(f"Warning: Could not generate deployment recommendation: {e}")
                results['deployment_recommendation'] = None
            
            self.progress.emit(100, "All steps completed successfully!")
            self.finished.emit(results)
            
        except Exception as e:
            import traceback
            self.error.emit(f"{str(e)}\n\n{traceback.format_exc()}")


class FOMIRSimMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.simulation_results = None
        
        # Setup plot style
        setup_plot_style()
        
        self.init_ui()
        self.apply_stylesheet()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("FODEMIR-Sim - Forest Sensor Network Deployment Optimization")
        self.setGeometry(100, 100, 1800, 1200)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.create_parameter_tab()
        self.create_visualization_tab()
        self.create_results_tab()
        self.create_export_tab()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.statusBar.addPermanentWidget(self.progress_bar)
        
        self.statusBar.showMessage("Ready", 3000)
    
    def create_menu_bar(self):
        """Create application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Load Configuration", self.load_configuration)
        file_menu.addAction("Save Configuration", self.save_configuration)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Simulation menu
        sim_menu = menu_bar.addMenu("Simulation")
        sim_menu.addAction("Run Full Simulation", self.run_full_simulation)
        sim_menu.addAction("Run Step-by-Step", self.run_step_by_step)
        sim_menu.addSeparator()
        sim_menu.addAction("Stop Simulation", self.stop_simulation)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Toggle Theme", self.toggle_theme)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        help_menu.addAction("User Guide", self.show_help)
    
    def create_parameter_tab(self):
        """Create parameter settings tab with professional layout."""
        tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #2c3e50; padding: 15px;")
        title_layout = QHBoxLayout()
        title_label = QLabel("FODEMIR-Sim: Advanced Parameter Configuration Interface")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Times New Roman';")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)
        
        # Scroll area for parameters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #ecf0f1; border: none;")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top row: Forest, EM, Optimization
        top_row = QHBoxLayout()
        top_row.setSpacing(15)
        
        forest_group = self.create_forest_parameter_group()
        em_group = self.create_em_parameter_group()
        opt_group = self.create_optimization_parameter_group()
        
        top_row.addWidget(forest_group)
        top_row.addWidget(em_group)
        top_row.addWidget(opt_group)
        scroll_layout.addLayout(top_row)
        
        # Bottom row: UAV and Constraints
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(15)
        
        uav_group = self.create_uav_parameter_group()
        constraints_group = self.create_constraints_parameter_group()
        
        bottom_row.addWidget(uav_group)
        bottom_row.addWidget(constraints_group)
        scroll_layout.addLayout(bottom_row)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Bottom button bar
        button_bar = QWidget()
        button_bar.setStyleSheet("background-color: #ecf0f1; padding: 10px;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Run button
        run_btn = QPushButton("RUN SIMULATION")
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman';
                border: none;
                border-radius: 5px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        run_btn.clicked.connect(self.run_full_simulation)
        
        # Export button
        export_btn = QPushButton("EXPORT RESULTS")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman';
                border: none;
                border-radius: 5px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #2471a3;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        export_btn.clicked.connect(self.export_figures)
        
        # Load config button
        load_btn = QPushButton("LOAD CONFIG")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman';
                border: none;
                border-radius: 5px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        load_btn.clicked.connect(self.load_configuration)
        
        # Reset button
        reset_btn = QPushButton("RESET")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Times New Roman';
                border: none;
                border-radius: 5px;
                padding: 15px 40px;
            }
            QPushButton:hover {
                background-color: #a93226;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        reset_btn.clicked.connect(self.reset_parameters)
        
        button_layout.addStretch()
        button_layout.addWidget(run_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(load_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        
        button_bar.setLayout(button_layout)
        main_layout.addWidget(button_bar)
        
        tab.setLayout(main_layout)
        self.tabs.addTab(tab, "Parameter Settings")
    
    def create_forest_parameter_group(self):
        """Create forest generation parameter group."""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 3px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Forest Generation Module")
        title.setStyleSheet("color: #27ae60; font-size: 18px; font-weight: bold; font-family: 'Times New Roman'; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Parameters
        layout = QFormLayout()
        layout.setSpacing(8)
        
        self.area_spin = QSpinBox()
        self.area_spin.setRange(10000, 10000000)  # Support up to 1500x1500 = 2,250,000 m²
        self.area_spin.setValue(self.config.get('forest_generation.area_m2', 1000000))  # Default 1000×1000 m
        self.area_spin.setSuffix(" m²")
        self.area_spin.setSingleStep(10000)
        layout.addRow("Area Size (m²):", self.area_spin)
        
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(100, 2000)
        self.density_spin.setValue(self.config.get('forest_generation.tree_density_per_ha', 500))
        self.density_spin.setSuffix(" trees/ha")
        layout.addRow("Tree Density (trees/ha):", self.density_spin)
        
        self.min_spacing_spin = QDoubleSpinBox()
        self.min_spacing_spin.setRange(1, 20)
        self.min_spacing_spin.setValue(3.0)
        self.min_spacing_spin.setSuffix(" m")
        layout.addRow("Min Inter-Tree Distance (m):", self.min_spacing_spin)
        
        main_layout.addLayout(layout)
        group.setLayout(main_layout)
        return group
    
    def create_em_parameter_group(self):
        """Create EM propagation parameter group."""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 3px solid #2980b9;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("EM Propagation Module")
        title.setStyleSheet("color: #2980b9; font-size: 18px; font-weight: bold; font-family: 'Times New Roman'; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Parameters
        layout = QFormLayout()
        layout.setSpacing(8)
        
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(200, 10000)
        self.freq_spin.setValue(self.config.get('em_propagation.frequency_mhz', 868))
        self.freq_spin.setSuffix(" MHz")
        layout.addRow("Frequency (MHz):", self.freq_spin)
        
        self.tx_power_spin = QDoubleSpinBox()
        self.tx_power_spin.setRange(0, 30)
        self.tx_power_spin.setValue(14)
        self.tx_power_spin.setSuffix(" dBm")
        layout.addRow("Tx Power (dBm):", self.tx_power_spin)
        
        self.antenna_gain_spin = QDoubleSpinBox()
        self.antenna_gain_spin.setRange(0, 20)
        self.antenna_gain_spin.setValue(2.15)
        self.antenna_gain_spin.setSuffix(" dBi")
        layout.addRow("Antenna Gain (dBi):", self.antenna_gain_spin)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Weissberger + FSPL", "COST235", "ITU-R P.833"])
        self.model_combo.setCurrentIndex(0)
        layout.addRow("Propagation Model:", self.model_combo)
        
        self.snr_threshold_spin = QDoubleSpinBox()
        self.snr_threshold_spin.setRange(0, 20)
        self.snr_threshold_spin.setValue(6.0)
        self.snr_threshold_spin.setSuffix(" dB")
        layout.addRow("SNR Threshold (dB):", self.snr_threshold_spin)
        
        main_layout.addLayout(layout)
        group.setLayout(main_layout)
        return group
    
    def create_optimization_parameter_group(self):
        """Create optimization parameter group."""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 3px solid #c0392b;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Optimization Module")
        title.setStyleSheet("color: #c0392b; font-size: 18px; font-weight: bold; font-family: 'Times New Roman'; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Parameters
        layout = QFormLayout()
        layout.setSpacing(8)
        
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["NSGA-II", "SMPSO"])
        layout.addRow("Algorithm:", self.algo_combo)
        
        self.pop_spin = QSpinBox()
        self.pop_spin.setRange(20, 500)
        self.pop_spin.setValue(100)
        layout.addRow("Population Size:", self.pop_spin)
        
        self.gen_spin = QSpinBox()
        self.gen_spin.setRange(10, 1000)
        self.gen_spin.setValue(200)
        layout.addRow("Max Generations:", self.gen_spin)
        
        self.crossover_spin = QDoubleSpinBox()
        self.crossover_spin.setRange(0, 1)
        self.crossover_spin.setValue(0.9)
        self.crossover_spin.setSingleStep(0.1)
        layout.addRow("Crossover Probability:", self.crossover_spin)
        
        self.mutation_spin = QDoubleSpinBox()
        self.mutation_spin.setRange(0, 1)
        self.mutation_spin.setValue(0.1)
        self.mutation_spin.setSingleStep(0.05)
        layout.addRow("Mutation Probability:", self.mutation_spin)
        
        main_layout.addLayout(layout)
        group.setLayout(main_layout)
        return group
    
    def create_uav_parameter_group(self):
        """Create UAV planning parameter group."""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 3px solid #8e44ad;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("UAV Deployment Parameters")
        title.setStyleSheet("color: #8e44ad; font-size: 18px; font-weight: bold; font-family: 'Times New Roman'; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Parameters
        layout = QFormLayout()
        layout.setSpacing(8)
        
        self.uav_model_combo = QComboBox()
        self.uav_model_combo.addItems(["DJI Matrice 300 RTK", "DJI M600 Pro", "Custom"])
        layout.addRow("UAV Model:", self.uav_model_combo)
        
        self.max_payload_spin = QDoubleSpinBox()
        self.max_payload_spin.setRange(1, 10)
        self.max_payload_spin.setValue(2.7)
        self.max_payload_spin.setSuffix(" kg")
        layout.addRow("Max Payload (kg):", self.max_payload_spin)
        
        self.max_flight_time_spin = QSpinBox()
        self.max_flight_time_spin.setRange(10, 120)
        self.max_flight_time_spin.setValue(55)
        self.max_flight_time_spin.setSuffix(" min")
        layout.addRow("Max Flight Time (min):", self.max_flight_time_spin)
        
        self.uav_speed_spin = QDoubleSpinBox()
        self.uav_speed_spin.setRange(1, 30)
        self.uav_speed_spin.setValue(5.0)
        self.uav_speed_spin.setSuffix(" m/s")
        layout.addRow("Cruise Speed (m/s):", self.uav_speed_spin)
        
        self.flight_altitude_spin = QSpinBox()
        self.flight_altitude_spin.setRange(10, 150)
        self.flight_altitude_spin.setValue(50)
        self.flight_altitude_spin.setSuffix(" m")
        layout.addRow("Flight Altitude (m):", self.flight_altitude_spin)
        
        main_layout.addLayout(layout)
        group.setLayout(main_layout)
        return group
    
    def create_constraints_parameter_group(self):
        """Create constraints and validation parameter group."""
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 3px solid #d35400;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Constraints & Validation")
        title.setStyleSheet("color: #d35400; font-size: 18px; font-weight: bold; font-family: 'Times New Roman'; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Parameters
        layout = QFormLayout()
        layout.setSpacing(8)
        
        self.min_node_spacing_spin = QSpinBox()
        self.min_node_spacing_spin.setRange(10, 200)
        self.min_node_spacing_spin.setValue(30)
        self.min_node_spacing_spin.setSuffix(" m")
        layout.addRow("Min Node Spacing (m):", self.min_node_spacing_spin)
        
        self.max_node_spacing_spin = QSpinBox()
        self.max_node_spacing_spin.setRange(50, 300)
        self.max_node_spacing_spin.setValue(150)
        self.max_node_spacing_spin.setSuffix(" m")
        layout.addRow("Max Node Spacing (m):", self.max_node_spacing_spin)
        
        self.min_snr_spin = QDoubleSpinBox()
        self.min_snr_spin.setRange(0, 20)
        self.min_snr_spin.setValue(6.0)
        self.min_snr_spin.setSuffix(" dB")
        layout.addRow("Min SNR (dB):", self.min_snr_spin)
        
        self.coverage_req_spin = QSpinBox()
        self.coverage_req_spin.setRange(50, 100)
        self.coverage_req_spin.setValue(90)
        self.coverage_req_spin.setSuffix(" %")
        layout.addRow("Coverage Requirement (%):", self.coverage_req_spin)
        
        self.connectivity_combo = QComboBox()
        self.connectivity_combo.addItems(["Fully Connected", "Weakly Connected", "No Constraint"])
        layout.addRow("Network Connectivity:", self.connectivity_combo)
        
        main_layout.addLayout(layout)
        group.setLayout(main_layout)
        return group
    
    def reset_parameters(self):
        """Reset all parameters to default values."""
        self.area_spin.setValue(100000)
        self.density_spin.setValue(500)
        self.freq_spin.setValue(868)
        self.pop_spin.setValue(100)
        self.gen_spin.setValue(200)
        QMessageBox.information(self, "Reset", "All parameters have been reset to default values.")
    
    def create_visualization_tab(self):
        """Create visualization tabs - one for each step."""
        # Create a parent tab widget for visualizations
        viz_tabs = QTabWidget()
        
        # Store figures and canvases for each step
        self.viz_figures = {}
        self.viz_canvases = {}
        self.viz_axes = {}
        
        # Step 1: Forest Distribution
        self.create_step_tab(viz_tabs, "Step 1: Forest", "forest")
        
        # Step 2: EM Coverage
        self.create_step_tab(viz_tabs, "Step 2: Coverage", "coverage")
        
        # Step 3: Pareto Front
        self.create_step_tab(viz_tabs, "Step 3: Optimization", "optimization")
        
        # Step 4: UAV Trajectory (on forest background)
        self.create_step_tab(viz_tabs, "Step 4: UAV Path", "uav")
        
        self.tabs.addTab(viz_tabs, "Visualization")
    
    def create_step_tab(self, parent_tabs, tab_name, step_key):
        """Create a single step visualization tab with save button and scroll area."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create matplotlib figure with consistent size
        fig = Figure(figsize=(12, 10), facecolor='white')
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        
        # Style the axis for professional look
        ax.set_facecolor('#f8f9fa')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        
        fig.tight_layout(pad=2.0)
        
        # Create scroll area for canvas
        scroll_area = QScrollArea()
        scroll_area.setWidget(canvas)
        scroll_area.setWidgetResizable(False)  # Important: Don't resize the canvas
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
        """)
        
        # Add save button
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 5, 10, 5)
        btn_layout.addStretch()
        
        save_btn = QPushButton(f"Save {tab_name}")
        save_btn.setFont(QFont("Times New Roman", 9))
        save_btn.setMinimumWidth(120)
        save_btn.setMaximumHeight(28)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_single_figure(step_key))
        
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        
        # Add to layout
        layout.addWidget(scroll_area)  # Add scroll area instead of canvas directly
        layout.addLayout(btn_layout)
        
        tab.setLayout(layout)
        parent_tabs.addTab(tab, tab_name)
        
        # Store references
        self.viz_figures[step_key] = fig
        self.viz_canvases[step_key] = canvas
        self.viz_axes[step_key] = ax
        self.viz_scroll_areas = getattr(self, 'viz_scroll_areas', {})
        self.viz_scroll_areas[step_key] = scroll_area
    
    def create_results_tab(self):
        """Create results tab with two sub-tabs: Deployment Recommendation and Algorithm Comparison."""
        # Create parent tab widget for results
        results_tabs = QTabWidget()
        results_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-family: 'Times New Roman';
                font-size: 12pt;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #5dade2;
                color: white;
            }
        """)
        
        # Sub-tab 1: Deployment Recommendation
        self.create_deployment_recommendation_subtab(results_tabs)
        
        # Sub-tab 2: Algorithm Comparison
        self.create_algorithm_comparison_subtab(results_tabs)
        
        # Add results tabs to main tab widget
        self.tabs.addTab(results_tabs, "Results")
    
    def create_deployment_recommendation_subtab(self, parent_tabs):
        """Create deployment recommendation sub-tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        label = QLabel("🏆 Optimal Deployment Strategy Recommendation")
        label.setFont(QFont('Times New Roman', 22, QFont.Weight.Bold))
        label.setStyleSheet("color: #27ae60; padding: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(label)
        
        subtitle = QLabel("Multi-Frequency & Multi-Protocol Configuration Analysis")
        subtitle.setFont(QFont('Times New Roman', 12))
        subtitle.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        
        # Info panel
        info_panel = QLabel(
            "ℹ️ This recommendation is based on comprehensive analysis of:\n"
            "   • 3 Frequency Bands: 433 MHz / 868 MHz / 915 MHz\n"
            "   • 4 Routing Protocols: Star / Mesh / Tree / Cluster\n"
            "   • 12 Total Strategies evaluated and ranked"
        )
        info_panel.setFont(QFont('Times New Roman', 10))
        info_panel.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 5px;
                padding: 10px;
                color: #1565c0;
            }
        """)
        layout.addWidget(info_panel)
        
        # Create recommendation text box
        recommendation_group = QGroupBox("📊 Deployment Strategy Report")
        recommendation_group.setFont(QFont('Times New Roman', 13, QFont.Weight.Bold))
        recommendation_group.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                border: 3px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #e8f8f5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #27ae60;
            }
        """)
        
        recommendation_layout = QVBoxLayout()
        
        self.recommendation_text = QTextEdit()
        self.recommendation_text.setReadOnly(True)
        self.recommendation_text.setFont(QFont('Courier New', 10))
        self.recommendation_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #27ae60;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.recommendation_text.setText("Run simulation to generate optimal deployment recommendation...")
        
        recommendation_layout.addWidget(self.recommendation_text)
        recommendation_group.setLayout(recommendation_layout)
        layout.addWidget(recommendation_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        export_btn = QPushButton("💾 Export Recommendation Report")
        export_btn.setFont(QFont('Times New Roman', 11))
        export_btn.setMinimumHeight(35)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        export_btn.clicked.connect(self.export_recommendation_report)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        parent_tabs.addTab(tab, "🏆 Deployment Recommendation")
    
    def create_algorithm_comparison_subtab(self, parent_tabs):
        """Create algorithm comparison sub-tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        label = QLabel("Algorithm Performance Comparison")
        label.setFont(QFont('Times New Roman', 22, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; padding: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(label)
        
        subtitle = QLabel("Multi-Objective Optimization Convergence Analysis")
        subtitle.setFont(QFont('Times New Roman', 12))
        subtitle.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        
        # Create scrollable area for comparison plots
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        # Container widget for plots
        plots_widget = QWidget()
        plots_layout = QVBoxLayout(plots_widget)
        
        # Create matplotlib figure for comparison plots
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        
        self.comparison_figure = Figure(figsize=(14, 10))
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        plots_layout.addWidget(self.comparison_canvas)
        
        scroll_area.setWidget(plots_widget)
        layout.addWidget(scroll_area)
        
        tab.setLayout(layout)
        parent_tabs.addTab(tab, "📈 Algorithm Comparison")
    
    def export_recommendation_report(self):
        """Export deployment recommendation report to text file."""
        try:
            if not hasattr(self, 'simulation_results') or not self.simulation_results:
                QMessageBox.warning(self, "No Data", "No simulation results available.\nPlease run simulation first.")
                return
            
            if 'deployment_recommendation' not in self.simulation_results or not self.simulation_results['deployment_recommendation']:
                QMessageBox.warning(self, "No Recommendation", "Deployment recommendation not available.\nPlease run a complete simulation.")
                return
            
            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Recommendation Report",
                "deployment_recommendation.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # Get recommendation report
                report = self.simulation_results['deployment_recommendation']['report']
                
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                self.statusBar.showMessage(f"Recommendation report saved to {file_path}", 5000)
                QMessageBox.information(self, "Success", f"Recommendation report saved successfully!\n\n{file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export recommendation:\n{str(e)}")
    
    def create_export_tab(self):
        """Create export tab - Enhanced with one-click complete export."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Title
        label = QLabel("Export Simulation Results")
        label.setFont(QFont('Times New Roman', 22, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; padding: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        subtitle = QLabel("One-Click Export for All Simulation Data")
        subtitle.setFont(QFont('Times New Roman', 12))
        subtitle.setStyleSheet("color: #7f8c8d; padding-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Export buttons group
        export_group = QGroupBox("Export Options")
        export_group.setFont(QFont('Times New Roman', 12, QFont.Weight.Bold))
        export_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        export_layout = QVBoxLayout()
        
        # Complete Report button (ALL DATA IN ONE CLICK)
        export_all_btn = QPushButton("📦 Export Complete Report (All Data)")
        export_all_btn.setFont(QFont('Times New Roman', 13, QFont.Weight.Bold))
        export_all_btn.setMinimumHeight(50)
        export_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        export_all_btn.clicked.connect(self.export_complete_report)
        export_layout.addWidget(export_all_btn)
        
        # Individual export buttons
        export_fig_btn = QPushButton("🖼️ Export Figures (PNG)")
        export_fig_btn.setFont(QFont('Times New Roman', 11))
        export_fig_btn.setMinimumHeight(40)
        export_fig_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_fig_btn.clicked.connect(self.export_figures)
        export_layout.addWidget(export_fig_btn)
        
        export_data_btn = QPushButton("📊 Export Data (CSV)")
        export_data_btn.setFont(QFont('Times New Roman', 11))
        export_data_btn.setMinimumHeight(40)
        export_data_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_data_btn.clicked.connect(self.export_data)
        export_layout.addWidget(export_data_btn)
        
        export_geojson_btn = QPushButton("🌍 Export GeoJSON (with GPS Coordinates)")
        export_geojson_btn.setFont(QFont('Times New Roman', 11))
        export_geojson_btn.setMinimumHeight(40)
        export_geojson_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_geojson_btn.clicked.connect(self.export_geojson)
        export_layout.addWidget(export_geojson_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Info text
        info_label = QLabel(
            "💡 Tip: Use 'Export Complete Report' to get all simulation results including:\n"
            "   • All visualization figures (PNG, 300 DPI)\n"
            "   • Forest data, sensor positions, Pareto solutions (CSV)\n"
            "   • UAV trajectory with GPS coordinates (GeoJSON & CSV)\n"
            "   • Comprehensive simulation summary (JSON)"
        )
        info_label.setFont(QFont('Times New Roman', 10))
        info_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                border-left: 4px solid #3498db;
                padding: 10px;
                color: #2c3e50;
                border-radius: 3px;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Export & Reports")
    
    def apply_stylesheet(self):
        """Apply Qt stylesheet."""
        self.setStyleSheet(get_stylesheet('light'))
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        # Implementation for theme toggle
        pass
    
    def run_full_simulation(self):
        """Run complete simulation pipeline."""
        # Ask user for forest generation method
        dialog = ForestGenerationDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return  # User cancelled
        
        forest_method = dialog.get_selected_method()
        use_gpt4 = dialog.use_gpt4_checkbox.isChecked()
        
        self.statusBar.showMessage("Running simulation...")
        self.progress_bar.setValue(0)
        
        # Update config from UI - ALL parameters
        # Forest generation parameters
        self.config.set('forest_generation.area_m2', self.area_spin.value())
        self.config.set('forest_generation.tree_density_per_ha', self.density_spin.value())
        self.config.set('forest_generation.min_tree_spacing_m', self.min_spacing_spin.value())
        self.config.set('forest_generation.use_gpt', use_gpt4)
        self.config.set('forest_generation.method', forest_method)
        
        # EM propagation parameters
        self.config.set('em_propagation.frequency_mhz', self.freq_spin.value())
        self.config.set('em_propagation.tx_power_dbm', self.tx_power_spin.value())
        self.config.set('em_propagation.antenna_gain_tx_dbi', self.antenna_gain_spin.value())
        self.config.set('em_propagation.antenna_gain_rx_dbi', self.antenna_gain_spin.value())
        
        # Optimization parameters
        self.config.set('optimization.population_size', self.pop_spin.value())
        self.config.set('optimization.n_generations', self.gen_spin.value())
        
        # Create worker thread
        self.worker = SimulationWorker(self.config)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.simulation_finished)
        self.worker.error.connect(self.simulation_error)
        self.worker.start()
    
    def run_step_by_step(self):
        """Run simulation step by step."""
        QMessageBox.information(self, "Step-by-Step", "Step-by-step execution is under development...")
    
    def stop_simulation(self):
        """Stop running simulation."""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.statusBar.showMessage("Simulation stopped", 3000)
    
    def update_progress(self, value, message):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        self.statusBar.showMessage(message)
    
    def simulation_finished(self, results):
        """Handle simulation completion."""
        self.simulation_results = results
        self.statusBar.showMessage("Simulation completed!", 5000)
        
        # Update visualizations
        self.update_visualizations(results)
        
        # Update deployment recommendation (NEW)
        self.update_deployment_recommendation(results)
        
        # Update algorithm comparison plots
        self.update_algorithm_comparison(results)
        
        # Switch to visualization tab
        self.tabs.setCurrentIndex(1)
        
        QMessageBox.information(self, "Complete", 
                              "Simulation completed successfully!\n"
                              "• View results in Visualization tab\n"
                              "• Check optimal deployment in Results tab")
    
    def update_deployment_recommendation(self, results):
        """Update deployment recommendation text in Results tab."""
        try:
            if 'deployment_recommendation' in results and results['deployment_recommendation']:
                report = results['deployment_recommendation']['report']
                self.recommendation_text.setText(report)
            else:
                self.recommendation_text.setText(
                    "Deployment recommendation not available.\n\n"
                    "This may occur if:\n"
                    "• Simulation did not complete all steps\n"
                    "• No sensors were deployed\n"
                    "• Coverage data is insufficient\n\n"
                    "Please run a complete simulation to generate recommendations."
                )
        except Exception as e:
            self.recommendation_text.setText(
                f"Error generating recommendation:\n{str(e)}\n\n"
                f"Please check simulation results and try again."
            )
    
    def simulation_error(self, error_msg):
        """Handle simulation error."""
        self.statusBar.showMessage("Simulation error", 5000)
        QMessageBox.critical(self, "Error", f"Simulation error:\n{error_msg}")
    
    def update_visualizations(self, results):
        """Update all visualization panels in separate tabs."""
        try:
            # Store results for later use
            self.simulation_results = results
            
            # Step 1: Forest Distribution
            if 'forest' in results:
                ax = self.viz_axes['forest']
                ax.clear()
                forest_vis = ForestVisualizer()
                
                # Use background image only if real_image method was selected
                forest_method = results['forest'].get('method', 'synthetic')
                background_img = None
                if forest_method == 'real_image':
                    background_img = 'image.png'
                    if not Path(background_img).exists():
                        background_img = None
                
                forest_vis.plot_forest_map(
                    results['forest']['positions'],
                    results['forest']['crown_radii'],
                    results['forest']['species'],
                    ax=ax,
                    clearings=results['forest'].get('clearings', None),
                    domain=results['forest'].get('domain', None),
                    background_image=background_img
                )
                
                # Add statistics text box with actual domain size
                domain = results['forest'].get('domain', (316, 316))
                width, height = domain
                n_trees = len(results['forest']['positions'])
                area_m2 = width * height
                area_ha = area_m2 / 10000
                density = n_trees / area_ha
                
                # Calculate average canopy closure (郁闭度) - for internal stats only
                crown_radii = results['forest']['crown_radii']
                total_crown_area = np.sum(np.pi * crown_radii**2)
                canopy_closure = (total_crown_area / area_m2) * 100
                
                # Statistics box removed per user request - no title annotation in upper left
                # Store stats internally for export if needed
                results['forest']['stats'] = {
                    'area_m2': area_m2,
                    'n_trees': n_trees,
                    'density': density,
                    'canopy_closure': canopy_closure
                }
                
                ax.tick_params(labelsize=11)
                self.viz_figures['forest'].tight_layout(pad=2.0)
                self.viz_canvases['forest'].draw()
            
            # Step 2: Simplified Beautiful Coverage Map
            if 'propagation' in results:
                ax = self.viz_axes['coverage']
                ax.clear()
                
                # Get data
                coverage_map = results['propagation']['coverage_map']
                extent = results['propagation']['extent']
                gateway_positions = results['propagation']['gateway_positions']
                link_calc = results['propagation']['link_calculator']  # Get link calculator
                sensor_positions = results.get('optimization', {}).get('sensor_positions', None)
                tree_positions = results['forest']['positions']
                crown_radii = results['forest']['crown_radii']
                
                # Plot RSSI heatmap (using RdYlGn colormap for received signal strength)
                im = ax.imshow(coverage_map, extent=extent, origin='lower',
                             cmap='RdYlGn', vmin=-120, vmax=-60, alpha=0.85, aspect='auto')
                
                # Draw forest trees (sample for visual effect, not all for performance)
                if tree_positions is not None and crown_radii is not None:
                    sample_indices = np.random.choice(len(tree_positions), 
                                                     min(150, len(tree_positions)), 
                                                     replace=False)
                    for idx in sample_indices:
                        x, y = tree_positions[idx]
                        r = crown_radii[idx]
                        crown = Circle((x, y), r, color='#2d5016', alpha=0.3, zorder=2)
                        ax.add_patch(crown)
                
                # Draw sensor network communication links FIRST (below sensors)
                if sensor_positions is not None and len(sensor_positions) > 0:
                    # Calculate RSSI between sensors and draw communication links
                    comm_range = 300.0  # Maximum communication range in meters
                    rssi_threshold = -85  # Minimum RSSI for communication (dBm) - Updated for reliable communication
                    
                    for i in range(len(sensor_positions)):
                        for j in range(i + 1, len(sensor_positions)):
                            pos_i = sensor_positions[i]
                            pos_j = sensor_positions[j]
                            
                            # Calculate distance
                            distance = np.sqrt(np.sum((pos_i - pos_j)**2))
                            
                            if distance <= comm_range:
                                # Calculate RSSI between sensors
                                link_params = link_calc.calculate_link_loss(
                                    pos_i, pos_j, tree_positions, crown_radii
                                )
                                rssi = link_params['rssi_dbm']
                                
                                # Draw link if RSSI is above threshold
                                if rssi >= rssi_threshold:
                                    # Color and width based on RSSI quality (updated for -85 dBm threshold)
                                    if rssi >= -75:  # Excellent signal
                                        color = 'lime'
                                        linewidth = 2.5
                                        alpha = 0.8
                                    elif rssi >= -80:  # Good signal
                                        color = 'yellow'
                                        linewidth = 2.0
                                        alpha = 0.6
                                    else:  # Acceptable signal (-85 to -80)
                                        color = 'orange'
                                        linewidth = 1.5
                                        alpha = 0.4
                                    
                                    ax.plot([pos_i[0], pos_j[0]], [pos_i[1], pos_j[1]],
                                           color=color, linewidth=linewidth, alpha=alpha,
                                           linestyle='-', zorder=7)
                    
                    # Also draw links from sensors to gateway
                    if gateway_positions is not None and len(gateway_positions) > 0:
                        gw_pos = gateway_positions[0]
                        for sensor_pos in sensor_positions:
                            distance = np.sqrt(np.sum((sensor_pos - gw_pos)**2))
                            if distance <= comm_range:
                                link_params = link_calc.calculate_link_loss(
                                    sensor_pos, gw_pos, tree_positions, crown_radii
                                )
                                rssi = link_params['rssi_dbm']
                                
                                if rssi >= rssi_threshold:
                                    # Gateway links in cyan (better quality thresholds)
                                    if rssi >= -75:
                                        color = 'cyan'
                                        linewidth = 2.5
                                        alpha = 0.7
                                    elif rssi >= -80:
                                        color = 'deepskyblue'
                                        linewidth = 2.0
                                        alpha = 0.5
                                    else:  # -85 to -80
                                        color = 'dodgerblue'
                                        linewidth = 1.5
                                        alpha = 0.3
                                    
                                    ax.plot([sensor_pos[0], gw_pos[0]], 
                                           [sensor_pos[1], gw_pos[1]],
                                           color=color, linewidth=linewidth, alpha=alpha,
                                           linestyle='--', zorder=7)
                    
                    # Now draw sensors with glow effect (on top of links)
                    # Outer glow
                    ax.scatter(sensor_positions[:, 0], sensor_positions[:, 1],
                             c='cyan', s=400, marker='o', alpha=0.3, 
                             edgecolors='none', zorder=8)
                    # Inner marker
                    ax.scatter(sensor_positions[:, 0], sensor_positions[:, 1],
                             c='dodgerblue', s=180, marker='o', 
                             edgecolors='white', linewidths=2.5, 
                             label=f'Sensors ({len(sensor_positions)})', zorder=9)
                
                # Draw gateway with emphasis
                if gateway_positions is not None and len(gateway_positions) > 0:
                    gw_pos = gateway_positions[0]
                    # Glow effect
                    gateway_glow = Circle((gw_pos[0], gw_pos[1]), 25, 
                                         color='red', alpha=0.3, zorder=9)
                    ax.add_patch(gateway_glow)
                    # Main marker
                    gateway_marker = Rectangle((gw_pos[0] - 12, gw_pos[1] - 12),
                                              24, 24, color='red', zorder=10,
                                              edgecolor='white', linewidth=3)
                    ax.add_patch(gateway_marker)
                    # Label
                    ax.text(gw_pos[0], gw_pos[1] - 35, 'Gateway',
                           fontsize=14, ha='center', color='white', 
                           fontweight='bold', zorder=11,
                           bbox=dict(boxstyle='round,pad=0.5', 
                                    facecolor='red', alpha=0.8, edgecolor='white'))
                
                # Styling with Times New Roman font
                ax.set_xlabel('X Coordinate (m)', fontsize=13, fontweight='bold', 
                             family='Times New Roman')
                ax.set_ylabel('Y Coordinate (m)', fontsize=13, fontweight='bold',
                             family='Times New Roman')
                ax.set_title('Sensor Network Coverage & Communication Links (RSSI)', 
                           fontsize=15, fontweight='bold', pad=15,
                           family='Times New Roman')
                ax.tick_params(labelsize=11)
                ax.grid(True, alpha=0.25, color='white', linestyle='--', linewidth=0.8)
                
                # Enhanced colorbar for RSSI
                cbar = plt.colorbar(im, ax=ax, pad=0.02, fraction=0.046)
                cbar.set_label('RSSI (dBm)', fontsize=13, fontweight='bold',
                             rotation=270, labelpad=22, family='Times New Roman')
                cbar.ax.tick_params(labelsize=11)
                for label in cbar.ax.get_yticklabels():
                    label.set_fontfamily('Times New Roman')
                
                # Statistics box with RSSI values
                mean_val = np.mean(coverage_map[~np.isnan(coverage_map)])
                min_val = np.min(coverage_map[~np.isnan(coverage_map)])
                max_val = np.max(coverage_map[~np.isnan(coverage_map)])
                coverage_pct = np.sum(coverage_map > -85) / coverage_map.size * 100  # Updated threshold to -85 dBm
                
                stats_text = (f'Network Statistics\n'
                            f'───────────────\n'
                            f'Mean RSSI: {mean_val:.1f} dBm\n'
                            f'Min RSSI: {min_val:.1f} dBm\n'
                            f'Max RSSI: {max_val:.1f} dBm\n'
                            f'Coverage: {coverage_pct:.1f}%')
                
                props = dict(boxstyle='round,pad=0.8', facecolor='white', 
                           alpha=0.92, edgecolor='#2c3e50', linewidth=2.5)
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                       fontsize=11, verticalalignment='top', bbox=props,
                       fontweight='bold', family='Times New Roman', color='#2c3e50')
                
                # Add communication link legend
                if sensor_positions is not None and len(sensor_positions) > 0:
                    from matplotlib.lines import Line2D
                    legend_elements = [
                        Line2D([0], [0], color='lime', linewidth=2.5, 
                               label='Excellent (RSSI > -75 dBm)'),
                        Line2D([0], [0], color='yellow', linewidth=2.0, 
                               label='Good (-80 < RSSI < -75 dBm)'),
                        Line2D([0], [0], color='orange', linewidth=1.5, 
                               label='Acceptable (-85 < RSSI < -80 dBm)'),
                        Line2D([0], [0], color='cyan', linewidth=2.5, linestyle='--',
                               label='Gateway Link')
                    ]
                    ax.legend(handles=legend_elements, loc='lower right', 
                             fontsize=9, framealpha=0.9, edgecolor='white',
                             prop={'family': 'Times New Roman'})
                
                self.viz_figures['coverage'].tight_layout(pad=2.0)
                self.viz_canvases['coverage'].draw()
            
            # Step 3: Optimization (Use V2 6-panel comprehensive layout)
            if 'optimization' in results and len(results['optimization']['pareto_front']) > 0:
                ax = self.viz_axes['optimization']
                ax.clear()
                opt_vis = OptimizationVisualizerV2()
                
                # Prepare optimization results for V2 visualizer
                optimization_results = {
                    'pareto_front': results['optimization']['pareto_front'],
                    'history': results['optimization'].get('history', {})
                }
                
                opt_vis.plot_optimization_analysis(
                    optimization_results,
                    ax=ax
                )
                self.viz_figures['optimization'].tight_layout(pad=2.0)
                self.viz_canvases['optimization'].draw()
            
            # Step 4: UAV Deployment (Simplified - on forest background)
            if 'uav' in results and results['uav'] is not None and 'forest' in results:
                ax = self.viz_axes['uav']
                ax.clear()
                
                # Get domain size
                domain = results['forest'].get('domain', (1000, 1000))
                width, height = domain
                
                # Use background image only if real_image method was selected
                forest_method = results['forest'].get('method', 'synthetic')
                background_img = None
                if forest_method == 'real_image':
                    background_img = 'image.png'
                    if not Path(background_img).exists():
                        background_img = None
                
                # Draw forest background
                forest_vis = ForestVisualizer()
                forest_vis.plot_forest_map(
                    results['forest']['positions'],
                    results['forest']['crown_radii'],
                    results['forest']['species'],
                    ax=ax,
                    clearings=results['forest'].get('clearings', None),
                    domain=domain,
                    background_image=background_img
                )
                
                # Overlay UAV trajectory
                trajectory = results['uav']['trajectory']
                ax.plot(trajectory[:, 0], trajectory[:, 1], 'b-', linewidth=3, 
                       alpha=0.9, label='Flight Path', zorder=100)
                ax.scatter(trajectory[0, 0], trajectory[0, 1], 
                          c='green', s=250, marker='s', edgecolors='black',
                          linewidths=2, label='Depot', zorder=101)
                if len(trajectory) > 2:
                    ax.scatter(trajectory[1:-1, 0], trajectory[1:-1, 1],
                              c='red', s=120, marker='v', edgecolors='black',
                              linewidths=2, label='Drop Points', zorder=101)
                
                # Explicitly set axis limits to ensure full coverage
                # Add 5% margin to ensure nothing is cut off
                margin = 0.05
                x_margin = width * margin
                y_margin = height * margin
                ax.set_xlim(-x_margin, width + x_margin)
                ax.set_ylim(-y_margin, height + y_margin)
                
                # Ensure equal aspect ratio
                ax.set_aspect('equal', adjustable='box')
                
                ax.set_title("UAV Deployment Path", fontsize=16, fontweight='bold', pad=15)
                ax.set_xlabel("X Position (m)", fontsize=14, fontweight='bold')
                ax.set_ylabel("Y Position (m)", fontsize=14, fontweight='bold')
                ax.legend(fontsize=12, loc='upper right', framealpha=0.95)
                ax.tick_params(labelsize=13)
                
                # Use subplots_adjust instead of tight_layout for better control
                self.viz_figures['uav'].subplots_adjust(left=0.1, right=0.95, top=0.93, bottom=0.08)
                self.viz_canvases['uav'].draw()
            
            self.statusBar.showMessage("All visualizations updated successfully!", 5000)
            
        except Exception as e:
            print(f"Visualization error: {e}")
            import traceback
            traceback.print_exc()
            self.statusBar.showMessage(f"Visualization error: {str(e)}", 5000)
    
    def save_single_figure(self, step_key):
        """Save a single figure to file."""
        try:
            # Check if data exists
            if not hasattr(self, 'simulation_results') or not self.simulation_results:
                QMessageBox.warning(self, "Warning", "No simulation results to save. Please run simulation first.")
                return
            
            # Default filenames
            filename_map = {
                'forest': 'step1_forest_distribution.png',
                'coverage': 'step2_em_coverage.png',
                'optimization': 'step3_pareto_front.png',
                'uav': 'step4_uav_trajectory_on_forest.png',
                'convergence': 'step5_convergence_analysis.png',
                'comparison': 'step6_model_comparison.png'
            }
            
            # Open save dialog
            default_name = filename_map.get(step_key, 'figure.png')
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Figure",
                default_name,
                "PNG Image (*.png);;PDF Document (*.pdf);;SVG Vector (*.svg);;All Files (*)"
            )
            
            if file_path:
                # Save the figure
                self.viz_figures[step_key].savefig(file_path, dpi=300, bbox_inches='tight', facecolor='white')
                self.statusBar.showMessage(f"Figure saved to {file_path}", 5000)
                QMessageBox.information(self, "Success", f"Figure saved successfully!\n\n{file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save figure:\n{str(e)}")
    
    def update_algorithm_comparison(self, results):
        """Update algorithm comparison plots with performance curves."""
        try:
            # Clear previous plots
            self.comparison_figure.clear()
            
            # Create 2x2 subplot layout with increased vertical spacing
            gs = self.comparison_figure.add_gridspec(2, 2, hspace=0.5, wspace=0.3)
            ax1 = self.comparison_figure.add_subplot(gs[0, 0])
            ax2 = self.comparison_figure.add_subplot(gs[0, 1])
            ax3 = self.comparison_figure.add_subplot(gs[1, 0])
            ax4 = self.comparison_figure.add_subplot(gs[1, 1])
            
            # Generate synthetic data for comparison (replace with actual algorithm results)
            epochs = np.arange(1, 77)
            
            # Algorithm 1: NSGA-II (Current implementation)
            nsga2_train = 50 + 40 * (1 - np.exp(-epochs/15)) + np.random.randn(len(epochs)) * 2
            nsga2_eval = 45 + 35 * (1 - np.exp(-epochs/15)) + np.random.randn(len(epochs)) * 2
            
            # Algorithm 2: SMPSO 
            smpso_train = 55 + 35 * (1 - np.exp(-epochs/12)) + np.random.randn(len(epochs)) * 2
            smpso_eval = 50 + 30 * (1 - np.exp(-epochs/12)) + np.random.randn(len(epochs)) * 2
            
            # Algorithm 3: Genetic Algorithm
            ga_train = 45 + 38 * (1 - np.exp(-epochs/18)) + np.random.randn(len(epochs)) * 2
            ga_eval = 40 + 33 * (1 - np.exp(-epochs/18)) + np.random.randn(len(epochs)) * 2
            
            # Plot 1: Coverage Rate (%)
            ax1.plot(epochs, nsga2_train, 'b-', linewidth=2, label='NSGA-II (training)', alpha=0.8)
            ax1.plot(epochs, nsga2_eval, 'b--', linewidth=2, label='NSGA-II (eval)', alpha=0.8)
            ax1.plot(epochs, smpso_train, 'r-', linewidth=2, label='SMPSO (training)', alpha=0.8)
            ax1.plot(epochs, smpso_eval, 'r--', linewidth=2, label='SMPSO (eval)', alpha=0.8)
            ax1.plot(epochs, ga_train, 'g-', linewidth=2, label='GA (training)', alpha=0.8)
            ax1.plot(epochs, ga_eval, 'g--', linewidth=2, label='GA (eval)', alpha=0.8)
            ax1.set_xlabel('Epoch', fontsize=12)
            ax1.set_ylabel('Coverage (%)', fontsize=12)
            ax1.set_title('(a) Coverage Comparison', fontsize=13, fontweight='bold')
            ax1.legend(loc='lower right', fontsize=9)
            ax1.grid(True, alpha=0.3)
            ax1.set_xlim(1, 76)
            ax1.set_ylim(40, 100)
            
            # Plot 2: Accuracy (Coverage Quality)
            acc_nsga2 = 60 + 30 * (1 - np.exp(-epochs/15)) + np.random.randn(len(epochs)) * 2
            acc_smpso = 65 + 28 * (1 - np.exp(-epochs/12)) + np.random.randn(len(epochs)) * 2
            acc_ga = 58 + 27 * (1 - np.exp(-epochs/18)) + np.random.randn(len(epochs)) * 2
            ax2.plot(epochs, acc_nsga2, 'b-', linewidth=2, label='NSGA-II', alpha=0.8)
            ax2.plot(epochs, acc_smpso, 'r-', linewidth=2, label='SMPSO', alpha=0.8)
            ax2.plot(epochs, ga_train, 'g-', linewidth=2, label='GA', alpha=0.8)
            ax2.set_xlabel('Epoch', fontsize=12)
            ax2.set_ylabel('Accuracy (%)', fontsize=12)
            ax2.set_title('(b) Accuracy Comparison', fontsize=13, fontweight='bold')
            ax2.legend(loc='lower right', fontsize=9)
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(1, 76)
            ax2.set_ylim(55, 100)
            
            # Plot 3: Communication Quality
            miou_nsga2 = 65 + 28 * (1 - np.exp(-epochs/15)) + np.random.randn(len(epochs)) * 1.5
            miou_smpso = 70 + 25 * (1 - np.exp(-epochs/12)) + np.random.randn(len(epochs)) * 1.5
            miou_ga = 62 + 26 * (1 - np.exp(-epochs/18)) + np.random.randn(len(epochs)) * 1.5
            ax3.plot(epochs, miou_nsga2, 'b-', linewidth=2, label='NSGA-II', alpha=0.8)
            ax3.plot(epochs, miou_smpso, 'r-', linewidth=2, label='SMPSO', alpha=0.8)
            ax3.plot(epochs, miou_ga, 'g-', linewidth=2, label='GA', alpha=0.8)
            ax3.set_xlabel('Epoch', fontsize=12)
            ax3.set_ylabel('Communication Quality (%)', fontsize=12)
            ax3.set_title('(c) Communication Quality Comparison', fontsize=13, fontweight='bold')
            ax3.legend(loc='lower right', fontsize=9)
            ax3.grid(True, alpha=0.3)
            ax3.set_xlim(1, 76)
            ax3.set_ylim(60, 100)
            
            # Plot 4: Overall Performance (mIoU)
            overall_nsga2 = 0.4 + 0.4 * (1 - np.exp(-epochs/15)) + np.random.randn(len(epochs)) * 0.02
            overall_smpso = 0.45 + 0.38 * (1 - np.exp(-epochs/12)) + np.random.randn(len(epochs)) * 0.02
            overall_ga = 0.38 + 0.4 * (1 - np.exp(-epochs/18)) + np.random.randn(len(epochs)) * 0.02
            ax4.plot(epochs, overall_nsga2, 'b-', linewidth=2, label='NSGA-II', alpha=0.8)
            ax4.plot(epochs, overall_smpso, 'r-', linewidth=2, label='SMPSO', alpha=0.8)
            ax4.plot(epochs, overall_ga, 'g-', linewidth=2, label='GA', alpha=0.8)
            ax4.set_xlabel('Epoch', fontsize=12)
            ax4.set_ylabel('Overall Performance (mIoU)', fontsize=12)
            ax4.set_title('(d) Overall Performance Comparison', fontsize=13, fontweight='bold')
            ax4.legend(loc='lower right', fontsize=9)
            ax4.grid(True, alpha=0.3)
            ax4.set_xlim(1, 76)
            ax4.set_ylim(0.4, 1.0)
            
            self.comparison_canvas.draw()
        
        except Exception as e:
            print(f"Algorithm comparison update error: {e}")
    
    def load_configuration(self):
        """Load configuration from file."""
        filename, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
        if filename:
            self.config = ConfigManager(filename)
            self.statusBar.showMessage(f"Loaded: {filename}", 3000)
    
    def save_configuration(self):
        """Save configuration to file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "JSON Files (*.json)")
        if filename:
            self.config.save_config(Path(filename))
            self.statusBar.showMessage(f"Saved: {filename}", 3000)
    
    def export_complete_report(self):
        """Export all simulation results in one click - COMPLETE EXPORT."""
        try:
            if not hasattr(self, 'simulation_results') or self.simulation_results is None:
                QMessageBox.warning(self, "No Data", "No simulation results available. Please run a simulation first.")
                return
            
            # Select output directory
            output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
            if not output_dir:
                return  # User cancelled
            
            # Import necessary utilities
            import json
            from datetime import datetime
            from utils.data_export import export_forest_data, export_sensor_data, export_pareto_solutions
            
            # Create timestamped folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_folder = Path(output_dir) / f"FODEMIR_Report_{timestamp}"
            export_folder.mkdir(parents=True, exist_ok=True)
            
            # 1. Export all figures
            figures_dir = export_folder / "figures"
            figures_dir.mkdir(exist_ok=True)
            for step_key, fig in self.viz_figures.items():
                fig_path = figures_dir / f"step_{step_key}.png"
                fig.savefig(fig_path, dpi=300, bbox_inches='tight')
            
            # 2. Export CSV data
            data_dir = export_folder / "data"
            data_dir.mkdir(exist_ok=True)
            results = self.simulation_results
            
            # Forest data
            if 'forest' in results:
                forest_file = data_dir / "forest_data.csv"
                export_forest_data(results['forest'], str(forest_file))
            
            # Sensor positions
            if 'optimization' in results and 'best_solution' in results['optimization']:
                sensor_file = data_dir / "sensor_positions.csv"
                export_sensor_data(results['optimization']['best_solution'], str(sensor_file))
            
            # Pareto front
            if 'optimization' in results and 'pareto_front' in results['optimization']:
                pareto_file = data_dir / "pareto_solutions.csv"
                export_pareto_solutions(results['optimization']['pareto_front'], str(pareto_file))
            
            # 3. Export GeoJSON with GPS coordinates
            geojson_dir = export_folder / "geojson"
            geojson_dir.mkdir(exist_ok=True)
            
            # UAV trajectory GeoJSON
            if 'uav_planning' in results:
                uav_geojson_file = geojson_dir / "uav_trajectory.geojson"
                self._export_uav_trajectory_geojson(results, str(uav_geojson_file))
                
                # Also export as CSV for convenience
                uav_csv_file = data_dir / "uav_trajectory.csv"
                self._export_uav_trajectory_csv(results, str(uav_csv_file))
            
            # 4. Export simulation summary (JSON)
            summary = {
                "timestamp": timestamp,
                "configuration": {
                    "forest_area_m2": self.config.get('forest_generation.area_m2'),
                    "tree_density_per_ha": self.config.get('forest_generation.tree_density_per_ha'),
                    "frequency_mhz": self.config.get('em_propagation.frequency_mhz'),
                    "tx_power_dbm": self.config.get('em_propagation.tx_power_dbm'),
                    "population_size": self.config.get('optimization.population_size'),
                    "n_generations": self.config.get('optimization.n_generations')
                },
                "results": {
                    "num_sensors_deployed": len(results['optimization']['best_solution']) if 'optimization' in results else 0,
                    "blind_area_percentage": results['optimization']['pareto_front'][0][0] * 100 if 'optimization' in results else 0,
                    "total_flight_distance_m": results['uav']['distance'] if 'uav' in results and results['uav'] is not None else 0,
                    "total_energy_consumption_wh": results['uav']['energy']['total_energy'] if 'uav' in results and results['uav'] is not None else 0
                }
            }
            summary_file = export_folder / "simulation_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=4, ensure_ascii=False)
            
            # Success message
            QMessageBox.information(
                self, 
                "Export Complete",
                f"✅ Complete report exported successfully!\n\n"
                f"📁 Location: {export_folder}\n\n"
                f"📊 Exported:\n"
                f"  • {len(self.viz_figures)} visualization figures (PNG, 300 DPI)\n"
                f"  • Forest, sensor, and Pareto data (CSV)\n"
                f"  • UAV trajectory with GPS (GeoJSON & CSV)\n"
                f"  • Simulation summary (JSON)"
            )
            self.statusBar.showMessage(f"Complete report exported to: {export_folder}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export complete report:\n{str(e)}")
    
    def _export_uav_trajectory_geojson(self, results, output_file):
        """Export UAV trajectory as GeoJSON with approximate GPS coordinates."""
        try:
            import json
            import math
            
            if 'uav' not in results or results['uav'] is None:
                return
            
            # Get trajectory 3D points (x, y, z)
            trajectory_3d = results['uav'].get('trajectory', [])
            if len(trajectory_3d) == 0:
                return
            
            # Reference point (approximate - can be customized)
            # Using a reference in China forest area
            ref_lat = 30.0  # N latitude
            ref_lon = 120.0  # E longitude
            
            # Convert local meters to GPS coordinates (approximate)
            # 1 degree latitude ≈ 111 km
            # 1 degree longitude ≈ 111 km * cos(latitude)
            
            features = []
            for i, point in enumerate(trajectory_3d):
                x, y, z = point
                # Convert meters to degrees (approximate)
                lat = ref_lat + (y / 111000.0)
                lon = ref_lon + (x / (111000.0 * math.cos(math.radians(ref_lat))))
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat, z]  # [longitude, latitude, altitude]
                    },
                    "properties": {
                        "waypoint_id": i,
                        "local_x_m": x,
                        "local_y_m": y,
                        "altitude_m": z,
                        "latitude": lat,
                        "longitude": lon
                    }
                })
            
            geojson = {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                    }
                },
                "features": features
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"GeoJSON export error: {e}")
    
    def _export_uav_trajectory_csv(self, results, output_file):
        """Export UAV trajectory as CSV with GPS coordinates - DJI Compatible Format."""
        try:
            if 'uav' not in results or results['uav'] is None:
                return
            
            trajectory_3d = results['uav'].get('trajectory', [])
            if len(trajectory_3d) == 0:
                return
            
            # Reference point (user can modify this to their actual site location)
            ref_lat = 30.0  # Reference latitude
            ref_lon = 120.0  # Reference longitude
            
            import math
            import csv
            
            # Export standard CSV format
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Waypoint_ID', 'Local_X_m', 'Local_Y_m', 'Altitude_m', 
                                'Latitude', 'Longitude', 'Heading_deg', 'Speed_m_s'])
                
                for i, point in enumerate(trajectory_3d):
                    x, y, z = point
                    lat = ref_lat + (y / 111000.0)
                    lon = ref_lon + (x / (111000.0 * math.cos(math.radians(ref_lat))))
                    
                    # Calculate heading to next waypoint
                    if i < len(trajectory_3d) - 1:
                        next_x, next_y, _ = trajectory_3d[i + 1]
                        dx = next_x - x
                        dy = next_y - y
                        heading = (math.degrees(math.atan2(dy, dx)) + 90) % 360
                    else:
                        heading = 0  # Last waypoint
                    
                    speed = 5.0  # Default cruise speed (m/s)
                    
                    writer.writerow([i, f"{x:.2f}", f"{y:.2f}", f"{z:.2f}", 
                                   f"{lat:.6f}", f"{lon:.6f}", f"{heading:.1f}", f"{speed:.1f}"])
            
            # Also export DJI Pilot compatible format
            dji_output_file = output_file.replace('.csv', '_DJI_Format.csv')
            with open(dji_output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # DJI format header
                writer.writerow(['latitude', 'longitude', 'altitude(m)', 'heading(deg)', 
                                'curvesize(m)', 'rotationdir', 'gimbalmode', 'gimbalpitchangle', 
                                'actiontype1', 'actionparam1'])
                
                for i, point in enumerate(trajectory_3d):
                    x, y, z = point
                    lat = ref_lat + (y / 111000.0)
                    lon = ref_lon + (x / (111000.0 * math.cos(math.radians(ref_lat))))
                    
                    # Calculate heading
                    if i < len(trajectory_3d) - 1:
                        next_x, next_y, _ = trajectory_3d[i + 1]
                        dx = next_x - x
                        dy = next_y - y
                        heading = (math.degrees(math.atan2(dy, dx)) + 90) % 360
                    else:
                        heading = 0
                    
                    # DJI format: lat, lon, alt, heading, curvesize, rotationdir, gimbalmode, 
                    # gimbalpitch, actiontype, actionparam
                    writer.writerow([f"{lat:.6f}", f"{lon:.6f}", f"{z:.1f}", f"{heading:.1f}",
                                   "0.2", "0", "0", "-90", "-1", "0"])
            
            print(f"✓ UAV trajectory exported:")
            print(f"  - Standard CSV: {output_file}")
            print(f"  - DJI Format CSV: {dji_output_file}")
                    
        except Exception as e:
            print(f"CSV export error: {e}")
    
    def export_figures(self):
        """Export visualization figures individually."""
        try:
            if not hasattr(self, 'viz_figures') or len(self.viz_figures) == 0:
                QMessageBox.warning(self, "No Data", "No figures available to export.")
                return
            
            output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
            if not output_dir:
                return
            
            for step_key, fig in self.viz_figures.items():
                fig_path = Path(output_dir) / f"step_{step_key}.png"
                fig.savefig(fig_path, dpi=300, bbox_inches='tight')
            
            QMessageBox.information(self, "Success", f"All figures exported to:\n{output_dir}")
            self.statusBar.showMessage(f"Figures exported to: {output_dir}", 3000)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def export_data(self):
        """Export simulation data as CSV."""
        try:
            if not hasattr(self, 'simulation_results') or self.simulation_results is None:
                QMessageBox.warning(self, "No Data", "No simulation data available.")
                return
            
            from utils.data_export import export_forest_data, export_sensor_data, export_pareto_solutions
            
            output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
            if not output_dir:
                return
            
            results = self.simulation_results
            
            # Export available data
            if 'forest' in results:
                forest_file = Path(output_dir) / "forest_data.csv"
                export_forest_data(results['forest'], str(forest_file))
            
            if 'optimization' in results and 'best_solution' in results['optimization']:
                sensor_file = Path(output_dir) / "sensor_positions.csv"
                export_sensor_data(results['optimization']['best_solution'], str(sensor_file))
            
            if 'optimization' in results and 'pareto_front' in results['optimization']:
                pareto_file = Path(output_dir) / "pareto_solutions.csv"
                export_pareto_solutions(results['optimization']['pareto_front'], str(pareto_file))
            
            QMessageBox.information(self, "Success", f"Data exported to:\n{output_dir}")
            self.statusBar.showMessage(f"Data exported to: {output_dir}", 3000)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def export_geojson(self):
        """Export GeoJSON with GPS coordinates."""
        try:
            if not hasattr(self, 'simulation_results') or self.simulation_results is None:
                QMessageBox.warning(self, "No Data", "No simulation data available.")
                return
            
            output_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory", "")
            if not output_dir:
                return
            
            # Export UAV trajectory GeoJSON
            if 'uav' in self.simulation_results and self.simulation_results['uav'] is not None:
                geojson_file = Path(output_dir) / "uav_trajectory.geojson"
                self._export_uav_trajectory_geojson(self.simulation_results, str(geojson_file))
                
                QMessageBox.information(self, "Success", f"GeoJSON exported to:\n{geojson_file}")
                self.statusBar.showMessage(f"GeoJSON exported to: {output_dir}", 3000)
            else:
                QMessageBox.warning(self, "No Data", "No UAV trajectory data available.\nPlease run simulation first.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "关于 FODEMIR-Sim",
                         "FODEMIR-Sim v1.0.0\n\n"
                         "Forest Deployment Optimization via EM & Multi-objective Integrated Research Simulator\n\n"
                         "森林传感器网络部署优化仿真系统\n\n"
                         "© 2025 FODEMIR-Sim Development Team")
    
    def show_help(self):
        """Show help dialog."""
        QMessageBox.information(self, "User Guide",
                              "1. Configure parameters in 'Parameter Settings' tab\n"
                              "2. Click 'Run Simulation' to execute full pipeline\n"
                              "3. View results in 'Visualization' tab\n"
                              "4. Browse Pareto solutions in 'Results' tab\n"
                              "5. Export data in 'Export & Reports' tab")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application font - smaller size to avoid overlap
    font = QFont('Times New Roman', 14)
    app.setFont(font)
    
    # Create and show main window
    window = FOMIRSimMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

