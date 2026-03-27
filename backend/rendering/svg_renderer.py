"""
SVG renderer for pool shot diagrams.
Generates clean, professional shot overlays using programmatic SVG.
"""

from typing import Dict, List, Optional
import numpy as np


# Color palette
COLORS = {
    "background": "#0D1117",
    "surface": "#161B22",
    "primary": "#58A6FF",
    "cue_path": "#F0F6FC",
    "object_path": "#79C0FF",
    "ghost_ball": "#58A6FF",
    "power_low": "#3FB950",
    "power_med": "#D29922",
    "power_high": "#F85149",
    "english_left": "#BC8CFF",
    "english_right": "#FFA657",
    "text_primary": "#F0F6FC",
    "text_muted": "#8B949E",
    "table_felt": "#0A4D2E",
    "table_rail": "#4A3728",
    "pocket": "#111111",
    "ball_white": "#FFFFFF",
    "ball_yellow": "#FFD700",
    "ball_blue": "#0000FF",
    "ball_red": "#FF0000",
    "ball_purple": "#800080",
    "ball_orange": "#FFA500",
    "ball_green": "#008000",
    "ball_maroon": "#800000",
    "ball_black": "#111111",
}


def get_ball_color(ball: Dict) -> str:
    """Get the SVG color for a ball based on its color/number."""
    color = ball.get("color", "cue")
    number = ball.get("number")
    
    color_map = {
        "cue": COLORS["ball_white"],
        "solid1": COLORS["ball_yellow"],
        "solid2": COLORS["ball_blue"],
        "solid3": COLORS["ball_red"],
        "solid4": COLORS["ball_purple"],
        "solid5": COLORS["ball_orange"],
        "solid6": COLORS["ball_green"],
        "solid7": COLORS["ball_maroon"],
        "solid8": COLORS["ball_black"],
        "stripe9": COLORS["ball_blue"],
        "stripe10": COLORS["ball_yellow"],
        "stripe11": COLORS["ball_red"],
        "stripe12": COLORS["ball_purple"],
        "stripe13": COLORS["ball_orange"],
        "stripe14": COLORS["ball_green"],
        "stripe15": COLORS["ball_maroon"],
    }
    
    return color_map.get(color, COLORS["ball_white"])


def render_shot_diagram(
    shot_data: Dict,
    balls: List[Dict],
    pockets: List[Dict],
    output_width: int = 800,
    output_height: int = 400,
    show_paths: bool = True,
    show_labels: bool = True,
    animated: bool = True
) -> str:
    """
    Render a complete shot diagram as SVG.
    
    Args:
        shot_data: Shot calculation result
        balls: All ball positions
        pockets: Pocket positions
        output_width: SVG width
        output_height: SVG height
        show_paths: Whether to show cue/object paths
        show_labels: Whether to show text labels
        animated: Whether to include draw animations
    
    Returns:
        SVG string
    """
    svg_parts = []
    
    # SVG header
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 {output_width} {output_height}" 
    width="{output_width}" height="{output_height}"
    style="background:{COLORS["background"]}">''')
    
    # Definitions (gradients, filters)
    svg_parts.append(_get_defs())
    
    # Table surface
    svg_parts.append(_render_table(output_width, output_height))
    
    # Pockets
    svg_parts.append(_render_pockets(pockets, output_width, output_height))
    
    # Paths (behind balls)
    if show_paths and "cue_path" in shot_data and shot_data["cue_path"]:
        svg_parts.append(_render_paths(shot_data, animated))
    
    # Ghost ball
    if shot_data.get("ghost_ball"):
        svg_parts.append(_render_ghost_ball(shot_data["ghost_ball"], animated))
    
    # Balls
    svg_parts.append(_render_balls(balls, shot_data))
    
    # Labels and indicators
    if show_labels:
        svg_parts.append(_render_power_indicator(shot_data, output_width, output_height))
        svg_parts.append(_render_english_indicator(shot_data, output_width, output_height))
        svg_parts.append(_render_angle_label(shot_data, output_width, output_height))
        svg_parts.append(_render_shot_info(shot_data, output_width, output_height))
    
    # Animation keyframes (if animated)
    if animated:
        svg_parts.append(_get_animations())
    
    svg_parts.append("</svg>")
    
    return "\n".join(svg_parts)


def _get_defs() -> str:
    """Get SVG definitions (gradients, filters)."""
    return '''
    <defs>
        <!-- Ghost ball gradient -->
        <radialGradient id="ghostBallGradient" cx="30%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#8FCFFF" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#58A6FF" stop-opacity="0.3"/>
        </radialGradient>
        
        <!-- Cue path gradient -->
        <linearGradient id="cuePathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#F0F6FC" stop-opacity="1"/>
            <stop offset="100%" stop-color="#F0F6FC" stop-opacity="0.5"/>
        </linearGradient>
        
        <!-- Object path gradient -->
        <linearGradient id="objectPathGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#79C0FF" stop-opacity="0.5"/>
            <stop offset="100%" stop-color="#79C0FF" stop-opacity="1"/>
        </linearGradient>
        
        <!-- Power arc gradient -->
        <linearGradient id="powerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#3FB950"/>
            <stop offset="50%" stop-color="#D29922"/>
            <stop offset="100%" stop-color="#F85149"/>
        </linearGradient>
        
        <!-- Drop shadow filter -->
        <filter id="ballShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="1" dy="1" stdDeviation="2" flood-color="#000" flood-opacity="0.5"/>
        </filter>
        
        <!-- Glow filter for ghost ball -->
        <filter id="ghostGlow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>'''


def _render_table(width: int, height: int) -> str:
    """Render the pool table surface."""
    # Felt surface
    felt = f'''<rect x="20" y="20" width="{width-40}" height="{height-40}" 
    fill="{COLORS["table_felt"]}" rx="8" ry="8"/>'''
    
    # Rail border
    rail = f'''<rect x="10" y="10" width="{width-20}" height="{height-20}" 
    fill="none" stroke="{COLORS["table_rail"]}" stroke-width="10" rx="12" ry="12"/>'''
    
    # Inner rail line
    inner_rail = f'''<rect x="20" y="20" width="{width-40}" height="{height-40}" 
    fill="none" stroke="{COLORS["table_rail"]}" stroke-width="2" rx="4" ry="4"
    stroke-opacity="0.5"/>'''
    
    # Head string line (quarter circle area)
    head_string = f'''<line x1="{width*0.25}" y1="20" x2="{width*0.25}" y2="{height-20}" 
    stroke="{COLORS["text_muted"]}" stroke-width="1" stroke-dasharray="4,4" stroke-opacity="0.3"/>'''
    
    return "\n".join([felt, rail, inner_rail, head_string])


def _render_pockets(pockets: List[Dict], width: int, height: int) -> str:
    """Render the pockets."""
    svg_parts = []
    
    pocket_radius = 12
    
    for pocket in pockets:
        x = pocket.get("x", 0)
        y = pocket.get("y", 0)
        
        # Scale pocket positions if they're in 0-1 range
        if x <= 1 and y <= 1:
            x = x * width
            y = y * height
        
        pocket_svg = f'''<circle cx="{x}" cy="{y}" r="{pocket_radius}" 
        fill="{COLORS["pocket"]}" stroke="{COLORS["table_rail"]}" stroke-width="2"/>'''
        svg_parts.append(pocket_svg)
    
    return "\n".join(svg_parts)


def _render_paths(shot_data: Dict, animated: bool) -> str:
    """Render cue path and object path."""
    svg_parts = []
    
    cue_path = shot_data.get("cue_path", [])
    object_path = shot_data.get("object_path", [])
    
    if animated:
        anim_id_cue = "animCuePath"
        anim_id_obj = "animObjectPath"
    else:
        anim_id_cue = None
        anim_id_obj = None
    
    # Cue path (white line from cue ball to ghost ball)
    if len(cue_path) >= 2:
        path_d = f"M {cue_path[0]['x']} {cue_path[0]['y']} L {cue_path[1]['x']} {cue_path[1]['y']}"
        anim_attr = f''' stroke-dasharray="1000" stroke-dashoffset="1000" 
        style="animation: drawCuePath 0.4s ease-out forwards;"''' if animated else ""
        cue_svg = f'''<path d="{path_d}" fill="none" stroke="{COLORS["cue_path"]}" 
        stroke-width="3" stroke-linecap="round" stroke-opacity="0.9"{anim_attr}/>'''
        svg_parts.append(cue_svg)
    
    # Object path (blue line from ghost ball to pocket)
    if len(object_path) >= 2:
        path_d = f"M {object_path[0]['x']} {object_path[0]['y']} L {object_path[1]['x']} {object_path[1]['y']}"
        anim_attr = f''' stroke-dasharray="1000" stroke-dashoffset="1000" 
        style="animation: drawObjectPath 0.4s ease-out 0.2s forwards;"''' if animated else ""
        obj_svg = f'''<path d="{path_d}" fill="none" stroke="{COLORS["object_path"]}" 
        stroke-width="2.5" stroke-linecap="round" stroke-opacity="0.8"{anim_attr}/>'''
        svg_parts.append(obj_svg)
        
        # Target pocket indicator
        target_pocket = shot_data.get("target_pocket", "")
        # Would need pocket position - simplified here
        pocket_circle = f'''<circle cx="{object_path[1]['x']}" cy="{object_path[1]['y']}" r="18" 
        fill="none" stroke="{COLORS["power_med"]}" stroke-width="2" stroke-dasharray="4,4"
        style="animation: pulse 1.5s ease-in-out infinite;"/>'''
        svg_parts.append(pocket_circle)
    
    return "\n".join(svg_parts)


def _render_ghost_ball(ghost_ball: Dict, animated: bool) -> str:
    """Render the ghost ball (impact position indicator)."""
    cx = ghost_ball.get("x", 0)
    cy = ghost_ball.get("y", 0)
    radius = 14
    
    anim_style = 'style="animation: ghostPulse 1.5s ease-in-out infinite;"' if animated else ""
    
    # Outer dashed circle
    outer = f'''<circle cx="{cx}" cy="{cy}" r="{radius+3}" fill="none" 
    stroke="{COLORS["ghost_ball"]}" stroke-width="2" stroke-dasharray="6,4" 
    stroke-opacity="0.7" {anim_style}/>'''
    
    # Inner filled circle with gradient
    inner = f'''<circle cx="{cx}" cy="{cy}" r="{radius}" fill="url(#ghostBallGradient)" 
    stroke="{COLORS["primary"]}" stroke-width="1.5" filter="url(#ghostGlow)"/>'''
    
    return "\n".join([outer, inner])


def _render_balls(balls: List[Dict], shot_data: Dict) -> str:
    """Render all pool balls."""
    svg_parts = []
    
    ghost_ball = shot_data.get("ghost_ball", {})
    target_ball_num = shot_data.get("target_ball_number")
    
    for ball in balls:
        x = ball.get("x", 0)
        y = ball.get("y", 0)
        radius = ball.get("radius", 10)
        if radius < 8:
            radius = 10  # Minimum readable size
        
        color = get_ball_color(ball)
        is_stripe = ball.get("color", "").startswith("stripe")
        
        # Determine if this is the target ball
        ball_num = ball.get("number")
        is_target = (ball_num == target_ball_num)
        is_cue = (ball.get("color") == "cue")
        
        # Highlight target ball
        if is_target:
            highlight = f'''<circle cx="{x}" cy="{y}" r="{radius+5}" fill="none" 
            stroke="{COLORS["power_med"]}" stroke-width="2" stroke-dasharray="4,4" stroke-opacity="0.8"/>'''
            svg_parts.append(highlight)
        
        # Ball shadow
        shadow = f'''<circle cx="{x+2}" cy="{y+2}" r="{radius}" fill="black" opacity="0.3"/>'''
        
        # Main ball
        if is_stripe:
            # Stripe ball: white with colored stripe band
            ball_body = f'''<circle cx="{x}" cy="{y}" r="{radius}" fill="{COLORS["ball_white"]}" 
            stroke="{color}" stroke-width="1" filter="url(#ballShadow)"/>'''
            stripe_height = radius * 0.5
            stripe = f'''<rect x="{x-radius}" y="{y-stripe_height/2}" width="{radius*2}" height="{stripe_height}" 
            fill="{color}" clip-path="url(#ballClip)"/>'''
            svg_parts.append(f'''<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>''')
        else:
            ball_body = f'''<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" 
            stroke="white" stroke-width="0.5" filter="url(#ballShadow)"/>'''
            svg_parts.append(ball_body)
        
        # Ball number (for numbered balls)
        if ball_num and ball_num != 8:  # Skip 8-ball for now
            text = f'''<text x="{x}" y="{y+4}" text-anchor="middle" font-family="Inter, sans-serif" 
            font-size="{radius*0.9}" font-weight="bold" fill="{'black' if color in [COLORS['ball_white'], COLORS['ball_yellow']] else 'white'}">
            {ball_num}</text>'''
            svg_parts.append(text)
        elif ball_num == 8:
            # 8-ball
            text = f'''<text x="{x}" y="{y+4}" text-anchor="middle" font-family="Inter, sans-serif" 
            font-size="{radius*0.9}" font-weight="bold" fill="white">8</text>'''
            svg_parts.append(text)
    
    return "\n".join(svg_parts)


def _render_power_indicator(shot_data: Dict, width: int, height: int) -> str:
    """Render the power indicator arc."""
    power = shot_data.get("power", 0.5)
    
    # Position in bottom-right
    cx = width - 80
    cy = height - 60
    radius = 30
    start_angle = 135  # degrees
    end_angle = 405  # degrees (full arc)
    
    # Calculate arc path
    arc_length = 270 * power
    end_x = cx + radius * np.cos(np.radians(start_angle + arc_length))
    end_y = cy + radius * np.sin(np.radians(start_angle + arc_length))
    
    large_arc = 1 if arc_length > 180 else 0
    
    arc_path = f"M {cx + radius * np.cos(np.radians(start_angle))} {cy + radius * np.sin(np.radians(start_angle))} "
    arc_path += f"A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y}"
    
    # Background arc
    bg_arc = f'''<path d="M {cx + radius * np.cos(np.radians(start_angle))} {cy + radius * np.sin(np.radians(start_angle))} 
    A {radius} {radius} 0 1 1 {cx + radius * np.cos(np.radians(end_angle-1))} {cy + radius * np.sin(np.radians(end_angle-1))}" 
    fill="none" stroke="{COLORS['surface']}" stroke-width="6" stroke-linecap="round"/>'''
    
    # Power arc
    power_color = _get_power_color(power)
    power_arc = f'''<path d="{arc_path}" fill="none" stroke="{power_color}" stroke-width="6" 
    stroke-linecap="round" style="animation: drawArc 0.6s ease-out forwards;"/>'''
    
    # Label
    label = f'''<text x="{cx}" y="{cy+45}" text-anchor="middle" font-family="JetBrains Mono, monospace" 
    font-size="11" fill="{COLORS['text_muted']}">Power {int(power*100)}%</text>'''
    
    return "\n".join([bg_arc, power_arc, label])


def _render_english_indicator(shot_data: Dict, width: int, height: int) -> str:
    """Render the English/spin indicator."""
    english = shot_data.get("english", 0)  # -1.0 to 1.0
    
    # Position in bottom-left
    cx = 80
    cy = height - 60
    radius = 25
    
    # Background circle
    bg = f'''<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{COLORS['surface']}" 
    stroke="{COLORS['text_muted']}" stroke-width="1" stroke-opacity="0.3"/>'''
    
    # Left side (left English)
    if english < 0:
        left_fill = f'''<path d="M {cx-radius} {cy} A {radius} {radius} 0 0 0 {cx} {cy-radius} L {cx} {cy+radius} Z" 
        fill="{COLORS['english_left']}" opacity="{abs(english)}"/>'''
    else:
        left_fill = f'''<path d="M {cx-radius} {cy} A {radius} {radius} 0 0 0 {cx} {cy-radius} L {cx} {cy+radius} Z" 
        fill="{COLORS['surface']}" opacity="0.3"/>'''
    
    # Right side (right English)
    if english > 0:
        right_fill = f'''<path d="M {cx+radius} {cy} A {radius} {radius} 0 0 1 {cx} {cy-radius} L {cx} {cy+radius} Z" 
        fill="{COLORS['english_right']}" opacity="{english}"/>'''
    else:
        right_fill = f'''<path d="M {cx+radius} {cy} A {radius} {radius} 0 0 1 {cx} {cy-radius} L {cx} {cy+radius} Z" 
        fill="{COLORS['surface']}" opacity="0.3"/>'''
    
    # Center divider
    divider = f'''<line x1="{cx}" y1="{cy-radius}" x2="{cx}" y2="{cy+radius}" 
    stroke="{COLORS['text_muted']}" stroke-width="1"/>'''
    divider2 = f'''<line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" 
    stroke="{COLORS['text_muted']}" stroke-width="1"/>'''
    
    # Label
    if abs(english) < 0.1:
        label_text = "Center"
        label_color = COLORS["text_muted"]
    elif english < 0:
        label_text = f"L {int(abs(english)*100)}%"
        label_color = COLORS["english_left"]
    else:
        label_text = f"R {int(english*100)}%"
        label_color = COLORS["english_right"]
    
    label = f'''<text x="{cx}" y="{cy+40}" text-anchor="middle" font-family="JetBrains Mono, monospace" 
    font-size="10" fill="{label_color}">{label_text}</text>'''
    
    return "\n".join([bg, left_fill, right_fill, divider, divider2, label])


def _render_angle_label(shot_data: Dict, width: int, height: int) -> str:
    """Render the shot angle label."""
    angle = shot_data.get("angle", 0)
    
    # Position near cue ball
    cue_path = shot_data.get("cue_path", [])
    if not cue_path:
        return ""
    
    cue_x = cue_path[0]["x"] + 40
    cue_y = cue_path[0]["y"] - 30
    
    label = f'''<text x="{cue_x}" y="{cue_y}" font-family="JetBrains Mono, monospace" 
    font-size="10" fill="{COLORS['text_muted']}">{angle:.0f}°</text>'''
    
    return label


def _render_shot_info(shot_data: Dict, width: int, height: int) -> str:
    """Render the shot quality summary."""
    target_pocket = shot_data.get("target_pocket", "—")
    target_ball = shot_data.get("target_ball_number", "?")
    
    # Position top-left
    x = 30
    y = 35
    
    pocket_label = target_pocket.replace('_', ' ').title() if target_pocket else "—"
    info = f'''<text x="{x}" y="{y}" font-family="Inter, sans-serif" font-size="13" 
    fill="{COLORS['text_primary']}" font-weight="600">Ball {target_ball} → {pocket_label}</text>'''
    
    return info


def _get_power_color(power: float) -> str:
    """Get the color for a power level."""
    if power < 0.33:
        return COLORS["power_low"]
    elif power < 0.66:
        return COLORS["power_med"]
    else:
        return COLORS["power_high"]


def _get_animations() -> str:
    """Get CSS animations for SVG elements."""
    return '''
    <style>
        @keyframes drawCuePath {
            to { stroke-dashoffset: 0; }
        }
        @keyframes drawObjectPath {
            to { stroke-dashoffset: 0; }
        }
        @keyframes ghostPulse {
            0%, 100% { transform: scale(1); opacity: 0.7; }
            50% { transform: scale(1.08); opacity: 1; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; }
        }
        @keyframes drawArc {
            from { stroke-dashoffset: 1000; }
            to { stroke-dashoffset: 0; }
        }
    </style>'''


