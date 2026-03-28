"""
Agent 2: Vision & Multimodal AI
Analyzes images for road damage classification, area estimation, and hazard detection.
"""

import time
import random
import hashlib
from datetime import datetime
from backend.models import (
    VisionAnalysis, AgentDecision, AuditLogEntry,
    DamageType
)


# Simulated vision analysis profiles
DAMAGE_PROFILES = [
    {
        "damage_type": DamageType.POTHOLE,
        "area_estimate": "medium",
        "road_type": "residential",
        "hazard_flags": ["pedestrian_zone"],
        "confidence_score": 0.87,
        "raw_analysis": "Detected circular depression in asphalt surface. Diameter ~40cm, depth ~8cm. Located on residential street with sidewalk."
    },
    {
        "damage_type": DamageType.POTHOLE,
        "area_estimate": "large",
        "road_type": "arterial",
        "hazard_flags": ["high_traffic", "near_intersection"],
        "confidence_score": 0.92,
        "raw_analysis": "Large pothole on arterial road near traffic intersection. Multiple tire marks indicate frequent encounters. Diameter ~80cm."
    },
    {
        "damage_type": DamageType.CRACK,
        "area_estimate": "small",
        "road_type": "residential",
        "hazard_flags": [],
        "confidence_score": 0.78,
        "raw_analysis": "Longitudinal crack along road surface. Length ~2m, width ~3cm. Minor surface degradation."
    },
    {
        "damage_type": DamageType.SINKHOLE,
        "area_estimate": "large",
        "road_type": "highway",
        "hazard_flags": ["structural_risk", "emergency_lane_blocked", "high_speed_zone"],
        "confidence_score": 0.95,
        "raw_analysis": "CRITICAL: Ground subsidence detected on highway shoulder. Possible underground erosion. Immediate closure recommended."
    },
    {
        "damage_type": DamageType.FLOODING,
        "area_estimate": "large",
        "road_type": "commercial",
        "hazard_flags": ["waterlogged", "electrical_hazard", "pedestrian_zone"],
        "confidence_score": 0.85,
        "raw_analysis": "Road flooding detected in commercial district. Water level ~15cm. Blocked storm drain visible."
    },
    {
        "damage_type": DamageType.SURFACE_WEAR,
        "area_estimate": "medium",
        "road_type": "arterial",
        "hazard_flags": ["school_zone"],
        "confidence_score": 0.72,
        "raw_analysis": "General surface deterioration on arterial road near school. Faded lane markings, rough texture."
    },
    {
        "damage_type": DamageType.MANHOLE,
        "area_estimate": "small",
        "road_type": "residential",
        "hazard_flags": ["missing_cover", "fall_hazard", "night_hazard"],
        "confidence_score": 0.94,
        "raw_analysis": "Open/missing manhole cover detected. Exposed utility access point on residential street. High fall risk."
    },
    {
        "damage_type": DamageType.POTHOLE,
        "area_estimate": "small",
        "road_type": "residential",
        "hazard_flags": [],
        "confidence_score": 0.65,
        "raw_analysis": "Minor pothole detected. Diameter ~15cm, shallow depth. Low immediate risk."
    },
]


class VisionMultimodalAgent:
    """
    Agent 2: Vision & Multimodal AI
    
    Responsibilities:
    - Analyze uploaded images for road damage
    - Classify damage type (pothole, crack, sinkhole, etc.)
    - Estimate damage area and road type
    - Detect safety hazards (school zone, highway, etc.)
    - Self-correct: if confidence < 0.5, flag for human review
    """
    
    AGENT_ID = "agent-2"
    AGENT_NAME = "Vision & Multimodal AI"
    
    def process(self, image_data: str = None, complaint_type_hint: str = "",
                complaint_id: str = "") -> tuple[VisionAnalysis, AgentDecision, list[AuditLogEntry]]:
        """
        Analyze image data and return vision analysis.
        Uses complaint_type_hint from Agent 1 to guide analysis.
        """
        start_time = time.time()
        audit_entries = []
        
        # ── Step 1: Validate image ─────────────────────────────────────
        
        if not image_data:
            # No image — generate analysis from text hint only
            audit_entries.append(self._audit("no_image",
                "No image provided, using text-based inference",
                "Generating analysis from complaint type hint only",
                complaint_id))
            
            analysis = self._infer_from_text(complaint_type_hint)
            analysis.confidence_score = max(0.35, analysis.confidence_score - 0.3)
            analysis.raw_analysis = f"[TEXT-INFERRED] {analysis.raw_analysis}"
            
        else:
            # ── Step 2: Simulate image analysis ────────────────────────
            
            audit_entries.append(self._audit("image_analysis_start",
                f"Processing image data ({len(image_data)} chars)",
                "Running simulated vision model", complaint_id))
            
            # Use image hash to deterministically pick a profile (for consistency)
            profile_idx = int(hashlib.md5(image_data.encode()[:100]).hexdigest(), 16) % len(DAMAGE_PROFILES)
            
            # If we have a type hint, try to match
            if complaint_type_hint:
                matching = [p for p in DAMAGE_PROFILES if p["damage_type"].value == complaint_type_hint]
                if matching:
                    profile = random.choice(matching)
                else:
                    profile = DAMAGE_PROFILES[profile_idx]
            else:
                profile = DAMAGE_PROFILES[profile_idx]
            
            # Add slight randomization to confidence
            conf_jitter = random.uniform(-0.05, 0.05)
            
            analysis = VisionAnalysis(
                damage_type=profile["damage_type"],
                area_estimate=profile["area_estimate"],
                road_type=profile["road_type"],
                hazard_flags=profile["hazard_flags"],
                confidence_score=max(0.1, min(1.0, profile["confidence_score"] + conf_jitter)),
                raw_analysis=profile["raw_analysis"]
            )
        
        # ── Step 3: Self-correction check ──────────────────────────────
        
        if analysis.confidence_score < 0.5:
            analysis.needs_human_review = True
            audit_entries.append(self._audit("low_confidence_flag",
                f"Confidence score {analysis.confidence_score:.2f} below threshold (0.5)",
                "Flagged for human review. Requesting additional image angles.",
                complaint_id))
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        decision = AgentDecision(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            input_summary=f"Image: {'Yes' if image_data else 'No'} | Type hint: {complaint_type_hint or 'none'}",
            output_summary=f"Damage: {analysis.damage_type.value} | Area: {analysis.area_estimate} | "
                          f"Hazards: {len(analysis.hazard_flags)} | Confidence: {analysis.confidence_score:.2f}",
            confidence=analysis.confidence_score,
            duration_ms=duration_ms,
            reasoning=f"Analyzed {'image' if image_data else 'text inference only'}. "
                      f"Detected {analysis.damage_type.value} damage, {analysis.area_estimate} area on {analysis.road_type} road. "
                      f"Hazard flags: {analysis.hazard_flags or 'none'}.",
            self_corrected=analysis.needs_human_review
        )
        
        audit_entries.append(self._audit("analysis_complete",
            f"Vision analysis finished in {duration_ms}ms",
            f"Damage={analysis.damage_type.value}, Area={analysis.area_estimate}, "
            f"Confidence={analysis.confidence_score:.2f}",
            complaint_id))
        
        return analysis, decision, audit_entries
    
    def _infer_from_text(self, complaint_type: str) -> VisionAnalysis:
        """Infer vision analysis from text complaint type when no image is available."""
        type_map = {
            "pothole": DamageType.POTHOLE,
            "crack": DamageType.CRACK,
            "sinkhole": DamageType.SINKHOLE,
            "flooding": DamageType.FLOODING,
            "surface_wear": DamageType.SURFACE_WEAR,
            "manhole": DamageType.MANHOLE,
        }
        
        damage = type_map.get(complaint_type, DamageType.POTHOLE)
        matching = [p for p in DAMAGE_PROFILES if p["damage_type"] == damage]
        
        if matching:
            profile = matching[0]
            return VisionAnalysis(
                damage_type=profile["damage_type"],
                area_estimate=profile["area_estimate"],
                road_type=profile["road_type"],
                hazard_flags=profile["hazard_flags"],
                confidence_score=profile["confidence_score"],
                raw_analysis=profile["raw_analysis"]
            )
        
        return VisionAnalysis(
            damage_type=DamageType.POTHOLE,
            area_estimate="medium",
            road_type="residential",
            confidence_score=0.5,
            raw_analysis="Default analysis — insufficient data for detailed classification."
        )
    
    def _audit(self, action: str, reasoning: str, outcome: str, complaint_id: str) -> AuditLogEntry:
        return AuditLogEntry(
            complaint_id=complaint_id,
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            action=action,
            reasoning=reasoning,
            outcome=outcome
        )
