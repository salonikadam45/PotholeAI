"""
Agent 1: Intake & Parser
Handles multimodal input (text, image, audio) and normalizes into structured complaint data.
"""

import re
import time
import random
from datetime import datetime
from backend.models import (
    ParsedComplaint, AgentDecision, AuditLogEntry, InputModality
)


# Keyword banks for extraction
URGENCY_KEYWORDS = [
    "dangerous", "urgent", "emergency", "hazard", "accident", "injury",
    "deep", "huge", "massive", "severe", "critical", "immediate",
    "unsafe", "risk", "collapse", "sinkhole", "flooding"
]

LOCATION_PATTERNS = [
    r"(?:near|at|on|beside|opposite|in front of|behind|next to)\s+(.+?)(?:\.|,|$)",
    r"(?:street|road|avenue|lane|drive|boulevard|highway|intersection)\s*(?:of\s+)?(.+?)(?:\.|,|$)",
    r"(\d+\s+\w+\s+(?:street|road|avenue|lane|drive|blvd|hwy))",
    r"((?:sector|block|ward|zone)\s*[-#]?\s*\d+)",
]

COMPLAINT_TYPE_KEYWORDS = {
    "pothole": ["pothole", "pot hole", "hole in road", "road hole", "cavity"],
    "crack": ["crack", "cracked", "fracture", "split", "broken road"],
    "sinkhole": ["sinkhole", "sink hole", "ground collapse", "cave in"],
    "flooding": ["flood", "waterlog", "water stagnation", "puddle", "drainage"],
    "surface_wear": ["worn", "faded", "eroded", "rough surface", "bumpy"],
    "manhole": ["manhole", "drain cover", "missing cover", "open drain"],
}

# Simulated audio transcriptions for demo
DEMO_AUDIO_TRANSCRIPTIONS = [
    "There is a very deep pothole on Main Street near the school crossing. Several cars have been damaged. Please fix it urgently.",
    "I want to report a dangerous road condition on Highway 45. The surface has collapsed and there is a sinkhole forming.",
    "The road near Block 7 market area is completely waterlogged due to broken drainage. It's been like this for weeks.",
    "There's a massive crack running across Elm Avenue. It's getting bigger every day and is now a safety hazard.",
    "Missing manhole cover on Park Road. Very dangerous especially at night. Someone could fall in.",
]


class IntakeParserAgent:
    """
    Agent 1: Intake & Parser
    
    Responsibilities:
    - Accept raw multimodal input (text, image, audio)
    - Extract location, complaint type, urgency signals
    - Normalize into structured ParsedComplaint
    - Handle garbled/empty inputs with error recovery
    """
    
    AGENT_ID = "agent-1"
    AGENT_NAME = "Intake & Parser"
    
    def process(self, text_input: str = "", image_data: str = None, 
                audio_data: str = None, location_hint: str = "") -> tuple[ParsedComplaint, AgentDecision, list[AuditLogEntry]]:
        """
        Process raw complaint input and return structured data.
        Returns: (ParsedComplaint, AgentDecision, list of AuditLogEntries)
        """
        start_time = time.time()
        audit_entries = []
        modalities = []
        combined_text = ""
        transcribed = ""
        
        # ── Step 1: Process each modality ──────────────────────────────
        
        # Text processing
        if text_input and text_input.strip():
            modalities.append(InputModality.TEXT)
            combined_text = text_input.strip()
            audit_entries.append(self._audit("text_intake", 
                f"Received text input ({len(text_input)} chars)", 
                "Text accepted for processing", ""))
        
        # Audio processing (simulated speech-to-text)
        if audio_data:
            modalities.append(InputModality.AUDIO)
            transcribed = self._simulate_transcription(audio_data)
            combined_text = f"{combined_text} {transcribed}".strip()
            audit_entries.append(self._audit("audio_transcription",
                f"Audio data received, simulating STT",
                f"Transcribed: '{transcribed[:80]}...'", ""))
        
        # Image processing
        has_image = False
        if image_data:
            modalities.append(InputModality.IMAGE)
            has_image = True
            audit_entries.append(self._audit("image_intake",
                "Image data received",
                "Image queued for Agent 2 vision analysis", ""))
        
        # ── Step 2: Validate input ─────────────────────────────────────
        
        if not combined_text and not has_image:
            duration_ms = int((time.time() - start_time) * 1000)
            decision = AgentDecision(
                agent_id=self.AGENT_ID,
                agent_name=self.AGENT_NAME,
                input_summary="Empty input received",
                output_summary="REJECTED: No usable input provided",
                confidence=0.0,
                duration_ms=duration_ms,
                reasoning="All input modalities were empty. Cannot process complaint.",
                error="No text, image, or audio input provided"
            )
            audit_entries.append(self._audit("validation_failed",
                "All modalities empty", "Complaint rejected — requesting resubmission", ""))
            return ParsedComplaint(modalities_used=modalities), decision, audit_entries
        
        # ── Step 3: Extract structured data ────────────────────────────
        
        extracted_location = self._extract_location(combined_text, location_hint)
        complaint_type = self._classify_type(combined_text)
        urgency_kws = self._extract_urgency(combined_text)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        parsed = ParsedComplaint(
            original_text=text_input.strip() if text_input else "",
            transcribed_audio=transcribed,
            extracted_location=extracted_location,
            complaint_type=complaint_type,
            urgency_keywords=urgency_kws,
            has_image=has_image,
            has_audio=bool(audio_data),
            modalities_used=modalities
        )
        
        confidence = self._calculate_confidence(parsed)
        
        decision = AgentDecision(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            input_summary=f"Modalities: {[m.value for m in modalities]} | Text length: {len(combined_text)}",
            output_summary=f"Type: {complaint_type} | Location: {extracted_location} | Urgency keywords: {len(urgency_kws)}",
            confidence=confidence,
            duration_ms=duration_ms,
            reasoning=f"Parsed {len(modalities)} input modalities. Extracted location='{extracted_location}', "
                      f"type='{complaint_type}', found {len(urgency_kws)} urgency indicators."
        )
        
        audit_entries.append(self._audit("parsing_complete",
            f"Processed {len(modalities)} modalities",
            f"Structured output ready. Confidence: {confidence:.2f}",
            ""))
        
        return parsed, decision, audit_entries
    
    def _extract_location(self, text: str, hint: str) -> str:
        """Extract location from text using regex patterns."""
        if hint and hint.strip():
            return hint.strip()
        
        text_lower = text.lower()
        for pattern in LOCATION_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        
        # Fallback: look for capitalized proper nouns (potential place names)
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and word.lower() not in ["i", "the", "a", "there", "please", "this", "it"]:
                # Check if next word is also capitalized (e.g., "Main Street")
                if i + 1 < len(words) and words[i+1][0].isupper():
                    return f"{word} {words[i+1]}"
        
        return "Location not specified"
    
    def _classify_type(self, text: str) -> str:
        """Classify complaint type from text keywords."""
        text_lower = text.lower()
        scores = {}
        for ctype, keywords in COMPLAINT_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[ctype] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "pothole"  # default
    
    def _extract_urgency(self, text: str) -> list[str]:
        """Find urgency-indicating keywords."""
        text_lower = text.lower()
        return [kw for kw in URGENCY_KEYWORDS if kw in text_lower]
    
    def _calculate_confidence(self, parsed: ParsedComplaint) -> float:
        """Calculate confidence based on extracted data quality."""
        score = 0.3  # base
        if parsed.extracted_location != "Location not specified":
            score += 0.25
        if parsed.complaint_type:
            score += 0.2
        if parsed.urgency_keywords:
            score += 0.15
        if len(parsed.modalities_used) > 1:
            score += 0.1
        return min(score, 1.0)
    
    def _simulate_transcription(self, audio_data: str) -> str:
        """Simulate speech-to-text for demo purposes."""
        return random.choice(DEMO_AUDIO_TRANSCRIPTIONS)
    
    def _audit(self, action: str, reasoning: str, outcome: str, complaint_id: str) -> AuditLogEntry:
        return AuditLogEntry(
            complaint_id=complaint_id,
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            action=action,
            reasoning=reasoning,
            outcome=outcome
        )
