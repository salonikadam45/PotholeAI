"""
Agent 3: Severity Classifier
Combines text, vision, and location signals to produce a severity score (1-10).
"""

import time
from backend.models import (
    SeverityAssessment, SeverityLevel, AgentDecision, AuditLogEntry,
    ParsedComplaint, VisionAnalysis, DamageType
)


# Urgency keyword weights
URGENCY_WEIGHTS = {
    "emergency": 3.0, "dangerous": 2.5, "hazard": 2.5, "accident": 3.0,
    "injury": 3.0, "collapse": 3.0, "sinkhole": 2.5, "urgent": 2.0,
    "immediate": 2.0, "unsafe": 2.0, "risk": 1.5, "severe": 2.0,
    "critical": 2.5, "deep": 1.5, "huge": 1.5, "massive": 2.0,
    "flooding": 1.5
}

# Damage type base severity
DAMAGE_SEVERITY = {
    DamageType.POTHOLE: 5.0,
    DamageType.CRACK: 3.0,
    DamageType.SINKHOLE: 9.0,
    DamageType.FLOODING: 6.5,
    DamageType.SURFACE_WEAR: 2.5,
    DamageType.MANHOLE: 7.5,
}

# Area multipliers
AREA_MULTIPLIERS = {
    "small": 0.7,
    "medium": 1.0,
    "large": 1.4,
}

# Hazard flag severity bonuses
HAZARD_BONUSES = {
    "school_zone": 1.5,
    "high_speed_zone": 1.5,
    "pedestrian_zone": 1.0,
    "high_traffic": 1.0,
    "near_intersection": 0.8,
    "structural_risk": 2.0,
    "emergency_lane_blocked": 1.5,
    "missing_cover": 2.0,
    "fall_hazard": 1.5,
    "night_hazard": 1.0,
    "electrical_hazard": 1.5,
    "waterlogged": 0.8,
}

# Road type risk modifiers
ROAD_RISK = {
    "highway": 1.3,
    "arterial": 1.1,
    "commercial": 1.0,
    "residential": 0.9,
}


class SeverityClassifierAgent:
    """
    Agent 3: Severity Classifier
    
    Scoring formula:
        severity = 0.3 × text_urgency + 0.4 × vision_damage + 0.2 × location_risk + 0.1 × recurrence
    
    Self-correction:
        If text urgency and vision damage scores differ by > 3 points,
        flags for Agent 2 re-analysis.
    """
    
    AGENT_ID = "agent-3"
    AGENT_NAME = "Severity Classifier"
    
    def process(self, parsed: ParsedComplaint, vision: VisionAnalysis,
                recurrence_count: int = 0, complaint_id: str = "") -> tuple[SeverityAssessment, AgentDecision, list[AuditLogEntry]]:
        """
        Classify severity using multi-signal weighted formula.
        """
        start_time = time.time()
        audit_entries = []
        
        # ── Step 1: Text urgency score (0-10) ─────────────────────────
        
        text_score = self._score_text_urgency(parsed)
        audit_entries.append(self._audit("text_scoring",
            f"Analyzed {len(parsed.urgency_keywords)} urgency keywords",
            f"Text urgency score: {text_score:.1f}/10",
            complaint_id))
        
        # ── Step 2: Vision damage score (0-10) ────────────────────────
        
        vision_score = self._score_vision_damage(vision)
        audit_entries.append(self._audit("vision_scoring",
            f"Damage type: {vision.damage_type.value}, Area: {vision.area_estimate}",
            f"Vision damage score: {vision_score:.1f}/10",
            complaint_id))
        
        # ── Step 3: Location risk score (0-10) ────────────────────────
        
        location_score = self._score_location_risk(vision, parsed)
        audit_entries.append(self._audit("location_scoring",
            f"Road type: {vision.road_type}, Hazards: {vision.hazard_flags}",
            f"Location risk score: {location_score:.1f}/10",
            complaint_id))
        
        # ── Step 4: Recurrence factor (0-10) ──────────────────────────
        
        recurrence_score = min(10.0, recurrence_count * 2.5)
        
        # ── Step 5: Weighted combination ──────────────────────────────
        
        severity_score = (
            0.3 * text_score +
            0.4 * vision_score +
            0.2 * location_score +
            0.1 * recurrence_score
        )
        severity_score = round(min(10.0, max(1.0, severity_score)), 1)
        
        # ── Step 6: Map to severity level ─────────────────────────────
        
        severity_level = self._map_severity(severity_score)
        
        # ── Step 7: Cross-validation (self-correction) ────────────────
        
        cross_valid = True
        flag_reanalysis = False
        score_diff = abs(text_score - vision_score)
        
        if score_diff > 3.0:
            cross_valid = False
            flag_reanalysis = True
            audit_entries.append(self._audit("cross_validation_failed",
                f"Text score ({text_score:.1f}) and Vision score ({vision_score:.1f}) differ by {score_diff:.1f} points",
                "SELF-CORRECTION: Flagging for Agent 2 re-analysis. Using higher of two scores as safety measure.",
                complaint_id))
            # Safety measure: use the higher score
            severity_score = round(min(10.0, max(severity_score, max(text_score, vision_score) * 0.8)), 1)
            severity_level = self._map_severity(severity_score)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        assessment = SeverityAssessment(
            severity_score=severity_score,
            severity_level=severity_level,
            text_urgency_score=round(text_score, 2),
            vision_damage_score=round(vision_score, 2),
            location_risk_score=round(location_score, 2),
            recurrence_factor=round(recurrence_score, 2),
            cross_validation_passed=cross_valid,
            flag_for_reanalysis=flag_reanalysis
        )
        
        decision = AgentDecision(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            input_summary=f"Text keywords: {len(parsed.urgency_keywords)} | "
                         f"Damage: {vision.damage_type.value} | Recurrence: {recurrence_count}",
            output_summary=f"Severity: {severity_score}/10 ({severity_level.value}) | "
                          f"Cross-validation: {'PASS' if cross_valid else 'FAIL'}",
            confidence=0.85 if cross_valid else 0.55,
            duration_ms=duration_ms,
            reasoning=f"Weighted formula: text({text_score:.1f})×0.3 + vision({vision_score:.1f})×0.4 + "
                      f"location({location_score:.1f})×0.2 + recurrence({recurrence_score:.1f})×0.1 = {severity_score}. "
                      f"{'Cross-validation passed.' if cross_valid else f'Cross-validation FAILED (diff={score_diff:.1f}). Used safety-adjusted score.'}",
            self_corrected=flag_reanalysis
        )
        
        audit_entries.append(self._audit("severity_classified",
            f"Final score computed via 4-signal weighted formula",
            f"Severity={severity_score}/10 ({severity_level.value}), Cross-valid={'PASS' if cross_valid else 'FAIL-ADJUSTED'}",
            complaint_id))
        
        return assessment, decision, audit_entries
    
    def _score_text_urgency(self, parsed: ParsedComplaint) -> float:
        """Score text urgency from 0-10 based on keyword presence and weight."""
        if not parsed.urgency_keywords:
            return 2.0  # base non-urgent score
        
        total_weight = sum(URGENCY_WEIGHTS.get(kw, 1.0) for kw in parsed.urgency_keywords)
        return min(10.0, 2.0 + total_weight)
    
    def _score_vision_damage(self, vision: VisionAnalysis) -> float:
        """Score vision damage from 0-10 based on damage type and area."""
        base = DAMAGE_SEVERITY.get(vision.damage_type, 5.0)
        multiplier = AREA_MULTIPLIERS.get(vision.area_estimate, 1.0)
        
        # Hazard bonuses
        hazard_bonus = sum(HAZARD_BONUSES.get(h, 0.5) for h in vision.hazard_flags)
        
        score = base * multiplier + hazard_bonus * 0.5
        return min(10.0, score)
    
    def _score_location_risk(self, vision: VisionAnalysis, parsed: ParsedComplaint) -> float:
        """Score location risk based on road type and hazard indicators."""
        road_mod = ROAD_RISK.get(vision.road_type, 1.0)
        base = 4.0 * road_mod
        
        # Hazard-specific bonuses for location risk
        loc_hazards = ["school_zone", "high_speed_zone", "pedestrian_zone", "near_intersection"]
        loc_bonus = sum(1.5 for h in vision.hazard_flags if h in loc_hazards)
        
        return min(10.0, base + loc_bonus)
    
    def _map_severity(self, score: float) -> SeverityLevel:
        """Map numerical score to severity level."""
        if score >= 8.0:
            return SeverityLevel.CRITICAL
        elif score >= 6.0:
            return SeverityLevel.HIGH
        elif score >= 4.0:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _audit(self, action: str, reasoning: str, outcome: str, complaint_id: str) -> AuditLogEntry:
        return AuditLogEntry(
            complaint_id=complaint_id,
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            action=action,
            reasoning=reasoning,
            outcome=outcome
        )
