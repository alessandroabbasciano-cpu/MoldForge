"""
Parameters Module
Defines the core data structure that holds all the physical and configuration 
parameters for the mold generation and deck geometry.
"""

class MoldParams:
    """
    A unified data class to store and pass all user-defined parameters to the 3D engine.
    Initializes with the factory default values.
    """
    def __init__(self):
        # --- OUTPUT OPTIONS ---
        self.MoldType = "Male_Mold"           # "Male_Mold", "Female_Mold", "Shaper_Template", or "Board_Preview"
        self.ShapeStyle = "Custom"            # "Custom" for Bezier, or the name of a DXF file
        self.ShapeOffsetY = 0.0               # Manual Y-axis shift for asymmetric DXF designs
        
        # --- TOGGLES & FEATURES ---
        self.AddIndicators = False            # Emboss 'N' and 'T' markers
        self.SideLocks = False                # Interlocking side tabs for mold alignment
        self.SideLocksGap = 0.15              # Gap in y axis between the interlocking tabs 
        self.AddTopShaper = False             # Add a top shaper to the mold
        self.AddFillet = True                 # Reinforcement curve at the base of the core
        self.FilletRadius = 5.0               # Radius of the base reinforcement
        self.AddGuideHoles = True             # Holes for metal alignment pins
        self.GuideDiameter = 6.5              # Diameter of the alignment pins
        self.GuideHoleCount = 6               # Number of guide holes (e.g., 4, 6, 8)
        self.GuideOffsetX = 6.0               # X-distance from the core edge
        self.GuideOffsetY = 10.0              # Y-distance from the mold's top/bottom edge
        self.AddWheelFlares = False           # Toggle 3D wheel flares
        self.AddMoldTruckPins = False         # Emboss truck hole pins on molds
        self.AddShaperTruckPins = False       # Emboss truck hole pins on shapers
        self.CutBase = False                  # Toggle to set Base Width equal to Core Width
        self.LogTruckWidths = False           # Flag to print deck width at truck coords
        self.ShowOuterWheelbase = False       # Toggle to show outer wheelbase equivalent
        self.IsMetric = True                  # Toggle for Metric (mm) vs Imperial (in)
        
        # --- MOLD DIMENSIONS ---
        self.MoldBaseWidth = 75.0             # Total width of the mold block
        self.MoldBaseHeight = 10.0            # Thickness of the solid structural base
        self.MoldCoreWidth = 45.0             # Width of the central pressing core
        self.MoldCoreHeight = 6.5             # Thickness of the core at its lowest point
        self.MoldLength = 115.0               # Total physical length of the mold block
        self.MoldCornerRadius = 5.0           # Radius of the mold's outer corners

        # --- TRUCK HOLES ---
        self.TruckHoleDiam = 1.7              # Diameter of the truck mounting holes
        self.TruckHoleDistL = 7.5             # Distance between the two truck holes (length)
        self.TruckHoleDistW = 5.5             # Distance between the two truck holes (width)
        
        # --- DECK GEOMETRY ---
        self.BoardWidth = 34.0                # Target width of the fingerboard deck
        self.Wheelbase = 44.0                 # Distance between the inner truck holes
        self.ConcaveDrop = 1.5                # Depth of the central concave
        self.ConcaveLength = 40.0             # Length of the central concave section
        self.AddSpoonKicks = False            # Toggle the spoon-shaped nose and tail sections
        self.SpoonDrop = 1.0                  # Additional drop in the nose and tail sections
        self.TubWidth = 8.0                   # Width of the totally flat central section
        self.VeneerThickness = 2.5            # Total physical thickness of the stacked wood veneers
        self.MoldGap = 2.5                    # Distance between the male and female molds
        
        # --- WHEEL FLARES ---
        self.FlareHeight = 0.5                # Maximum Z-height of the wheel flare bumps
        self.FlareLength = 10.0               # Total length of the flare along the board edge
        self.FlareWidth = 6.0                 # Distance the flare extends inwards
        self.FlarePosY = 3.0                  # Y-axis placement offset relative to the truck center

        # --- KICKS (NOSE & TAIL) ---
        self.NoseLength = 16.5                # Physical length of the nose section
        self.TailLength = 16.5                # Physical length of the tail section
        self.NoseAngle = 22.0                 # Steepness angle of the nose
        self.TailAngle = 22.0                 # Steepness angle of the tail
        self.NoseTransitionLength = 8.0       # Length of the smooth bend into the nose
        self.TailTransitionLength = 8.0       # Length of the smooth bend into the tail
        self.NoseKickGap = 1.5                # Flat distance from truck to nose transition
        self.TailKickGap = 1.5                # Flat distance from truck to tail transition
        
        # --- SHAPER / TEMPLATE ---
        self.ShaperHeight = 10.0              # Thickness of the 3D printed routing template
        self.FilletYellow = 3.0               # Radius of the shape's corner fillets (Custom Bezier)
        
        # --- BEZIER HANDLES (NOSE) ---
        self.NoseStraightP = 20.0             # Length of the straight parallel section (%)
        self.NoseCtrl1X = 100.0               # X-axis position of primary Bezier control point
        self.NoseCtrl1Y = 60.0                # Y-axis position of primary Bezier control point
        self.NoseCtrl2X = 85.0                # X-axis position of secondary Bezier control point
        
        # --- BEZIER HANDLES (TAIL) ---
        self.TailStraightP = 20.0             # Length of the straight parallel section (%)
        self.TailCtrl1X = 100.0               # X-axis position of primary Bezier control point
        self.TailCtrl1Y = 60.0                # Y-axis position of primary Bezier control point
        self.TailCtrl2X = 85.0                # X-axis position of secondary Bezier control point

        # --- LOGO / DEBOSS ---
        self.AddLogo = False                  # Enable/disable logo generation entirely
        self.LogoText = "TEXT"                # String rendered as 3D text
        self.LogoSize = 30.0                  # Approximate letter height in mm
        self.LogoDepth = 0.5                  # Extrusion depth of text
        self.LogoOffsetY = 0.0                # Vertical offset along board length
        self.LogoSpacing = 0.9                # Spacing multiplier between letters
        self.LogoRotationDeg = 0.0            # Rotation of each letter around Z axis (degrees)
        self.LogoInvert = True                # Mirror text for mold readability