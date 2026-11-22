"""Native bd_materials helpers with scalar PBR properties for viewer/snapshot/GLB compatibility."""

from bd_materials import metals, plastics, textile, wood


def apply_hardwood_walnut(shape) -> None:
    """Apply dark American walnut hardwood finish to a frame moulding part."""
    mat = wood.walnut()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.45)
    shape.material = mat
    shape.color = "#4A2E1B"


def apply_spline_walnut(shape) -> None:
    """Apply contrasting dark roasted walnut finish to corner spline joinery keys."""
    mat = wood.walnut()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.42)
    shape.material = mat
    shape.color = "#28160C"


def apply_veneer_plywood(shape) -> None:
    """Apply satin light warm-yellow birch/ash veneer plywood finish to the slotted mid-board."""
    mat = wood.birch()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.55)
    shape.material = mat
    shape.color = "#D6B884"


def apply_spacer_mdf(shape) -> None:
    """Apply dark-stained veneered MDF finish to the internal spacer strips."""
    mat = wood.mdf()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.68)
    shape.material = mat
    shape.color = "#3A2B22"


def apply_backboard_mdf(shape) -> None:
    """Apply natural/warm dark MDF finish to the removable backboard."""
    mat = wood.mdf()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.75)
    shape.material = mat
    shape.color = "#8E7358"


def apply_acrylic(shape) -> None:
    """Apply clear 1.5 mm PMMA acrylic cover appearance."""
    mat = plastics.pmma()
    mat.pbr = mat.pbr.strip_maps().override(
        roughness=0.05,
        transmission=0.92,
        ior=1.49,
        opacity=0.22,
    )
    shape.material = mat
    shape.color = "#DCEFF5"


def apply_medal_gold(shape) -> None:
    """Apply satin brushed gold/brass finish to a medal."""
    mat = metals.gold()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.26, metalness=0.95)
    shape.material = mat
    shape.color = "#D4AF37"


def apply_ribbon_fabric(shape) -> None:
    """Apply deep navy woven textile finish to a medal ribbon."""
    mat = textile.woven()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.82)
    shape.material = mat
    shape.color = "#1C355E"


def apply_hardware_steel(shape) -> None:
    """Apply dark gunmetal/zinc-plated heavy-duty steel finish to turn buttons, D-rings, and screws."""
    mat = metals.mild_steel()
    mat.pbr = mat.pbr.strip_maps().override(roughness=0.32, metalness=0.9)
    shape.material = mat
    shape.color = "#4E555E"

