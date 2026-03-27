"""
OpenCV-based pool ball detector.
Uses Hough circle detection + HSV color classification.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional


# Pool ball colors in HSV (H: 0-180 in OpenCV)
BALL_COLOR_RANGES = {
    "cue": {"lower": (0, 0, 80), "upper": (180, 55, 255)},
    "solid1": {"lower": (15, 40, 80), "upper": (35, 255, 255)},   # Yellow
    "solid2": {"lower": (85, 30, 50), "upper": (135, 255, 255)}, # Blue
    "solid3": {"lower": (0, 50, 60), "upper": (15, 255, 255)},    # Red
    "solid4": {"lower": (130, 30, 50), "upper": (170, 255, 255)}, # Purple
    "solid5": {"lower": (5, 50, 60), "upper": (25, 255, 255)},   # Orange
    "solid6": {"lower": (45, 40, 50), "upper": (80, 255, 255)},  # Green
    "solid7": {"lower": (0, 30, 30), "upper": (20, 200, 150)},   # Maroon/Brown
    "solid8": {"lower": (0, 0, 0), "upper": (180, 80, 80)},      # Black (8-ball)
    "stripe9":  {"lower": (85, 30, 50), "upper": (135, 255, 255)}, # Blue stripe
    "stripe10": {"lower": (15, 40, 80), "upper": (35, 255, 255)}, # Yellow stripe
    "stripe11": {"lower": (0, 50, 60), "upper": (15, 255, 255)}, # Red stripe
    "stripe12": {"lower": (130, 30, 50), "upper": (170, 255, 255)}, # Purple stripe
    "stripe13": {"lower": (5, 50, 60), "upper": (25, 255, 255)}, # Orange stripe
    "stripe14": {"lower": (45, 40, 50), "upper": (80, 255, 255)}, # Green stripe
    "stripe15": {"lower": (0, 30, 30), "upper": (20, 200, 150)}, # Maroon stripe
}


def detect_balls(image_bytes: bytes, table_size: str = "9ft") -> Dict:
    """
    Detect pool balls in an image.
    Uses Hough circles to find circular objects, then classifies by color.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"balls": [], "table_corners": [], "cue_ball": None, "detection_confidence": 0.0}
    
    height, width = img.shape[:2]
    
    # Ball diameter range in pixels (based on table size)
    if table_size == "7ft":
        expected_ball_px = min(width, height) * 0.035
    else:
        expected_ball_px = min(width, height) * 0.028
    
    min_radius = int(expected_ball_px * 0.6)
    max_radius = int(expected_ball_px * 1.3)
    
    # Preprocess
    blurred = cv2.GaussianBlur(img, (9, 9), 2)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Step 1: Find all circular objects using Hough transform
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1, 30,
        param1=50, param2=25,
        minRadius=min_radius, maxRadius=max_radius
    )
    
    detected_balls = []
    cue_ball = None
    
    if circles is not None:
        for circle in circles[0]:
            cx, cy, r = circle
            
            # Sample color at circle center
            x, y = int(cx), int(cy)
            if not (0 <= x < width and 0 <= y < height):
                continue
            
            # Get HSV at center pixel
            h, s, v = hsv[y, x]
            
            # Classify by color
            color, number = classify_ball_hsv(h, s, v)
            
            ball = {
                "x": float(cx),
                "y": float(cy),
                "radius": float(r),
                "color": color,
                "number": number
            }
            detected_balls.append(ball)
            
            if color == "cue":
                cue_ball = ball
    
    # Remove duplicates (same position)
    detected_balls = deduplicate_balls(detected_balls, min_radius * 0.5)
    
    # Re-find cue ball after deduplication
    cue_ball = next((b for b in detected_balls if b["color"] == "cue"), None)
    
    # Detect table corners
    detected_corners = detect_table_corners(img)
    
    # Calculate confidence
    confidence = calculate_detection_confidence(detected_balls, detected_corners, width, height)
    
    return {
        "balls": detected_balls,
        "table_corners": detected_corners,
        "cue_ball": cue_ball,
        "detection_confidence": confidence
    }


def classify_ball_hsv(h: int, s: int, v: int) -> Tuple[str, Optional[int]]:
    """
    Classify a ball based on its HSV color at center.
    Returns (color_name, ball_number).
    """
    # Cue ball: low saturation, high value (white/cream)
    if s < 60 and v > 70:
        return ("cue", None)
    
    # Black (8-ball): very low value, low saturation
    if v < 80 and s < 80:
        return ("solid8", 8)
    
    # Maroon/Brown (6 and 14): low saturation, dark
    if s < 60 and 30 <= v < 150:
        # Could be maroon or dark yellow - check hue
        if 0 <= h <= 20 or h >= 160:
            return ("solid7", 7)
        elif 45 <= h <= 80:
            return ("solid14", 14)
    
    # Color mapping by hue range
    # Yellow (1, 9): H 15-35
    if 10 <= h <= 40 and s >= 40:
        return ("solid1", 1)
    
    # Blue (2, 9): H 85-135
    if 80 <= h <= 140 and s >= 30:
        return ("solid2", 2)
    
    # Red (3, 11): H 0-15 or 160-180
    if (h <= 15 or h >= 160) and s >= 50:
        return ("solid3", 3)
    
    # Purple (4, 12): H 130-170
    if 125 <= h <= 175 and s >= 30:
        return ("solid4", 4)
    
    # Orange (5, 13): H 5-25 (between red and yellow)
    if 5 <= h <= 30 and s >= 50:
        return ("solid5", 5)
    
    # Green (6, 14): H 45-80
    if 40 <= h <= 85 and s >= 40:
        return ("solid6", 6)
    
    # Unknown - return as gray/white
    if s < 40:
        return ("cue", None)
    
    # Fallback
    return ("solid1", 1)


def deduplicate_balls(balls: List[Dict], min_distance: float) -> List[Dict]:
    """Remove balls that are too close to each other."""
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


def detect_table_corners(img: np.ndarray) -> List[Dict[str, float]]:
    """
    Detect table corners using edge detection and Hough lines.
    """
    height, width = img.shape[:2]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=20)
    
    if lines is None or len(lines) < 4:
        return [
            {"x": float(width * 0.1), "y": float(height * 0.1)},
            {"x": float(width * 0.9), "y": float(height * 0.1)},
            {"x": float(width * 0.1), "y": float(height * 0.9)},
            {"x": float(width * 0.9), "y": float(height * 0.9)}
        ]
    
    horizontal_lines = []
    vertical_lines = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        
        if angle < 10 or angle > 170:
            horizontal_lines.append((y1 + y2) / 2)
        elif 80 < angle < 100:
            vertical_lines.append((x1 + x2) / 2)
    
    if not horizontal_lines or not vertical_lines:
        return [
            {"x": float(width * 0.1), "y": float(height * 0.1)},
            {"x": float(width * 0.9), "y": float(height * 0.1)},
            {"x": float(width * 0.1), "y": float(height * 0.9)},
            {"x": float(width * 0.9), "y": float(height * 0.9)}
        ]
    
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
    
    ball_count_score = min(len(balls) / 10, 1.0) * 0.5
    corner_score = min(len(corners) / 4, 1.0) * 0.3
    
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
