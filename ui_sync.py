"""
UI Synchronization & Validation Module
Acts as the logic controller between the graphical user interface and the underlying data model.
Handles parameter syncing, mechanical limit validation, symmetry mirroring, and interactive 2D editor updates.
"""

from email.policy import default

import cq_model
import shape_loader

def on_shape_style_changed(app, text):
    """
    Handles switching between different deck outline styles (Custom Bezier vs loaded DXF).
    Resets specific parameters that don't translate well between shape types.
    """
    # Reset Shape Shift Y to 0.0 when picking a new shape to prevent immediate misalignment.
    # We skip this ONLY if we are currently batch-loading a preset file.
    if not getattr(app, 'is_updating_preset', False):
        app.spin_shape_offset_y.blockSignals(True)
        app.spin_shape_offset_y.setValue(0.0)
        app.spin_shape_offset_y.blockSignals(False)
    
    # Sync the rest of the UI (this will also automatically disable symmetry if a DXF is chosen)
    sync_editor_from_spinboxes(app)
    app.schedule_update()

def sync_symmetry(app, source):
    """
    Mirrors the parameters between Nose and Tail if the 'Symmetrical' checkbox is active.
    Uses an internal '_syncing' flag to prevent infinite recursive loops when spinboxes trigger each other.
    """
    if getattr(app, '_syncing', False) or getattr(app, 'is_updating_preset', False) or not app.chk_sym.isChecked(): 
        sync_editor_from_spinboxes(app)
        return
    
    app._syncing = True
    
    # Copy values from Nose to Tail
    if source == "Nose":
        app.spin_t_s_y.setValue(app.spin_n_s_y.value())
        app.spin_t_c1x.setValue(app.spin_n_c1x.value())
        app.spin_t_c1y.setValue(app.spin_n_c1y.value())
        app.spin_t_c2x.setValue(app.spin_n_c2x.value())
        app.spin_t_trans.setValue(app.spin_n_trans.value())
        app.spin_t_gap.setValue(app.spin_n_gap.value())
        app.spin_tail_ang.setValue(app.spin_nose_ang.value())
        app.spin_tail_len.setValue(app.spin_nose_len.value())
    # Copy values from Tail to Nose
    else:
        app.spin_n_s_y.setValue(app.spin_t_s_y.value())
        app.spin_n_c1x.setValue(app.spin_t_c1x.value())
        app.spin_n_c1y.setValue(app.spin_t_c1y.value())
        app.spin_n_c2x.setValue(app.spin_t_c2x.value())
        app.spin_n_trans.setValue(app.spin_t_trans.value())
        app.spin_n_gap.setValue(app.spin_t_gap.value())
        app.spin_nose_ang.setValue(app.spin_tail_ang.value())
        app.spin_nose_len.setValue(app.spin_tail_len.value())
        
    app._syncing = False
    
    # Update the 2D preview with the newly mirrored values
    sync_editor_from_spinboxes(app)

def validate_cross_dependencies(app):
    """
    The main mechanical validation guard.
    Ensures that user inputs don't break the physical constraints of the mold or the 3D engine.
    Adjusts limits dynamically and flashes the UI widgets to warn the user of bound collisions.
    """
    if getattr(app, "_is_validating", False): return
    app._is_validating = True
    
    try:
        # --- Hardware Constraints ---
        core_w = app.spin_width.value()
        
        # Board cannot be wider than the pressing core
        if app.spin_board_w.value() > core_w:
            app.flash_widget(app.spin_board_w)
            app.log(f"Board Width auto-reduced to {core_w}mm (Max is Core Width)", "WARN")
        app.spin_board_w.setMaximum(core_w)
        
        # Mold base must be at least as wide as the core
        if app.spin_base_w.value() < core_w:
            app.flash_widget(app.spin_base_w)
            app.log(f"Mold Base Width auto-increased to {core_w}mm (Min is Core Width)", "WARN")
        app.spin_base_w.setMinimum(core_w)
        
        # Tub flat section cannot exceed the total board width minus a safe margin
        board_w = app.spin_board_w.value()
        max_tub = max(0.0, board_w - 18.0)
        if app.spin_tub.value() > max_tub:
            app.flash_widget(app.spin_tub)
            app.log(f"Tub Width auto-reduced to {max_tub}mm", "WARN")
        app.spin_tub.setMaximum(max_tub)
        
        # --- Deck Geometry Limits ---
        wb = app.spin_wb.value()
        
        # Concave length cannot exceed the wheelbase
        if app.spin_concave_len.value() > wb:
            app.flash_widget(app.spin_concave_len)
            app.log(f"Concave Length auto-reduced to {wb}mm", "WARN")
        app.spin_concave_len.setMaximum(wb)
        
        nose_l = app.spin_nose_len.value()
        tail_l = app.spin_tail_len.value()
        
        # Kick transitions cannot be longer than the kick itself
        trans_max_n = max(1.0, nose_l - 2.0)
        if app.spin_n_trans.value() > trans_max_n:
            app.flash_widget(app.spin_n_trans)
        app.spin_n_trans.setMaximum(trans_max_n)
        
        trans_max_t = max(1.0, tail_l - 2.0)
        if app.spin_t_trans.value() > trans_max_t:
            app.flash_widget(app.spin_t_trans)
        app.spin_t_trans.setMaximum(trans_max_t)
        
        # Guide holes must physically fit in the mold shoulders
        base_w = app.spin_base_w.value()
        max_guide = max(0.1, ((base_w - core_w) / 2.0) - 2.0)
        if app.spin_guide_d.value() > max_guide:
            app.flash_widget(app.spin_guide_d)
            app.log(f"Guide Diameter auto-reduced to {max_guide:.1f}mm", "WARN")
        app.spin_guide_d.setMaximum(max_guide)
        
        # Mold length must accommodate the entire physical board
        truck_l_val = app.spin_truck_l.value()
        kick_gap_n = app.spin_n_gap.value()
        kick_gap_t = app.spin_t_gap.value()
        total_len = wb + (2 * truck_l_val) + kick_gap_n + kick_gap_t + nose_l + tail_l
        
        if app.spin_length.value() < total_len:
            app.flash_widget(app.spin_length)
            app.log(f"Mold Length auto-increased to {total_len}mm (Total Board Length)", "WARN")
        app.spin_length.setMinimum(total_len)

        # --- Dynamic Shift Guard ---
        # Prevents OpenCASCADE core dump by keeping the asymmetric shape strictly inside the mold block
        safety_margin = 2.0
        max_shift = max(0.0, (app.spin_length.value() - total_len) / 2.0 - safety_margin)
        app.spin_shape_offset_y.setRange(-max_shift, max_shift)

    finally:
        app._is_validating = False

def sync_editor_from_spinboxes(app):
    """
    Syncs the 2D Interactive Designer widget with the current spinbox values.
    Also handles loading external DXF files to render their preview on the 2D canvas.
    """
    if getattr(app, '_updating_from_editor', False): return
    
    style = app.combo_shape_style.currentText()
    is_bezier = (style == "Custom")
    
    # Enable/Disable Bezier handle controls based on shape style
    app.spin_n_s_y.setEnabled(is_bezier)
    app.spin_n_c1x.setEnabled(is_bezier)
    app.spin_n_c1y.setEnabled(is_bezier)
    app.spin_n_c2x.setEnabled(is_bezier)
    app.spin_t_s_y.setEnabled(is_bezier)
    app.spin_t_c1x.setEnabled(is_bezier)
    app.spin_t_c1y.setEnabled(is_bezier)
    app.spin_t_c2x.setEnabled(is_bezier)
    
    app.chk_sym.setEnabled(is_bezier)
    if not is_bezier:
        app.chk_sym.setChecked(False)
    
    # Fetch DXF points if a custom library shape is selected
    if not is_bezier:
        total_l = (app.spin_wb.value()) + (app.spin_truck_l.value() * 2) + \
                  (app.spin_n_gap.value() + app.spin_nose_len.value()) + \
                  (app.spin_t_gap.value() + app.spin_tail_len.value())
        pts, _ = shape_loader.load_and_scale_dxf(style, app.spin_board_w.value(), total_l, app.spin_shape_offset_y.value())
        app.shape_editor.set_custom_shape(pts if pts else [])
    else:
        app.shape_editor.set_custom_shape([])

    # Update the interactive handles depending on which target (Nose/Tail) is being edited
    target = app.combo_edit_target.currentText()
    if target == "Nose":
        app.shape_editor.set_values(app.spin_n_s_y.value(), app.spin_n_c1x.value(), app.spin_n_c1y.value(), app.spin_n_c2x.value())
        length = app.spin_nose_len.value()
        gap_val = app.spin_n_gap.value()
    else:
        app.shape_editor.set_values(app.spin_t_s_y.value(), app.spin_t_c1x.value(), app.spin_t_c1y.value(), app.spin_t_c2x.value())
        length = app.spin_tail_len.value()
        gap_val = app.spin_t_gap.value()
        
    # Pass hardware context to the 2D widget so it can draw trucks, flares, and kick lines accurately
    app.shape_editor.set_board_context(
        target=target, length=length, width=app.spin_board_w.value(),
        wb=app.spin_wb.value(), truck_l=app.spin_truck_l.value(),
        truck_w=app.spin_truck_w.value(), truck_d=app.spin_truck_d.value(),
        gap=gap_val, rounding=app.spin_fillet_yellow.value(),
        flare_en=app.chk_flares.isChecked(), flare_l=app.spin_flare_l.value(),
        flare_w=app.spin_flare_w.value(), flare_y=app.spin_flare_py.value()
    )

def update_params_object(app):
    """
    Gathers all values from the UI input widgets and commits them to the internal `app.params` object.
    This object serves as the sole payload passed to the CadQuery 3D engine in the background thread.
    """
    p = app.params
    p.MoldType = app.combo_type.currentText()
    p.ShapeStyle = app.combo_shape_style.currentText()
    p.ShapeOffsetY = app.spin_shape_offset_y.value()
    p.SideLocks = app.chk_sidelocks.isChecked()
    p.AddTopShaper = app.chk_top_shaper.isChecked()
    p.AddFillet = app.chk_fillet.isChecked()
    p.FilletRadius = app.spin_fillet_rad.value()
    p.AddGuideHoles = app.chk_guide_d.isChecked()
    p.GuideDiameter = app.spin_guide_d.value()
    
    if hasattr(app, 'combo_guide_count'):
        p.GuideHoleCount = int(app.combo_guide_count.currentText())
    if hasattr(app, 'spin_guide_ox'):
        p.GuideOffsetX = app.spin_guide_ox.value()
    if hasattr(app, 'spin_guide_oy'):
        p.GuideOffsetY = app.spin_guide_oy.value()
        
    p.AddIndicators = app.chk_indicators.isChecked()
    
    p.MoldLength = app.spin_length.value()
    p.MoldCoreWidth = app.spin_width.value()
    p.MoldBaseHeight = app.spin_base_h.value()
    p.MoldBaseWidth = app.spin_base_w.value()
    p.MoldCoreHeight = app.spin_core_h.value()
    p.MoldGap = app.spin_mold_gap.value()
    
    p.Wheelbase = app.spin_wb.value()
    p.BoardWidth = app.spin_board_w.value()
    p.ConcaveDrop = app.spin_concave.value()
    p.ConcaveLength = app.spin_concave_len.value()
    p.TubWidth = app.spin_tub.value()
    p.VeneerThickness = app.spin_veneer.value()
    
    p.NoseAngle = app.spin_nose_ang.value()
    p.TailAngle = app.spin_tail_ang.value()
    p.NoseLength = app.spin_nose_len.value()
    p.TailLength = app.spin_tail_len.value()
    
    p.NoseTransitionLength = app.spin_n_trans.value()
    p.TailTransitionLength = app.spin_t_trans.value()
    p.NoseKickGap = app.spin_n_gap.value()
    p.TailKickGap = app.spin_t_gap.value()

    p.TruckHoleDistL = app.spin_truck_l.value()
    p.TruckHoleDistW = app.spin_truck_w.value()
    p.TruckHoleDiam = app.spin_truck_d.value()
    
    if hasattr(app, 'chk_sidelocks'): p.SideLocks = app.chk_sidelocks.isChecked()
    if hasattr(app, 'chk_fillet'): p.AddFillet = app.chk_fillet.isChecked()
    if hasattr(app, 'chk_guide_d'): p.AddGuideHoles = app.chk_guide_d.isChecked()
    if hasattr(app, 'combo_guide_count'): p.GuideHoleCount = int(app.combo_guide_count.currentText())
    if hasattr(app, 'spin_guide_ox'): p.GuideOffsetX = app.spin_guide_ox.value()
    if hasattr(app, 'spin_guide_oy'): p.GuideOffsetY = app.spin_guide_oy.value()
    if hasattr(app, 'chk_indicators'): p.AddIndicators = app.chk_indicators.isChecked()
    if hasattr(app, 'chk_top_shaper'): p.AddTopShaper = app.chk_top_shaper.isChecked()
    if hasattr(app, 'spin_shaper_h'): p.ShaperHeight = app.spin_shaper_h.value()
    if hasattr(app, 'spin_fillet_yellow'): p.FilletYellow = app.spin_fillet_yellow.value()
    if hasattr(app, 'spin_shape_offset_y'): p.ShapeOffsetY = app.spin_shape_offset_y.value()
    if hasattr(app, 'chk_mold_pins'): p.AddMoldTruckPins = app.chk_mold_pins.isChecked()
    if hasattr(app, 'chk_shaper_pins'): p.AddShaperTruckPins = app.chk_shaper_pins.isChecked()
    if hasattr(app, 'chk_flares'):
        p.AddWheelFlares = app.chk_flares.isChecked()
        p.FlareHeight = app.spin_flare_h.value()
        p.FlareLength = app.spin_flare_l.value()
        p.FlareWidth = app.spin_flare_w.value()
        p.FlarePosY = app.spin_flare_py.value()
    
    p.NoseCtrl1X = app.spin_n_c1x.value()
    p.NoseCtrl1Y = app.spin_n_c1y.value()
    p.NoseCtrl2X = app.spin_n_c2x.value()
    p.NoseStraightP = app.spin_n_s_y.value()
    
    p.TailCtrl1X = app.spin_t_c1x.value()
    p.TailCtrl1Y = app.spin_t_c1y.value()
    p.TailCtrl2X = app.spin_t_c2x.value()
    p.TailStraightP = app.spin_t_s_y.value()

def reset_to_defaults(app):
    """
    Restores all UI inputs to their factory defaults (defined in cq_model.MoldParams).
    Temporarily suspends the 3D rendering pipeline during the reset to avoid massive lag.
    """
    app.is_updating_preset = True 
    try:
        default = cq_model.MoldParams()
        app.spin_length.setValue(default.MoldLength)
        app.spin_width.setValue(default.MoldCoreWidth)
        app.spin_base_h.setValue(default.MoldBaseHeight)
        app.spin_base_w.setValue(default.MoldBaseWidth)
        app.spin_core_h.setValue(default.MoldCoreHeight)
        app.spin_wb.setValue(default.Wheelbase)
        app.spin_board_w.setValue(default.BoardWidth)
        app.spin_concave.setValue(default.ConcaveDrop)
        app.spin_concave_len.setValue(default.ConcaveLength)
        app.spin_tub.setValue(default.TubWidth)
        app.spin_nose_ang.setValue(default.NoseAngle)
        app.spin_tail_ang.setValue(default.TailAngle)
        app.spin_nose_len.setValue(default.NoseLength)
        app.spin_tail_len.setValue(default.TailLength)
        
        app.spin_n_trans.setValue(default.NoseTransitionLength)
        app.spin_t_trans.setValue(default.TailTransitionLength)
        app.spin_n_gap.setValue(default.NoseKickGap)
        app.spin_t_gap.setValue(default.TailKickGap)
        
        app.spin_mold_gap.setValue(default.MoldGap)
        app.spin_veneer.setValue(default.VeneerThickness)
        
        app.spin_truck_l.setValue(default.TruckHoleDistL)
        app.spin_truck_w.setValue(default.TruckHoleDistW)
        app.spin_truck_d.setValue(default.TruckHoleDiam)

        if hasattr(app, 'chk_sidelocks'): app.chk_sidelocks.setChecked(default.SideLocks)
        if hasattr(app, 'chk_fillet'): app.chk_fillet.setChecked(default.AddFillet)
        if hasattr(app, 'chk_guide_d'): 
            app.chk_guide_d.setChecked(default.AddGuideHoles)
            if hasattr(app, 'combo_guide_count'):
                app.combo_guide_count.setCurrentText(str(default.GuideHoleCount))
            if hasattr(app, 'spin_guide_ox'):
                app.spin_guide_ox.setValue(default.GuideOffsetX)
            if hasattr(app, 'spin_guide_oy'):
                app.spin_guide_oy.setValue(default.GuideOffsetY)
        if hasattr(app, 'chk_indicators'): app.chk_indicators.setChecked(default.AddIndicators)
        if hasattr(app, 'chk_top_shaper'): app.chk_top_shaper.setChecked(default.AddTopShaper)
        if hasattr(app, 'spin_shaper_h'): app.spin_shaper_h.setValue(default.ShaperHeight)
        if hasattr(app, 'spin_fillet_yellow'): app.spin_fillet_yellow.setValue(default.FilletYellow)
        if hasattr(app, 'spin_shape_offset_y'): app.spin_shape_offset_y.setValue(default.ShapeOffsetY)
        if hasattr(app, 'chk_mold_pins'): app.AddMoldTruckPins = app.chk_mold_pins.isChecked()
        if hasattr(app, 'chk_shaper_pins'): app.AddShaperTruckPins = app.chk_shaper_pins.isChecked()
        if hasattr(app, 'chk_flares'):
            app.chk_flares.setChecked(default.AddWheelFlares)
            app.spin_flare_h.setValue(default.FlareHeight)
            app.spin_flare_l.setValue(default.FlareLength)
            app.spin_flare_w.setValue(default.FlareWidth)
            app.spin_flare_py.setValue(default.FlarePosY)
        
        app.spin_n_c1x.setValue(default.NoseCtrl1X)
        app.spin_n_c1y.setValue(default.NoseCtrl1Y)
        app.spin_n_c2x.setValue(default.NoseCtrl2X)
        app.spin_n_s_y.setValue(default.NoseStraightP)
        
        app.spin_t_c1x.setValue(default.TailCtrl1X)
        app.spin_t_c1y.setValue(default.TailCtrl1Y)
        app.spin_t_c2x.setValue(default.TailCtrl2X)
        app.spin_t_s_y.setValue(default.TailStraightP)
        
        # Enforce mechanical limits on the newly set default values
        validate_cross_dependencies(app)
        app.log("All parameters reset to default values.", "INFO")

    finally:
        # Re-enable the pipeline and trigger a single master render
        app.is_updating_preset = False
        
    app.start_preview()