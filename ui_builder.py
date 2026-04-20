"""
UI Builder Module
Responsible for scaffolding the main application window, initializing the 3D viewport,
setting up the camera toolbar overlay, and assembling the various dock panels.
"""

import sys
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGridLayout, QMainWindow, QCheckBox
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
from custom_widgets import CollapsibleDockTitleBar
import ui_panels
import ui_menus

# --- MACOS DEADLOCK FIX: DISABLE SYNCHRONOUS PAINT ---
if sys.platform == 'darwin':
    def _mac_paint_patch(self, event):
        return
    QtInteractor.paintEvent = _mac_paint_patch

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
    
    # ==========================================
    # --- CAMERA TOOLBAR (LEFT OVERLAY) ---
    # ==========================================
    cam_toolbar = QHBoxLayout()
    cam_toolbar.setContentsMargins(15, 15, 15, 15) 
    button_style = """
        QPushButton { background-color: #3b3b3b; color: #66b2ff; border: 1px solid #555; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #4a6984; border: 1px solid #66b2ff; }
        QPushButton:pressed { background-color: #1a1a1a; }
    """
    
    camera_views = [
        ("ISO", app.plotter.view_isometric), 
        ("TOP", app.plotter.view_xy), 
        ("FRONT", app.plotter.view_xz), 
        ("SIDE", app.plotter.view_yz)
    ]
    
    for label, func in camera_views:
        btn = QPushButton(label)
        btn.setFixedSize(50, 30)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setStyleSheet(button_style)
        btn.clicked.connect(func)
        cam_toolbar.addWidget(btn)

    # --- NEW MEASUREMENT TOOL WITH EXTERNAL DISPLAY (FINAL FIX) ---
    app.btn_measure = QPushButton("MEASURE")
    app.btn_measure.setFixedSize(70, 30)
    app.btn_measure.setFocusPolicy(Qt.NoFocus)
    app.btn_measure.setStyleSheet(button_style)
    app.btn_measure.setCheckable(True)
    
    # Label for the measurement value
    app.lbl_measure_val = QLabel("")
    # Changed background to a solid dark color to prevent text overlapping (ghosting)
    app.lbl_measure_val.setStyleSheet("color: #e67e22; font-weight: bold; margin-left: 10px; font-size: 14px; background-color: #1a1a1a; padding: 0px 5px; border-radius: 3px;")    
    app.lbl_measure_val.hide() # Keep it hidden by default
    
    def toggle_measure(checked):
        if checked:
            # UI Feedback
            app.btn_measure.setStyleSheet(button_style + "border: 2px solid #e67e22; background-color: #3b3b3b;")
            app.lbl_measure_val.setText("Select 2 points...")
            app.lbl_measure_val.show()
            
            # Callback MUST accept 3 arguments from PyVista (point 1, point 2, and the calculated distance)
            def update_display(p1, p2, distance):
                if distance > 0:
                    app.lbl_measure_val.setText(f"{distance:.2f} mm")
                else:
                    app.lbl_measure_val.setText("Select 2 points...")

            # Activate the measurement widget and capture the resulting object
            widget = app.plotter.add_measurement_widget(
                callback=update_display,
                color="#e67e22"
            )
            
            # COMPLETELY hide the native 3D floating text by forcing an empty text format
            try:
                if widget is not None:
                    widget.GetDistanceRepresentation().SetLabelFormat("")
            except Exception: 
                pass
            
            app.log("Measurement Tool ON: Click two points on the 3D model.", "INFO")
        else:
            # UI Feedback
            app.btn_measure.setStyleSheet(button_style)
            app.plotter.clear_measure_widgets()
            app.lbl_measure_val.hide()
            app.lbl_measure_val.setText("") 
            app.log("Measurement Tool OFF.", "INFO")
            
    app.btn_measure.clicked.connect(toggle_measure)
    
    cam_toolbar.addWidget(app.btn_measure)
    cam_toolbar.addWidget(app.lbl_measure_val)
    
    viewer_grid.addLayout(cam_toolbar, 0, 0, Qt.AlignTop | Qt.AlignLeft)

    # ==========================================
    # --- LIVE PREVIEW & GENERATE (RIGHT OVERLAY) ---
    # ==========================================
    action_toolbar = QVBoxLayout()
    action_toolbar.setContentsMargins(15, 15, 15, 15)
    action_toolbar.setSpacing(10) # Space between checkbox and button

    app.chk_live_update = QCheckBox("Live Preview")
    app.chk_live_update.setChecked(True)
    app.chk_live_update.setStyleSheet("color: #66b2ff; font-weight: bold;")
    app.chk_live_update.setFocusPolicy(Qt.NoFocus)

    app.btn_generate = QPushButton("GENERATE 3D")
    app.btn_generate.setFixedSize(120, 30)
    app.btn_generate.setFocusPolicy(Qt.NoFocus)
    app.btn_generate.setStyleSheet("""
        QPushButton { background-color: #e67e22; color: #ffffff; border: 1px solid #d35400; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #d35400; }
        QPushButton:pressed { background-color: #a04000; }
    """)
    
    # The magic trick: retain space when the button is hidden so the UI doesn't jump
    size_policy = app.btn_generate.sizePolicy()
    size_policy.setRetainSizeWhenHidden(True)
    app.btn_generate.setSizePolicy(size_policy)
    
    app.btn_generate.hide() 
    
    app.chk_live_update.stateChanged.connect(lambda state: app.btn_generate.setVisible(not state))
    
    # Add widgets to the vertical layout, aligned to the right
    action_toolbar.addWidget(app.chk_live_update, alignment=Qt.AlignRight)
    action_toolbar.addWidget(app.btn_generate, alignment=Qt.AlignRight)
    
    # Place the layout in the top-right corner of the viewport
    viewer_grid.addLayout(action_toolbar, 0, 0, Qt.AlignTop | Qt.AlignRight)
    # ==========================================

    main_layout.addWidget(viewer_container)

    # --- DOCK PANELS INITIALIZATION ---
    ui_panels.setup_docks(app)

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

    app.splitDockWidget(app.dock_designer, app.dock_bottom, Qt.Vertical)
    app.resizeDocks([app.dock_designer, app.dock_bottom], [400, 60], Qt.Vertical)


def setup_menu(app):
    """
    Delegates the creation of the top menu bar to the ui_menus module.
    """
    ui_menus.setup_menu(app)