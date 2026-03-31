"""
UI Panels Module
Constructs the dockable panels, layout groups, and input widgets for the MOLD F.O.R.G.E. application.
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFormLayout, QFrame, QProgressBar,
                               QScrollArea, QComboBox, QCheckBox, QGroupBox, 
                               QPlainTextEdit, QDockWidget)
from PySide6.QtCore import Qt
from custom_widgets import NoScrollSpinBox, KickShapeEditor

def add_param(app, target_layout, label_text, min_val, max_val, default, tooltip=""):
    """
    Helper function to create a labeled NoScrollSpinBox, add it to a FormLayout,
    and wire its valueChanged signal to the app's update scheduler.
    Optionally applies a tooltip to both the label and the spinbox.
    """
    spin = NoScrollSpinBox()
    spin.setRange(min_val, max_val)
    spin.setValue(default)
    spin.setSingleStep(0.1)
    
    lbl = QLabel(label_text)
    
    if tooltip:
        spin.setToolTip(tooltip)
        lbl.setToolTip(tooltip)
        
    target_layout.addRow(lbl, spin)
    spin.valueChanged.connect(lambda: app.schedule_update())
    return spin

def setup_docks(app):
    """
    Initializes all dockable widgets (Left, Right, Bottom) and builds the parameter forms.
    """
    
    # ==========================================
    # LEFT DOCK: OUTPUT & MOLD SETTINGS
    # ==========================================
    app.dock_left = QDockWidget("Settings Output", app)
    app.dock_left.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    left_panel = QFrame()
    left_layout = QVBoxLayout(left_panel)
    scroll_left = QScrollArea()
    scroll_left.setWidgetResizable(True)
    scroll_content_left = QWidget()
    left_controls_layout = QVBoxLayout(scroll_content_left)
    
    # --- OUTPUT OPTIONS GROUP ---
    group_out = QGroupBox("OUTPUT OPTIONS")
    layout_out = QFormLayout(group_out)
    
    app.combo_type = QComboBox()
    app.combo_type.addItems(["Board_Preview", "Male_Mold", "Female_Mold", "Shaper_Template"])
    app.combo_type.setToolTip("Select the type of 3D object to generate and preview.")
    app.combo_type.currentTextChanged.connect(app.on_type_changed)
    
    lbl_type = QLabel("Object Type:")
    lbl_type.setToolTip("Select the type of 3D object to generate and preview.")
    layout_out.addRow(lbl_type, app.combo_type)
    
    app.chk_wireframe = QCheckBox("Clean Wireframe (Feature Edges)")
    app.chk_wireframe.setToolTip("Toggle to show only main feature edges instead of full triangulation.")
    app.chk_wireframe.setChecked(True)
    app.chk_wireframe.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_wireframe)
    
    app.chk_indicators = QCheckBox("Add N/T Indicators")
    app.chk_indicators.setToolTip("Emboss 'N' (Nose) and 'T' (Tail) markers on the mold/template.")
    app.chk_indicators.setChecked(True)
    app.chk_indicators.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_indicators)
    
    app.chk_sidelocks = QCheckBox("Enable SideLocks (Vertical Print)")
    app.chk_sidelocks.setToolTip("Add interlocking side tabs to align the molds perfectly during pressing.")
    app.chk_sidelocks.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_sidelocks)

    app.chk_top_shaper = QCheckBox("Add Top Shaper Shell")
    app.chk_top_shaper.setToolTip("Generates the mating top shell next to the Shaper Template. Useful for pressing thin veneers.")
    app.chk_top_shaper.setChecked(False)
    app.chk_top_shaper.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_top_shaper)
    
    app.chk_fillet = QCheckBox("Base Reinforcement (AddFillet)")
    app.chk_fillet.setToolTip("Add a curved fillet at the base of the mold core to prevent stress fractures.")
    app.chk_fillet.setChecked(True)
    layout_out.addRow(app.chk_fillet)
    
    app.spin_fillet_rad = add_param(app, layout_out, "Fillet Radius (mm)", 0.0, 10.0, app.params.FilletRadius, "Radius of the base reinforcement curve.")
    
    def update_fillet_vis():
        """Dynamically hides the Fillet Radius spinner if AddFillet is unchecked."""
        chk = app.chk_fillet.isChecked()
        app.spin_fillet_rad.setVisible(chk)
        lbl = layout_out.labelForField(app.spin_fillet_rad)
        if lbl: lbl.setVisible(chk)
        
        if not chk:
            app.spin_fillet_rad.setValue(0.0)
        elif app.spin_fillet_rad.value() == 0.0:
            app.spin_fillet_rad.setValue(5.0)
            
        app.schedule_update()

    app.chk_fillet.stateChanged.connect(lambda _: update_fillet_vis())
    
    app.chk_guide_d = QCheckBox("Add Guide Holes")
    app.chk_guide_d.setToolTip("Add vertical holes through the mold for metal alignment pins.")
    app.chk_guide_d.setChecked(True)
    layout_out.addRow(app.chk_guide_d)   
    
    app.spin_guide_d = add_param(app, layout_out, "Guide Diameter (mm)", 0.0, 10.0, app.params.GuideDiameter, "Diameter of the alignment pin holes.")
    
    def update_guide_vis():
        """Dynamically hides the Guide Diameter spinner if Add Guide Holes is unchecked."""
        chk = app.chk_guide_d.isChecked()
        app.spin_guide_d.setVisible(chk)
        lbl = layout_out.labelForField(app.spin_guide_d)
        if lbl: lbl.setVisible(chk)
        
        if not chk:
            app.spin_guide_d.setValue(0.0)
        elif app.spin_guide_d.value() == 0.0:
            app.spin_guide_d.setValue(6.5)
            
        app.schedule_update()

    app.chk_guide_d.stateChanged.connect(lambda _: update_guide_vis())

    app.chk_flares = QCheckBox("Enable Wheel Flares")
    app.chk_flares.setToolTip("Generate 3D wheel flares/wells on the deck surface to prevent wheelbite.")
    app.chk_flares.setChecked(False)
    app.chk_flares.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_flares)

    app.chk_mold_pins = QCheckBox("Truck Pins (Molds)")
    app.chk_mold_pins.setToolTip("Replaces through-holes with marking pins on the molds (Male/Female).")
    app.chk_mold_pins.setChecked(False)
    app.chk_mold_pins.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_mold_pins)
    
    app.chk_shaper_pins = QCheckBox("Truck Pins (Shaper)")
    app.chk_shaper_pins.setToolTip("Replaces through-holes with marking pins on the shapers (Shaper Template).")
    app.chk_shaper_pins.setChecked(False)
    app.chk_shaper_pins.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_shaper_pins)

    # Initialize dynamic visibility
    update_fillet_vis()
    update_guide_vis()

    left_controls_layout.addWidget(group_out)

    # --- SHAPE STYLE & PRESETS GROUP ---
    group_shape_style = QGroupBox("SHAPE STYLE / PRESETS")
    layout_shape_style = QFormLayout(group_shape_style)
    app.combo_shape_style = QComboBox()
    
# DYNAMIC DXF SCANNING: Loads .dxf files from the shapes_library folder
    import sys
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
            base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    shapes_dir = os.path.join(base_dir, "shapes_library")   
    available_shapes = ["Custom"]
    
    if os.path.exists(shapes_dir):
        for file_name in sorted(os.listdir(shapes_dir)):
            if file_name.lower().endswith('.dxf'):
                available_shapes.append(file_name[:-4])
                
    app.combo_shape_style.addItems(available_shapes)
    app.combo_shape_style.setToolTip("Choose the deck outline: Custom parametric Bezier or a loaded DXF file.")
    app.combo_shape_style.currentTextChanged.connect(lambda: app.schedule_update())
    
    lbl_shape = QLabel("Select Shape:")
    lbl_shape.setToolTip("Choose the deck outline: Custom parametric Bezier or a loaded DXF file.")
    layout_shape_style.addRow(lbl_shape, app.combo_shape_style)
    
    app.spin_shape_offset_y = add_param(app, layout_shape_style, "Shape Shift Y (mm)", -100.0, 100.0, app.params.ShapeOffsetY, "Shift the DXF shape along the length axis. Useful for asymmetric boards like Fishtails.")
    app.spin_shape_offset_y.valueChanged.connect(app.sync_editor_from_spinboxes)

    # --- PRESETS 
    
    app.combo_preset = QComboBox()
    app.combo_preset.addItem("Custom")
    app.combo_preset.addItems(sorted(app.presets_data.keys()))
    
    lbl_preset = QLabel("Load Preset:")
    lbl_preset.setToolTip("Load a pre-configured deck and mold setup.")
    layout_shape_style.addRow(lbl_preset, app.combo_preset)
    
    app.btn_save_preset = QPushButton("Save")
    app.btn_save_preset.setToolTip("Save the current exact configuration into the local JSON database.")
    
    app.btn_delete_preset = QPushButton("Reset")
    app.btn_delete_preset.setToolTip("Reset all parameters to factory defaults.")
    
    layout_preset_actions = QHBoxLayout()
    layout_preset_actions.addWidget(app.btn_save_preset)
    layout_preset_actions.addWidget(app.btn_delete_preset)
    
    layout_shape_style.addRow("", layout_preset_actions)
    
    def update_delete_btn_state(text):
        if text == "Custom":
            app.btn_delete_preset.setText("Reset")
            app.btn_delete_preset.setToolTip("Reset all parameters to factory defaults.")
            app.btn_delete_preset.setStyleSheet("QPushButton { color: #ff6b6b; } QPushButton:hover { background-color: #fa5b21; }")
        else:
            app.btn_delete_preset.setText("Delete")
            app.btn_delete_preset.setToolTip("Permanently delete the selected preset.")
            app.btn_delete_preset.setStyleSheet("QPushButton { color: #ff6b6b; } QPushButton:hover { background-color: #5a2a2a; }")

    app.combo_preset.currentTextChanged.connect(update_delete_btn_state)

    layout_preset_actions = QHBoxLayout()
    layout_preset_actions.addWidget(app.btn_save_preset)
    layout_preset_actions.addWidget(app.btn_delete_preset)
    
    layout_shape_style.addRow("", layout_preset_actions)
    
    left_controls_layout.addWidget(group_shape_style)

    # --- MOLD DIMENSIONS GROUP ---
    group_dim = QGroupBox("MOLD DIMENSIONS")
    layout_dim = QFormLayout(group_dim)
    app.spin_length = add_param(app, layout_dim, "Mold Length (mm)", 90, 160, app.params.MoldLength, "Total physical length of the mold block.")
    app.spin_width = add_param(app, layout_dim, "Core Width (mm)", 30, 70, app.params.MoldCoreWidth, "Width of the central pressing core.")
    app.spin_base_h = add_param(app, layout_dim, "Base Height (mm)", 2, 40, app.params.MoldBaseHeight, "Thickness of the solid structural base of the mold.")
    app.spin_base_w = add_param(app, layout_dim, "Base Width (mm)", 30, 90, app.params.MoldBaseWidth, "Total width of the mold block, including side shoulders.")
    app.spin_core_h = add_param(app, layout_dim, "Min. Core Thickness (mm)", 2, 30, app.params.MoldCoreHeight, "Thickness of the core at its lowest/thinnest point.")
    app.spin_mold_gap = add_param(app, layout_dim, "Mold Gap (mm)", 0.5, 5, app.params.MoldGap, "Distance between the male and female molds (usually equals Veneer Thickness).")
    left_controls_layout.addWidget(group_dim)

    # --- TRUCKS HOLES GROUP ---
    group_trucks = QGroupBox("TRUCKS HOLES")
    layout_trucks = QFormLayout(group_trucks)
    app.spin_truck_l = add_param(app, layout_trucks, "Hole Distance (Length) (mm)", 5.0, 15.0, app.params.TruckHoleDistL, "Distance between the two truck holes along the length axis.")
    app.spin_truck_w = add_param(app, layout_trucks, "Hole Distance (Width) (mm)", 3.0, 10.0, app.params.TruckHoleDistW, "Distance between the two truck holes along the width axis.")
    app.spin_truck_d = add_param(app, layout_trucks, "Hole Diameter (mm)", 1.0, 3.0, app.params.TruckHoleDiam, "Diameter of the truck mounting holes.")
    left_controls_layout.addWidget(group_trucks)
    
    scroll_left.setWidget(scroll_content_left)
    left_layout.addWidget(scroll_left)

    app.dock_left.setWidget(left_panel)
    app.addDockWidget(Qt.LeftDockWidgetArea, app.dock_left)


    # ==========================================
    # RIGHT DOCK: DECK GEOMETRY
    # ==========================================
    app.dock_right = QDockWidget("Board Parameters", app)
    app.dock_right.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    scroll_right = QScrollArea()
    scroll_right.setWidgetResizable(True)
    scroll_content_right = QWidget()
    right_controls_layout = QVBoxLayout(scroll_content_right)

    # --- DECK GEOMETRY GROUP ---
    group_deck = QGroupBox("DECK GEOMETRY")
    layout_deck = QFormLayout(group_deck)
    app.spin_wb = add_param(app, layout_deck, "Wheelbase (mm)", 30, 60, app.params.Wheelbase, "Distance between the inner truck holes.")
    app.spin_board_w = add_param(app, layout_deck, "Board Width (mm)", 26, 40, app.params.BoardWidth, "Maximum target width of the fingerboard deck.")
    app.spin_concave = add_param(app, layout_deck, "Concave Drop (mm)", 0, 3.5, app.params.ConcaveDrop, "Depth of the concave curve in the center of the board.")
    app.spin_concave_len = add_param(app, layout_deck, "Concave Length (mm)", 10, 60, app.params.ConcaveLength, "Length of the central concave section before kicks begin.")
    app.spin_tub = add_param(app, layout_deck, "Tub Width - Flat (mm)", 0, 20, app.params.TubWidth, "Width of the totally flat central section (Tub concave).")
    app.spin_veneer = add_param(app, layout_deck, "Veneer Thickness (mm)", 0.5, 5.0, app.params.VeneerThickness, "Total physical thickness of the stacked wood veneers.")
    right_controls_layout.addWidget(group_deck)

    # --- WHEEL FLARES GROUP ---
    app.group_flares = QGroupBox("WHEEL FLARES")
    layout_flares = QFormLayout(app.group_flares)
    app.spin_flare_h = add_param(app, layout_flares, "Flare Height (mm)", 0.0, 1.5, app.params.FlareHeight, "Maximum Z-height of the wheel flare bumps.")
    app.spin_flare_l = add_param(app, layout_flares, "Flare Length (mm)", 2.0, 25.0, app.params.FlareLength, "Total length of the flare along the board edge.")
    app.spin_flare_w = add_param(app, layout_flares, "Flare Inward Width (mm)", 1.0, 15.0, app.params.FlareWidth, "Distance the flare extends inwards from the edge towards the center.")
    app.spin_flare_py = add_param(app, layout_flares, "Offset Y (from truck mm)", -5.0, 15.0, app.params.FlarePosY, "Y-axis placement offset of the flare relative to the truck center.")
    right_controls_layout.addWidget(app.group_flares)

    # Wire flare visibility
    app.chk_flares.stateChanged.connect(lambda: app.group_flares.setVisible(app.chk_flares.isChecked()))
    app.group_flares.setVisible(app.chk_flares.isChecked())

    # --- KICKS (NOSE / TAIL) GROUP ---
    group_kicks = QGroupBox("KICKS (NOSE / TAIL)")
    layout_kicks = QFormLayout(group_kicks)
    app.spin_nose_ang = add_param(app, layout_kicks, "Nose Angle (°)", 0, 30, app.params.NoseAngle, "Steepness angle of the nose.")
    app.spin_tail_ang = add_param(app, layout_kicks, "Tail Angle (°)", 0, 30, app.params.TailAngle, "Steepness angle of the tail.")
    app.spin_nose_len = add_param(app, layout_kicks, "Nose Length (mm)", 3, 30, app.params.NoseLength, "Physical length of the nose section.")
    app.spin_tail_len = add_param(app, layout_kicks, "Tail Length (mm)", 3, 30, app.params.TailLength, "Physical length of the tail section.")
    app.spin_n_trans = add_param(app, layout_kicks, "Nose Transition (mm)", 1, 15, app.params.NoseTransitionLength, "Length of the smooth bend transitioning into the nose.")
    app.spin_t_trans = add_param(app, layout_kicks, "Tail Transition (mm)", 1, 15, app.params.TailTransitionLength, "Length of the smooth bend transitioning into the tail.")
    app.spin_n_gap = add_param(app, layout_kicks, "Nose Gap (Flat) (mm)", 0, 20, app.params.NoseKickGap, "Flat distance between outer truck holes and the start of the nose transition.")
    app.spin_t_gap = add_param(app, layout_kicks, "Tail Gap (Flat) (mm)", 0, 20, app.params.TailKickGap, "Flat distance between outer truck holes and the start of the tail transition.")
    right_controls_layout.addWidget(group_kicks)
    
    # --- SHAPER / OUTLINE GROUP ---
    group_shaper = QGroupBox("SHAPER / OUTLINE")
    layout_shaper = QFormLayout(group_shaper)
    app.spin_shaper_h = add_param(app, layout_shaper, "Template Height (mm)", 1, 30, app.params.ShaperHeight, "Thickness of the 3D printed routing template.")
    app.spin_fillet_yellow = add_param(app, layout_shaper, "Edge Rounding (mm)", 0.0, 50.0, app.params.FilletYellow, "Radius of the shape's corner fillets (only applies to Custom Bezier shape).")
    
    lbl_n = QLabel("-- Nose Handles --")
    lbl_n.setStyleSheet("color: #aaa;")
    layout_shaper.addRow(lbl_n)
    app.spin_n_s_y = add_param(app, layout_shaper, "Yellow (Y %)", 0, 100, app.params.NoseStraightP, "Length of the straight parallel section before nose tapering starts.")
    app.spin_n_c1x = add_param(app, layout_shaper, "Red (X %)", 0, 100, app.params.NoseCtrl1X, "X-axis position of the primary Bezier control point.")
    app.spin_n_c1y = add_param(app, layout_shaper, "Red (Y %)", 0, 100, app.params.NoseCtrl1Y, "Y-axis position of the primary Bezier control point.")
    app.spin_n_c2x = add_param(app, layout_shaper, "Blue (X %)", 0, 100, app.params.NoseCtrl2X, "X-axis position of the secondary Bezier control point (tip shape).")
    
    lbl_t = QLabel("-- Tail Handles --")
    lbl_t.setStyleSheet("color: #aaa;")
    layout_shaper.addRow(lbl_t)
    app.spin_t_s_y = add_param(app, layout_shaper, "Yellow (Y %)", 0, 100, app.params.TailStraightP, "Length of the straight parallel section before tail tapering starts.")
    app.spin_t_c1x = add_param(app, layout_shaper, "Red (X %)", 0, 100, app.params.TailCtrl1X, "X-axis position of the primary Bezier control point.")
    app.spin_t_c1y = add_param(app, layout_shaper, "Red (Y %)", 0, 100, app.params.TailCtrl1Y, "Y-axis position of the primary Bezier control point.")
    app.spin_t_c2x = add_param(app, layout_shaper, "Blue (X %)", 0, 100, app.params.TailCtrl2X, "X-axis position of the secondary Bezier control point (tip shape).")
    
    right_controls_layout.addWidget(group_shaper)
    
    scroll_right.setWidget(scroll_content_right)
    right_layout.addWidget(scroll_right)
    app.dock_right.setWidget(right_panel)
    app.addDockWidget(Qt.RightDockWidgetArea, app.dock_right)


    # ==========================================
    # BOTTOM DOCKS: DESIGNER & CONSOLE
    # ==========================================
    
    # --- 2D BEZIER DESIGNER ---
    app.dock_designer = QDockWidget("Interactive Shape Designer", app)
    app.dock_designer.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea | Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
    designer_widget = QWidget()
    designer_layout = QVBoxLayout(designer_widget)
    
    combo_layout = QHBoxLayout()
    combo_layout.addWidget(QLabel("Target:"))
    app.combo_edit_target = QComboBox()
    app.combo_edit_target.addItems(["Nose", "Tail"])
    app.combo_edit_target.setToolTip("Select whether to edit the Nose or Tail Bezier handles.")
    app.combo_edit_target.currentTextChanged.connect(app.sync_editor_from_spinboxes)
    combo_layout.addWidget(app.combo_edit_target)
    
    app.chk_sym = QCheckBox("Symmetrical")
    app.chk_sym.setToolTip("Mirror Bezier changes symmetrically between Nose and Tail.")
    app.chk_sym.setChecked(True)
    combo_layout.addWidget(app.chk_sym)
    designer_layout.addLayout(combo_layout)

    app.shape_editor = KickShapeEditor()
    app.shape_editor.shapeChanged.connect(app.on_graphical_shape_changed)
    designer_layout.addWidget(app.shape_editor)
    
    app.dock_designer.setWidget(designer_widget)
    app.addDockWidget(Qt.BottomDockWidgetArea, app.dock_designer)

    # --- LOG CONSOLE & PROGRESS BAR ---
    app.dock_bottom = QDockWidget("Log Console", app)
    app.dock_bottom.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
    
    console_container = QWidget()
    console_layout = QVBoxLayout(console_container)
    console_layout.setContentsMargins(0, 0, 0, 0)
    console_layout.setSpacing(0)
    
    app.log_console = QPlainTextEdit()
    app.log_console.setReadOnly(True)
    app.log_console.setStyleSheet("background-color: #1a1a1a; color: #e0e0e0; font-family: Consolas, monospace; border-top: 1px solid #333; border-bottom: none;")
    
    app.progress_bar = QProgressBar()
    app.progress_bar.setFixedHeight(8)  
    app.progress_bar.setTextVisible(False)
    app.progress_bar.setStyleSheet("""
        QProgressBar { background-color: #1a1a1a; border: none; border-top: 1px solid #333; }
        QProgressBar::chunk { background-color: #e67e22; }
    """)
    
    sp_retain = app.progress_bar.sizePolicy()
    sp_retain.setRetainSizeWhenHidden(True)
    app.progress_bar.setSizePolicy(sp_retain)
    app.progress_bar.hide()
    
    console_layout.addWidget(app.log_console)
    console_layout.addWidget(app.progress_bar)
    
    app.dock_bottom.setWidget(console_container)
    app.addDockWidget(Qt.BottomDockWidgetArea, app.dock_bottom)