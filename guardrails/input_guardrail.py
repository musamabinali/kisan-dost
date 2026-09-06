"""Input guardrails for safety and relevance."""

from specialists import GuardrailFunctionOutput, input_guardrail
from models import FarmerProfile, FarmContext
from config.constants import BANNED_PESTICIDES
from config.prompts.system_prompts import GUARDRAIL_INSTRUCTIONS
import logging
import re

logger = logging.getLogger(__name__)

# Off-topic patterns
OFF_TOPIC_PATTERNS = [
    r"\b(cricket|football|movie|film|song|music|politics|election|news|celebrity)\b",
    r"\b(recipe|cooking|food|restaurant)\b",
    r"\b(programming|code|software|computer|ai|artificial intelligence)\b",
    r"\b(religion|prayer|namaz|quran|bible)\b",
]

# Unsafe patterns - medical advice, dangerous requests
UNSAFE_PATTERNS = [
    r"\b(human|person|people|patient|doctor|medical|health|medicine|drug|pill|tablet)\b.*\b(advice|recommend|prescribe|treat|diagnose)\b",
    r"\b(bomb|explosive|weapon|gun|poison|kill|suicide|hurt|harm|attack)\b",
    r"\b(illegal|banned|prohibited)\b.*\b(pesticide|chemical|fertilizer)\b",
]

# PII patterns (beyond farmer's own info)
PII_PATTERNS = [
    r"\b\d{5}-\d{7}-\d{1}\b",  # CNIC pattern
    r"\b\d{11}\b",  # Phone number
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions|rules|prompts)",
    r"forget\s+(everything|all)\s+(you\s+)?(know|learned)",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"system\s*:|assistant\s*:|user\s*:",
    r"```.*```",
    r"<\|.*\|>",
]

@input_guardrail
async def input_guardrail(
    ctx, 
    agent, 
    input_text: str
) -> GuardrailFunctionOutput:
    """
    Input guardrail that rejects off-topic or unsafe requests.
    
    Checks for:
    - Off-topic queries (non-farming)
    - Unsafe requests (medical advice, dangerous content)
    - PII requests
    - Prompt injection attempts
    """
    text_lower = input_text.lower()
    
    # Check for prompt injection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"Prompt injection detected: {input_text[:100]}")
            return GuardrailFunctionOutput(
                output_info={
                    "rejected": True,
                    "reason": "prompt_injection",
                    "message": "I can't process that request. Please ask a farming-related question."
                },
                tripwire_triggered=True
            )
    
    # Check for unsafe content
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"Unsafe request detected: {input_text[:100]}")
            return GuardrailFunctionOutput(
                output_info={
                    "rejected": True,
                    "reason": "unsafe",
                    "message": "I can only provide agricultural advice. For medical or safety concerns, please consult appropriate professionals."
                },
                tripwire_triggered=True
            )
    
    # Check for PII requests
    for pattern in PII_PATTERNS:
        if re.search(pattern, input_text):
            logger.warning(f"PII request detected")
            return GuardrailFunctionOutput(
                output_info={
                    "rejected": True,
                    "reason": "pii",
                    "message": "I can't share or request personal identification information."
                },
                tripwire_triggered=True
            )
    
    # Check for off-topic (but allow if farming context words present)
    farming_context_words = [
        "farm", "khet", "zameen", "acre", "hectare", "crop", "fasal", 
        "seed", "beej", "tractor", "tube well", "tubewell", "irrigation",
        "fertilizer", "khad", "pest", "keera", "disease", "bimari",
        "mandi", "price", "rate", "sell", "bech", "profit", "munafa",
        "weather", "mosam", "rain", "barish", "government", "sarkari",
        "subsidy", "kisan", "card", "loan", "qarz"
    ]
    
    has_farming_context = any(word in text_lower for word in farming_context_words)
    
    if not has_farming_context:
        for pattern in OFF_TOPIC_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"Off-topic query: {input_text[:100]}")
                return GuardrailFunctionOutput(
                    output_info={
                        "rejected": True,
                        "reason": "off_topic",
                        "message": "I'm Kisan Dost - an agricultural advisor. I can only help with farming questions like crops, pests, fertilizers, prices, weather, or government schemes."
                    },
                    tripwire_triggered=True
                )
    
    # Check for banned pesticide mentions
    for pesticide in BANNED_PESTICIDES:
        if pesticide.replace("_", " ") in text_lower:
            logger.warning(f"Banned pesticide mentioned: {pesticide}")
            return GuardrailFunctionOutput(
                output_info={
                    "rejected": True,
                    "reason": "banned_pesticide",
                    "message": f"That pesticide is banned in Pakistan. I cannot provide information about it. Please ask about approved alternatives."
                },
                tripwire_triggered=True
            )
    
    # All checks passed
    return GuardrailFunctionOutput(
        output_info={
            "rejected": False,
            "reason": "allowed"
        },
        tripwire_triggered=False
    )