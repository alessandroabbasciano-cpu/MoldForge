"""
UI Menus Module
Constructs the top menu bar for the MOLD F.O.R.G.E. application, 
linking UI actions to their respective application methods.
"""

import webbrowser


def setup_menu(app):
    """
    Builds the main menu bar (File, View, Help) and connects all 
    dropdown actions to the application's core functions.
    """
    menu_bar = app.menuBar()
    
    # ==========================================
    # FILE MENU
    # Handles loading configs, exporting STLs, and exiting.
    # ==========================================
    file_menu = menu_bar.addMenu("File")
    
    # Load a previously saved .txt configuration
    action_load_config = file_menu.addAction("Load Config File (*.txt)...")
    action_load_config.triggered.connect(app.load_config_file)
    file_menu.addSeparator()
    
    # Export the currently viewed 3D object strictly as a STEP file
    app.action_export = file_menu.addAction("Export Current Object (STEP)...")
    app.action_export.setEnabled(False) # Disabled until a successful render completes
    app.action_export.triggered.connect(app.export_step)
    
    # Automatically generate and export all mold parts and the shaper template
    action_batch = file_menu.addAction("Batch Export (Molds + Shaper)...")
    action_batch.triggered.connect(app.batch_export)
    file_menu.addSeparator() 
    
    # Exit application safely
    action_exit = file_menu.addAction("Exit")
    action_exit.triggered.connect(app.close)
    
    # ==========================================
    # VIEW MENU
    # Controls 3D viewport settings and UI panel visibility.
    # ==========================================
    view_menu = menu_bar.addMenu("View")
    
    # Toggle 3D grid and scale markers around the object
    app.action_axes = view_menu.addAction("Show Scale Grid")
    app.action_axes.setCheckable(True)
    app.action_axes.setChecked(False)
    app.action_axes.triggered.connect(app.start_preview)
    view_menu.addSeparator()
    
    # Toggle cross-section clipping plane to look inside the mold
    app.action_clip = view_menu.addAction("Enable Clipping Plane")
    app.action_clip.setCheckable(True)
    app.action_clip.triggered.connect(app.toggle_clipping)
    
    # Switch display units in the log output (mm vs inches)
    app.action_units = view_menu.addAction("Unit: Metric (mm)")
    app.action_units.triggered.connect(app.toggle_units)
    
    # Show or hide all dock panels (Fullscreen mode for the 3D viewer)
    action_toggle_controls = view_menu.addAction("Show/Hide Controls")
    action_toggle_controls.setShortcut("F11")
    action_toggle_controls.triggered.connect(app.toggle_controls)

    view_menu.addSeparator()

    # Unleash The Beast: Removes all dimensional safety limits
    app.action_extreme = view_menu.addAction("Unleash the Beast (Extreme Mode)")
    app.action_extreme.setCheckable(True)
    app.action_extreme.setChecked(False)
    app.action_extreme.triggered.connect(app.toggle_extreme_mode)

    # ==========================================
    # HELP MENU
    # About dialog and community support links.
    # ==========================================
    help_menu = app.menuBar().addMenu("Help")

    # Wiki
    action_wiki = help_menu.addAction("User Manual")
    action_wiki.setShortcut("F1")  
    action_wiki.triggered.connect(lambda: webbrowser.open("https://github.com/alessandroabbasciano-cpu/MoldForge/blob/main/wiki/1-Introduction.md"))
    
    help_menu.addSeparator()
    
    # Opens external browser to GitHub Releases
    action_updates = help_menu.addAction("Download Updates...")
    action_updates.triggered.connect(lambda: webbrowser.open("https://github.com/alessandroabbasciano-cpu/MoldForge/releases/latest"))

    # Opens external browser to PayPal
    action_support = help_menu.addAction("Support the Project")
    action_support.triggered.connect(app.open_support_link)
    
    # Displays the styled HTML 'About' dialog
    action_about = help_menu.addAction("About & License")
    action_about.triggered.connect(app.show_about_dialog)