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