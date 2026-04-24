"""
UI Panels Module
Constructs the dockable panels, layout groups, and input widgets for the MOLD F.O.R.G.E. application.
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFormLayout, QFrame, QProgressBar,
                               QScrollArea, QComboBox, QCheckBox, QGroupBox, 
                               QPlainTextEdit, QDockWidget, QLineEdit)
from PySide6.QtCore import Qt
from custom_widgets import NoScrollSpinBox, KickShapeEditor
from PySide6.QtGui import QFontDatabase

def add_param(app, target_layout, label_text, min_val, max_val, default, tooltip=""):
    """
    Helper function to create a labeled NoScrollSpinBox, add it to a FormLayout,
    and wire its valueChanged signal to the app's update scheduler.
    """
    spin = NoScrollSpinBox()
    spin.setRange(min_val, max_val)
    # Store original safe limits for Extreme Mode toggling
    spin.orig_min = min_val  
    spin.orig_max = max_val  
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
    
    app.chk_sidelocks = QCheckBox("Enable SideLocks")
    app.chk_sidelocks.setToolTip("Add interlocking side tabs to align the molds perfectly during pressing.")
    layout_out.addRow(app.chk_sidelocks)
    
    app.spin_sidelocks_gap = add_param(app, layout_out, "SideLocks Y Gap (mm)", 0.05, 0.30, app.params.SideLocksGap, "Clearance between male and female locks. 0.15 is ideal for sliding fit.")
    app.spin_sidelocks_gap.setSingleStep(0.01) 
    
    def update_sidelocks_vis():
        """Dynamically hides the SideLocks Gap spinner if SideLocks is unchecked."""
        chk = app.chk_sidelocks.isChecked()
        app.spin_sidelocks_gap.setVisible(chk)
        lbl = layout_out.labelForField(app.spin_sidelocks_gap)
        if lbl: 
            lbl.setVisible(chk)
        app.schedule_update()

    app.chk_sidelocks.stateChanged.connect(lambda _: update_sidelocks_vis())
    update_sidelocks_vis() # Inizializza lo stato visivo all'avvio

    app.chk_top_shaper = QCheckBox("Add Top Shaper Shell")
    app.chk_top_shaper.setToolTip("Generates the mating top shell next to the Shaper Template. Useful for pressing thin veneers.")
    app.chk_top_shaper.setChecked(False)
    app.chk_top_shaper.stateChanged.connect(lambda: app.schedule_update())
    layout_out.addRow(app.chk_top_shaper)

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

    app.chk_cut_base = QCheckBox("Cut Base (Flush Sides)")
    app.chk_cut_base.setToolTip("Sets the mold's Base Width equal to the Core Width, creating flush sides for vertical printing.")
    app.chk_cut_base.setChecked(False)
    layout_out.addRow(app.chk_cut_base)

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
        if lbl: 
            lbl.setVisible(chk)
        
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
    
    # New: Guide Hole Count ComboBox
    app.combo_guide_count = QComboBox()
    # Populate with even numbers from 4 up to 20
    app.combo_guide_count.addItems([str(i) for i in range(4, 22, 2)])
    # Set the default value from params (as a string)
    default_count_str = str(app.params.GuideHoleCount)
    if default_count_str in [app.combo_guide_count.itemText(i) for i in range(app.combo_guide_count.count())]:
        app.combo_guide_count.setCurrentText(default_count_str)
    else:
        app.combo_guide_count.setCurrentText("6")
        
    lbl_count = QLabel("Hole Count:")
    lbl_count.setToolTip("Number of alignment holes (must be an even number).")
    layout_out.addRow(lbl_count, app.combo_guide_count)
    app.combo_guide_count.currentTextChanged.connect(app.schedule_update)

    # New: Offset Spinboxes
    app.spin_guide_ox = add_param(app, layout_out, "Offset X (mm)", -20.0, 50.0, app.params.GuideOffsetX, "Distance of holes from the pressing core edge.")
    app.spin_guide_oy = add_param(app, layout_out, "Offset Y (mm)", 0.0, 100.0, app.params.GuideOffsetY, "Distance of holes from the mold's top/bottom ends.")

    def update_guide_vis():
        """Dynamically hides all guide-related parameters if Add Guide Holes is unchecked."""
        chk = app.chk_guide_d.isChecked()
        
        # Diameter
        app.spin_guide_d.setVisible(chk)
        lbl_d = layout_out.labelForField(app.spin_guide_d)
        if lbl_d: 
            lbl_d.setVisible(chk)
        
        # Count
        app.combo_guide_count.setVisible(chk)
        lbl_c = layout_out.labelForField(app.combo_guide_count)
        if lbl_c: 
            lbl_c.setVisible(chk)
        
        # Offset X
        app.spin_guide_ox.setVisible(chk)
        lbl_ox = layout_out.labelForField(app.spin_guide_ox)
        if lbl_ox: 
            lbl_ox.setVisible(chk)
        
        # Offset Y
        app.spin_guide_oy.setVisible(chk)
        lbl_oy = layout_out.labelForField(app.spin_guide_oy)
        if lbl_oy: 
            lbl_oy.setVisible(chk)
        
        if not chk:
            app.spin_guide_d.setValue(0.0)
        elif app.spin_guide_d.value() == 0.0:
            app.spin_guide_d.setValue(6.5)
            
        app.schedule_update()

    app.chk_guide_d.stateChanged.connect(lambda _: update_guide_vis())

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
    app.combo_preset.addItem("Default / Reset")
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
        """Updates the visual state of the delete/reset button based on current selection."""
        clean_text = text.replace("[M] ", "") if text else ""
        
        # Support both the new and legacy default names
        if clean_text == "Default / Reset" or clean_text == "Custom":
            app.btn_delete_preset.setText("Reset")
            app.btn_delete_preset.setToolTip("Reset all parameters to factory defaults.")
            app.btn_delete_preset.setStyleSheet("QPushButton { color: #ff6b6b; } QPushButton:hover { background-color: #fa5b21; }")
        else:
            app.btn_delete_preset.setText("Delete")
            app.btn_delete_preset.setToolTip("Permanently delete the selected preset.")
            app.btn_delete_preset.setStyleSheet("QPushButton { color: #ff6b6b; } QPushButton:hover { background-color: #5a2a2a; }")

    app.combo_preset.currentTextChanged.connect(update_delete_btn_state)
    
    # Force the initial state correctly on startup
    update_delete_btn_state(app.combo_preset.currentText())

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
    
    def update_cut_base_vis():
        """
        Dynamically hides the Base Width spinner and disables Guide Holes 
        AND Base Fillet if Cut Base (Flush Sides) is checked.
        Restores defaults when unchecked.
        """
        chk = app.chk_cut_base.isChecked()
        
        # Manage visibility of Base Width slider
        app.spin_base_w.setVisible(not chk)
        lbl = layout_dim.labelForField(app.spin_base_w)
        if lbl: 
            lbl.setVisible(not chk)
        
        if chk:
            # Force Base Width to match Core Width
            app.spin_base_w.setValue(app.spin_width.value())
            
            # Disable and uncheck Guide Holes and Fillet
            app.chk_guide_d.setChecked(False)
            app.chk_guide_d.setEnabled(False)
            
            app.chk_fillet.setChecked(False)
            app.chk_fillet.setEnabled(False)
        else:
            # Re-enable Guide Holes and Fillet when shoulders are restored
            app.chk_guide_d.setEnabled(True)
            app.chk_fillet.setEnabled(True)
            
            # Restore to default checked state
            app.chk_guide_d.setChecked(True)
            app.chk_fillet.setChecked(True)
            
            # Restore the Base Width to its factory default
            if app.spin_base_w.value() <= app.spin_width.value():
                app.spin_base_w.setValue(75.0)
            
        # Trigger visibility updates for child parameters
        update_guide_vis()
        update_fillet_vis()
        
        app.schedule_update()

    app.chk_cut_base.stateChanged.connect(lambda _: update_cut_base_vis())
    update_cut_base_vis()

    left_controls_layout.addWidget(group_dim)

    # --- TRUCKS HOLES GROUP ---
    group_trucks = QGroupBox("TRUCKS HOLES")
    layout_trucks = QFormLayout(group_trucks)
    
    # New: Toggle to show/hide dimensions
    app.chk_modify_trucks = QCheckBox("Custom Dimensions")
    app.chk_modify_trucks.setToolTip("Unlock to modify the standard truck hole spacing and diameter.")
    app.chk_modify_trucks.setChecked(False)
    layout_trucks.addRow(app.chk_modify_trucks)
    
    app.spin_truck_l = add_param(app, layout_trucks, "Hole Distance (Length) (mm)", 5.0, 15.0, app.params.TruckHoleDistL, "Distance between the two truck holes along the length axis.")
    app.spin_truck_w = add_param(app, layout_trucks, "Hole Distance (Width) (mm)", 3.0, 10.0, app.params.TruckHoleDistW, "Distance between the two truck holes along the width axis.")
    app.spin_truck_d = add_param(app, layout_trucks, "Hole Diameter (mm)", 1.0, 3.0, app.params.TruckHoleDiam, "Diameter of the truck mounting holes.")
    
    def update_trucks_vis():
        """Dynamically hides the dimension spinners if Custom Dimensions is unchecked."""
        chk = app.chk_modify_trucks.isChecked()
        
        # Length
        app.spin_truck_l.setVisible(chk)
        lbl_l = layout_trucks.labelForField(app.spin_truck_l)
        if lbl_l: 
            lbl_l.setVisible(chk)
        
        # Width
        app.spin_truck_w.setVisible(chk)
        lbl_w = layout_trucks.labelForField(app.spin_truck_w)
        if lbl_w: 
            lbl_w.setVisible(chk)
        
        # Diameter
        app.spin_truck_d.setVisible(chk)
        lbl_d = layout_trucks.labelForField(app.spin_truck_d)
        if lbl_d: 
            lbl_d.setVisible(chk)

    # Wire the checkbox to the visibility function
    app.chk_modify_trucks.stateChanged.connect(lambda _: update_trucks_vis())
    # Run once at startup to hide the fields by default
    update_trucks_vis()
    
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
    # NEW: Reference row with two separate labels for perfect grid alignment
    app.lbl_outer_wb_title = QLabel("Outer Eq. (mm):")
    app.lbl_outer_wb_title.setStyleSheet("color: #66b2ff; font-weight: bold; font-size: 11px;")
    app.lbl_outer_wb_val = QLabel("0.0")
    app.lbl_outer_wb_val.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 11px;")
    # Adding a standard row ensures alignment with other parameters
    layout_deck.addRow(app.lbl_outer_wb_title, app.lbl_outer_wb_val)
    # Hide both by default
    app.lbl_outer_wb_title.setVisible(False)
    app.lbl_outer_wb_val.setVisible(False)
    app.spin_board_w = add_param(app, layout_deck, "Board Width (mm)", 26, 40, app.params.BoardWidth, "Maximum target width of the fingerboard deck.")
    app.spin_concave = add_param(app, layout_deck, "Concave Drop (mm)", 0, 3.5, app.params.ConcaveDrop, "Depth of the concave curve in the center of the board.")
    app.spin_concave_len = add_param(app, layout_deck, "Concave Length (mm)", 10, 60, app.params.ConcaveLength, "Length of the central concave section before kicks begin.")
    app.spin_tub = add_param(app, layout_deck, "Tub Width - Flat (mm)", 0, 20, app.params.TubWidth, "Width of the totally flat central section (Tub concave).")
    app.spin_veneer = add_param(app, layout_deck, "Veneer Thickness (mm)", 0.5, 5.0, app.params.VeneerThickness, "Total physical thickness of the stacked wood veneers.")
    # --- SPOON KICKS ---
    app.chk_spoon = QCheckBox("Enable Spoon Kicks")
    app.chk_spoon.setToolTip("Adds 3D concave curvature to the Nose and Tail (Spoon effect).")
    app.chk_spoon.setChecked(app.params.AddSpoonKicks)
    layout_deck.addRow(app.chk_spoon)
    
    app.spin_spoon_drop = add_param(app, layout_deck, "Spoon Depth (mm)", 0.0, 2.0, app.params.SpoonDrop, "Depth of the concave on the kicks.")
    
    def update_spoon_vis():
        visible = app.chk_spoon.isChecked()
        app.spin_spoon_drop.setVisible(visible)
        lbl = layout_deck.labelForField(app.spin_spoon_drop)
        if lbl: 
            lbl.setVisible(visible)
        app.schedule_update()

    app.chk_spoon.stateChanged.connect(update_spoon_vis)
    update_spoon_vis() # Initialize state

    app.chk_flares = QCheckBox("Enable Wheel Flares")
    app.chk_flares.setToolTip("Generate 3D wheel flares/wells on the deck surface to prevent wheelbite.")
    app.chk_flares.setChecked(False)
    app.chk_flares.stateChanged.connect(lambda: app.schedule_update())
    layout_deck.addRow(app.chk_flares)
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
    app.spin_shaper_h = add_param(app, layout_shaper, "Shaper Height (mm)", 1, 30, app.params.ShaperHeight, "Thickness of the 3D printed routing template.")
    app.spin_fillet_yellow = add_param(app, layout_shaper, "Edge Rounding (mm)", 0.0, 50.0, app.params.FilletYellow, "Radius of the shape's corner fillets (only applies to Custom Bezier shape).")
    
    # --- Nose Handles Button ---
    app.btn_nose_handles = QPushButton("▼ Nose Handles")
    app.btn_nose_handles.setFlat(True) # Removes button background
    app.btn_nose_handles.setStyleSheet("text-align: left; color: #aaa; font-weight: bold;")
    app.btn_nose_handles.setCursor(Qt.PointingHandCursor) # Changes cursor to hand pointer
    layout_shaper.addRow(app.btn_nose_handles)
    
    app.spin_n_s_y = add_param(app, layout_shaper, "Yellow (Y %)", 0, 100, app.params.NoseStraightP, "Length of the straight parallel section before nose tapering starts.")
    app.spin_n_c1x = add_param(app, layout_shaper, "Red (X %)", 0, 100, app.params.NoseCtrl1X, "X-axis position of the primary Bezier control point.")
    app.spin_n_c1y = add_param(app, layout_shaper, "Red (Y %)", 0, 100, app.params.NoseCtrl1Y, "Y-axis position of the primary Bezier control point.")
    app.spin_n_c2x = add_param(app, layout_shaper, "Blue (X %)", 0, 100, app.params.NoseCtrl2X, "X-axis position of the secondary Bezier control point (tip shape).")
    
    # --- Tail Handles Button ---
    app.btn_tail_handles = QPushButton("▼ Tail Handles")
    app.btn_tail_handles.setFlat(True)
    app.btn_tail_handles.setStyleSheet("text-align: left; color: #aaa; font-weight: bold;")
    app.btn_tail_handles.setCursor(Qt.PointingHandCursor)
    layout_shaper.addRow(app.btn_tail_handles)
    
    app.spin_t_s_y = add_param(app, layout_shaper, "Yellow (Y %)", 0, 100, app.params.TailStraightP, "Length of the straight parallel section before tail tapering starts.")
    app.spin_t_c1x = add_param(app, layout_shaper, "Red (X %)", 0, 100, app.params.TailCtrl1X, "X-axis position of the primary Bezier control point.")
    app.spin_t_c1y = add_param(app, layout_shaper, "Red (Y %)", 0, 100, app.params.TailCtrl1Y, "Y-axis position of the primary Bezier control point.")
    app.spin_t_c2x = add_param(app, layout_shaper, "Blue (X %)", 0, 100, app.params.TailCtrl2X, "X-axis position of the secondary Bezier control point (tip shape).")

    # --- Toggle Functions ---
    def toggle_nose_handles(state=None):
        # If state is explicitly provided (True/False), use it. 
        # Otherwise (on click), toggle current visibility.
        is_visible = state if state is not None else not app.spin_n_s_y.isVisible()
        
        arrow = "▼" if is_visible else "▶"
        app.btn_nose_handles.setText(f"{arrow} Nose Handles")
        
        widgets = [app.spin_n_s_y, app.spin_n_c1x, app.spin_n_c1y, app.spin_n_c2x]
        for w in widgets:
            w.setVisible(is_visible)
            lbl = layout_shaper.labelForField(w)
            if lbl: 
                lbl.setVisible(is_visible)

    def toggle_tail_handles(state=None):
        is_visible = state if state is not None else not app.spin_t_s_y.isVisible()
        
        arrow = "▼" if is_visible else "▶"
        app.btn_tail_handles.setText(f"{arrow} Tail Handles")
        
        widgets = [app.spin_t_s_y, app.spin_t_c1x, app.spin_t_c1y, app.spin_t_c2x]
        for w in widgets:
            w.setVisible(is_visible)
            lbl = layout_shaper.labelForField(w)
            if lbl: 
                lbl.setVisible(is_visible)

    # IMPORTANT: Use lambda to ensure the button click doesn't pass 
    # its own arguments to our functions
    app.btn_nose_handles.clicked.connect(lambda: toggle_nose_handles())
    app.btn_tail_handles.clicked.connect(lambda: toggle_tail_handles())
    
    # Force collapse to FALSE explicitly on startup
    toggle_nose_handles(False)
    toggle_tail_handles(False)

    right_controls_layout.addWidget(group_shaper)
    
    scroll_right.setWidget(scroll_content_right)
    right_layout.addWidget(scroll_right)
    app.dock_right.setWidget(right_panel)
    app.addDockWidget(Qt.RightDockWidgetArea, app.dock_right)

    # --- LOGO / BRANDING GROUP ---
    group_logo = QGroupBox("LOGO / BRANDING")
    layout_logo = QFormLayout(group_logo)

    # enable toggle
    app.chk_logo = QCheckBox("Enable Logo Deboss")
    app.chk_logo.setChecked(app.params.AddLogo)
    layout_logo.addRow("Enable:", app.chk_logo)

    # invert (mirror for mold readability)
    app.chk_logo_invert = QCheckBox("Invert (Readable After Pressing)")
    app.chk_logo_invert.setChecked(app.params.LogoInvert)
    app.chk_logo_invert.stateChanged.connect(lambda: app.schedule_update())
    layout_logo.addRow("Invert:", app.chk_logo_invert)

    # text input
    app.input_logo_text = QLineEdit()
    app.input_logo_text.setText(app.params.LogoText)
    app.input_logo_text.textChanged.connect(lambda: app.schedule_update())
    layout_logo.addRow("Text:", app.input_logo_text)

    # font selector
    app.combo_logo_font = QComboBox()
    # Fetches all installed system fonts dynamically
    app.combo_logo_font.addItems(QFontDatabase.families())
    app.combo_logo_font.setCurrentText(app.params.LogoFont)
    
    app.combo_logo_font.currentTextChanged.connect(lambda: app.schedule_update())
    layout_logo.addRow("Font:", app.combo_logo_font)

    # size
    app.spin_logo_size = add_param(
        app, layout_logo,
        "Size (mm)", 1, 80,
        app.params.LogoSize,
        "Overall size of logo text"
    )

    # depth
    app.spin_logo_depth = add_param(
        app, layout_logo,
        "Depth (mm)", 0.1, 1.5,
        app.params.LogoDepth,
        "Emboss/deboss depth"
    )

    # offset X
    app.spin_logo_off_x = add_param(
        app, layout_logo,
        "Offset X (mm)", -50, 50,
        app.params.LogoOffsetX,
        "Move logo left/right"
    )

    # offset Y
    app.spin_logo_off_y = add_param(
        app, layout_logo,
        "Offset Y (mm)", -50, 50,
        app.params.LogoOffsetY,
        "Move logo up/down deck"
    )

    # spacing between letters
    app.spin_logo_spacing = add_param(
        app, layout_logo,
        "Spacing", 0.2, 1.5,
        app.params.LogoSpacing,
        "Spacing between letters (multiplier of size)"
    )

    # rotation
    app.spin_logo_rot = add_param(
        app, layout_logo,
        "Rotation (°)", 0, 360,
        app.params.LogoRotationDeg,
        "Rotate logo orientation"
    )

    def update_logo_vis():
        visible = app.chk_logo.isChecked()
        
        widgets = [
            app.chk_logo_invert, app.input_logo_text, app.combo_logo_font,
            app.spin_logo_size, app.spin_logo_depth, app.spin_logo_off_x, 
            app.spin_logo_off_y, app.spin_logo_spacing, app.spin_logo_rot
        ]
        
        for widget in widgets:
            widget.setVisible(visible)
            lbl = layout_logo.labelForField(widget)
            if lbl:
                lbl.setVisible(visible)
                
        app.schedule_update()

    app.chk_logo.stateChanged.connect(lambda _: update_logo_vis())
    update_logo_vis() 

    # add group to UI
    right_controls_layout.addWidget(group_logo)


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
    # ==========================================
    # GLOBAL UI TWEAKS
    # ==========================================
    # Find all QGroupBox elements and compress their top internal layout margin 
    # to eliminate the excessive gap under the blue titles.
    for group in app.findChildren(QGroupBox):
        layout = group.layout()
        if layout:
            # setContentsMargins(left, top, right, bottom)
            # Default is usually (9, 9, 9, 9). We crush the top margin to 2.
            layout.setContentsMargins(9, 2, 9, 9)
            # We also reduce the vertical spacing between the rows inside the box
            layout.setSpacing(4)