from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Intent(str, Enum):
    LOAN_APPLICATION = "loan_application"
    LOAN_INQUIRY = "loan_inquiry"  # Add this line
    CARD_BLOCKING = "card_blocking"
    CARD_INQUIRY = "card_inquiry"
    CARD_APPLICATION = "card_application"
    BALANCE_INQUIRY = "balance_inquiry"
    TRANSACTION_HISTORY = "transaction_history"
    GENERAL_INQUIRY = "general_inquiry"
    GREETING = "greeting"
    GOODBYE = "goodbye"


class ConversationState(str, Enum):
    IDLE = "idle"
    COLLECTING_INFO = "collecting_info"
    PROCESSING = "processing"
    CONFIRMING = "confirming"
    COMPLETED = "completed"

class ConversationContext(BaseModel):
    session_id: str
    user_id: str
    current_intent: Optional[Intent] = None
    conversation_state: ConversationState = ConversationState.IDLE
    collected_data: Dict[str, Any] = {}
    conversation_history: List[Dict[str, Any]] = []
    workflow_step: str = ""
    interruption_stack: List[Dict[str, Any]] = []
    ai_confidence: float = 0.0
    last_ai_reasoning: str = ""

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    workflow_active: bool = False
    completed: bool = False
    context_switched: bool = False
    clarification_needed: bool = False
    ai_confidence: Optional[float] = None
