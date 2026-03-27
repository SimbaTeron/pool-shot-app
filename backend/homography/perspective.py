"""
Homography engine for perspective correction.
Maps a 2D camera view of a pool table to a flat top-down view.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional


# Real-world table dimensions in inches
TABLE_DIMENSIONS = {
    "7ft": {"width": 78, "height": 39, "name": "Bar 7ft"},
    "9ft": {"width": 100, "height": 50, "name": "Regulation 9ft"}
}

# Pocket positions relative to table dimensions (0.0 to 1.0)
POCKET_POSITIONS = {
    "7ft": {
        "top_left": (0.08, 0.08),
        "top_right": (0.92, 0.08),
        "middle_left": (0.0, 0.5),
        "middle_right": (1.0, 0.5),
        "bottom_left": (0.08, 0.92),
        "bottom_right": (0.92, 0.92)
    },
    "9ft": {
        "top_left": (0.07, 0.07),
        "top_right": (0.93, 0.07),
        "middle_left": (0.0, 0.5),
        "middle_right": (1.0, 0.5),
        "bottom_left": (0.07, 0.93),
        "bottom_right": (0.93, 0.93)
    }
}


def compute_homography(corners: List[Dict[str, float]], table_size: str) -> Tuple[Optional[np.ndarray], int, int]:
    """
    Compute homography matrix to transform camera view to top-down view.
    
    Args:
        corners: 4 table corners from detection (each with x, y)
        table_size: "7ft" or "9ft"
    
    Returns:
        Tuple of (homography_matrix, output_width, output_height) in pixels
        Returns (None, 0, 0) if corners are invalid
    """
    if len(corners) != 4:
        return None, 0, 0
    
    dims = TABLE_DIMENSIONS[table_size]
    aspect_ratio = dims["width"] / dims["height"]  # Should be 2:1
    
    # Sort corners: top-left, top-right, bottom-left, bottom-right
    sorted_corners = sort_corners(corners)
    
    # Source points (detected corners in image)
    src_pts = np.array([
        [sorted_corners[0]["x"], sorted_corners[0]["y"]],  # top-left
        [sorted_corners[1]["x"], sorted_corners[1]["y"]],  # top-right
        [sorted_corners[2]["x"], sorted_corners[2]["y"]],  # bottom-left
        [sorted_corners[3]["x"], sorted_corners[3]["y"]]   # bottom-right
    ], dtype=np.float32)
    
    # Calculate output dimensions maintaining aspect ratio
    # Use the larger dimension as reference
    max_dim = 800  # Max output dimension in pixels
    if aspect_ratio >= 2:
        output_width = max_dim
        output_height = int(max_dim / aspect_ratio)
    else:
        output_height = max_dim
        output_width = int(max_dim * aspect_ratio)
    
    # Destination points (flat top-down view)
    dst_pts = np.array([
        [0, 0],
        [output_width - 1, 0],
        [0, output_height - 1],
        [output_width - 1, output_height - 1]
    ], dtype=np.float32)
    
    # Compute homography
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    
    if H is None:
        return None, 0, 0
    
    return H, output_width, output_height


def sort_corners(corners: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """Sort corners into top-left, top-right, bottom-left, bottom-right order."""
    pts = [(c["x"], c["y"]) for c in corners]
    
    # Sort by x to get left/right
    pts.sort(key=lambda p: p[0])
    left_pts = pts[:2]
    right_pts = pts[2:]
    
    # Sort each side by y to get top/bottom
    left_pts.sort(key=lambda p: p[1])
    right_pts.sort(key=lambda p: p[1])
    
    return [
        {"x": left_pts[0][0], "y": left_pts[0][1]},   # top-left
        {"x": right_pts[0][0], "y": right_pts[0][1]},  # top-right
        {"x": left_pts[1][0], "y": left_pts[1][1]},   # bottom-left
        {"x": right_pts[1][0], "y": right_pts[1][1]}   # bottom-right
    ]


def warp_point(x: float, y: float, H: np.ndarray) -> Tuple[float, float]:
    """Transform a point using the homography matrix."""
    pt = np.array([x, y, 1.0])
    warped = H @ pt
    return (warped[0] / warped[2], warped[1] / warped[2])


def warp_ball(ball: Dict, H: np.ndarray) -> Dict:
    """Transform a ball's position using the homography matrix."""
    if "x" not in ball or "y" not in ball:
        return ball
    
    new_x, new_y = warp_point(ball["x"], ball["y"], H)
    return {
        **ball,
        "x": round(new_x, 2),
        "y": round(new_y, 2)
    }


def warp_balls(balls: List[Dict], H: np.ndarray) -> List[Dict]:
    """Transform all ball positions."""
    return [warp_ball(ball, H) for ball in balls]


def get_pocket_positions(table_size: str, H: np.ndarray, output_width: int, output_height: int) -> List[Dict]:
    """
    Get pocket positions in warped coordinates.
    
    Returns list of {name, x, y} for each pocket.
    """
    pockets = POCKET_POSITIONS[table_size]
    result = []
    
    for name, (rx, ry) in pockets.items():
        # Convert relative position to pixel position
        x = rx * output_width
        y = ry * output_height
        result.append({"name": name, "x": round(x, 2), "y": round(y, 2)})
    
    return result


def pixels_to_inches(x: float, y: float, table_size: str, output_width: int, output_height: int) -> Tuple[float, float]:
    """Convert pixel coordinates to real-world inches."""
    dims = TABLE_DIMENSIONS[table_size]
    
    inches_x = (x / output_width) * dims["width"]
    inches_y = (y / output_height) * dims["height"]
    
    return (round(inches_x, 2), round(inches_y, 2))


def inches_to_pixels(x_inches: float, y_inches: float, table_size: str, output_width: int, output_height: int) -> Tuple[float, float]:
    """Convert real-world inches to pixel coordinates."""
    dims = TABLE_DIMENSIONS[table_size]
    
    x = (x_inches / dims["width"]) * output_width
    y = (y_inches / dims["height"]) * output_height
    
    return (round(x, 2), round(y, 2))


def get_table_mask(output_width: int, output_height: int) -> np.ndarray:
    """Generate a mask showing the playable table surface (excluding rails)."""
    mask = np.zeros((output_height, output_width), dtype=np.uint8)
    
    # Inner table boundary (rails are typically 1.5-2 inches)
    rail_thickness = int(min(output_width, output_height) * 0.04)
    
    mask[rail_thickness:-rail_thickness, rail_thickness:-rail_thickness] = 255
    
    return mask


def validate_ball_on_table(ball: Dict, output_width: int, output_height: int) -> bool:
    """Check if a ball is within the playable table surface."""
    if "x" not in ball or "y" not in ball:
        return False
    
    x, y = ball["x"], ball["y"]
    
    # Apply margin for rails
    margin = int(min(output_width, output_height) * 0.04)
    
    return (margin <= x <= output_width - margin and 
            margin <= y <= output_height - margin)
