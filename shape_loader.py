"""
Shape Loader Module
Handles the importation, scaling, and processing of external DXF files.
Converts 2D CAD outlines into both UI-friendly point arrays and CadQuery 3D faces.
"""

import cadquery as cq
import os
import sys

def load_and_scale_dxf(shape_name, target_width, target_length, offset_y=0.0):
    """
    Loads a DXF, samples points for 2D/3D use, and returns 
    both the sampled points (for the UI canvas) and the Face (for the 3D engine).
    Includes an offset_y parameter to manually align asymmetric shapes (like Fishtails).
    
    Args:
        shape_name (str): The filename of the DXF (without extension).
        target_width (float): The desired physical width of the board (mm).
        target_length (float): The total physical length of the board (mm).
        offset_y (float): Manual Y-axis shift for asymmetric designs.
        
    Returns:
        tuple: (pts_mm: list of tuples, dxf_face: cq.Face) or (None, None) on failure.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in base_dir:
            base_dir = os.path.abspath(os.path.join(base_dir, '../../..'))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    dxf_path = os.path.join(base_dir, "shapes_library", f"{shape_name}.dxf")
    
    if not os.path.exists(dxf_path):
        print(f"WARNING: {dxf_path} not found.")
        return None, None

    try:
        # Import the raw DXF geometry into CadQuery
        imported = cq.importers.importDXF(dxf_path)
        shape_wire = imported.wires().toPending().wire().val()
        bbox = shape_wire.BoundingBox()
        
        # Prevent division by zero if the DXF is empty or corrupted
        if bbox.xlen == 0 or bbox.ylen == 0:
            return None, None

        # Calculate scaling factors to match the user's parametric dimensions
        scale_x = target_width / bbox.xlen
        scale_y = target_length / bbox.ylen
        
        # Find the center of the bounding box to center the shape at (0,0)
        center_x = (bbox.xmin + bbox.xmax) / 2.0
        center_y = (bbox.ymin + bbox.ymax) / 2.0
        
        # --- GEOMETRY RE-SAMPLING ---
        # Instead of scaling the complex DXF directly (which often causes topological errors),
        # we sample points along the perimeter and rebuild a mathematically clean spline.
        n_samples = 150
        pts_mm = []
        for i in range(n_samples + 1):
            # positionAt returns a point along the wire length (0.0 to 1.0)
            p = shape_wire.positionAt(i / float(n_samples))
            
            # Center the point, apply the custom scale, and shift it via the asymmetry offset
            nx = (p.x - center_x) * scale_x
            ny = ((p.y - center_y) * scale_y) + offset_y
            pts_mm.append((nx, ny)) 
            
        # --- 3D ENGINE RECONSTRUCTION ---
        # Convert 2D tuples back into CadQuery 3D Vectors (Z=0)
        cq_pts = [cq.Vector(p[0], p[1], 0) for p in pts_mm]
        
        try:
            # Attempt to build a smooth, continuous B-Spline (best for smooth skate decks)
            spline_edge = cq.Edge.makeSpline(cq_pts)
            new_wire = cq.Wire.assembleEdges([spline_edge]).close()
        except Exception:
            # Fallback: If the shape has sharp corners (like swallow tails) that break the spline,
            # build a high-resolution polygon instead.
            new_wire = cq.Wire.makePolygon(cq_pts).close()
            
        # Convert the closed wire into a solid Face ready for 3D extrusion
        dxf_face = cq.Face.makeFromWires(new_wire)
        
        # Return both the raw points (for the 2D UI preview) and the Face (for the 3D generation)
        return pts_mm, dxf_face
        
    except Exception as e:
        # Catching generic errors prevents the whole app from crashing if a bad DXF is loaded
        print(f"DXF Loader Error: {e}")
        return None, None