"""
Main Application Entry Point - MOLD F.O.R.G.E.
Initializes the PySide6 UI, manages the multi-threaded rendering pipeline, 
and orchestrates communication between the UI components and the CadQuery 3D engine.
"""

import os
import sys
import json
import locale
import tempfile
import subprocess
import urllib.request
import multiprocessing

try:
    from version import __version__ # type: ignore # 
    APP_VERSION = __version__
except ImportError:
    APP_VERSION = "Dev-Build"

# --- CRITICAL FIX FOR MATPLOTLIB DEADLOCK ON MACOS ---
# 1. Force Matplotlib to use a writable temp directory for its cache
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

# 2. Prevent background system processes (like 'fc-list') from inheriting
# PyInstaller's injected library paths, which causes silent infinite deadlocks.
# We temporarily monkey-patch subprocess.Popen so ONLY child processes lose the 
# DYLD_LIBRARY_PATH, allowing the main Python app to load C-extensions safely!
_original_popen = subprocess.Popen

class PatchedPopen(_original_popen):
    def __init__(self, *args, **kwargs):
        env = kwargs.get('env')
        if env is None:
            env = dict(os.environ)
        env.pop('DYLD_LIBRARY_PATH', None)
        kwargs['env'] = env
        super().__init__(*args, **kwargs)

subprocess.Popen = PatchedPopen

try:
    import matplotlib
    matplotlib.use('Agg') # Force non-interactive backend to avoid Qt conflicts
    import matplotlib.font_manager
finally:
    subprocess.Popen = _original_popen # Restore normal behavior

# --- PLATFORM SPECIFIC FIXES ---
os.environ["LC_NUMERIC"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"
try:
    locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
except Exception:
    pass

if sys.platform == 'darwin':
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    os.environ["VTK_RENDERER_BACKEND"] = "OpenGL2"
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    os.environ['QT_LOGGING_RULES'] = 'qt.gui.painting.warning=false;qt.qpa.fonts.warning=false'
    os.environ["EVENT_NOKQUEUE"] = "1" # Fix for certain VTK event loop issues on Mac
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

# LINUX FIX: Force X11/XWayland backend. VTK/OpenGL crashes natively on Wayland.
if sys.platform == 'linux':
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

if getattr(sys, 'frozen', False) and sys.platform == 'win32':
    for module_dir in ['casadi', 'cadquery', 'OCP']:
        dll_path = os.path.join(sys._MEIPASS, module_dir)
        if os.path.exists(dll_path):
            os.add_dll_directory(dll_path)

import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl, QObject
from PySide6.QtGui import QTextCursor, QDesktopServices, QIcon
from community_browser import CommunityBrowserDialog
import shape_loader

# Application Modules
import cq_model
import file_manager
import ui_builder
import ui_sync
import viewer_3d

class EmittingStream(QObject):
    """
    Custom stream object used to intercept standard output (stdout) and 
    standard error (stderr) from the console and redirect it to the UI Log widget.
    """
    textWritten = Signal(str)
    
    def write(self, text):
        self.textWritten.emit(str(text))
        
    def flush(self):
        pass

class GeneratorWorker(QThread):
    """
    Background worker thread dedicated to executing the heavy CadQuery 3D geometry generation.
    Prevents the main Qt GUI thread from freezing during complex lofting operations.
    """
    work_finished = Signal(object) 
    error = Signal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        import time
        start_time = time.time()
        try:
            result = cq_model.build_mold(self.params)
            elapsed = time.time() - start_time
            self.work_finished.emit(result)
        except Exception as e:
            import traceback
            self.error.emit(str(e) + "\n" + traceback.format_exc())

class UpdateCheckerWorker(QThread):
    """
    Background thread that silently queries the public GitHub API.
    If it fails (e.g., no internet connection), it dies silently without UI errors.
    """
    update_found = Signal(str)

    def run(self):
        try:
            url = "https://api.github.com/repos/alessandroabbasciano-cpu/MoldForge/releases/latest"
            
            # Custom header to prevent GitHub API rate limits/blocks
            req = urllib.request.Request(url, headers={'User-Agent': 'MoldForge-App'})
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").replace("v", "")
                
                # Compare fetched version with the existing global APP_VERSION
                # Skip the check if running a Dev-Build
                if APP_VERSION != "Dev-Build" and latest_version and latest_version > APP_VERSION:
                    self.update_found.emit(latest_version)
                    
        except Exception:
            # Zero-trust approach: fail silently on any network or parsing error
            pass
class MoldApp(QMainWindow):
    """
    The Main Window class. Holds the UI state, centralizes event routing,
    and manages the timer for live preview updates.
    """
    def __init__(self):
        super().__init__()
        self._is_loading = True
        self.setWindowTitle(f"MOLD F.O.R.G.E. - Fingerboard Design Suite ({APP_VERSION})")
        self.resize(1450, 950)

        # Global Application Stylesheet (Dark Industrial Theme)
        self.setStyleSheet("""
            * { font-family: 'Segoe UI', 'Consolas', 'Menlo', monospace; }
            QMainWindow, QWidget { background-color: #2b2b2b; color: #e0e0e0; }
            QGroupBox { font-weight: bold; border: 1px solid #4a6984; border-radius: 6px; margin-top: 15px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; color: #66b2ff; }
            QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit { background-color: #3b3b3b; border: 1px solid #555; padding: 4px; border-radius: 3px; }
            QSplitter::handle { background-color: #1a1a1a; width: 4px; }
            QSplitter::handle:hover { background-color: #66b2ff; }
            /* --- TOP MENU BAR --- */
            QMenuBar { background-color: #1a1a1a; color: #e0e0e0; border-bottom: 1px solid #4a6984; }
            QMenuBar::item { background-color: transparent; padding: 6px 12px; }
            QMenuBar::item:selected { background-color: #3b3b3b; color: #66b2ff; border-radius: 3px; }
            /* --- DROPDOWN MENUS --- */
            QMenu { 
                background-color: #252525; 
                border: 2px solid #4a6984; /* Bordo azzurro netto per staccare dal fondo */
                border-radius: 4px; 
                padding: 5px 0px; 
            }
            QMenu::item { 
                padding: 6px 30px 6px 35px; /* Spazio a sinistra per la spunta */
                color: #e0e0e0; 
            }
            QMenu::item:selected { 
                background-color: #4a6984; /* Evidenziazione azzurra al passaggio del mouse */
                color: #ffffff; 
            }
            QMenu::separator { 
                height: 1px; 
                background-color: #444; 
                margin: 4px 10px; 
            }
            /* --- CHECKBOX INDICATORS NEI MENU --- */
            QMenu::indicator { 
                width: 14px; 
                height: 14px; 
                left: 10px; /* Posizione a sinistra */
                border: 1px solid #888; 
                border-radius: 3px; 
            }
            QMenu::indicator:checked { 
                background-color: #e67e22; /* Quadrato arancione ben visibile quando spuntato */
                border: 1px solid #e67e22; 
            }
        """)        
        # Core State Variables
        self.params = cq_model.MoldParams()
        self.is_metric = True
        self.clipping_enabled = False
        self.presets_data = {}
        self.current_result = None

        # --- UPDATE SCHEDULER ---
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(2000)
        self.update_timer.timeout.connect(self.start_preview)

        self.is_updating_preset = True
        
        # Initialize sub-modules
        file_manager.load_databases(self)
        ui_builder.setup_ui(self)
        ui_builder.setup_menu(self)

        # --- STARTUP RENDERING GUARD ---
        self.setup_connections()
        self.sync_editor_from_spinboxes()
        self.is_updating_preset = False

        # --- CONSOLE REDIRECTION ---
        self.stdout_stream = EmittingStream()
        self.stdout_stream.textWritten.connect(self.normal_output_written)
        sys.stdout = self.stdout_stream

        self.stderr_stream = EmittingStream()
        self.stderr_stream.textWritten.connect(self.error_output_written)
        sys.stderr = self.stderr_stream

        # --- INITIALIZATION LOG ---
        self.log("============================", "INFO")
        self.log(f"MOLD F.O.R.G.E. - {APP_VERSION}", "INFO")
        self.log("============================", "INFO")
        self.log("System initialized. Ready to shred.", "INFO")

        self._is_loading = False

        # --- UPDATE CHECKER ---
        self.update_worker = UpdateCheckerWorker()
        self.update_worker.update_found.connect(self.on_update_found)
        self.update_worker.start()
        
        # Force the first explicit render
        QTimer.singleShot(200, self.start_preview)
        
        # --- CLOSE NATIVE SPLASH SCREEN (Cross-platform safe) ---
        # On macOS ARM64, the splash IPC often fails or is not initialized.
        # We skip this entirely on Darwin to avoid KeyError: '_PYI_SPLASH_IPC'.
        if sys.platform != 'darwin':
            try:
                import pyi_splash # type: ignore
                if pyi_splash.is_alive():
                    pyi_splash.close()
            except (ImportError, KeyError):
                # Silently fail if the module or IPC is not available
                pass
    
    def on_update_found(self, latest_version):
        self.log(f">>> NEW VERSION AVAILABLE: v{latest_version} <<<", "WARN")
        self.log("Go to the top menu: 'Help' -> 'Download Updates...' to get it.", "WARN")

    def setup_connections(self):
        self.combo_preset.currentTextChanged.connect(self.apply_main_preset)
        self.combo_shape_style.currentTextChanged.connect(self.on_shape_style_changed)
        self.btn_save_preset.clicked.connect(self.save_preset)
        self.btn_delete_preset.clicked.connect(self.delete_preset)
        self.btn_generate.clicked.connect(self.start_preview)

        for spin in [self.spin_nose_ang, self.spin_nose_len, self.spin_n_trans, self.spin_n_gap, 
                     self.spin_n_c1x, self.spin_n_c1y, self.spin_n_c2x, self.spin_n_s_y]:
            spin.valueChanged.connect(lambda: self.sync_symmetry("Nose"))
            
        for spin in [self.spin_tail_ang, self.spin_tail_len, self.spin_t_trans, self.spin_t_gap, 
                     self.spin_t_c1x, self.spin_t_c1y, self.spin_t_c2x, self.spin_t_s_y]:
            spin.valueChanged.connect(lambda: self.sync_symmetry("Tail"))

        for spin in [self.spin_nose_len, self.spin_tail_len, self.spin_board_w, self.spin_n_gap, 
                     self.spin_t_gap, self.spin_truck_l, self.spin_truck_w, self.spin_truck_d]:
            spin.valueChanged.connect(self.sync_editor_from_spinboxes)

        if hasattr(self, 'spin_fillet_yellow'):
            self.spin_fillet_yellow.valueChanged.connect(self.sync_editor_from_spinboxes)

        if hasattr(self, 'chk_flares'):
            self.chk_flares.stateChanged.connect(self.sync_editor_from_spinboxes)
            self.spin_flare_l.valueChanged.connect(self.sync_editor_from_spinboxes)
            self.spin_flare_w.valueChanged.connect(self.sync_editor_from_spinboxes)
            self.spin_flare_py.valueChanged.connect(self.sync_editor_from_spinboxes)
            
        for spin in [self.spin_width, self.spin_base_w, self.spin_board_w, self.spin_wb,
                     self.spin_nose_len, self.spin_tail_len, self.spin_truck_l, 
                     self.spin_n_gap, self.spin_t_gap, self.spin_n_trans, self.spin_t_trans]:
            spin.valueChanged.connect(self.validate_cross_dependencies)
            
        self.validate_cross_dependencies()    

    def on_shape_style_changed(self, text):
        ui_sync.on_shape_style_changed(self, text)

    def sync_editor_from_spinboxes(self):
        ui_sync.sync_editor_from_spinboxes(self)

    def update_params_object(self):
        ui_sync.update_params_object(self)

    def validate_cross_dependencies(self):
        ui_sync.validate_cross_dependencies(self)

    def reset_to_defaults(self):
        ui_sync.reset_to_defaults(self)

    def sync_symmetry(self, source):
        ui_sync.sync_symmetry(self, source)

    def _clean_modded_combo(self):
        self.combo_preset.blockSignals(True)
        for i in range(self.combo_preset.count()):
            t = self.combo_preset.itemText(i)
            if t.startswith("[M] "):
                self.combo_preset.setItemText(i, t.replace("[M] ", ""))
        self.combo_preset.blockSignals(False)

    def apply_main_preset(self, preset_name):
        clean_name = preset_name.replace("[M] ", "")
        self._clean_modded_combo()
        file_manager.apply_main_preset(self, clean_name)

    def save_preset(self):
        self._clean_modded_combo()
        file_manager.save_preset(self)

    def delete_preset(self):
        current_selection = self.combo_preset.currentText()
        if current_selection == "Custom":
            self.reset_to_defaults()
        else:
            self._clean_modded_combo()
            file_manager.delete_preset(self)

    def load_config_file(self):
        file_manager.load_config_file(self)

    def export_step(self):
        file_manager.export_step(self)

    def batch_export(self):
        file_manager.batch_export(self)

    def on_success(self, result):
        self.current_result = result
        self.ui_loading(False)
        self.action_export.setEnabled(True)
        viewer_3d.render_mold(self, result)

    def on_graphical_shape_changed(self, sy, c1x, c1y, c2x):
        self._updating_from_editor = True 
        if self.combo_edit_target.currentText() == "Nose":
            self.spin_n_s_y.setValue(sy)
            self.spin_n_c1x.setValue(c1x)
            self.spin_n_c1y.setValue(c1y)
            self.spin_n_c2x.setValue(c2x)
        else:
            self.spin_t_s_y.setValue(sy)
            self.spin_t_c1x.setValue(c1x)
            self.spin_t_c1y.setValue(c1y)
            self.spin_t_c2x.setValue(c2x)
        self._updating_from_editor = False
        self.schedule_update()

    def schedule_update(self):
        if getattr(self, 'is_updating_preset', False): return 

        if hasattr(self, 'combo_preset'):
            idx = self.combo_preset.currentIndex()
            text = self.combo_preset.currentText()
            if text != "Custom" and not text.startswith("[M] "):
                self.combo_preset.blockSignals(True)
                self.combo_preset.setItemText(idx, f"[M] {text}")
                self.combo_preset.blockSignals(False)

        if hasattr(self, 'chk_live_update') and not self.chk_live_update.isChecked():
            return

        if hasattr(self, 'update_timer'):
            self.update_timer.start()

    def toggle_extreme_mode(self, enabled):
        """
        Toggles dimensional safety limits on all UI spinboxes and geometry generation.
        Forces Live Update off to prevent calculation loops.
        """
        self.params.ExtremeMode = enabled
        
        if enabled:
            reply = QMessageBox.warning(
                self, 
                "Unleash The Beast",
                "WARNING: Extreme Mode removes all safety limits.\n"
                "You can now input physically impossible dimensions.\n\n"
                "To prevent fatal calculation loops, LIVE PREVIEW is now disabled.\n"
                "Adjust your parameters calmly, then press 'GENERATE MOLD'.\n\n"
                "Proceed at your own risk?", 
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                self.action_extreme.setChecked(False)
                self.params.ExtremeMode = False
                return

            self.log(">>> BEAST MODE UNLEASHED: Safety clamps disabled! <<<", "WARN")
            
            # Force Live Update OFF and disable the checkbox to prevent accidents
            self.chk_live_update.setChecked(False)
            self.chk_live_update.setEnabled(False)
            
            # Unlock all spinboxes to massive values
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'orig_min') and hasattr(widget, 'orig_max'):
                    widget.setMinimum(-9999.0)
                    widget.setMaximum(9999.0)
        else:
            self.log("Safety limits and Live Update access restored.", "INFO")
            
            # Unlock the Live Update checkbox so the user can use it again
            self.chk_live_update.setEnabled(True)
            
            # Restore original safe limits
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'orig_min') and hasattr(widget, 'orig_max'):
                    widget.setMinimum(widget.orig_min)
                    widget.setMaximum(widget.orig_max)
            
    def normal_output_written(self, text):
        t = text.strip()
        if t: self.log(t, "INFO")

    def error_output_written(self, text):
        t = text.strip()
        if t: self.log(t, "ERROR")

    def log(self, message, type="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color_map = {"INFO": "#3498db", "ERROR": "#e74c3c", "WARN": "#f1c40f"}
        color = color_map.get(type, "#e0e0e0")
        message_html = str(message).replace("\n", "<br>")
        self.log_console.appendHtml(
            f"<font color='#888'>[{timestamp}]</font> "
            f"<font color='{color}'><b>{type}:</b></font> "
            f"<font color='#e0e0e0'>{message_html}</font>"
        )
        self.log_console.moveCursor(QTextCursor.End)

    def flash_widget(self, widget):
        if not hasattr(widget, "orig_style"): widget.orig_style = widget.styleSheet()
        widget.setStyleSheet("background-color: #e67e22; color: #ffffff; font-weight: bold;")
        QTimer.singleShot(500, lambda: widget.setStyleSheet(widget.orig_style))

    def on_type_changed(self, text):
        is_mold = text in ["Male_Mold", "Female_Mold"]
        self.chk_sidelocks.setEnabled(is_mold)
        self.chk_fillet.setEnabled(is_mold)
        self.chk_guide_d.setEnabled(is_mold)
        self._has_rendered_once = False
        self.schedule_update()

    def toggle_controls(self):
        is_visible = self.dock_left.isVisible() or self.dock_right.isVisible() or self.dock_bottom.isVisible() or self.dock_designer.isVisible()
        self.dock_left.setVisible(not is_visible)
        self.dock_right.setVisible(not is_visible)
        self.dock_bottom.setVisible(not is_visible)
        self.dock_designer.setVisible(not is_visible)
        state = "Hidden" if is_visible else "Visible"
        self.log(f"Dock panels {state}. Press F11 to toggle.", "INFO")

    def toggle_clipping(self, enabled):
        self.clipping_enabled = enabled
        self.log(f"Clipping plane {'activated' if enabled else 'deactivated'}.", "INFO")
        self.start_preview()

    def toggle_units(self):
        self.is_metric = not self.is_metric
        unit = "Metric (mm)" if self.is_metric else "Imperial (in)"
        self.action_units.setText(f"Unit: {unit}")
        if self.is_metric:
            self.log("Max Dimensions in the Log will now be displayed in Millimeters (mm).", "INFO")
        else:
            self.log("Max Dimensions in the Log will now be displayed in Inches (in). All input parameters remain in mm.", "INFO")
        if self.current_result: self.start_preview()

    def open_support_link(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/moldforge"))

    def show_about_dialog(self):
        about_html = (
            "<div style='text-align: left; padding: 20px;'>"
            "<h1 style='color: #66b2ff; margin: 0 0 5px 0; font-size: 26px;'>MOLD F.O.R.G.E.</h1>"
            "<p style='color: #aaa; font-style: italic; font-weight: bold; font-size: 13px; margin: 0 0 15px 0;'>"
            "<i><b>F</b>ORGE <b>O</b>utputs <b>R</b>ealistic <b>G</b>narly <b>E</b>quipment.</i></p>"
            "<hr style='background-color: #4a6984; height: 1px; border: none; margin: 15px 0;'>"

            "<div style='display: text-align: left; margin: 0 auto 15px auto;'>"
            "<div style='margin-bottom: 5px;'><b>Version:</b> <span style='color: #2ecc71; font-weight: bold;'>{APP_VERSION}</span></div>"
            "<div style='margin-bottom: 5px;'><b>Geometry Engine:</b> <span style='color: #e0e0e0;'>CadQuery / OpenCASCADE</span></div>"
            "<div style='margin-bottom: 5px;'><b>Render Engine:</b> <span style='color: #e0e0e0;'>PyVista / VTK</span></div>"
            "<div style='margin-bottom: 5px;'><b>GUI Framework:</b> <span style='color: #e0e0e0;'>PySide6 (Qt Core)</span></div>"
            "</div>"
            "<hr style='background-color: #4a6984; height: 1px; border: none; margin: 15px 0;'>"
            "<p style='color: #e67e22; font-weight: bold; margin-top: 15px; font-size: 14px;'>"
            "Developed with passion for the fingerboard community.</p>"
            "<p style='font-size: 14px; color: #888; margin-top: 15px;'>"
            "<b>License:</b> Code AGPLv3 / Design CC BY-NC-SA 4.0</p>"
            "</div>"
        )
        QMessageBox.about(self, "About MOLD F.O.R.G.E.", about_html)
    
    def start_preview(self):
        if getattr(self, '_is_loading', False):
            return
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()

        if getattr(self, 'worker', None) and self.worker.isRunning():
            self._render_pending = True
            self.log("Calculation queued...", "INFO")
            return
            
        self._render_pending = False
        self.update_params_object()
        self.ui_loading(True)
        self.worker = GeneratorWorker(self.params)
        self.worker.work_finished.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_error(self, msg):
        self.ui_loading(False)
        QMessageBox.critical(self, "Error", msg)
        if getattr(self, '_render_pending', False):
            QTimer.singleShot(100, self.start_preview)

    def ui_loading(self, loading):
        if loading: 
            self.progress_bar.setRange(0, 100) 
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.log(">>> CALCULATING HIGH-RES GEOMETRY... PLEASE WAIT <<<", "WARN")
            if not hasattr(self, 'fake_timer'):
                from PySide6.QtCore import QTimer
                self.fake_timer = QTimer(self)
                self.fake_timer.timeout.connect(lambda: self.progress_bar.setValue(min(95, self.progress_bar.value() + 5)))
            self.fake_timer.start(100)
        else: 
            if hasattr(self, 'fake_timer'):
                self.fake_timer.stop()
            self.progress_bar.setValue(100)
            self.progress_bar.hide()
    
    def open_community_browser(self):
        """Opens the community store and updates UI if a download occurred."""
        shapes_dir = os.path.join(self.base_dir, "shapes_library") if hasattr(self, 'base_dir') else "shapes_library"
        
        dialog = CommunityBrowserDialog(self, local_shapes_dir=shapes_dir)
        dialog.exec()
        
        if dialog.downloaded_something:
            self.refresh_shapes_combobox()

    def refresh_shapes_combobox(self):
        """Reloads the shapes_library and updates the combobox dynamically."""
        current_selection = self.combo_shape_style.currentText()
        
        shapes_dir = os.path.join(self.base_dir, "shapes_library") if hasattr(self, 'base_dir') else "shapes_library"
        dxf_files = [f for f in os.listdir(shapes_dir) if f.lower().endswith('.dxf')]
        
        self.combo_shape_style.blockSignals(True)
        self.combo_shape_style.clear()
        self.combo_shape_style.addItem("Custom")
        
        for dxf in sorted(dxf_files):
            shape_name = os.path.splitext(dxf)[0]
            self.combo_shape_style.addItem(shape_name)
            
        index = self.combo_shape_style.findText(current_selection)
        if index >= 0:
            self.combo_shape_style.setCurrentIndex(index)
            
        self.combo_shape_style.blockSignals(False)
        self.log("Community Shapes list updated successfully.", "INFO")

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    
    # CRITICAL MACOS FIX: Set proper OpenGL profile for Metal translation
    if sys.platform == 'darwin':
        import os
        from PySide6.QtGui import QSurfaceFormat
        
        fmt = QSurfaceFormat()
        fmt.setRenderableType(QSurfaceFormat.OpenGL)
        fmt.setVersion(4, 1)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        fmt.setRedBufferSize(8)
        fmt.setGreenBufferSize(8)
        fmt.setBlueBufferSize(8)
        fmt.setAlphaBufferSize(8)
        fmt.setDepthBufferSize(24)
        fmt.setStencilBufferSize(8)
        QSurfaceFormat.setDefaultFormat(fmt)
        
        os.environ["VTK_DISABLE_CHROMA_SUBSAMPLING"] = "1"

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
            base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
            
        os.chdir(base_dir)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)
        
    icon_png = os.path.join(base_dir, 'icon.png')
    icon_ico = os.path.join(base_dir, 'icon.ico')
    
    if sys.platform == 'linux' and os.path.exists(icon_png):
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_png))
    elif os.path.exists(icon_ico):
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_ico))
        
    w = MoldApp()
    
    if sys.platform == 'linux':
        w.showMaximized()
        w.activateWindow()
    elif sys.platform == 'darwin':
        w.show()
        w.activateWindow()
    else:
        from PySide6.QtCore import Qt
        w.setWindowFlags(w.windowFlags() | Qt.WindowStaysOnTopHint)
        w.showMaximized()
        w.setWindowFlags(w.windowFlags() & ~Qt.WindowStaysOnTopHint)
        w.showMaximized()
        w.activateWindow()
        
    sys.exit(app.exec())