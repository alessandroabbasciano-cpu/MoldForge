"""
Core Geometry Engine - MOLD F.O.R.G.E.
Responsible for the high-precision 3D generation of fingerboard molds and decks.
Uses complex lofts, trigonometric transitions, and boolean operations to create
production-ready CAD models.
"""

import cadquery as cq
import math
from cq_utils import clamp, make_bezier_approx, make_rounded_box
from params import MoldParams
import shape_loader

def make_shaper_outline(params):
    """
    Generates the 2D footprint of the board.
    Supports both dynamic Bezier curves and imported DXF shapes.
    """
    total_l = (params.Wheelbase) + (params.TruckHoleDistL * 2) + \
              (params.NoseKickGap + params.NoseLength) + \
              (params.TailKickGap + params.TailLength)
    target_w = params.BoardWidth

    # --- DXF MODE ---
    if params.ShapeStyle != "Custom":
        pts, dxf_face = shape_loader.load_and_scale_dxf(params.ShapeStyle, target_w, total_l, params.ShapeOffsetY)
        if dxf_face:
            return dxf_face

    # --- CUSTOM BEZIER MODE ---
    wb, nose_len, tail_len = params.Wheelbase, params.NoseLength, params.TailLength
    kick_gap_n, kick_gap_t = params.NoseKickGap, params.TailKickGap
    truck_len = params.TruckHoleDistL
    
    # Calculate the Y coordinate for the very tip of the board
    y_tip_nose = (wb/2.0) + truck_len + kick_gap_n + nose_len
    y_tip_tail = -((wb/2.0) + truck_len + kick_gap_t + tail_len)
    
    w_half, half_tip_w = params.BoardWidth / 2.0, 0.1
    
    # Setup Nose Bezier Vectors
    n_straight_y = params.NoseStraightP / 100.0
    n_c1x, n_c1y = params.NoseCtrl1X / 100.0, params.NoseCtrl1Y / 100.0
    n_c2x = params.NoseCtrl2X / 100.0
    
    P_yellow_n = cq.Vector(w_half, y_tip_nose * n_straight_y, 0)
    P_red_n = cq.Vector(half_tip_w + (w_half - half_tip_w) * n_c1x, y_tip_nose * n_c1y, 0)
    P_blue_n = cq.Vector(half_tip_w + (w_half - half_tip_w) * n_c2x, y_tip_nose, 0) 
    P_tip_n = cq.Vector(half_tip_w, y_tip_nose, 0)
    
    # Setup Tail Bezier Vectors
    t_straight_y = params.TailStraightP / 100.0
    t_c1x, t_c1y = params.TailCtrl1X / 100.0, params.TailCtrl1Y / 100.0
    t_c2x = params.TailCtrl2X / 100.0
    
    P_yellow_t = cq.Vector(w_half, y_tip_tail * t_straight_y, 0)
    P_red_t = cq.Vector(half_tip_w + (w_half - half_tip_w) * t_c1x, y_tip_tail * t_c1y, 0)
    P_blue_t = cq.Vector(half_tip_w + (w_half - half_tip_w) * t_c2x, y_tip_tail, 0) 
    P_tip_t = cq.Vector(half_tip_w, y_tip_tail, 0)
    
    # Assemble the half-outline wire
    e_flat_t = cq.Edge.makeLine(cq.Vector(0, y_tip_tail, 0), P_tip_t)
    e_crv_t = make_bezier_approx([P_tip_t, P_blue_t, P_red_t, P_yellow_t])
    e_crv_n = make_bezier_approx([P_yellow_n, P_red_n, P_blue_n, P_tip_n])
    e_flat_n = cq.Edge.makeLine(P_tip_n, cq.Vector(0, y_tip_nose, 0))
    
    edges_list = [e_flat_t, e_crv_t]
    if abs(P_yellow_n.y - P_yellow_t.y) > 1e-4:
        edges_list.append(cq.Edge.makeLine(P_yellow_t, P_yellow_n))
    edges_list.extend([e_crv_n, e_flat_n])
    
    # Mirror and create the 2D Face
    wire_half = cq.Wire.assembleEdges(edges_list)
    full_wire = cq.Wire.assembleEdges(wire_half.Edges() + wire_half.mirror(cq.Vector(1,0,0)).Edges())
    return cq.Face.makeFromWires(full_wire)

def build_mold(params: MoldParams):
    """
    Main orchestration function. Builds the requested part (Male, Female, or Template)
    using boolean subtraction of 'Cutter' solids from base blocks.
    """
    # --- DYNAMIC CORE PROTECTION ---
    # Prevents holes in the female mold when using extreme concave drops or kick angles
    extra_kicks = max(0.0, max(params.NoseAngle, params.TailAngle) - 20.0) * 0.15
    dynamic_core_height = params.MoldCoreHeight + extra_kicks

    base_width = params.MoldBaseWidth
    base_height = params.MoldBaseHeight
    core_width = clamp(params.MoldCoreWidth, 29.0, 70.0)
    mold_len = params.MoldLength
    
    # Layout for Guide Holes (Alignment pins)
    gx = (core_width / 2.0) + ((base_width - core_width) / 4.0)
    gy = (mold_len / 2.0) - 10.0
    guides_loc = [(gx, 0), (gx, gy), (gx, -gy), (-gx, 0), (-gx, gy), (-gx, -gy)]
    
    # Layout for Truck Mounting Holes
    tx, y_fi, y_ri = params.TruckHoleDistW, params.Wheelbase / 2.0, -params.Wheelbase / 2.0
    y_fo, y_ro = y_fi + params.TruckHoleDistL, y_ri - params.TruckHoleDistL
    trucks_loc = [(tx, y_fi), (-tx, y_fi), (tx, y_fo), (-tx, y_fo), (tx, y_ri), (-tx, y_ri), (tx, y_ro), (-tx, y_ro)]

    # Vertical Target offsets for Male and Female parts
    z_mount_target = base_height + dynamic_core_height
    z_fem_target = z_mount_target + params.MoldGap

    # --- CONCAVE GEOMETRY CALCULATION ---
    board_width = params.BoardWidth
    tub_width = clamp(params.TubWidth, 0.0, board_width - 18.0)
    eff_width_half = (board_width - tub_width) / 2.0
    concave_depth = params.ConcaveDrop
    
    # Using the Sagitta formula to calculate the radius of the concave circle
    if concave_depth > 0.01 and eff_width_half > 0.1:
        radius_concave = (eff_width_half**2 + concave_depth**2) / (2.0 * concave_depth)
    else:
        radius_concave = 100000.0 # Effectively flat

    dx_core = (core_width / 2.0) - (tub_width / 2.0) if tub_width > 0.1 else (core_width / 2.0)
    max_concave_rise = 0.0
    
    if radius_concave < 5000:
        if dx_core < radius_concave:
            max_concave_rise = radius_concave - math.sqrt(radius_concave**2 - dx_core**2)
        else:
            max_concave_rise = radius_concave

    def build_cutter_solids(radius_val, z_offset_flat, z_limit):
        """
        Generates a massive 'Cutter' solid by lofting multiple 2D profiles.
        This solid is used to carve the board's surface out of a mold block.
        """
        # Trigonometric setup for smooth kick transitions
        sin_n = math.sin(math.radians(params.NoseAngle))
        rad_nose = (params.NoseTransitionLength / sin_n) if sin_n > 0.001 else 500.0
        sin_t = math.sin(math.radians(params.TailAngle))
        rad_tail = (params.TailTransitionLength / sin_t) if sin_t > 0.001 else 500.0
        
        y_kick_start_nose = (params.Wheelbase / 2.0) + params.TruckHoleDistL + params.NoseKickGap
        y_kick_start_tail = -((params.Wheelbase / 2.0) + params.TruckHoleDistL + params.TailKickGap)
        y_concave_end = params.ConcaveLength / 2.0
        gen_width = core_width + 20.0 
        y_tip_nose = mold_len / 2.0 + 4.0
        y_tip_tail = -(mold_len / 2.0 + 4.0)

        def get_slice_wire(y_pos, z_pos, rot):
            """Generates a single 2D cross-section at a specific Y position."""
            x_outer = gen_width / 2.0
            x_inner = tub_width / 2.0 if tub_width > 0.1 else 0.0
            
            y_abs = abs(y_pos)
            local_kick_start = y_kick_start_nose if y_pos >= 0 else abs(y_kick_start_tail)
            
            # Interpolate concave depth based on Y position (full in center, zero at kicks)
            if y_abs <= y_concave_end:
                concave_factor = 1.0
            elif y_abs >= local_kick_start or abs(rot) > 0.1:
                concave_factor = 0.0
            else:
                denom = local_kick_start - y_concave_end
                if denom < 0.01:
                    concave_factor = 0.0
                else:
                    # S-Curve (Cosine) interpolation to remove the geometric scar (C1 continuity)
                    t = (y_abs - y_concave_end) / denom
                    concave_factor = (math.cos(t * math.pi) + 1.0) / 2.0
                    
            # Wheel Flare calculation
            add_flare = False
            flare_y_falloff = 0.0
            if getattr(params, 'AddWheelFlares', False):
                fy = (params.Wheelbase / 2.0) + params.FlarePosY
                fl = params.FlareLength / 2.0
                dist_from_wheel_y = min(abs(y_pos - fy), abs(y_pos - (-fy)))
                
                if dist_from_wheel_y < fl:
                    add_flare = True
                    flare_y_falloff = math.cos((dist_from_wheel_y / fl) * (math.pi / 2.0))

            # Point generation for the section curve
            STEPS = 30
            pts_local = []
            for i in range(STEPS + 1):
                t = i / float(STEPS)
                current_x = x_outer - (t * gen_width)
                abs_x = abs(current_x)
                
                if abs_x <= x_inner:
                    current_z = 0.0
                else:
                    dx = abs_x - x_inner
                    
                    if dx <= eff_width_half:
                        if dx < radius_val:
                            current_z = (radius_val - math.sqrt(radius_val**2 - dx**2)) * concave_factor
                        else:
                            current_z = radius_val * concave_factor
                    else:
                        if eff_width_half < radius_val:
                            z_edge = radius_val - math.sqrt(radius_val**2 - eff_width_half**2)
                            slope = eff_width_half / math.sqrt(radius_val**2 - eff_width_half**2)
                            extra_x = dx - eff_width_half
                            current_z = (z_edge + (slope * extra_x)) * concave_factor
                        else:
                            current_z = radius_val * concave_factor
                        
                if add_flare:
                    fx_edge = params.BoardWidth / 2.0
                    fw = params.FlareWidth
                    dist_from_edge_inward = fx_edge - abs_x
                    
                    if dist_from_edge_inward <= 0:
                        flare_x_falloff = 1.0
                    elif dist_from_edge_inward < fw:
                        flare_x_falloff = math.cos((dist_from_edge_inward / fw) * (math.pi / 2.0))
                    else:
                        flare_x_falloff = 0.0
                        
                    current_z += params.FlareHeight * flare_y_falloff * flare_x_falloff

                pts_local.append(cq.Vector(current_x, 0, current_z))
                
            # Apply 3D Rotation for kicks and Translation for positioning
            pts_global = []
            for p in pts_local:
                z_shifted = p.z + z_offset_flat 
                rad_rot = math.radians(rot)
                new_y = p.y * math.cos(rad_rot) - z_shifted * math.sin(rad_rot)
                new_z = p.y * math.sin(rad_rot) + z_shifted * math.cos(rad_rot)
                pts_global.append(cq.Vector(p.x, new_y + y_pos, new_z + z_pos))
                
            if z_limit > 0:
                pts_curve = pts_global[::-1] 
            else:
                pts_curve = pts_global
                
            p_start = pts_curve[0]
            p_end = pts_curve[-1]
            
            p_limit_end = cq.Vector(p_end.x, p_end.y, z_limit)
            p_limit_start = cq.Vector(p_start.x, p_start.y, z_limit)
            
            e1 = cq.Edge.makeSpline(pts_curve)
            e2 = cq.Edge.makeLine(p_end, p_limit_end)
            e3 = cq.Edge.makeLine(p_limit_end, p_limit_start)
            e4 = cq.Edge.makeLine(p_limit_start, p_start)
            
            return cq.Wire.assembleEdges([e1, e2, e3, e4])

        # --- LOFT SECTION ASSEMBLY ---
        sec_tail, sec_center, sec_nose = [], [], []
        
        KICK_SLICES = 25
        # Tail generation
        dist_tail = abs(y_tip_tail - y_kick_start_tail)
        for i in range(KICK_SLICES):
            ratio = ((KICK_SLICES - 1) - i) / float(KICK_SLICES - 1)
            d_y = dist_tail * ratio
            y_curr = y_kick_start_tail - d_y
            limit_y = rad_tail * math.sin(math.radians(params.TailAngle))
            if d_y <= limit_y:
                arg = rad_tail**2 - d_y**2
                z_curr = rad_tail - math.sqrt(arg if arg>0 else 0)
                rot = -math.degrees(math.asin(clamp(d_y/rad_tail, -1, 1)))
            else:
                z_limit_tail = rad_tail - (rad_tail * math.cos(math.radians(params.TailAngle)))
                z_curr = z_limit_tail + ((d_y - limit_y) * math.tan(math.radians(params.TailAngle)))
                rot = -params.TailAngle
                
            sec_tail.append(get_slice_wire(y_curr, z_curr, rot))
            
        # Center generation (High-Density Transition Zones)
        flat_points = [0.0]
        
        # 1. Central constant concave zone (Lower resolution needed)
        num_flat = 10
        if y_concave_end > 0.1:
            for i in range(num_flat + 1):
                y = (y_concave_end / float(num_flat)) * i
                flat_points.extend([y, -y])
                
        # 2. Nose Transition zone (High resolution to smooth the S-Curve)
        num_trans = 20
        dist_trans_nose = y_kick_start_nose - y_concave_end
        if dist_trans_nose > 0.1:
            for i in range(1, num_trans + 1):
                y = y_concave_end + (dist_trans_nose / float(num_trans)) * i
                flat_points.append(y)
                
        # 3. Tail Transition zone (High resolution)
        dist_trans_tail = abs(y_kick_start_tail) - y_concave_end
        if dist_trans_tail > 0.1:
            for i in range(1, num_trans + 1):
                y = -(y_concave_end + (dist_trans_tail / float(num_trans)) * i)
                flat_points.append(y)

        sorted_points = sorted(list(set(flat_points)))
        
        filtered_points = [sorted_points[0]]
        for pt in sorted_points[1:]:
            if pt - filtered_points[-1] > 0.01:
                filtered_points.append(pt)

        for y_p in filtered_points:
            sec_center.append(get_slice_wire(y_p, 0, 0))
            
        # Nose generation
        dist_nose = y_tip_nose - y_kick_start_nose
        for i in range(KICK_SLICES):
            ratio = i / float(KICK_SLICES - 1)
            d_y = dist_nose * ratio
            y_curr = y_kick_start_nose + d_y
            limit_y = rad_nose * math.sin(math.radians(params.NoseAngle))
            if d_y <= limit_y:
                arg = rad_nose**2 - d_y**2
                z_curr = rad_nose - math.sqrt(arg if arg>0 else 0)
                rot = math.degrees(math.asin(clamp(d_y/rad_nose, -1, 1)))
            else:
                z_limit_nose = rad_nose - (rad_nose * math.cos(math.radians(params.NoseAngle)))
                z_curr = z_limit_nose + ((d_y - limit_y) * math.tan(math.radians(params.NoseAngle)))
                rot = params.NoseAngle
                
            sec_nose.append(get_slice_wire(y_curr, z_curr, rot))

        all_wires = sec_tail[:-1] + sec_center[:-1] + sec_nose
        single_cutter = cq.Solid.makeLoft(all_wires, ruled=True)
        return [single_cutter]

    # Generate the Three Primary Cutters
    cutters_up = build_cutter_solids(radius_concave, 0.0, 200.0)
    cutters_down = build_cutter_solids(radius_concave, params.MoldGap, -200.0)
    cutters_down_veneer = build_cutter_solids(radius_concave, -params.VeneerThickness, -200.0)

    # Move cutters to the target assembly height
    def move_cutters(cutters, z_val):
        return [c.translate(cq.Vector(0, 0, z_val)) for c in cutters]
        
    cutters_up = move_cutters(cutters_up, z_mount_target)
    cutters_down = move_cutters(cutters_down, z_mount_target)
    cutters_down_veneer = move_cutters(cutters_down_veneer, z_mount_target)

    def apply_cuts(block, cutters):
        for c in cutters: 
            block = block.cut(c)
        return block
    
    # --- SPECIALIZED SELECTORS ---
    yt_nose = (params.Wheelbase/2.0) + params.TruckHoleDistL + params.NoseKickGap + params.NoseLength
    yt_tail = -((params.Wheelbase/2.0) + params.TruckHoleDistL + params.TailKickGap + params.TailLength)
    w_half_b = params.BoardWidth / 2.0
    yy_n = yt_nose * (params.NoseStraightP / 100.0)
    yy_t = yt_tail * (params.TailStraightP / 100.0)

    class YellowEdgeSelector(cq.Selector):
        """Custom selector to find specific vertical edges for the 'Straight Section' rounding."""
        def __init__(self, pts, tol=2.0):
            self.pts = pts
            self.tol = tol

        def filter(self, objectList):
            res = []
            for obj in objectList:
                if hasattr(obj, "startPoint") and hasattr(obj, "endPoint"):
                    try:
                        v1, v2 = obj.startPoint(), obj.endPoint()
                        if abs(v1.x - v2.x) < 0.1 and abs(v1.y - v2.y) < 0.1:
                            for px, py in self.pts:
                                if abs(v1.x - px) < self.tol and abs(v1.y - py) < self.tol:
                                    res.append(obj)
                                    break
                    except Exception:
                        pass
            return res

    def apply_yellow_fillet(solid_obj, radius):
        """Applies rounding to the specific 'Straight' edges of the custom shape."""
        if radius < 0.1: return solid_obj
        try:
            pts = [(w_half_b, yy_n), (-w_half_b, yy_n), (w_half_b, yy_t), (-w_half_b, yy_t)]
            sel = YellowEdgeSelector(pts, tol=2.0)
            if not solid_obj.edges(sel).vals():
                return solid_obj
            return solid_obj.edges(sel).fillet(radius)
        except Exception:
            return solid_obj

    # Boilerplate tool generation (Trucks & Guides)
    truck_holes_cutter = cq.Workplane("XY").pushPoints(trucks_loc).circle(params.TruckHoleDiam / 2.0).extrude(500).translate((0, 0, -100))
    
    guide_holes_cutter = None
    if params.GuideDiameter > 0.1:
        guide_holes_cutter = cq.Workplane("XY").pushPoints(guides_loc).circle(params.GuideDiameter / 2.0).extrude(500).translate((0, 0, -100))
    
    # --- TRUCK PINS (MARKERS) ---
    pin_radius_base = (params.TruckHoleDiam / 2.0) + 0.2
    pin_height = (params.VeneerThickness / 2.0) - 0.1
    tip_radius = 0.25
    
    # Calculate taper angle for a 0.5mm tip
    taper_angle = math.degrees(math.atan((pin_radius_base - tip_radius) / pin_height))
    
    # Sink extension to prevent zero-thickness geometry on curved boolean operations
    sink = 1.5
    true_base_radius = pin_radius_base + (sink * math.tan(math.radians(taper_angle)))
    total_height = pin_height + sink

    # Female Mold Pin (Positive, pointing down)
    female_pins = cq.Workplane("XY").pushPoints(trucks_loc).circle(true_base_radius).extrude(total_height, taper=taper_angle).mirror("XY").translate((0, 0, z_fem_target + sink))

    # Male Mold Hole (Negative, pointing down to carve the core surface)
    male_pin_holes = cq.Workplane("XY").pushPoints(trucks_loc).circle(true_base_radius + 0.4).extrude(total_height + 0.5, taper=taper_angle).mirror("XY").translate((0, 0, z_mount_target + sink))

    # Bottom Shaper Pin (Positive, pointing up)
    shaper_pins_up = cq.Workplane("XY").pushPoints(trucks_loc).circle(true_base_radius).extrude(total_height, taper=taper_angle).translate((0, 0, z_mount_target - sink))
    
    # Top Shaper Pin (Positive, pointing down)
    z_shaper_bottom = z_mount_target - params.VeneerThickness
    shaper_pins_down = cq.Workplane("XY").pushPoints(trucks_loc).circle(true_base_radius).extrude(total_height, taper=taper_angle).mirror("XY").translate((0, 0, z_shaper_bottom + sink))    
    
    # Calculate total stack height
    rise_nose = params.NoseLength * math.sin(math.radians(params.NoseAngle))
    rise_tail = params.TailLength * math.sin(math.radians(params.TailAngle))
    max_kick_rise = max(rise_nose, rise_tail)
    
    top_z = z_fem_target + max(max_kick_rise, max_concave_rise) + dynamic_core_height + 5
    total_height = top_z + base_height
    
    # SideLock Dimensioning
    lock_ext = 12.0
    male_lw = max(15.0, core_width - 30.0)  
    clearance = 0.4  
    gap_width = male_lw + (clearance * 2.0)
    fem_lw = (base_width - gap_width) / 2.0  
    ly = (mold_len / 2.0) + (lock_ext / 2.0)
    fx = (gap_width / 2.0) + (fem_lw / 2.0)

    # --- PART GENERATION BRANCHES ---
    if params.MoldType == "Male_Mold":
        max_z = z_mount_target + 50.0
        core_box = cq.Workplane("XY").box(core_width, mold_len, max_z).translate((0, 0, max_z / 2.0))
        male_core = apply_cuts(core_box, cutters_up)
        base = make_rounded_box(base_width, mold_len, base_height, params.MoldCornerRadius)
        final = male_core.union(base)
        
        if params.AddFillet and params.FilletRadius > 0.0:
            try:
                safe_margin = 0.5 
                effective_radius = min(params.FilletRadius, dynamic_core_height - safe_margin)
                box = cq.selectors.BoxSelector(
                    (-core_width/2 - 0.5, -mold_len/2 - 0.5, base_height - 0.5),
                    (core_width/2 + 0.5, mold_len/2 + 0.5, base_height + 0.5)
                )
                final = final.edges("|Y").edges(box).fillet(effective_radius)
            except Exception:
                pass
        
        final = final.cut(truck_holes_cutter)
        if getattr(params, 'AddMoldTruckPins', False):
            final = final.cut(male_pin_holes)
        else:
            final = final.cut(truck_holes_cutter)

        if params.AddGuideHoles and guide_holes_cutter is not None:            
            final = final.cut(guide_holes_cutter)

        if params.AddIndicators:
            font_size = 12.0  
            text_depth = 1.0
            y_pos_nose = (params.MoldLength / 2.0) - 15.0
            y_pos_tail = -(params.MoldLength / 2.0) + 15.0
            text_n = cq.Workplane("XY").center(0, y_pos_nose).text("N", font_size, text_depth).mirror("YZ")
            text_t = cq.Workplane("XY").center(0, y_pos_tail).text("T", font_size, text_depth).mirror("YZ")
            final = final.cut(text_n).cut(text_t)
            
        if params.SideLocks:
            safe_clearance = params.MoldGap + 3.0
            male_lock_h = max(5.0, total_height - safe_clearance)
            male_locks = (
                cq.Workplane("XY")
                .pushPoints([(0, ly), (0, -ly)])
                .box(male_lw, lock_ext, male_lock_h)
                .translate((0, 0, male_lock_h / 2.0))
            )
            try: male_locks = male_locks.edges(">Z").chamfer(1.5) 
            except Exception: pass
            final = final.union(male_locks)
            
        return final

    elif params.MoldType == "Female_Mold":
        final = cq.Workplane("XY").box(base_width, mold_len, total_height).translate((0, 0, total_height / 2.0))
        final = apply_cuts(final, cutters_down)
        
        shoulder_tool = (
            cq.Workplane("XY")
            .rect(base_width + 10.0, mold_len + 10.0) 
            .rect(core_width, mold_len)           
            .extrude(top_z)
        )
        final = final.cut(shoulder_tool)
        
        if params.AddFillet and params.FilletRadius > 0.0:
            try:
                safe_margin = 0.5 
                effective_radius = min(params.FilletRadius, dynamic_core_height - safe_margin)
                box = cq.selectors.BoxSelector(
                    (-core_width/2 - 0.5, -mold_len/2 - 0.5, top_z - 0.5),
                    (core_width/2 + 0.5, mold_len/2 + 0.5, top_z + 0.5)
                )
                final = final.edges("|Y").edges(box).fillet(effective_radius)
            except Exception:
                pass

        if getattr(params, 'AddMoldTruckPins', False):
            final = final.union(female_pins)
        else:
            final = final.cut(truck_holes_cutter)
        
        if params.AddGuideHoles and guide_holes_cutter is not None:            
            final = final.cut(guide_holes_cutter)   

        if params.AddIndicators:
            bbox = final.val().BoundingBox()
            font_size = 12.0  
            text_depth = 1.0  
            y_pos_nose = (params.MoldLength / 2.0) - 12.0
            y_pos_tail = -(params.MoldLength / 2.0) + 12.0
            text_n = cq.Workplane("XY").workplane(offset=bbox.zmax).center(0, y_pos_nose).text("N", font_size, -text_depth)
            text_t = cq.Workplane("XY").workplane(offset=bbox.zmax).center(0, y_pos_tail).text("T", font_size, -text_depth)
            final = final.cut(text_n).cut(text_t)
            
        if params.SideLocks:
            safe_clearance = params.MoldGap + 3.0
            fem_lock_bottom = safe_clearance
            fem_lock_h = max(5.0, total_height - safe_clearance)
            female_locks = (
                cq.Workplane("XY")
                .pushPoints([(fx, ly), (-fx, ly), (fx, -ly), (-fx, -ly)])
                .box(fem_lw, lock_ext, fem_lock_h)
                .translate((0, 0, fem_lock_bottom + (fem_lock_h / 2.0)))
            )
            try: female_locks = female_locks.edges("<Z").chamfer(1.5) 
            except Exception: pass
            final = final.union(female_locks)
             
        return final.translate((0, 0, -z_fem_target))
                 
    elif params.MoldType == "Shaper_Template":
        outline_face = make_shaper_outline(params)
        
        # --- ORIGINAL SHAPER (TOP SHAPER SHELL) ---
        # Generated using cutters_down_veneer. Fits into the concave top of the deck.
        template_raw = cq.Workplane("XY").add(outline_face.outerWire()).toPending().extrude(params.ShaperHeight + z_mount_target + 50)
        
        if params.ShapeStyle == "Custom":
            template_raw = apply_yellow_fillet(template_raw, params.FilletYellow)
            
        template = apply_cuts(template_raw, cutters_down_veneer)
        
        z_flat_top = z_mount_target + params.ShaperHeight
        trim_box = cq.Workplane("XY").box(500, 500, 500).translate((0, 0, z_flat_top + 250))

        # 1. MAIN SHAPER (TOP SHELL)
        template = template.cut(trim_box)
        
        if getattr(params, 'AddShaperTruckPins', False):
            template = template.union(shaper_pins_down)
        else:
            template = template.cut(truck_holes_cutter)
        
        y_tip_nose = (params.Wheelbase / 2.0) + params.TruckHoleDistL + params.NoseKickGap + params.NoseLength
        y_tip_tail = -((params.Wheelbase / 2.0) + params.TruckHoleDistL + params.TailKickGap + params.TailLength)
        font_size = 11.0  
        text_depth = 0.6

        if params.AddIndicators:
            bbox = template.val().BoundingBox()
            text_n = cq.Workplane("XY").workplane(offset=bbox.zmax).center(0, y_tip_nose - 10.0).text("N", font_size, -text_depth)
            text_t = cq.Workplane("XY").workplane(offset=bbox.zmax).center(0, y_tip_tail + 10.0).text("T", font_size, -text_depth)
            template = template.cut(text_n).cut(text_t)
            
        # Move the base shaper to the floor (Z=0)
        template = template.translate((0, 0, -(z_mount_target - params.VeneerThickness)))

        # --- CONTRO-SHAPER (BOTTOM SHAPER SHELL) ---
        if getattr(params, 'AddTopShaper', False):
            # We use cutters_up to get the space BELOW the deck.
            # This generates a block with a concave top face that cradles the OUTSIDE of the deck.
            bottom_raw = cq.Workplane("XY").add(outline_face.outerWire()).toPending().extrude(z_mount_target + 50)
            
            if params.ShapeStyle == "Custom":
                bottom_raw = apply_yellow_fillet(bottom_raw, params.FilletYellow)
                
            bottom_template = apply_cuts(bottom_raw, cutters_up)
            
            # Trim the block from below so it sits exactly at ShaperHeight thickness
            z_flat_bottom = z_mount_target - params.ShaperHeight
            trim_box_bottom = cq.Workplane("XY").box(500, 500, 500).translate((0, 0, z_flat_bottom - 250))
            bottom_template = bottom_template.cut(trim_box_bottom)
            
            if getattr(params, 'AddShaperTruckPins', False):
                bottom_template = bottom_template.union(shaper_pins_up)
            else:
                bottom_template = bottom_template.cut(truck_holes_cutter)
            
            if params.AddIndicators:
                # Carve the text into the flat bottom face
                text_n_bot = cq.Workplane("XY").workplane(offset=z_flat_bottom).center(0, y_tip_nose - 10.0).text("N", font_size, text_depth).mirror("YZ")
                text_t_bot = cq.Workplane("XY").workplane(offset=z_flat_bottom).center(0, y_tip_tail + 10.0).text("T", font_size, text_depth).mirror("YZ")
                bottom_template = bottom_template.cut(text_n_bot).cut(text_t_bot)
            
            # Shift it laterally on the X axis and drop its flat bottom exactly to the floor (Z=0)
            offset_x = params.MoldBaseWidth + 10.0
            bottom_template = bottom_template.translate((offset_x, 0, -z_flat_bottom))
            
            # Merge both solids into a single object for preview and export
            template = template.add(bottom_template.vals())

        return template

    elif params.MoldType == "Board_Preview":
        outline_face = make_shaper_outline(params)
        board_prism = cq.Workplane("XY").add(outline_face.outerWire()).toPending().extrude(z_mount_target + 50)
        
        if params.ShapeStyle == "Custom":
            board_prism = apply_yellow_fillet(board_prism, params.FilletYellow)
        
        board = apply_cuts(board_prism, cutters_up)
        board = apply_cuts(board, cutters_down_veneer)
        board = board.cut(truck_holes_cutter)
        
        return board.translate((0, 0, -(z_mount_target - params.VeneerThickness)))

    else:
        return cq.Workplane("XY").box(10, 10, 10)