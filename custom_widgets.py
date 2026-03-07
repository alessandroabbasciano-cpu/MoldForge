"""
Custom Widgets Module
Provides specialized UI components for MOLD F.O.R.G.E., including a 
non-scrolling spinbox and an interactive 2D Bezier shape editor 
for real-time board outline design.self.setSingleStep(1.0)
"""

from PySide6.QtWidgets import QWidget, QDoubleSpinBox
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
import math

class NoScrollSpinBox(QDoubleSpinBox):
    """
    A customized QDoubleSpinBox that ignores mouse wheel events 
    unless the widget specifically has focus. This prevents accidental 
    parameter changes while scrolling through the side panels.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSingleStep(0.1)
        
    def wheelEvent(self, event):
        if not self.hasFocus(): 
            event.ignore()
        else: 
            super().wheelEvent(event)

class KickShapeEditor(QWidget):
    """
    An interactive 2D canvas for designing board outlines using Bezier curves.
    Supports real-time handle dragging, DXF preview overlays, and advanced 
    visualization of fillet/rounding geometry.
    """
    shapeChanged = Signal(float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280) 
        self.s_y = 20.0             # Straight section percentage
        self.c1x, self.c1y = 100.0, 35.0  # Control Point 1 percentages
        self.c2x = 85.0             # Control Point 2 X percentage
        self.active_handle = None   # Currently dragged handle index
        self.board_ctx = None       # Physical board dimensions and context
        self.is_bezier_mode = True  # Toggle between Custom Bezier and DXF view
        self.custom_points = []     # Points from an imported DXF

    def set_values(self, s_y, c1x, c1y, c2x):
        """Updates internal handle percentages and refreshes the canvas."""
        self.s_y, self.c1x, self.c1y, self.c2x = s_y, c1x, c1y, c2x
        self.update()

    def set_custom_shape(self, points):
        """Switch to DXF preview mode if points are provided, otherwise Bezier mode."""
        self.custom_points = points
        self.is_bezier_mode = (points is None or len(points) == 0)
        self.update()

    def set_board_context(self, target, length, width, wb, truck_l, truck_w, truck_d, gap, rounding, flare_en=False, flare_l=12.0, flare_w=7.0, flare_y=2.5):
        """Stores physical board dimensions to ensure the 2D drawing is at the correct scale."""
        self.board_ctx = {
            "target": target, "length": length, "width": width,
            "wb": wb, "truck_l": truck_l, "truck_w": truck_w, "truck_d": truck_d,
            "gap": gap, "rounding": rounding,
            "flare_en": flare_en, "flare_l": flare_l, "flare_w": flare_w, "flare_y": flare_y
        }
        self.update()

    def get_board_params(self):
        """Helper to safely retrieve board context with fallback defaults."""
        if not self.board_ctx:
            return {
                "length": 16.5, "width": 34.0, "wb": 44.0,
                "truck_l": 7.5, "truck_w": 5.5, "truck_d": 1.7, "gap": 1.5, "rounding": 1.0,
                "flare_en": False, "flare_l": 12.0, "flare_w": 7.0, "flare_y": 2.5
            }
        return self.board_ctx

    def get_transform(self):
        """
        Calculates the scaling and translation factors to map 
        physical millimeters to widget pixels while maintaining aspect ratio.
        """
        ctx = self.get_board_params()
        # Calculate the maximum physical extent to fit in the view
        max_y_mm = (ctx["wb"] / 2.0) + ctx["truck_l"] + ctx["gap"] + ctx["length"]
        max_x_mm = ctx["width"] / 2.0
        
        mx = 40       # Horizontal margin
        my_top = 30   # Top margin
        my_bot = 35   # Bottom margin
        
        view_w = self.width() - mx * 2
        view_h = self.height() - my_top - my_bot
        
        if view_w <= 0 or view_h <= 0: 
            return 1.0, 0.0, 0.0, max_y_mm, max_x_mm
            
        # Determine best fit scale
        scale = min(view_w / max_y_mm, view_h / max_x_mm)
        draw_w = max_y_mm * scale
        
        # Calculate origins for centering
        origin_x = mx + (view_w - draw_w) / 2.0
        origin_y = self.height() - my_bot
        
        return scale, origin_x, origin_y, max_y_mm, max_x_mm

    def to_px(self, x_mm, y_mm):
        """Converts millimeter coordinates to screen pixels."""
        scale, ox, oy, _, _ = self.get_transform()
        return QPointF(ox + y_mm * scale, oy - x_mm * scale)

    def to_mm(self, px, py):
        """Converts screen pixels back to millimeter coordinates."""
        scale, ox, oy, _, _ = self.get_transform()
        y_mm = (px - ox) / scale
        x_mm = (oy - py) / scale
        return x_mm, y_mm

    def get_points(self):
        """Calculates the pixel positions for the Bezier control handles."""
        ctx = self.get_board_params()
        _, _, _, max_y, _ = self.get_transform()
        w_half = ctx["width"] / 2.0
        tip_w = 0.1
        
        # Map percentages to physical coordinates
        y_yellow = max_y * (self.s_y / 100.0)
        p_str = self.to_px(w_half, y_yellow)
        
        x_red = tip_w + (w_half - tip_w) * (self.c1x / 100.0)
        y_red = max_y * (self.c1y / 100.0)
        p_red = self.to_px(x_red, y_red)
        
        x_blue = tip_w + (w_half - tip_w) * (self.c2x / 100.0)
        p_blue = self.to_px(x_blue, max_y)
        
        p_tip = self.to_px(tip_w, max_y)
        p_center = self.to_px(w_half, 0)
        
        return p_center, p_str, p_red, p_blue, p_tip

    def get_handle_rects(self):
        """Returns the hit-box rectangles for mouse interaction handles."""
        _, p_str, c1, c2, _ = self.get_points()
        return QRectF(p_str.x()-7, p_str.y()-7, 14, 14), QRectF(c1.x()-7, c1.y()-7, 14, 14), QRectF(c2.x()-7, c2.y()-7, 14, 14)

    def paintEvent(self, event):
        """Main rendering loop for the 2D Designer UI."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor("#1e1e1e"))
        
        scale, ox, oy, max_y, max_x = self.get_transform()
        ctx = self.get_board_params()
        
        # --- DRAW COORDINATE GRID ---
        painter.setPen(QPen(QColor("#444"), 1))
        for i in range(0, int(max_y) + 5, 10):
            pt = self.to_px(max_x, i)
            painter.drawLine(pt, pt + QPointF(0, -5))
            painter.drawText(pt + QPointF(-5, -10), str(i))
            
        for i in range(0, int(max_x) + 5, 5):
            pt = self.to_px(i, 0)
            painter.drawLine(pt, pt + QPointF(-5, 0))
            painter.drawText(pt + QPointF(-25, 5), str(i))
            
        # Draw main axes
        painter.setPen(QPen(QColor("#66b2ff"), 2))
        painter.drawLine(self.to_px(0, 0), self.to_px(0, max_y)) 
        
        painter.setPen(QPen(QColor("#555"), 2))
        painter.drawLine(self.to_px(max_x, 0), self.to_px(0, 0)) 
        
        # Draw bounding limits
        painter.setPen(QPen(QColor("#444"), 2, Qt.DashLine))
        painter.drawLine(self.to_px(max_x, 0), self.to_px(max_x, max_y)) 
        painter.drawLine(self.to_px(0, max_y), self.to_px(max_x, max_y)) 
        
        # Draw Kick-Start line
        y_kick = (ctx["wb"] / 2.0) + ctx["truck_l"] + ctx["gap"]
        painter.setPen(QPen(QColor("#7f8c8d"), 1, Qt.DotLine))
        painter.drawLine(self.to_px(0, y_kick), self.to_px(max_x, y_kick))
        painter.drawText(self.to_px(max_x, y_kick) + QPointF(5, 5), "KICK START")

        # --- DRAW TRUCK HOLES ---
        y_t_inner = ctx["wb"] / 2.0
        y_t_outer = y_t_inner + ctx["truck_l"]
        x_t = ctx["truck_w"]
        r_t_px = (ctx["truck_d"] / 2.0) * scale
        
        painter.setPen(QPen(QColor("#aaa"), 1.5))
        painter.setBrush(QColor("#111"))
        painter.drawEllipse(self.to_px(x_t, y_t_inner), max(2.0, r_t_px), max(2.0, r_t_px))
        painter.drawEllipse(self.to_px(x_t, y_t_outer), max(2.0, r_t_px), max(2.0, r_t_px))

        # --- DRAW WHEEL FLARES ---
        if ctx.get("flare_en", False):
            fy = (ctx["wb"] / 2.0) + ctx.get("flare_y", 2.5)
            fl = ctx.get("flare_l", 12.0)
            fw = min(ctx.get("flare_w", 7.0), max_x)
            
            p_tl = self.to_px(max_x, fy - fl / 2.0)
            p_br = self.to_px(max_x - fw, fy + fl / 2.0)
            flare_rect = QRectF(p_tl, p_br)
            
            painter.setPen(QPen(QColor("#9b59b6"), 1.5, Qt.DashLine))
            painter.setBrush(QColor(155, 89, 182, 50))
            painter.drawRoundedRect(flare_rect, 5, 5)
            painter.setPen(QColor("#9b59b6"))
            painter.drawText(p_tl + QPointF(5, -5), "FLARE")

        # --- DRAW THE BOARD OUTLINE ---
        if not self.is_bezier_mode and self.custom_points:
            # Mode: DXF Preview
            quad_pts = [pt for pt in self.custom_points if pt[0] >= -0.1]
            if ctx["target"] == "Nose":
                quad_pts = sorted([pt for pt in quad_pts if pt[1] >= -0.1], key=lambda p: p[1])
            else:
                quad_pts = sorted([(pt[0], abs(pt[1])) for pt in quad_pts if pt[1] <= 0.1], key=lambda p: p[1])
            
            path = QPainterPath()
            if quad_pts:
                path.moveTo(self.to_px(quad_pts[0][0], quad_pts[0][1]))
                for pt in quad_pts[1:]:
                    path.lineTo(self.to_px(pt[0], pt[1]))
                painter.setPen(QPen(QColor("#2ecc71"), 3))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
        else:
            # Mode: Custom Bezier
            pts = self.get_points()
            p0, p1, p2, p3 = pts[1], pts[2], pts[3], pts[4]
            p_board_center_edge = self.to_px(max_x, 0)
            y_edge = p0.y()
            
            rounding = ctx["rounding"]
            r_px = rounding * scale
            
            valid_fillet = False
            best_t = 0.0
            best_c = QPointF()
            best_p = QPointF()
            angle_t2 = 0.0
            
            # --- TRUE ORIGIN FILLET CALCULATION ---
            # This segment finds where a rounding radius (fillet) would tangentially 
            # meet the Bezier curve to create a smooth, production-safe transition.
            if rounding > 0.1:
                target_y = y_edge + r_px
                min_diff = float('inf')
                
                # Iteratively sample the Bezier curve to find the tangency point
                for i in range(1, 401):
                    t = i / 400.0
                    u = 1 - t
                    # Bezier Cubic Formula
                    bx = u**3 * p0.x() + 3*u**2*t * p1.x() + 3*u*t**2 * p2.x() + t**3 * p3.x()
                    by = u**3 * p0.y() + 3*u**2*t * p1.y() + 3*u*t**2 * p2.y() + t**3 * p3.y()
                    
                    # First Derivative (Tangent vector)
                    tx = 3*u**2 * (p1.x() - p0.x()) + 6*u*t * (p2.x() - p1.x()) + 3*t**2 * (p3.x() - p2.x())
                    ty = 3*u**2 * (p1.y() - p0.y()) + 6*u*t * (p2.y() - p1.y()) + 3*t**2 * (p3.y() - p2.y())
                    
                    length = math.hypot(tx, ty)
                    if length < 1e-5: continue
                    
                    # Perpendicular Normal vector
                    nx = -ty / length
                    ny = tx / length
                    if ny < 0: nx, ny = -nx, -ny
                        
                    # Candidate for circle center
                    ox = bx + r_px * nx
                    oy = by + r_px * ny
                    
                    diff = abs(oy - target_y)
                    if diff < min_diff:
                        min_diff = diff
                        best_t = t
                        best_c = QPointF(ox, target_y)
                        best_p = QPointF(bx, by)
                
                if min_diff < 5.0 and best_t > 0.005 and best_t < 0.995:
                    valid_fillet = True
                    dy = best_c.y() - best_p.y()
                    dx = best_p.x() - best_c.x()
                    angle_t2 = math.degrees(math.atan2(dy, dx))

            # --- RENDER FINAL OUTLINE ---
            if valid_fillet:
                # Draw Filleted Shape
                painter.setPen(QPen(QColor("#2ecc71"), 3))
                painter.drawLine(p_board_center_edge, QPointF(best_c.x(), y_edge))
                
                rect = QRectF(best_c.x() - r_px, best_c.y() - r_px, r_px * 2.0, r_px * 2.0)
                sweep = 90.0 - angle_t2
                painter.drawArc(rect, int(angle_t2 * 16), int(sweep * 16))
                
                # Draw the 'valid' portion of the Bezier
                path_valid_bezier = QPainterPath()
                path_valid_bezier.moveTo(best_p)
                STEPS = 40
                for i in range(1, STEPS + 1):
                    t = best_t + (1.0 - best_t) * (i / STEPS)
                    u = 1 - t
                    bx = u**3 * p0.x() + 3*u**2*t * p1.x() + 3*u*t**2 * p2.x() + t**3 * p3.x()
                    by = u**3 * p0.y() + 3*u**2*t * p1.y() + 3*u*t**2 * p2.y() + t**3 * p3.y()
                    path_valid_bezier.lineTo(bx, by)
                painter.drawPath(path_valid_bezier)
                
                # Draw the 'Wedge' - the material that is cut away by the rounding
                path_wedge = QPainterPath()
                path_wedge.moveTo(best_c.x(), y_edge)
                path_wedge.lineTo(p0)
                for i in range(1, STEPS + 1):
                    t = best_t * (i / STEPS)
                    u = 1 - t
                    bx = u**3 * p0.x() + 3*u**2*t * p1.x() + 3*u*t**2 * p2.x() + t**3 * p3.x()
                    by = u**3 * p0.y() + 3*u**2*t * p1.y() + 3*u*t**2 * p2.y() + t**3 * p3.y()
                    path_wedge.lineTo(bx, by)
                path_wedge.arcTo(rect, angle_t2, sweep) 
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(230, 126, 34, 150)) # Orange fill for visibility
                painter.drawPath(path_wedge)
                
                # Draw ghost of the original sharp corner
                painter.setPen(QPen(QColor("#e67e22"), 1.5, Qt.DashLine))
                painter.drawLine(QPointF(best_c.x(), y_edge), p0)
                path_ghost = QPainterPath()
                path_ghost.moveTo(p0)
                for i in range(1, STEPS + 1):
                    t = best_t * (i / STEPS)
                    u = 1 - t
                    bx = u**3 * p0.x() + 3*u**2*t * p1.x() + 3*u*t**2 * p2.x() + t**3 * p3.x()
                    by = u**3 * p0.y() + 3*u**2*t * p1.y() + 3*u*t**2 * p2.y() + t**3 * p3.y()
                    path_ghost.lineTo(bx, by)
                painter.drawPath(path_ghost)
                
                # Visual guide for the Fillet Center
                painter.setPen(QPen(QColor(230, 126, 34, 50), 1, Qt.DashLine))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(best_c, r_px, r_px)
                painter.setPen(QPen(QColor("#e67e22"), 1, Qt.SolidLine))
                painter.drawLine(best_c + QPointF(-5, 0), best_c + QPointF(5, 0))
                painter.drawLine(best_c + QPointF(0, -5), best_c + QPointF(0, 5))
                painter.drawText(int(best_c.x() - 25), int(best_c.y() + 15), "+ True Origin")
                painter.drawText(int(p0.x() + 10), int(p0.y() - 15), f"CUT R{rounding}")
                
            else:
                # Standard Shape (No Fillet or Fillet Failed)
                path = QPainterPath()
                path.moveTo(p_board_center_edge)
                path.lineTo(p0)
                path.cubicTo(p1, p2, p3)
                
                painter.setPen(QPen(QColor("#2ecc71"), 3))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
                
                if rounding > 0.1:
                    painter.setPen(QColor("#e74c3c"))
                    painter.drawText(int(p0.x() + 10), int(p0.y() - 15), f"FILLET FAILED (R too large)")

            # Draw handle connector lines (visual aid)
            painter.setPen(QPen(QColor("#3498db"), 1.5, Qt.DotLine))
            painter.drawLine(pts[1], pts[2]) 
            painter.drawLine(pts[4], pts[3]) 
            
            # Draw handle info text
            painter.setPen(QColor("#f1c40f"))
            painter.drawText(int(pts[1].x() - 15), int(pts[1].y() - 12), f"Str: {self.s_y:.0f}%")
            painter.setPen(QColor("#e74c3c"))
            painter.drawText(int(pts[2].x() + 10), int(pts[2].y() - 5), f"{self.c1x:.0f}%, {self.c1y:.0f}%")
            painter.setPen(QColor("#3498db"))
            painter.drawText(int(pts[3].x() + 10), int(pts[3].y() + 5), f"{self.c2x:.0f}%, 100%")

        # --- DRAW INTERACTIVE HANDLES ---
        handle_alpha = 255 if self.is_bezier_mode else 40 # Dim handles if in DXF mode
        rect_s, rect1, rect2 = self.get_handle_rects()
        
        painter.setBrush(QBrush(QColor(241, 196, 15, handle_alpha))) # Yellow Handle
        painter.setPen(QPen(QColor(255, 255, 255, handle_alpha), 1.5))
        painter.drawEllipse(rect_s)
        
        painter.setBrush(QBrush(QColor(231, 76, 60, handle_alpha)))   # Red Handle
        painter.drawEllipse(rect1)
        
        painter.setBrush(QBrush(QColor(52, 152, 219, handle_alpha)))  # Blue Handle
        painter.drawEllipse(rect2)
        
        painter.setPen(QColor("#66b2ff"))
        painter.drawText(self.to_px(max_x/2, 0) + QPointF(-50, 20), "BOARD CENTER (Y=0)")

    def mousePressEvent(self, event):
        """Detects if a handle was clicked and starts the dragging process."""
        if not self.is_bezier_mode: return
        rect_s, rect1, rect2 = self.get_handle_rects()
        # Adjusted for larger hit area (10px padding)
        if rect_s.adjusted(-10, -10, 10, 10).contains(event.position()): self.active_handle = 0
        elif rect1.adjusted(-10, -10, 10, 10).contains(event.position()): self.active_handle = 1
        elif rect2.adjusted(-10, -10, 10, 10).contains(event.position()): self.active_handle = 2

    def mouseMoveEvent(self, event):
        """Updates handle positions based on mouse movement and triggers UI sync."""
        if not self.is_bezier_mode or self.active_handle is None: return
        ctx = self.get_board_params()
        _, _, _, max_y, _ = self.get_transform()
        w_half = ctx["width"] / 2.0
        tip_w = 0.1
        
        x_mm, y_mm = self.to_mm(event.position().x(), event.position().y())
        
        if self.active_handle == 0: # Yellow: Straight Length
            val = (y_mm / max_y) * 100.0
            self.s_y = max(0.0, min(100.0, val))
        elif self.active_handle == 1: # Red: Main Curve Control
            val_y = (y_mm / max_y) * 100.0
            val_x = ((x_mm - tip_w) / (w_half - tip_w)) * 100.0
            self.c1x = max(0.0, min(100.0, val_x))
            self.c1y = max(0.0, min(100.0, val_y))
        elif self.active_handle == 2: # Blue: Tip Shape Control
            val_x = ((x_mm - tip_w) / (w_half - tip_w)) * 100.0
            self.c2x = max(0.0, min(100.0, val_x))
        
        self.update()
        # Signal app.py to update the spinboxes and trigger a 3D re-render
        self.shapeChanged.emit(self.s_y, self.c1x, self.c1y, self.c2x)

    def mouseReleaseEvent(self, event):
        """Ends the dragging process."""
        self.active_handle = None