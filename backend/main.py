"""
Pool Shot App API
FastAPI backend for ball detection, shot calculation, and diagram rendering.
"""

import os
import base64
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from dotenv import load_dotenv

# Import modules
from detection.opencv_detector import detect_balls
from homography.perspective import compute_homography, warp_balls, get_pocket_positions
from physics.shot_calculator import calculate_shot, get_shot_quality_description
from rendering.svg_renderer import render_shot_diagram

load_dotenv()

app = FastAPI(
    title="Pool Shot App API",
    description="AI-powered pool shot coach — ball detection, physics, and shot diagrams",
    version="1.0.0"
)

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class DetectRequest(BaseModel):
    image_base64: str
    table_size: str = "9ft"  # "7ft" or "9ft"


class BallPosition(BaseModel):
    x: float
    y: float
    color: str
    number: int | None = None


class DetectResponse(BaseModel):
    balls: list[BallPosition]
    table_corners: list[dict]
    cue_ball: dict | None
    detection_confidence: float


class CalculateShotRequest(BaseModel):
    balls: list[BallPosition]
    cue_ball: dict
    table_size: str = "9ft"
    game_type: str = "8ball"  # "8ball", "9ball", "straight"
    skill_level: str = "intermediate"  # "beginner", "intermediate", "pro"


class ShotResult(BaseModel):
    ghost_ball: dict | None
    cue_path: list[dict]
    object_path: list[dict]
    target_pocket: str | None
    target_ball_number: int | None
    power: float
    english: float
    angle: float
    distance: float
    score: float
    confidence: float
    quality_description: str | None = None
    error: str | None = None


class DiagramRequest(BaseModel):
    shot_data: dict
    balls: list[BallPosition]
    pockets: list[dict]
    output_width: int = 800
    output_height: int = 400


# --- API Routes ---

@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "ok",
        "app": "Pool Shot App API",
        "version": "1.0.0"
    }


@app.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest):
    """
    Detect pool balls in an image.
    
    Takes a base64-encoded JPEG image and table size.
    Returns ball positions, table corners, and detection confidence.
    """
    try:
        # Validate table size
        if request.table_size not in ["7ft", "9ft"]:
            raise HTTPException(status_code=400, detail="table_size must be '7ft' or '9ft'")
        
        # Decode image
        image_data = base64.b64decode(request.image_base64)
        
        # Detect balls
        result = detect_balls(image_data, request.table_size)
        
        return DetectResponse(
            balls=result["balls"],
            table_corners=result["table_corners"],
            cue_ball=result["cue_ball"],
            detection_confidence=result["detection_confidence"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-shot", response_model=ShotResult)
async def calculate_shot_endpoint(request: CalculateShotRequest):
    """
    Calculate the optimal shot based on ball positions.
    
    Takes current ball layout, game type, and skill level.
    Returns ghost ball position, paths, power, English, and confidence.
    """
    try:
        # Validate inputs
        if request.table_size not in ["7ft", "9ft"]:
            raise HTTPException(status_code=400, detail="table_size must be '7ft' or '9ft'")
        if request.game_type not in ["8ball", "9ball", "straight"]:
            raise HTTPException(status_code=400, detail="game_type must be '8ball', '9ball', or 'straight'")
        if request.skill_level not in ["beginner", "intermediate", "pro"]:
            raise HTTPException(status_code=400, detail="skill_level must be 'beginner', 'intermediate', or 'pro'")
        
        # Compute homography for pocket positions
        # For now, use default pocket positions based on table size
        from homography.perspective import POCKET_POSITIONS
        
        pocket_data = POCKET_POSITIONS[request.table_size]
        pockets = [
            {"name": name, "x": rx * 800, "y": ry * 400}  # Scaled to typical output
            for name, (rx, ry) in pocket_data.items()
        ]
        
        # Calculate shot
        result = calculate_shot(
            cue_ball=request.cue_ball,
            balls=[b.dict() for b in request.balls],
            pockets=pockets,
            table_size=request.table_size,
            game_type=request.game_type,
            skill_level=request.skill_level
        )
        
        # Add quality description
        if "error" not in result:
            result["quality_description"] = get_shot_quality_description(result)
        
        return ShotResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagram")
async def get_diagram(request: DiagramRequest):
    """
    Render a shot diagram as SVG.
    
    Takes shot calculation result, ball positions, and pocket positions.
    Returns an SVG image.
    """
    try:
        # Render SVG
        svg_content = render_shot_diagram(
            shot_data=request.shot_data,
            balls=[b.dict() for b in request.balls],
            pockets=request.pockets,
            output_width=request.output_width,
            output_height=request.output_height
        )
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={"Content-Disposition": "inline"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-and-calculate")
async def detect_and_calculate(request: DetectRequest):
    """
    Combined endpoint: detect balls and calculate optimal shot in one call.
    
    This is the main endpoint for the app flow.
    """
    try:
        # Validate table size
        if request.table_size not in ["7ft", "9ft"]:
            raise HTTPException(status_code=400, detail="table_size must be '7ft' or '9ft'")
        
        # Decode image
        image_data = base64.b64decode(request.image_base64)
        
        # Step 1: Detect balls
        detection = detect_balls(image_data, request.table_size)
        
        # Step 2: Compute homography
        H, output_w, output_h = compute_homography(
            detection["table_corners"],
            request.table_size
        )
        
        # Step 3: Warp ball positions to top-down view
        if H is not None:
            warped_balls = warp_balls(detection["balls"], H)
            warped_cue = None
            if detection["cue_ball"]:
                from homography.perspective import warp_ball
                warped_cue = warp_ball(detection["cue_ball"], H)
        else:
            warped_balls = detection["balls"]
            warped_cue = detection["cue_ball"]
            output_w, output_h = 800, 400
        
        # Step 4: Get pocket positions in warped space
        from homography.perspective import POCKET_POSITIONS
        pocket_data = POCKET_POSITIONS[request.table_size]
        pockets = [
            {"name": name, "x": rx * output_w, "y": ry * output_h}
            for name, (rx, ry) in pocket_data.items()
        ]
        
        # Step 5: Calculate shot (use defaults)
        shot = calculate_shot(
            cue_ball=warped_cue or {"x": output_w * 0.25, "y": output_h * 0.5},
            balls=warped_balls,
            pockets=pockets,
            table_size=request.table_size,
            game_type="8ball",
            skill_level="intermediate"
        )
        
        # Step 6: Render diagram
        svg_content = render_shot_diagram(
            shot_data=shot,
            balls=warped_balls,
            pockets=pockets,
            output_width=output_w,
            output_height=output_h
        )
        
        return {
            "detection": {
                "balls": warped_balls,
                "table_corners": detection["table_corners"],
                "cue_ball": warped_cue,
                "confidence": detection["detection_confidence"]
            },
            "shot": shot,
            "shot_quality": get_shot_quality_description(shot) if "error" not in shot else None,
            "diagram_svg": svg_content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Startup ---

@app.on_event("startup")
async def startup():
    print("[Pool Shot App API] Starting...")
    print("Endpoints:")
    print("   GET  /              - Health check")
    print("   POST /detect        - Detect balls in image")
    print("   POST /calculate-shot - Calculate optimal shot")
    print("   POST /diagram       - Render shot diagram SVG")
    print("   POST /detect-and-calculate - Combined endpoint")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
