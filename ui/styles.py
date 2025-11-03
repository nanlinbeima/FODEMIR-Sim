"""
Qt Stylesheets

Professional stylesheets for FODEMIR-Sim application.
"""

# Modern light theme stylesheet
LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
    font-family: 'Times New Roman';
    font-size: 25pt;
}

QWidget {
    font-family: 'Times New Roman';
    font-size: 25pt;
    color: #333333;
}

QTabWidget::pane {
    border: 2px solid #cccccc;
    border-radius: 8px;
    background-color: white;
}

QTabBar::tab {
    background-color: #e0e0e0;
    border: 2px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 12px 25px;
    margin-right: 4px;
    font-size: 23pt;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid white;
    color: #2196F3;
}

QTabBar::tab:hover:!selected {
    background-color: #f0f0f0;
}

QGroupBox {
    border: 2px solid #2196F3;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    font-size: 24pt;
    font-weight: bold;
    color: #2196F3;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 15px;
    background-color: white;
    border-radius: 4px;
}

QLabel {
    font-size: 22pt;
    color: #444444;
    padding: 4px;
}

QPushButton {
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 25px;
    font-size: 23pt;
    font-weight: bold;
    min-height: 45px;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    border: 2px solid #cccccc;
    border-radius: 4px;
    padding: 8px 12px;
    background-color: white;
    font-size: 22pt;
    min-height: 40px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 10px solid #666666;
    margin-right: 8px;
}

QTextEdit {
    border: 2px solid #cccccc;
    border-radius: 4px;
    padding: 10px;
    background-color: white;
    font-size: 20pt;
}

QTableWidget {
    border: 2px solid #cccccc;
    border-radius: 4px;
    background-color: white;
    gridline-color: #e0e0e0;
    font-size: 20pt;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #BBDEFB;
    color: #000000;
}

QHeaderView::section {
    background-color: #2196F3;
    color: white;
    font-size: 21pt;
    font-weight: bold;
    padding: 10px;
    border: none;
    border-right: 1px solid #1976D2;
    border-bottom: 2px solid #1976D2;
}

QScrollBar:vertical {
    border: none;
    background-color: #f0f0f0;
    width: 16px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #BDBDBD;
    border-radius: 8px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #9E9E9E;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f0f0f0;
    height: 16px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #BDBDBD;
    border-radius: 8px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #9E9E9E;
}

QProgressBar {
    border: 2px solid #cccccc;
    border-radius: 6px;
    text-align: center;
    font-size: 20pt;
    font-weight: bold;
    min-height: 35px;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 4px;
}

QStatusBar {
    background-color: #e0e0e0;
    border-top: 2px solid #cccccc;
    font-size: 20pt;
}

QMenuBar {
    background-color: #2196F3;
    color: white;
    font-size: 23pt;
    padding: 5px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 20px;
}

QMenuBar::item:selected {
    background-color: #1976D2;
    border-radius: 4px;
}

QMenu {
    background-color: white;
    border: 2px solid #cccccc;
    font-size: 22pt;
    padding: 5px;
}

QMenu::item {
    padding: 10px 30px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #BBDEFB;
}

QToolTip {
    background-color: #FFF9C4;
    color: #333333;
    border: 2px solid #FBC02D;
    border-radius: 4px;
    padding: 8px;
    font-size: 20pt;
}

QCheckBox {
    spacing: 10px;
    font-size: 22pt;
}

QCheckBox::indicator {
    width: 28px;
    height: 28px;
    border: 2px solid #cccccc;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

QRadioButton {
    spacing: 10px;
    font-size: 22pt;
}

QRadioButton::indicator {
    width: 26px;
    height: 26px;
    border: 2px solid #cccccc;
    border-radius: 13px;
}

QRadioButton::indicator:checked {
    background-color: #2196F3;
    border-color: #2196F3;
}

QSlider::groove:horizontal {
    height: 10px;
    background-color: #e0e0e0;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background-color: #2196F3;
    width: 24px;
    height: 24px;
    margin: -7px 0;
    border-radius: 12px;
}

QSlider::handle:horizontal:hover {
    background-color: #1976D2;
}
"""

# Dark theme stylesheet (optional)
DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    font-family: 'Times New Roman';
    font-size: 25pt;
}

QWidget {
    font-family: 'Times New Roman';
    font-size: 25pt;
    color: #e0e0e0;
    background-color: #1e1e1e;
}

QTabWidget::pane {
    border: 2px solid #444444;
    border-radius: 8px;
    background-color: #2d2d2d;
}

QTabBar::tab {
    background-color: #3a3a3a;
    border: 2px solid #444444;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 12px 25px;
    margin-right: 4px;
    font-size: 23pt;
    font-weight: bold;
    color: #e0e0e0;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    border-bottom: 2px solid #2d2d2d;
    color: #64B5F6;
}

QTabBar::tab:hover:!selected {
    background-color: #4a4a4a;
}

QGroupBox {
    border: 2px solid #64B5F6;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    font-size: 24pt;
    font-weight: bold;
    color: #64B5F6;
}

QLabel {
    font-size: 22pt;
    color: #e0e0e0;
    background-color: transparent;
}

QPushButton {
    background-color: #1976D2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 25px;
    font-size: 23pt;
    font-weight: bold;
    min-height: 45px;
}

QPushButton:hover {
    background-color: #2196F3;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    border: 2px solid #444444;
    border-radius: 4px;
    padding: 8px 12px;
    background-color: #2d2d2d;
    color: #e0e0e0;
    font-size: 22pt;
    min-height: 40px;
}

QTableWidget {
    border: 2px solid #444444;
    border-radius: 4px;
    background-color: #2d2d2d;
    color: #e0e0e0;
    gridline-color: #444444;
    font-size: 20pt;
}

QHeaderView::section {
    background-color: #1976D2;
    color: white;
    font-size: 21pt;
    font-weight: bold;
    padding: 10px;
    border: none;
}

QStatusBar {
    background-color: #3a3a3a;
    border-top: 2px solid #444444;
    font-size: 20pt;
    color: #e0e0e0;
}
"""


def get_stylesheet(theme: str = 'light') -> str:
    """
    Get stylesheet for specified theme.
    
    Args:
        theme: Theme name ('light' or 'dark')
    
    Returns:
        Qt stylesheet string
    """
    if theme == 'dark':
        return DARK_THEME
    else:
        return LIGHT_THEME


