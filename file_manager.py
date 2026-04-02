"""
File Manager Module
Handles data persistence, including loading/saving JSON presets, 
parsing custom configuration text files, and exporting 3D STL models 
with high-precision tolerances.
"""

import os
import sys
import json
import datetime
import cadquery as cq
import cq_model
from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QApplication

def load_databases(app):
    """
    Loads the local JSON database containing deck and mold presets.
    Populates the 'presets_data' dictionary in the main application.
    """
    if getattr(sys, 'frozen', False): 
        base_dir = os.path.dirname(sys.executable)
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
            base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
    else: 
        base_dir = os.path.dirname(os.path.abspath(__file__))

    path_presets = os.path.join(base_dir, "fb_presets.json")
    
    if os.path.exists(path_presets):
        try:
            with open(path_presets, 'r') as f:
                app.presets_data = json.load(f)
        except Exception as e:
            print(f"Error loading presets: {e}")

def apply_main_preset(app, preset_name):
    """
    Maps parameters from a chosen JSON preset to the UI spinboxes and combos.
    Uses a dictionary mapping to efficiently update all numeric inputs.
    """
    if preset_name == "Default / Reset":
        app.reset_to_defaults()
        return
    if preset_name not in app.presets_data: return
    
    # Silence the UI update signal to prevent multiple re-renders during batch update
    app.is_updating_preset = True
    try:
        data = app.presets_data[preset_name]
        
        # Define the mapping between JSON keys and specific UI SpinBoxes
        mapping = { 
            "MoldCoreHeight": app.spin_core_h, "Wheelbase": app.spin_wb, "ConcaveDrop": app.spin_concave, 
            "NoseLength": app.spin_nose_len, "TailLength": app.spin_tail_len, "NoseAngle": app.spin_nose_ang, 
            "TailAngle": app.spin_tail_ang, "ConcaveLength": app.spin_concave_len, "TubWidth": app.spin_tub, 
            "NoseTransitionLength": app.spin_n_trans, "TailTransitionLength": app.spin_t_trans,
            "NoseKickGap": app.spin_n_gap, "TailKickGap": app.spin_t_gap,
            "MoldGap": app.spin_mold_gap, "VeneerThickness": app.spin_veneer,
            "TruckHoleDistL": app.spin_truck_l, "TruckHoleDistW": app.spin_truck_w, "TruckHoleDiam": app.spin_truck_d,
            "NoseCtrl1X": app.spin_n_c1x, "NoseCtrl1Y": app.spin_n_c1y, "NoseCtrl2X": app.spin_n_c2x, "NoseStraightP": app.spin_n_s_y,
            "TailCtrl1X": app.spin_t_c1x, "TailCtrl1Y": app.spin_t_c1y, "TailCtrl2X": app.spin_t_c2x, "TailStraightP": app.spin_t_s_y,
            "FlareHeight": app.spin_flare_h, "FlareLength": app.spin_flare_l,
            "FlareWidth": app.spin_flare_w, "FlarePosY": app.spin_flare_py,
            "ShapeOffsetY": app.spin_shape_offset_y
        }
        for key, val in data.items():
            if key in mapping: mapping[key].setValue(float(val))
            if key == "ShapeStyle": 
                app.combo_shape_style.setCurrentText(str(val))
            # Handle legacy keys or consolidated parameters
            if key == "TransitionLength":
                app.spin_n_trans.setValue(float(val)); app.spin_t_trans.setValue(float(val))
            if key == "KickGap":
                app.spin_n_gap.setValue(float(val)); app.spin_t_gap.setValue(float(val))

        # --- FIX: CHECKBOX STATE MANAGEMENT ---
        check_map = { 
            "SideLocks": app.chk_sidelocks, "AddFillet": app.chk_fillet, 
            "AddGuideHoles": app.chk_guide_d, "AddIndicators": app.chk_indicators, 
            "AddWheelFlares": app.chk_flares 
        }
        for key, checkbox in check_map.items():
            if key in data:
                # Support both strict booleans and string representations ("True"/"False")
                is_checked = str(data[key]).lower() == "true"
                checkbox.setChecked(is_checked)

        # --- FIX: AUTOMATIC SYMMETRY DETECTION ---
        is_sym = True
        if "NoseAngle" in data and "TailAngle" in data:
            if float(data["NoseAngle"]) != float(data["TailAngle"]): is_sym = False
        if "NoseLength" in data and "TailLength" in data:
            if float(data["NoseLength"]) != float(data["TailLength"]): is_sym = False
        if "NoseCtrl1X" in data and "TailCtrl1X" in data:
            if float(data["NoseCtrl1X"]) != float(data["TailCtrl1X"]): is_sym = False

        app.chk_sym.blockSignals(True)
        app.chk_sym.setChecked(is_sym)
        app.chk_sym.blockSignals(False)

    finally:
        app.is_updating_preset = False
       
    # Trigger a single master render after all parameters are loaded
    app.start_preview()

def save_preset(app):
    """
    Gathers current UI parameters and saves them as a new named preset in the JSON file.
    Automatically refreshes the preset dropdown list upon completion.
    """
    preset_name, ok = QInputDialog.getText(app, "Save Preset", "Preset Name:")
    if ok and preset_name:
        if getattr(sys, 'frozen', False): 
            base_dir = os.path.dirname(sys.executable)
            if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
                base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
        else: 
            base_dir = os.path.dirname(__file__)

        preset_file = os.path.join(base_dir, "fb_presets.json")
        data = {}
        if os.path.exists(preset_file):
            with open(preset_file, "r") as f:
                try: data = json.load(f)
                except: pass
        
        # Commit current UI values to the parameters object
        app.update_params_object()
        current_params = app.params.__dict__.copy()
        # Remove 'MoldType' from preset so it doesn't force a specific piece when loaded
        current_params.pop("MoldType", None)
        
        data[preset_name] = current_params
        
        with open(preset_file, "w") as f: 
            json.dump(data, f, indent=4)
            
        QMessageBox.information(app, "Success", f"Preset '{preset_name}' saved successfully!")
        
        # Refresh the UI list
        load_databases(app)
        app.combo_preset.clear()
        app.combo_preset.addItem("Default / Reset")
        app.combo_preset.addItems(sorted(app.presets_data.keys()))
        app.combo_preset.setCurrentText(preset_name)

def load_config_file(app):
    """
    Parses a legacy or custom '.txt' configuration file. 
    Ideal for loading parameters exported alongside STL files.
    """
    path, _ = QFileDialog.getOpenFileName(app, "Load Configuration", "", "Text Files (*.txt);;All Files (*)")
    if not path: return 
    try:
        with open(path, 'r') as f: lines = f.readlines()
        parsed_data = {}
        parsing_started = False
        
        for line in lines:
            line = line.strip()
            # Start parsing after the header separator
            if line.startswith("---"): parsing_started = True; continue
            if line and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    parsed_data[parts[0].strip()] = parts[1].strip()
        
        if not parsed_data:
            app.log("Invalid or empty configuration file.", "ERROR")
            QMessageBox.warning(app, "Warning", "Could not read parameters from this file.")
            return

        # Apply the parsed dictionary to the actual UI widgets
        apply_parsed_data_to_ui(app, parsed_data)
        
        app.log(f"Configuration loaded successfully from {os.path.basename(path)}")
        app.start_preview()
    except Exception as e:
        app.on_error(f"Error loading config: {e}")

def apply_parsed_data_to_ui(app, data):
    """
    Sub-helper that populates every UI widget based on a raw dictionary.
    Includes comprehensive mapping for spinboxes, checkboxes, and combos.
    """
    app.is_updating_preset = True
    try:
        spin_map = { 
            "MoldLength": app.spin_length, "MoldCoreWidth": app.spin_width, "MoldBaseHeight": app.spin_base_h, 
            "MoldBaseWidth": app.spin_base_w, "MoldCoreHeight": app.spin_core_h, "Wheelbase": app.spin_wb, 
            "BoardWidth": app.spin_board_w, "ConcaveDrop": app.spin_concave, "ConcaveLength": app.spin_concave_len, 
            "TubWidth": app.spin_tub, "NoseAngle": app.spin_nose_ang, "TailAngle": app.spin_tail_ang, 
            "NoseLength": app.spin_nose_len, "TailLength": app.spin_tail_len, 
            "NoseTransitionLength": app.spin_n_trans, "TailTransitionLength": app.spin_t_trans,
            "NoseKickGap": app.spin_n_gap, "TailKickGap": app.spin_t_gap,
            "MoldGap": app.spin_mold_gap, "VeneerThickness": app.spin_veneer,
            "TruckHoleDistL": app.spin_truck_l, "TruckHoleDistW": app.spin_truck_w, "TruckHoleDiam": app.spin_truck_d,
            "FilletRadius": app.spin_fillet_rad, "GuideDiameter": app.spin_guide_d,
            "ShaperHeight": app.spin_shaper_h, "FilletYellow": app.spin_fillet_yellow,
            "NoseCtrl1X": app.spin_n_c1x, "NoseCtrl1Y": app.spin_n_c1y,
            "NoseCtrl2X": app.spin_n_c2x, "NoseStraightP": app.spin_n_s_y,
            "TailCtrl1X": app.spin_t_c1x, "TailCtrl1Y": app.spin_t_c1y,
            "TailCtrl2X": app.spin_t_c2x, "TailStraightP": app.spin_t_s_y,
            "FlareHeight": app.spin_flare_h, "FlareLength": app.spin_flare_l,
            "FlareWidth": app.spin_flare_w, "FlarePosY": app.spin_flare_py,
            "ShapeOffsetY": app.spin_shape_offset_y
        }
        
        for key, spinbox in spin_map.items():
            if key in data:
                try: spinbox.setValue(float(data[key]))
                except ValueError: pass 
                
        if "ShapeStyle" in data:
            app.combo_shape_style.setCurrentText(str(data["ShapeStyle"]))

        # Handle unified/legacy keys
        if "TransitionLength" in data:
            try: 
                val = float(data["TransitionLength"])
                app.spin_n_trans.setValue(val); app.spin_t_trans.setValue(val)
            except ValueError: pass

        if "KickGap" in data:
            try: 
                val = float(data["KickGap"])
                app.spin_n_gap.setValue(val); app.spin_t_gap.setValue(val)
            except ValueError: pass

        check_map = { "SideLocks": app.chk_sidelocks, "AddFillet": app.chk_fillet, 
                     "AddGuideHoles": app.chk_guide_d, "AddIndicators": app.chk_indicators, 
                     "AddWheelFlares": app.chk_flares }
        for key, checkbox in check_map.items():
            if key in data: checkbox.setChecked(data[key] == "True")
        
        if "MoldType" in data:
            idx = app.combo_type.findText(data["MoldType"])
            if idx >= 0: app.combo_type.setCurrentIndex(idx)

        # --- FIX: AUTOMATIC SYMMETRY DETECTION FOR .TXT FILES ---
        is_sym = True
        try:
            if "NoseAngle" in data and "TailAngle" in data:
                if float(data["NoseAngle"]) != float(data["TailAngle"]): is_sym = False
            if "NoseLength" in data and "TailLength" in data:
                if float(data["NoseLength"]) != float(data["TailLength"]): is_sym = False
            if "NoseCtrl1X" in data and "TailCtrl1X" in data:
                if float(data["NoseCtrl1X"]) != float(data["TailCtrl1X"]): is_sym = False
        except ValueError:
            pass
            
        app.chk_sym.blockSignals(True)
        app.chk_sym.setChecked(is_sym)
        app.chk_sym.blockSignals(False)
        
        if "MoldType" in data:
            idx = app.combo_type.findText(data["MoldType"])
            if idx >= 0: app.combo_type.setCurrentIndex(idx)
    finally:
        app.is_updating_preset = False

def delete_preset(app):
    """
    Deletes the currently selected custom preset from the JSON file.
    Prevents deletion of the hardcoded 'Default / Reset' state.
    """
    preset_name = app.combo_preset.currentText()
    if preset_name == "Default / Reset":
        QMessageBox.warning(app, "Warning", "Cannot delete the default reset state.")
        return
    
    if not preset_name or preset_name not in app.presets_data:
        return

    reply = QMessageBox.question(
        app, "Confirm Delete", 
        f"Are you sure you want to permanently delete the preset '{preset_name}'?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        if getattr(sys, 'frozen', False): 
            base_dir = os.path.dirname(sys.executable)
            if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
                base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
        else: 
            base_dir = os.path.dirname(__file__)

        preset_file = os.path.join(base_dir, "fb_presets.json")
        if os.path.exists(preset_file):
            with open(preset_file, "r") as f:
                try: 
                    data = json.load(f)
                except Exception: 
                    data = {}
            
            if preset_name in data:
                del data[preset_name]
                with open(preset_file, "w") as f: 
                    json.dump(data, f, indent=4)
        
        app.log(f"Preset '{preset_name}' successfully deleted.", "WARN")
        
        # Refresh the database and UI
        load_databases(app)
        
        app.is_updating_preset = True
        app.combo_preset.clear()
        app.combo_preset.addItem("Default / Reset")
        app.combo_preset.addItems(sorted(app.presets_data.keys()))
        app.is_updating_preset = False
        
        # Force the UI back to the default state to avoid ghostly parameters
        app.combo_preset.setCurrentIndex(0)
        apply_main_preset(app, "Default / Reset")

def export_step(app):
    """
    Exports the current 3D model exclusively as a STEP file 
    for pure mathematically perfect curves.
    """
    if not app.current_result: return
    
    default_name = f"{app.params.MoldType}"
    
    path, _ = QFileDialog.getSaveFileName(
        app, 
        "Save 3D Model", 
        default_name, 
        "STEP File (*.step)"
    )
    
    if path:
        try:
            if not path.lower().endswith('.step'): 
                path += ".step"
            
            cq.exporters.export(app.current_result, path)
            
            base_path = os.path.splitext(path)[0]
            config_path = base_path + "_config.txt"
            with open(config_path, "w") as f:
                f.write(f"MOLD F.O.R.G.E. - Export Report\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-" * 40 + "\n")
                for k, v in app.params.__dict__.items(): 
                    f.write(f"{k}: {v}\n")
            
            app.log(f"Export successful: {os.path.basename(path)} and config file.")
            QMessageBox.information(app, "Success", "3D Model (STEP) and Configuration saved!")
        except Exception as e:
            app.on_error(str(e))

def batch_export(app):
    """
    Automated production pipeline.
    Sequentially generates and exports the Male Mold, Female Mold, and Shaper Template.
    Automatically creates a dedicated subfolder to prevent cluttering the user's directories.
    """
    save_dir = QFileDialog.getExistingDirectory(app, "Select Export Destination")
    if not save_dir: return
    
    # Prompt for a Project Name to create a dedicated subfolder
    default_name = f"MoldForged_{datetime.datetime.now().strftime('%y%m%d_%H%M')}"
    project_name, ok_name = QInputDialog.getText(
        app, 
        "Project Name", 
        "Enter a name for this project (a dedicated folder will be created):",
        text=default_name
    )
    if not ok_name or not project_name.strip(): return
    project_name = project_name.strip()
    
    # Create the dedicated subfolder
    project_dir = os.path.join(save_dir, project_name)
    try:
        os.makedirs(project_dir, exist_ok=True)
    except Exception as e:
        QMessageBox.critical(app, "Folder Error", f"Could not create project folder:\n{e}")
        return

    parts_to_export = ["Male_Mold", "Female_Mold", "Shaper_Template"]
    original_type = app.params.MoldType 
    
    app.ui_loading(True)
    app.update_params_object()
    
    try:
        for m_type in parts_to_export:
            # Temporarily switch the internal mold type and force a re-generation
            app.params.MoldType = m_type
            # Force UI to process events so the loading bar stays responsive
            QApplication.processEvents()
            
            result = cq_model.build_mold(app.params)
            
            # Export strictly as mathematically perfect STEP
            filepath_step = os.path.join(project_dir, f"{project_name}_{m_type}.step")
            cq.exporters.export(result, filepath_step)
            
        # Create the master batch report inside the new folder
        config_path = os.path.join(project_dir, f"{project_name}_Config.txt")
        with open(config_path, "w") as f:
            f.write(f"MOLD F.O.R.G.E. - Batch Export Report\nProject: {project_name}\nDate: {datetime.datetime.now().strftime('%y-%m-%d %H:%M')}\n" + "-" * 40 + "\n")
            for k, v in app.params.__dict__.items():
                if k != "MoldType": 
                    f.write(f"{k}: {v}\n")
                    
        QMessageBox.information(app, "Export Completed", f"Project successfully exported into:\n{project_dir}")
    except Exception as e:
        app.on_error(f"Error during export: {e}")
    finally:
        # Restore the original mold type in the UI to match the current view
        app.params.MoldType = original_type
        app.ui_loading(False)