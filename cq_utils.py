"""
CadQuery Utilities Module
Provides geometric helper functions for coordinate clamping, 
Bezier curve generation, and specialized primitive construction.
"""

import cadquery as cq

def clamp(n, minn, maxn):
    """
    Constrains a value between a defined minimum and maximum range.
    
    Args:
        n (float): The value to clamp.
        minn (float): The lower bound.
        maxn (float): The upper bound.
    """
    return max(min(maxn, n), minn)

def make_bezier_approx(control_points, n_steps=32):
    """
    Generates a smooth CadQuery Edge using a cubic Bezier approximation.
    Samples points along the curve and connects them with a B-Spline.
    
    Args:
        control_points (list): A list of 4 cq.Vector objects (P0, P1, P2, P3).
        n_steps (int): The number of sampling points. Higher values increase precision.
        
    Returns:
        cq.Edge: A smooth spline edge based on the control points.
    """
    p0, p1, p2, p3 = control_points
    sampled_points = []
    
    for i in range(n_steps + 1):
        t = i / float(n_steps)
        u = 1 - t
        
        # Cubic Bezier basis functions (coefficients)
        c0 = u**3
        c1 = 3 * u**2 * t
        c2 = 3 * u * t**2
        c3 = t**3
        
        # Calculate resulting coordinate for the current step 't'
        nx = c0*p0.x + c1*p1.x + c2*p2.x + c3*p3.x
        ny = c0*p0.y + c1*p1.y + c2*p2.y + c3*p3.y
        nz = c0*p0.z + c1*p1.z + c2*p2.z + c3*p3.z
        
        sampled_points.append(cq.Vector(nx, ny, nz))
        
    # Create a high-quality B-Spline passing through all sampled points
    return cq.Edge.makeSpline(sampled_points)

def make_rounded_box(width, length, height, radius):
    """
    Creates a rectangular box with rounded vertical edges (|Z).
    
    Args:
        width (float): Total width (X-axis).
        length (float): Total length (Y-axis).
        height (float): Extrusion height (Z-axis).
        radius (float): Corner fillet radius.
        
    Returns:
        cq.Workplane: A solid rounded box starting from the XY plane.
    """
    wp = cq.Workplane("XY")
    
    # If the radius is too small, return a standard box to avoid OCCT fillet errors
    if radius < 0.1:
        return wp.box(width, length, height).translate((0, 0, height/2))
    
    # Draw rectangle, extrude, and select all vertical edges for filleting
    return wp.rect(width, length).extrude(height).edges("|Z").fillet(radius)

def make_logo_solid(params):
    """
    Generates a 3D text solid for logo debossing on the mold surface.

    Each letter is created as an individual solid, transformed (mirrored/rotated),
    then positioned and fused into a single combined logo geometry.

    This function supports:
    - Per-letter spacing control
    - Per-letter rotation (orientation)
    - Optional mirroring for deboss readability.

    Args:
        params (MoldParams): Parameter object containing logo configuration
    
    Returns:
        cq.Workplane | None:
            A Workplane containing the fused logo solid, or None if no text is provided.
    """
    
    # Normalize and validate input text
    text = params.LogoText.strip().upper()

    # Early exit if no valid text
    if not text:
        return None

    # Calculate vertical spacing between letters
    # Spacing is proportional to logo size for consistent scaling
    spacing = params.LogoSize * params.LogoSpacing
    n = len(text)

    solids = []

    # Per-letter generation
    for i, letter in enumerate(text):
        # Center letters vertically around origin
        # Ensures symmetric placement regardless of string length
        y = spacing * (n/2 - i - 0.5)

        # Create individual letter as a solid
        wp = (
            cq.Workplane("XY")
            .text(
                letter,
                params.LogoSize,        # Letter height (mm)
                params.LogoDepth,       # Extrusion depth (mm)
                kind="bold",
                combine=True            # Ensures a single clean solid per letter
            )
        )

        # Extract underlying solid for transformation
        solid = wp.val()

        # --- INVERSION (MOLD READABILITY) ---
        # Mirrored across YZ plane (flip x-axis)
        # This ensures text appears correct after pressing into material
        # Must be applied before rotation to maintain correct orientation
        if params.LogoInvert:
            solid = solid.mirror("YZ")

        # --- ROTATION (LETTER ORIENTATION) ---
        # Rotate each letter independently around Z-axis
        # Allows vertical, angled, or inverted text layouts
        if params.LogoRotationDeg != 0:
            solid = solid.rotate(
                (0, 0, 0),
                (0, 0, 1),
                params.LogoRotationDeg
            )

        # --- POSITIONING ---
        # Translate letter into final position along board length (Y-axis)
        solid = solid.translate((0, y, 0))

        solids.append(solid)
    
    # Safety check (should rarely trigger)
    if not solids:
        return None

    # --- COMBINE ALL LETTERS ---
    # Fuse individual letter solids into a single continuous geometry
    logo = solids[0]
    for s in solids[1:]:
        logo = logo.fuse(s)

    # Return as Workplane for compatibility with downstream operations
    return cq.Workplane("XY").add(logo)