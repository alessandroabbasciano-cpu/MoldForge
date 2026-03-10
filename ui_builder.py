"""
UI Builder Module
Responsible for scaffolding the main application window, initializing the 3D viewport,
setting up the camera toolbar overlay, and assembling the various dock panels.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGridLayout, QMainWindow
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
from custom_widgets import CollapsibleDockTitleBar
import ui_panels
import ui_menus

def setup_ui(app):
    """
    Constructs the primary user interface layout.
    Sets up the central 3D rendering canvas, overlays the camera control buttons,
    and delegates the creation of side panels to the ui_panels module.
    """
    # --- MAIN WINDOW SETUP ---
    # Allow panels to be nested and animated when docking/undocking
    app.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)
    # Reserve the bottom corners for the Left and Right side panels
    app.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
    app.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)

    # --- CENTRAL WIDGET (3D VIEWER) ---
    main_widget = QWidget()
    app.setCentralWidget(main_widget)
    main_layout = QVBoxLayout(main_widget)
    # Remove margins so the 3D viewport stretches to the absolute edges of the window
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    viewer_container = QFrame()
    viewer_grid = QGridLayout(viewer_container)
    viewer_grid.setContentsMargins(0, 0, 0, 0)
    
    # Initialize the PyVista Qt Interactor (the actual 3D canvas)
    app.plotter = QtInteractor(viewer_container)
    app.plotter.set_background(color="#1a1a1a", top="#4a6984")
    app.plotter.camera_position = 'iso'
    viewer_grid.addWidget(app.plotter, 0, 0)
    
    # --- CAMERA TOOLBAR (OVERLAY) ---
    # These buttons float over the top-left corner of the 3D viewport
    cam_toolbar = QHBoxLayout()
    cam_toolbar.setContentsMargins(15, 15, 15, 15) 
    button_style = """
        QPushButton { background-color: #3b3b3b; color: #66b2ff; border: 1px solid #555; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #4a6984; border: 1px solid #66b2ff; }
        QPushButton:pressed { background-color: #1a1a1a; }
    """
    
    # Map labels to their respective PyVista camera functions
    camera_views = [
        ("ISO", app.plotter.view_isometric), 
        ("TOP", app.plotter.view_xy), 
        ("FRONT", app.plotter.view_xz), 
        ("SIDE", app.plotter.view_yz)
    ]
    
    for label, func in camera_views:
        btn = QPushButton(label)
        btn.setFixedSize(50, 30)
        # NoFocus prevents the buttons from stealing keyboard inputs intended for the 3D viewer
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setStyleSheet(button_style)
        btn.clicked.connect(func)
        cam_toolbar.addWidget(btn)
        
    cam_toolbar.addStretch() # Pushes buttons to the left alignment
    viewer_grid.addLayout(cam_toolbar, 0, 0, Qt.AlignTop | Qt.AlignLeft)
    main_layout.addWidget(viewer_container)

    # --- DOCK PANELS INITIALIZATION ---
    # Delegate the creation of sliders, toggles, and UI logic to the ui_panels module
    ui_panels.setup_docks(app)

    # Apply the custom collapsible title bar to all generated docks
    docks_to_upgrade = [
        app.dock_left, 
        app.dock_right, 
        app.dock_designer, 
        app.dock_bottom
    ]
    
    for dock in docks_to_upgrade:
        original_title = dock.windowTitle()
        custom_bar = CollapsibleDockTitleBar(dock, original_title)
        dock.setTitleBarWidget(custom_bar)

    # Stack the 2D Bezier Designer and the Log Console vertically at the bottom of the screen
    app.splitDockWidget(app.dock_designer, app.dock_bottom, Qt.Vertical)
    app.resizeDocks([app.dock_designer, app.dock_bottom], [400, 60], Qt.Vertical)


def setup_menu(app):
    """
    Delegates the creation of the top menu bar to the ui_menus module.
    """
    ui_menus.setup_menu(app)