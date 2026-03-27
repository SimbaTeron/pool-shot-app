"""
OpenCV-based pool ball detector.
Uses HSV color segmentation + Hough circle detection.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional


# Pool ball colors in HSV (H: 0-180 in OpenCV)
BALL_COLOR_RANGES = {
    "cue": {"lower": (0, 0, 150), "upper": (30, 60, 255)},
    "solid1": {"lower": (0, 100, 100), "upper": (10, 255, 255)},   # Yellow
    "solid2": {"lower": (100, 100, 50), "upper": (130, 255, 255)}, # Blue
    "solid3": {"lower": (0, 100, 50), "upper": (30, 255, 255)},    # Red
    "solid4": {"lower": (130, 80, 50), "upper": (170, 255, 255)}, # Purple
    "solid5": {"lower": (15, 100, 50), "upper": (45, 255, 255)}, # Orange
    "solid6": {"lower": (75, 80, 50), "upper": (95, 255, 255)},   # Green
    "solid7": {"lower": (0, 50, 30), "upper": (20, 150, 150)},   # Maroon/Brown
    "solid8": {"lower": (0, 0, 0), "upper": (180, 255, 30)},     # Black (8-ball)
    "stripe9": {"lower": (100, 100, 50), "upper": (130, 255, 255)}, # Blue stripe
    "stripe10": {"lower": (0, 100, 100), "upper": (10, 255, 255)}, # Yellow stripe
    "stripe11": {"lower": (0, 100, 50), "upper": (30, 255, 255)}, # Red stripe
    "stripe12": {"lower": (130, 80, 50), "upper": (170, 255, 255)}, # Purple stripe
    "stripe13": {"lower": (15, 100, 50), "upper": (45, 255, 255)}, # Orange stripe
    "stripe14": {"lower": (75, 80, 50), "upper": (95, 255, 255)}, # Green stripe
    "stripe15": {"lower": (0, 50, 30), "upper": (20, 150, 150)}, # Maroon stripe
}

# Pocket positions relative to table dimensions (2:1 ratio)
# Order: top-left, top-right, middle-left, middle-right, bottom-left, bottom-right
POCKET_POSITIONS = [
    (0.05, 0.05),   # Top-left corner
    (0.95, 0.05),   # Top-right corner
    (0.0, 0.5),     # Middle-left
    (1.0, 0.5),     # Middle-right
    (0.05, 0.95),   # Bottom-left corner
    (0.95, 0.95),   # Bottom-right corner
]


def detect_balls(image_bytes: bytes, table_size: str = "9ft") -> Dict:
    """
    Detect pool balls in an image.
    
    Args:
        image_bytes: Raw JPEG image bytes
        table_size: "7ft" or "9ft" (affects expected ball diameter range)
    
    Returns:
        Dict with balls, table_corners, cue_ball, confidence
    """
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"balls": [], "table_corners": [], "cue_ball": None, "detection_confidence": 0.0}
    
    height, width = img.shape[:2]
    
    # Ball diameter range in pixels (based on table size)
    # 7ft: ~78" table, 9ft: ~100" table
    if table_size == "7ft":
        expected_ball_px = min(width, height) * 0.035
    else:
        expected_ball_px = min(width, height) * 0.028
    
    min_radius = int(expected_ball_px * 0.85)
    max_radius = int(expected_ball_px * 1.2)
    
    # Preprocess
    blurred = cv2.GaussianBlur(img, (9, 9), 2)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    detected_balls = []
    detected_corners = []
    
    # Detect cue ball first (white, most reflective)
    cue_mask = create_cue_ball_mask(hsv)
    cue_ball = find_ball_in_mask(cue_mask, hsv, min_radius, max_radius, "cue")
    if cue_ball:
        detected_balls.append(cue_ball)
    
    # Detect colored balls
    for color_name, ranges in BALL_COLOR_RANGES.items():
        if color_name == "cue":
            continue
        mask = cv2.inRange(hsv, np.array(ranges["lower"]), np.array(ranges["upper"]))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        balls = find_balls_in_mask(mask, hsv, min_radius, max_radius, color_name)
        detected_balls.extend(balls)
    
    # Remove duplicates (balls detected in multiple color ranges)
    detected_balls = deduplicate_balls(detected_balls, min_radius * 0.5)
    
    # Find cue ball in final list
    cue_ball_result = next((b for b in detected_balls if b["color"] == "cue"), None)
    
    # Detect table corners
    detected_corners = detect_table_corners(img)
    
    # Calculate confidence based on ball count and detection quality
    confidence = calculate_detection_confidence(detected_balls, detected_corners, width, height)
    
    return {
        "balls": detected_balls,
        "table_corners": detected_corners,
        "cue_ball": cue_ball_result,
        "detection_confidence": confidence
    }


def create_cue_ball_mask(hsv: np.ndarray) -> np.ndarray:
    """Create a mask for the cue ball (white/cream colored)."""
    # White/cream range - cue balls are slightly off-white
    lower_white = np.array([0, 0, 150])
    upper_white = np.array([30, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Also check for very bright areas (reflections)
    lower_bright = np.array([0, 0, 200])
    upper_bright = np.array([180, 30, 255])
    bright_mask = cv2.inRange(hsv, lower_bright, upper_bright)
    
    return cv2.bitwise_or(mask, bright_mask)


def find_ball_in_mask(mask: np.ndarray, hsv: np.ndarray, min_radius: int, max_radius: int, color: str) -> Optional[Dict]:
    """Find a single ball in a mask (used for cue ball)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Find largest contour
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    
    if area < (min_radius ** 2) * 0.5:
        return None
    
    # Fit circle
    ((x, y), radius) = cv2.minEnclosingCircle(largest)
    
    if min_radius <= radius <= max_radius:
        return {
            "x": float(x),
            "y": float(y),
            "radius": float(radius),
            "color": color,
            "number": None
        }
    
    return None


def find_balls_in_mask(mask: np.ndarray, hsv: np.ndarray, min_radius: int, max_radius: int, color: str) -> List[Dict]:
    """Find multiple balls in a mask (used for colored balls)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    balls = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area < (min_radius ** 2) * 0.5:
            continue
        
        ((x, y), radius) = cv2.minEnclosingCircle(contour)
        
        if min_radius <= radius <= max_radius:
            # Determine ball number from color
            number = color_name_to_number(color)
            balls.append({
                "x": float(x),
                "y": float(y),
                "radius": float(radius),
                "color": color,
                "number": number
            })
    
    return balls


def deduplicate_balls(balls: List[Dict], min_distance: float) -> List[Dict]:
    """Remove balls that are too close to each other (likely duplicates)."""
    if not balls:
        return []
    
    unique = []
    for ball in balls:
        is_duplicate = False
        for unique_ball in unique:
            dist = np.sqrt((ball["x"] - unique_ball["x"])**2 + (ball["y"] - unique_ball["y"])**2)
            if dist < min_distance:
                is_duplicate = True
                break
        if not is_duplicate:
            unique.append(ball)
    
    return unique


def color_name_to_number(color: str) -> Optional[int]:
    """Map color name to ball number."""
    mapping = {
        "solid1": 1, "solid2": 2, "solid3": 3, "solid4": 4,
        "solid5": 5, "solid6": 6, "solid7": 7, "solid8": 8,
        "stripe9": 9, "stripe10": 10, "stripe11": 11, "stripe12": 12,
        "stripe13": 13, "stripe14": 14, "stripe15": 15,
        "cue": None
    }
    return mapping.get(color)


def detect_table_corners(img: np.ndarray) -> List[Dict[str, float]]:
    """
    Detect table corners using edge detection and Hough lines.
    Returns the 4 corner points of the table.
    """
    height, width = img.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Canny edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Detect lines using HoughLinesP
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=20)
    
    if lines is None or len(lines) < 4:
        # Fallback: return image corners as approximate table corners
        return [
            {"x": float(width * 0.1), "y": float(height * 0.1)},
            {"x": float(width * 0.9), "y": float(height * 0.1)},
            {"x": float(width * 0.1), "y": float(height * 0.9)},
            {"x": float(width * 0.9), "y": float(height * 0.9)}
        ]
    
    # Find the 4 most prominent horizontal and vertical lines
    horizontal_lines = []
    vertical_lines = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        
        if angle < 10 or angle > 170:  # Nearly horizontal
            horizontal_lines.append((y1 + y2) / 2)
        elif 80 < angle < 100:  # Nearly vertical
            vertical_lines.append((x1 + x2) / 2)
    
    if not horizontal_lines or not vertical_lines:
        return [
            {"x": float(width * 0.1), "y": float(height * 0.1)},
            {"x": float(width * 0.9), "y": float(height * 0.1)},
            {"x": float(width * 0.1), "y": float(height * 0.9)},
            {"x": float(width * 0.9), "y": float(height * 0.9)}
        ]
    
    # Get median positions
    horizontal_lines.sort()
    vertical_lines.sort()
    
    top_y = np.median(horizontal_lines[:len(horizontal_lines)//2])
    bottom_y = np.median(horizontal_lines[len(horizontal_lines)//2:])
    left_x = np.median(vertical_lines[:len(vertical_lines)//2])
    right_x = np.median(vertical_lines[len(vertical_lines)//2:])
    
    return [
        {"x": float(left_x), "y": float(top_y)},
        {"x": float(right_x), "y": float(top_y)},
        {"x": float(left_x), "y": float(bottom_y)},
        {"x": float(right_x), "y": float(bottom_y)}
    ]


def calculate_detection_confidence(balls: List[Dict], corners: List[Dict], img_width: int, img_height: int) -> float:
    """Calculate a confidence score for the detection."""
    if not balls:
        return 0.0
    
    # Base confidence from number of balls detected
    # A full rack has 16 balls (1 cue + 15 object)
    ball_count_score = min(len(balls) / 10, 1.0) * 0.5
    
    # Confidence from table corner detection
    corner_score = min(len(corners) / 4, 1.0) * 0.3
    
    # Confidence from ball distribution (should be spread across the table)
    if len(balls) >= 2:
        xs = [b["x"] for b in balls]
        ys = [b["y"] for b in balls]
        spread_x = max(xs) - min(xs)
        spread_y = max(ys) - min(ys)
        expected_spread_x = img_width * 0.6
        expected_spread_y = img_height * 0.6
        spread_score = min(spread_x / expected_spread_x, 1.0) * 0.1 + min(spread_y / expected_spread_y, 1.0) * 0.1
    else:
        spread_score = 0.0
    
    return round(ball_count_score + corner_score + spread_score, 2)
