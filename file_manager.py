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
    Loads parameters from a chosen JSON preset.
    Uses the universal ui_sync.apply_state_to_ui for bulletproof mapping.
    """
    import ui_sync
    if preset_name == "Default / Reset":
        ui_sync.reset_to_defaults(app)
        return
    if preset_name not in app.presets_data: 
        return
    
    data = app.presets_data[preset_name]
    loaded_params = cq_model.MoldParams()
    
    # Safely update the fresh params object with the JSON data
    for key, value in data.items():
        if hasattr(loaded_params, key):
            # Ensure string booleans from older JSONs are parsed correctly
            if isinstance(value, str):
                if value.lower() == 'true': 
                    value = True
                elif value.lower() == 'false': 
                    value = False
            setattr(loaded_params, key, value)
            
    # Apply the fully assembled object to the UI
    ui_sync.apply_state_to_ui(app, loaded_params)

def save_preset(app):
    """
    Gathers current UI parameters and saves them as a new named preset in the JSON file.
    Automatically refreshes the preset dropdown list upon completion without triggering false loads.
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
                try: 
                    data = json.load(f)
                except Exception: 
                    pass
        
        # Commit current UI values to the parameters object
        app.update_params_object()
        current_params = app.params.__dict__.copy()
        current_params.pop("MoldType", None)
        current_params.pop("ExtremeMode", None)
        
        data[preset_name] = current_params
        
        with open(preset_file, "w") as f: 
            json.dump(data, f, indent=4)
            
        QMessageBox.information(app, "Success", f"Preset '{preset_name}' saved successfully!")
        
        # Refresh the UI list
        load_databases(app)
        
        app.combo_preset.blockSignals(True)
        app.combo_preset.clear()
        app.combo_preset.addItem("Default / Reset")
        app.combo_preset.addItems(sorted(app.presets_data.keys()))
        
        # Unblock signals BEFORE setting the text to natively trigger the button state update
        app.combo_preset.blockSignals(False)
        app.combo_preset.setCurrentText(preset_name)

def load_config_file(app):
    """
    Parses a legacy or custom '.txt' configuration file. 
    Ideal for loading parameters exported alongside STL files.
    """
    path, _ = QFileDialog.getOpenFileName(app, "Load Configuration", "", "Text Files (*.txt);;All Files (*)")
    if not path: 
        return 
    try:
        with open(path, 'r') as f: 
            lines = f.readlines()
        parsed_data = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith("---"): 
                continue
            if line and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    parsed_data[parts[0].strip()] = parts[1].strip()
        
        if not parsed_data:
            app.log("Invalid or empty configuration file.", "ERROR")
            QMessageBox.warning(app, "Warning", "Could not read parameters from this file.")
            return

        apply_parsed_data_to_ui(app, parsed_data)
        
        app.log(f"Configuration loaded successfully from {os.path.basename(path)}")
    except Exception as e:
        app.on_error(f"Error loading config: {e}")

def apply_parsed_data_to_ui(app, data):
    """
    Sub-helper that populates every UI widget based on a raw dictionary of strings.
    Uses the universal ui_sync.apply_state_to_ui for bulletproof mapping.
    """
    import ui_sync
    loaded_params = cq_model.MoldParams()
    
    for key, value_str in data.items():
        if hasattr(loaded_params, key):
            orig_val = getattr(loaded_params, key)
            try:
                # Cast the string back to its intended data type based on factory defaults
                if isinstance(orig_val, bool):
                    setattr(loaded_params, key, value_str.lower() == "true")
                elif isinstance(orig_val, int):
                    setattr(loaded_params, key, int(float(value_str)))
                elif isinstance(orig_val, float):
                    setattr(loaded_params, key, float(value_str))
                else:
                    setattr(loaded_params, key, value_str)
            except ValueError:
                pass
                
    # Handle legacy txt keys if present
    if "TransitionLength" in data:
        try: 
            val = float(data["TransitionLength"])
            loaded_params.NoseTransitionLength = val
            loaded_params.TailTransitionLength = val
        except ValueError: 
            pass

    if "KickGap" in data:
        try: 
            val = float(data["KickGap"])
            loaded_params.NoseKickGap = val
            loaded_params.TailKickGap = val
        except ValueError: 
            pass

    # Retain the requested MoldType from the txt file
    if "MoldType" in data:
        idx = app.combo_type.findText(data["MoldType"])
        if idx >= 0: 
            app.combo_type.setCurrentIndex(idx)

    ui_sync.apply_state_to_ui(app, loaded_params)

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
        
        app.combo_preset.blockSignals(True)
        app.combo_preset.clear()
        app.combo_preset.addItem("Default / Reset")
        app.combo_preset.addItems(sorted(app.presets_data.keys()))
        
        # Unblock signals BEFORE changing index so apply_main_preset triggers naturally
        app.combo_preset.blockSignals(False)
        app.combo_preset.setCurrentIndex(0)

def export_step(app):
    """
    Exports the current 3D model exclusively as a STEP file 
    for pure mathematically perfect curves.
    """
    if not app.current_result: 
        return
    
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
                    if k != "ExtremeMode":
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
    if not save_dir: 
        return
    
    # Prompt for a Project Name to create a dedicated subfolder
    default_name = f"MoldForged_{datetime.datetime.now().strftime('%y%m%d_%H%M')}"
    project_name, ok_name = QInputDialog.getText(
        app, 
        "Project Name", 
        "Enter a name for this project (a dedicated folder will be created):",
        text=default_name
    )
    if not ok_name or not project_name.strip(): 
        return
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
                if k not in ["MoldType", "ExtremeMode"]: 
                    f.write(f"{k}: {v}\n")
                    
        QMessageBox.information(app, "Export Completed", f"Project successfully exported into:\n{project_dir}")
    except Exception as e:
        app.on_error(f"Error during export: {e}")
    finally:
        # Restore the original mold type in the UI to match the current view
        app.params.MoldType = original_type
        app.ui_loading(False)

def get_base_dir():
    """Helper to locate the writable application directory in PyInstaller."""
    if getattr(sys, 'frozen', False): 
        base_dir = os.path.dirname(sys.executable)
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
            base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
        return base_dir
    else: 
        return os.path.dirname(os.path.abspath(__file__))

def save_last_session(app):
    """
    Dumps the current parameter object to a session file on exit.
    Also captures the purely visual state of the preset dropdown.
    """
    path = os.path.join(get_base_dir(), "last_session.json")
    try:
        # Copy the parameters dictionary to avoid altering the active object
        session_data = app.params.__dict__.copy()
        
        # Inject the active preset name as a special UI-only key
        if hasattr(app, 'combo_preset'):
            session_data["_ActivePreset"] = app.combo_preset.currentText()
            
        with open(path, 'w') as f:
            json.dump(session_data, f, indent=4)
    except Exception:
        pass  # Fail silently on exit if there are permission issues

def load_last_session(app):
    """
    Loads the session file on startup and pushes it to the UI.
    Restores both the physical parameters and the visual preset dropdown state.
    """
    import ui_sync
    path = os.path.join(get_base_dir(), "last_session.json")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Extract the UI-only preset name (defaults to Reset if missing)
            active_preset = data.pop("_ActivePreset", "Default / Reset")
            
            # Create a fresh params object
            loaded_params = cq_model.MoldParams()
            
            # Update it safely with the loaded dictionary
            for key, value in data.items():
                if hasattr(loaded_params, key):
                    setattr(loaded_params, key, value)
            
            # Apply to UI
            ui_sync.apply_state_to_ui(app, loaded_params)
            
            # --- RESTORE THE PRESET DROPDOWN STATE ---
            if hasattr(app, 'combo_preset'):
                # Block signals so setting the text doesn't trigger a false reload
                app.combo_preset.blockSignals(True)
                app.combo_preset.setCurrentText(active_preset)
                # Update the Delete/Reset button visual state to match the loaded text
                if hasattr(app, 'btn_delete_preset'):
                    clean_text = active_preset.replace("[M] ", "")
                    if clean_text == "Default / Reset" or clean_text == "Custom":
                        app.btn_delete_preset.setText("Reset")
                        app.btn_delete_preset.setStyleSheet("QPushButton { color: #ff6b6b; } QPushButton:hover { background-color: #fa5b21; }")
                    else:
                        app.btn_delete_preset.setText("Delete")
                        app.btn_delete_preset.setStyleSheet("QPushButton { color: #ff6b6b; } QPushButton:hover { background-color: #5a2a2a; }")
                app.combo_preset.blockSignals(False)
            
            app.log("Last session state restored automatically.", "INFO")
            return True
        except Exception as e:
            app.log(f"Failed to load last session: {e}", "WARN")
    return False