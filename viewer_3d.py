"""
3D Viewer Module
Handles the translation of CadQuery solid objects into PyVista meshes,
manages the rendering pipeline, applies material shading, and controls
the 3D viewport interactions.
"""

import os
import tempfile
import pyvista as pv
import cadquery as cq
from PySide6.QtCore import QTimer

def render_mold(app, result):
    """
    Exports the CadQuery solid to a temporary STL, cleans the mesh,
    calculates dimensions, and displays it via PyVista with advanced shading.
    
    Args:
        app: The main application instance (MoldApp) containing UI state and parameters.
        result: The CadQuery Workplane/Solid object to be rendered.
    """
    mode = app.params.MoldType
    
    # Material presets based on mold type to visually distinguish parts
    if mode == "Female_Mold": 
        color = "#3498db"
        spec = 0.6; diff = 0.8; spec_p = 30
    elif mode == "Male_Mold": 
        color = "#e74c3c"
        spec = 0.6; diff = 0.8; spec_p = 30
    elif mode == "Shaper_Template": 
        color = "#2ecc71"
        spec = 0.4; diff = 0.8; spec_p = 15
    else: 
        color = "#d4a373" 
        spec = 0.1; diff = 0.9; spec_p = 5
        
    # Create a temporary STL file to bridge CadQuery and PyVista
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = tmp.name
        
    try:
        # Export logic: lower tolerance means higher resolution mesh (heavier)
        cq.exporters.export(result, tmp_path, tolerance=0.05, angularTolerance=0.05)
        
        # PyVista Mesh Processing
        mesh = pv.read(tmp_path)
        mesh = mesh.clean()

        # --- TOPOLOGICAL GATEKEEPER ---
        if mesh.n_points == 0 or mesh.n_cells == 0:
            raise ValueError("The 3D engine generated empty or invalid geometry. "
                             "Possible extreme asymmetry or boolean operation failure.")
        
        # Compute normals for smooth shading. split_vertices prevents shading artifacts on sharp edges
        mesh.compute_normals(cell_normals=False, point_normals=True, split_vertices=True, feature_angle=45, inplace=True)
        
        # Center the mesh to the origin. This ensures the orbit camera revolves perfectly around the object
        bounds = mesh.bounds
        mesh.translate((-bounds[0], -bounds[2], -bounds[4]), inplace=True)
        
        # Dimension calculation for the log console
        dim_x = bounds[1] - bounds[0] 
        dim_y = bounds[3] - bounds[2] 
        dim_z = bounds[5] - bounds[4] 
        
        if getattr(app, 'is_metric', True): 
            unit_str = "mm"
        else:
            dim_x /= 25.4; dim_y /= 25.4; dim_z /= 25.4; unit_str = "in"
        
        app.log(f"Ready. Max Dimensions: {dim_x:.2f} x {dim_y:.2f} x {dim_z:.2f} {unit_str}", "INFO")
        
        # Save current camera state before clearing the scene
        cam_pos = app.plotter.camera_position
        
        app.plotter.clear()
        app.plotter.clear_plane_widgets()
        
        # --- GRAPHICS PIPELINE & SHADOWS FIX ---
        try:
            # Force a preliminary render to initialize C++ OpenGL Framebuffers
            app.plotter.render()
            # Safely enable Anti-Aliasing (MSAA) and Screen-Space Ambient Occlusion (SSAO)
            app.plotter.enable_anti_aliasing('msaa') 
            app.plotter.enable_ssao(radius=2.0, bias=0.5) 
        except Exception: 
            # Ignore VTK/OpenGL fallback errors silently on unsupported hardware (e.g., some Macs)
            pass 
        # ---------------------------------------

        mat_kwargs = {
            "color": color,
            "smooth_shading": True,
            "specular": spec,       
            "diffuse": diff,        
            "ambient": 0.15,       
            "specular_power": spec_p   
        }

        use_clean_wireframe = app.chk_wireframe.isChecked()
        
        # Render execution
        if app.clipping_enabled:
            # VTK algorithms (like clip plane) do not support smooth point-normals shading
            clip_kwargs = mat_kwargs.copy()
            clip_kwargs["smooth_shading"] = False
            app.plotter.add_mesh_clip_plane(mesh, show_edges=not use_clean_wireframe, **clip_kwargs)
        else:
            if use_clean_wireframe:
                # Draw the solid object without all triangle edges
                app.plotter.add_mesh(mesh, show_edges=False, **mat_kwargs)
                # Extract and draw only the sharp feature edges for a cleaner CAD look
                edges = mesh.extract_feature_edges(feature_angle=30)
                app.plotter.add_mesh(edges, color="#999999", line_width=1.5, name="edges")
            else:
                # Standard render with all triangles visible
                app.plotter.add_mesh(mesh, show_edges=True, edge_color="#333333", **mat_kwargs)
            
        app.plotter.set_background(color="#1a1a1a", top="#4a6984")
        app.plotter.enable_lightkit()
        app.plotter.add_axes(color="white")
        
        if app.action_axes.isChecked():
            app.plotter.show_grid(color="#e0e0e0", font_size=10, font_family="arial", bold=False, fmt="%.2f", n_xlabels=3, n_ylabels=3, n_zlabels=3)
        
        # --- CAMERA POSITIONING ---
        if getattr(app, '_has_rendered_once', False) and cam_pos is not None:
            # Restore the user's camera angle
            app.plotter.camera_position = cam_pos
        else:
            # First time render: setup a nice default view
            app.plotter.view_isometric() # Force Isometric View
            app.plotter.reset_camera()   # Fit to boundaries
            app._has_rendered_once = True

    except Exception as e:
        app.on_error(str(e))
    finally:
        # Cleanup temporary STL to prevent disk clutter
        if os.path.exists(tmp_path): 
            os.remove(tmp_path)
        
    # Check if a new render was requested while the previous one was processing
    if getattr(app, '_render_pending', False):
        QTimer.singleShot(100, app.start_preview)