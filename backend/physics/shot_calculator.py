"""
Shot calculator - physics engine for pool shot recommendations.
Calculates cue path, object path, ghost ball position, power, and English.
"""

import math
from typing import List, Dict, Tuple, Optional


# Pool ball diameter in inches
BALL_DIAMETER = 2.25
BALL_RADIUS = BALL_DIAMETER / 2

# Pocket diameter in inches (corner vs side)
POCKET_DIAMETER_CORNER = 4.5
POCKET_DIAMETER_SIDE = 4.0

# Pocket names for reference
POCKET_NAMES = [
    "top_left", "top_right", "middle_left", "middle_right", "bottom_left", "bottom_right"
]

# Game-specific rules
GAME_RULES = {
    "8ball": {
        "description": "8-ball",
        "considers_scratch": True,
        "considers分组": True,  # Solids vs stripes
        "safest_shot_priority": True
    },
    "9ball": {
        "description": "9-ball",
        "considers_scratch": False,
        "considers分组": False,
        "safest_shot_priority": False,
        "lowest_ball_first": True
    },
    "straight": {
        "description": "Straight pool",
        "considers_scratch": False,
        "considers分组": False,
        "safest_shot_priority": False
    }
}

# Skill level adjustments
SKILL_ADJUSTMENTS = {
    "beginner": {
        "ghost_ball_offset": 0.3,  # Larger ghost ball (easier hit)
        "max_english": 0.3,       # Limited English
        "min_power": 0.4,
        "preferred_angle_range": (20, 65)  # Prefer medium cuts (20-65°)
    },
    "intermediate": {
        "ghost_ball_offset": 0.15,
        "max_english": 0.6,
        "min_power": 0.3,
        "preferred_angle_range": (5, 80)  # Allow thin cuts and nearly straight (5-80°)
    },
    "pro": {
        "ghost_ball_offset": 0.0,  # Precise
        "max_english": 1.0,
        "min_power": 0.1,
        "preferred_angle_range": (0, 89)  # Nearly any cut angle (0-89°)
    }
}


def calculate_shot(
    cue_ball: Dict,
    balls: List[Dict],
    pockets: List[Dict],
    table_size: str,
    game_type: str,
    skill_level: str
) -> Dict:
    """
    Calculate the optimal shot based on current table state.
    
    Args:
        cue_ball: Cue ball position {x, y}
        balls: All ball positions [{x, y, color, number}, ...]
        pockets: Pocket positions [{name, x, y}, ...]
        table_size: "7ft" or "9ft"
        game_type: "8ball", "9ball", or "straight"
        skill_level: "beginner", "intermediate", or "pro"
    
    Returns:
        Shot result dict with ghost_ball, paths, power, english, angle, confidence
    """
    if not cue_ball or "x" not in cue_ball or "y" not in cue_ball:
        return create_error_result("Cue ball not found")
    
    if not balls or len(balls) < 1:
        return create_error_result("No object balls found")
    
    if not pockets or len(pockets) < 6:
        return create_error_result("Pocket positions not available")
    
    # Get game rules and skill adjustments
    rules = GAME_RULES.get(game_type, GAME_RULES["8ball"])
    skill = SKILL_ADJUSTMENTS.get(skill_level, SKILL_ADJUSTMENTS["intermediate"])
    
    # Filter out cue ball from object balls
    object_balls = [b for b in balls if b.get("color") != "cue"]
    
    if not object_balls:
        return create_error_result("No object balls on table")
    
    # Score all possible shots
    shots = []
    for ball in object_balls:
        for pocket in pockets:
            shot = score_shot(cue_ball, ball, pocket, skill)
            if shot:
                shots.append(shot)
    
    if not shots:
        return create_error_result("No valid shots found")
    
    # Sort by score (higher is better)
    shots.sort(key=lambda s: s["score"], reverse=True)
    
    # Apply game-specific filtering
    if game_type == "9ball":
        # In 9-ball, must hit lowest numbered ball first
        lowest_ball = min(object_balls, key=lambda b: b.get("number", 99) if b.get("number") else 99)
        if lowest_ball.get("number"):
            shots = [s for s in shots if s["target_ball"].get("number") == lowest_ball["number"]]
            if not shots:
                shots = [s for s in shots if s["target_ball"].get("number") in range(1, 10)]
    
    # Take best shot
    best_shot = shots[0]
    
    # Calculate paths
    cue_path = calculate_cue_path(cue_ball, best_shot["ghost_ball"])
    object_path = calculate_object_path(best_shot["ghost_ball"], best_shot["target_pocket"])
    
    # Calculate power and English based on distance and angle
    distance = math.sqrt(
        (best_shot["ghost_ball"]["x"] - cue_ball["x"])**2 +
        (best_shot["ghost_ball"]["y"] - cue_ball["y"])**2
    )
    angle = best_shot["angle"]
    
    power = calculate_power(distance, angle, skill)
    english = calculate_english(angle, distance, skill, best_shot)
    
    return {
        "ghost_ball": best_shot["ghost_ball"],
        "cue_path": cue_path,
        "object_path": object_path,
        "target_pocket": best_shot["target_pocket"]["name"],
        "target_ball_number": best_shot["target_ball"].get("number"),
        "power": round(power, 2),
        "english": round(english, 2),  # -1.0 to 1.0
        "angle": round(angle, 1),     # degrees
        "distance": round(distance, 1),
        "score": round(best_shot["score"], 2),
        "confidence": round(best_shot["confidence"], 2)
    }


def score_shot(
    cue_ball: Dict,
    object_ball: Dict,
    pocket: Dict,
    skill: Dict
) -> Optional[Dict]:
    """
    Score a specific shot (cue ball → object ball → pocket).
    Returns None if shot is not physically possible.
    """
    # Calculate cue ball to object ball vector
    dx_obj = object_ball["x"] - cue_ball["x"]
    dy_obj = object_ball["y"] - cue_ball["y"]
    dist_cue_to_obj = math.sqrt(dx_obj**2 + dy_obj**2)
    
    if dist_cue_to_obj < BALL_DIAMETER:
        return None  # Balls overlapping or same position
    
    # Calculate object ball to pocket vector
    dx_pocket = pocket["x"] - object_ball["x"]
    dy_pocket = pocket["y"] - object_ball["y"]
    dist_obj_to_pocket = math.sqrt(dx_pocket**2 + dy_pocket**2)
    
    if dist_obj_to_pocket < BALL_DIAMETER:
        return None  # Ball is at pocket
    
    # Calculate angle between cue-to-object and object-to-pocket lines
    # This determines if the shot is geometrically possible
    cue_angle = math.atan2(dy_obj, dx_obj)
    pocket_angle = math.atan2(dy_pocket, dx_pocket)
    angle_diff = abs(cue_angle - pocket_angle)
    # Normalize to [0, pi] — angles > 180° get wrapped
    if angle_diff > math.pi:
        angle_diff = 2 * math.pi - angle_diff
    # shot_angle: degrees of required ball deflection (small = thin cut)
    shot_angle = angle_diff * (180 / math.pi)
    
    # Ghost ball position (where cue ball needs to be for center-to-center contact)
    # Ghost ball is offset in the direction of the pocket
    offset_x = (dx_pocket / dist_obj_to_pocket) * BALL_RADIUS
    offset_y = (dy_pocket / dist_obj_to_pocket) * BALL_RADIUS
    
    ghost_ball = {
        "x": object_ball["x"] + offset_x,
        "y": object_ball["y"] + offset_y
    }
    
    # shot_angle already computed above (angle_diff * 180/pi, capped at pi)
    
    # Check if shot angle is within acceptable range for skill level
    min_angle, max_angle = skill["preferred_angle_range"]
    if shot_angle < min_angle or shot_angle > max_angle:
        return None
    
    # Check if object ball can fit in pocket (cut angle limit)
    # Corner pocket: ball can enter at up to ~67° off-center
    # Side pocket: ball can enter at up to ~75° off-center
    max_cut_angle = 67.5
    if "middle" in pocket.get("name", ""):
        max_cut_angle = 75.0
    if shot_angle > max_cut_angle:
        return None
    
    # Calculate score based on multiple factors
    score = 0.0
    
    # Distance score (closer = easier, higher score)
    total_distance = dist_cue_to_obj + dist_obj_to_pocket
    max_reasonable_distance = 2000  # pixels
    distance_score = max(0, 1 - (total_distance / max_reasonable_distance)) * 30
    score += distance_score
    
    # Angle score (straighter = easier, higher score)
    angle_score = (shot_angle / 90) * 30
    score += angle_score
    
    # Pocket difficulty (corner pockets are harder)
    pocket_difficulty = 1.0
    if "middle" in pocket["name"]:
        pocket_difficulty = 0.8
    score += pocket_difficulty * 20
    
    # Skill-based ghost ball offset (larger = easier)
    ghost_ball_offset = skill.get("ghost_ball_offset", 0.15)
    adjusted_ghost = {
        "x": ghost_ball["x"] - offset_x * ghost_ball_offset,
        "y": ghost_ball["y"] - offset_y * ghost_ball_offset
    }
    
    # Confidence based on margin for error
    # Higher skill = more confidence
    confidence_base = 0.5 + skill["ghost_ball_offset"] * 2
    confidence = min(confidence_base, 0.95)
    
    return {
        "target_ball": object_ball,
        "target_pocket": pocket,
        "ghost_ball": adjusted_ghost,
        "angle": shot_angle,
        "cue_ball_to_object_distance": dist_cue_to_obj,
        "object_to_pocket_distance": dist_obj_to_pocket,
        "score": score,
        "confidence": confidence
    }


def calculate_cue_path(cue_ball: Dict, ghost_ball: Dict) -> List[Dict]:
    """Calculate the path the cue ball travels."""
    return [
        {"x": round(cue_ball["x"], 2), "y": round(cue_ball["y"], 2)},
        {"x": round(ghost_ball["x"], 2), "y": round(ghost_ball["y"], 2)}
    ]


def calculate_object_path(ghost_ball: Dict, target_pocket: Dict) -> List[Dict]:
    """Calculate the path the object ball travels after contact."""
    return [
        {"x": round(ghost_ball["x"], 2), "y": round(ghost_ball["y"], 2)},
        {"x": round(target_pocket["x"], 2), "y": round(target_pocket["y"], 2)}
    ]


def calculate_power(distance: float, angle: float, skill: Dict) -> float:
    """
    Calculate recommended power (0.0 to 1.0).
    
    Factors:
    - Distance (longer = need more power)
    - Cut angle (more cut = need controlled power)
    """
    # Base power from distance (normalize to 0-1)
    # Assume max practical distance is ~1500 pixels
    distance_power = min(distance / 1500, 1.0) * 0.5
    
    # Angle adjustment (more cut = slightly less power for control)
    angle_factor = 1.0 - (abs(angle - 45) / 90) * 0.3
    
    # Skill factor (higher skill = can use more precise power)
    skill_power = 0.5 + skill["ghost_ball_offset"] * 0.5
    
    power = distance_power * angle_factor * skill_power
    
    # Clamp to skill minimum
    min_power = skill.get("min_power", 0.3)
    power = max(power, min_power)
    
    return min(power, 1.0)


def calculate_english(angle: float, distance: float, skill: Dict, shot: Dict) -> float:
    """
    Calculate recommended English/spin (-1.0 to 1.0).
    
    - Positive = right English (draw/screw potential)
    - Negative = left English
    0.0 = center ball
    """
    max_english = skill.get("max_english", 0.5)
    
    # For straight shots, minimal English needed
    if angle > 60:  # Nearly straight
        return 0.0
    
    # For cut shots, slight English helps with spin transfer
    # Right English for left-side cuts, left English for right-side cuts
    # This is a simplified model
    
    english = 0.0
    
    # Adjust for distance (longer shots benefit from running English)
    if distance > 500:
        english = 0.2 * max_english
    
    # Adjust based on target ball position relative to pocket
    # (simplified - doesn't account for full geometry)
    
    return max(-max_english, min(max_english, english))


def create_error_result(reason: str) -> Dict:
    """Create an error result."""
    return {
        "error": reason,
        "ghost_ball": None,
        "cue_path": [],
        "object_path": [],
        "target_pocket": None,
        "power": 0.0,
        "english": 0.0,
        "angle": 0.0,
        "confidence": 0.0
    }


def get_shot_quality_description(shot: Dict) -> str:
    """Get a human-readable description of shot quality."""
    power = shot.get("power", 0)
    angle = shot.get("angle", 90)
    english = shot.get("english", 0)
    
    if power < 0.3:
        power_desc = "Soft"
    elif power < 0.6:
        power_desc = "Medium"
    else:
        power_desc = "Power"
    
    if angle > 60:
        angle_desc = "Straight"
    elif angle > 30:
        angle_desc = "Cut"
    else:
        angle_desc = "Thin cut"
    
    if abs(english) < 0.1:
        spin_desc = "Center ball"
    elif english > 0:
        spin_desc = f"Right {abs(int(english * 100))}%"
    else:
        spin_desc = f"Left {abs(int(english * 100))}%"
    
    return f"{power_desc} {angle_desc} shot — {spin_desc}"
