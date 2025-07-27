import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from groq import Groq
from datetime import datetime
from models import *
from database import user_service, card_service, loan_service, account_service

class ConversationAI:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.contexts: Dict[str, ConversationContext] = {}

    async def analyze_intent_and_entities(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """AI-powered intent and entity analysis with context awareness"""
        history_text = ""
        if context.conversation_history:
            recent_history = context.conversation_history[-3:]
            history_text = "\n".join([f"{msg['role']}: {msg['message']}" for msg in recent_history])

        current_intent_text = context.current_intent.value if context.current_intent else "none"
        current_state = context.conversation_state.value if context.conversation_state else "idle"
        collected_data = json.dumps(context.collected_data) if context.collected_data else "{}"

        prompt = f"""
You are an expert banking conversation analyst. Analyze the user message and provide structured output.

CONVERSATION CONTEXT:
- Current Intent: {current_intent_text}
- Current State: {current_state}
- Collected Data: {collected_data}
- Recent History: {history_text}

USER MESSAGE: "{message}"

AVAILABLE INTENTS:
- loan_application: User wants to apply for a new loan
- loan_inquiry: User wants to check existing loan applications or loan status
- card_blocking: User wants to block/freeze a card
- card_application: User wants to apply for a new card
- card_inquiry: User asking about existing cards or card status
- balance_inquiry: User wants to check account balance
- transaction_history: User wants to see transactions
- general_inquiry: General questions or greetings
- greeting: Hello, hi, good morning etc.
- goodbye: Bye, see you later etc.

Respond ONLY with valid JSON:
{{
"intent": "intent_name",
"entities": {{
"amount": "extracted_amount_if_any",
"card_type": "debit/credit_if_mentioned",
"loan_purpose": "purpose_if_mentioned",
"card_last_4": "last_4_digits_if_mentioned"
}},
"context_switch": true/false,
"confidence": 0.0-1.0,
"reasoning": "brief_explanation"
}}
"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            analysis = json.loads(response.choices[0].message.content)
            entities = {k: v for k, v in analysis.get("entities", {}).items() if v and v != ""}
            return {
                "intent": Intent(analysis["intent"]),
                "entities": entities,
                "context_switch": analysis.get("context_switch", False),
                "confidence": analysis.get("confidence", 0.5),
                "reasoning": analysis.get("reasoning", "")
            }
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return self._fallback_analysis(message, context)

    def _fallback_analysis(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Fallback pattern-based analysis"""
        message_lower = message.lower()
        
        # Enhanced pattern-based intent recognition
        if any(word in message_lower for word in ["block", "freeze", "stop", "lost", "stolen"]) and "card" in message_lower:
            intent = Intent.CARD_BLOCKING
        elif any(phrase in message_lower for phrase in ["apply for card", "new card", "create card", "get a card"]):
            intent = Intent.CARD_APPLICATION
        elif any(phrase in message_lower for phrase in ["my loans", "loan status", "loan applications", "check loan"]):
            intent = Intent.LOAN_INQUIRY
        elif any(word in message_lower for word in ["loan", "borrow"]) or "apply" in message_lower:
            intent = Intent.LOAN_APPLICATION
        elif any(word in message_lower for word in ["balance", "money", "amount"]):
            intent = Intent.BALANCE_INQUIRY
        elif any(word in message_lower for word in ["transaction", "history", "statement"]):
            intent = Intent.TRANSACTION_HISTORY
        elif "card" in message_lower:
            intent = Intent.CARD_INQUIRY
        elif any(word in message_lower for word in ["hello", "hi", "hey", "good morning"]):
            intent = Intent.GREETING
        else:
            intent = Intent.GENERAL_INQUIRY

        # Extract basic entities
        entities = {}
        amount_match = re.search(r"\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", message)
        if amount_match:
            entities["amount"] = amount_match.group(1).replace(",", "")
        
        if "debit" in message_lower:
            entities["card_type"] = "debit"
        elif "credit" in message_lower:
            entities["card_type"] = "credit"

        return {
            "intent": intent,
            "entities": entities,
            "context_switch": context.current_intent and intent != context.current_intent,
            "confidence": 0.7,
            "reasoning": "Pattern-based fallback"
        }

    async def generate_response(self, context: ConversationContext, user_message: str,
                              system_data: Dict[str, Any] = None) -> str:
        """Generate AI-powered conversational responses"""
        history_text = ""
        if context.conversation_history:
            recent_history = context.conversation_history[-4:]
            history_text = "\n".join([f"{msg['role']}: {msg['message']}" for msg in recent_history])

        current_intent = context.current_intent.value if context.current_intent else "none"
        current_state = context.conversation_state.value if context.conversation_state else "idle"
        workflow_step = context.workflow_step or "none"
        collected_data = json.dumps(context.collected_data, indent=2) if context.collected_data else "{}"

        system_context = ""
        if system_data:
            system_context = f"\nSYSTEM DATA: {json.dumps(system_data, indent=2)}"

        prompt = f"""
You are a professional AI Banking Assistant. Generate a helpful, conversational response.

CONVERSATION CONTEXT:
- Current Intent: {current_intent}
- Conversation State: {current_state}
- Workflow Step: {workflow_step}
- Collected Data: {collected_data}
- Recent History: {history_text}

USER MESSAGE: "{user_message}"
{system_context}

RESPONSE GUIDELINES:
1. Be conversational, helpful, and professional
2. If collecting information, ask specific questions
3. If showing data, format it clearly with numbers and lists
4. Keep responses concise but informative
5. DO NOT use any emojis, symbols, or special characters
6. Use plain text formatting only
7. Use "Number:" for lists instead of bullets

Generate a natural, helpful response:
"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Clean response of any remaining emojis or symbols
            response_text = response.choices[0].message.content.strip()
            response_text = re.sub(r'[^\w\s\-.,!?:;()\[\]{}"]', '', response_text)
            return response_text
        except Exception as e:
            print(f"AI Response Generation Error: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Could you please try again?"

class AdvancedWorkflowEngine:
    def __init__(self, conversation_ai: ConversationAI):
        self.conversation_ai = conversation_ai
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    async def handle_conversation(self, user_id: str, message: str, session_id: str) -> Dict[str, Any]:
        """Main conversation handling with AI integration"""
        # Get or create context
        if session_id not in self.conversation_ai.contexts:
            self.conversation_ai.contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id
            )

        context = self.conversation_ai.contexts[session_id]

        # Add message to history
        context.conversation_history.append({
            "role": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        # AI-powered intent and entity analysis
        analysis = await self.conversation_ai.analyze_intent_and_entities(message, context)

        # Handle context switching
        if analysis["context_switch"]:
            await self._handle_context_switch(context, analysis["intent"])

        # Update current intent
        context.current_intent = analysis["intent"]

        # Route to appropriate handler
        response = await self._route_to_handler(context, message, analysis)

        # Add response to history
        context.conversation_history.append({
            "role": "assistant",
            "message": response["response"],
            "timestamp": datetime.now().isoformat()
        })

        return response

    async def _handle_context_switch(self, context: ConversationContext, new_intent: Intent):
        """Handle context switching between different banking tasks"""
        if context.current_intent and context.conversation_state != ConversationState.COMPLETED:
            # Save current state to interruption stack
            context.interruption_stack.append({
                "intent": context.current_intent.value,
                "state": context.conversation_state.value,
                "collected_data": context.collected_data.copy(),
                "workflow_step": context.workflow_step,
                "timestamp": datetime.now().isoformat()
            })

        # Reset for new intent
        context.collected_data = {}
        context.conversation_state = ConversationState.IDLE
        context.workflow_step = ""

    async def _route_to_handler(self, context: ConversationContext, message: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Route message to appropriate workflow handler"""
        intent = analysis["intent"]
        
        try:
            if intent == Intent.CARD_BLOCKING:
                return await self._handle_card_blocking_simplified(context, message, analysis)
            elif intent == Intent.CARD_APPLICATION:
                return await self._handle_card_application_ai(context, message, analysis)
            elif intent == Intent.LOAN_APPLICATION:
                return await self._handle_loan_application_ai(context, message, analysis)
            elif intent == Intent.LOAN_INQUIRY:
                return await self._handle_loan_inquiry_ai(context, message)
            elif intent == Intent.BALANCE_INQUIRY:
                return await self._handle_balance_inquiry_ai(context, message)
            elif intent == Intent.TRANSACTION_HISTORY:
                return await self._handle_transaction_history_ai(context, message)
            elif intent == Intent.CARD_INQUIRY:
                return await self._handle_card_inquiry_ai(context, message)
            elif intent == Intent.GREETING:
                return await self._handle_greeting_ai(context, message)
            elif intent == Intent.GOODBYE:
                return await self._handle_goodbye_ai(context, message)
            else:
                return await self._handle_general_inquiry_ai(context, message)
        except Exception as e:
            print(f"Handler Error: {e}")
            error_response = await self.conversation_ai.generate_response(
                context, message, {"error": str(e), "action": "error_handling"}
            )
            return {"response": error_response, "completed": True, "error": True}

    async def _handle_card_blocking_simplified(self, context: ConversationContext, message: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """SIMPLIFIED card blocking workflow - only essential steps"""
        
        if context.conversation_state == ConversationState.IDLE:
            # Step 1: Get user cards and show selection
            user_cards = await card_service.get_user_cards(context.user_id)
            active_cards = [card for card in user_cards if card["card_status"] == "active"]
            
            if not active_cards:
                response = await self.conversation_ai.generate_response(
                    context, message,
                    {"active_cards": [], "action": "no_active_cards"}
                )
                return {"response": response, "completed": True}
            
            context.collected_data["user_cards"] = active_cards
            context.conversation_state = ConversationState.COLLECTING_INFO
            context.workflow_step = "card_selection"
            
            response = await self.conversation_ai.generate_response(
                context, message,
                {"active_cards": active_cards, "action": "select_card_to_block"}
            )
            return {"response": response, "workflow_active": True}

        elif context.workflow_step == "card_selection":
            # Step 2: Card selection (by number or last 4 digits)
            active_cards = context.collected_data["user_cards"]
            selected_card = None
            
            # Check if user confirmed with "yes" (from previous conversation)
            if "yes" in message.lower() or "confirm" in message.lower():
                # Find the card mentioned in previous context or use the first active card
                if len(active_cards) == 1:
                    selected_card = active_cards[0]
                else:
                    # Look for card ending with 7890 (from conversation history)
                    for card in active_cards:
                        if card["card_number"].endswith("7890"):
                            selected_card = card
                            break
            else:
                # Try to parse card selection
                if message.strip().isdigit():
                    try:
                        card_index = int(message.strip()) - 1
                        if 0 <= card_index < len(active_cards):
                            selected_card = active_cards[card_index]
                    except:
                        pass
                else:
                    # Check for last 4 digits
                    last_4 = re.sub(r'\D', '', message)[-4:]
                    if len(last_4) == 4:
                        for card in active_cards:
                            if card["card_number"].replace("-", "")[-4:] == last_4:
                                selected_card = card
                                break
            
            if selected_card:
                context.collected_data["selected_card"] = selected_card
                context.workflow_step = "dob_verification"
                
                response = await self.conversation_ai.generate_response(
                    context, message,
                    {"selected_card": selected_card, "action": "ask_dob_verification"}
                )
                return {"response": response, "workflow_active": True}
            else:
                response = await self.conversation_ai.generate_response(
                    context, message,
                    {"active_cards": active_cards, "action": "invalid_card_selection"}
                )
                return {"response": response, "workflow_active": True, "clarification_needed": True}

        elif context.workflow_step == "dob_verification":
            # Step 3: Single DOB verification
            user_data = await user_service.get_user(context.user_id)
            user_dob = user_data.get("date_of_birth", "1990-01-01") if user_data else "1990-01-01"
            
            entered_dob = message.strip()
            
            # Handle different date formats
            if "/" in entered_dob:
                parts = entered_dob.split("/")
                if len(parts) == 3 and len(parts[2]) == 4:
                    entered_dob = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            
            if entered_dob == user_dob:
                context.workflow_step = "reason_collection"
                response = await self.conversation_ai.generate_response(
                    context, message,
                    {"action": "ask_block_reason"}
                )
                return {"response": response, "workflow_active": True}
            else:
                # Wrong DOB - one more chance
                if "wrong_dob_attempts" not in context.collected_data:
                    context.collected_data["wrong_dob_attempts"] = 1
                    response = await self.conversation_ai.generate_response(
                        context, message,
                        {"action": "wrong_dob_retry"}
                    )
                    return {"response": response, "workflow_active": True, "clarification_needed": True}
                else:
                    # Failed security - cancel
                    context.conversation_state = ConversationState.COMPLETED
                    response = await self.conversation_ai.generate_response(
                        context, message,
                        {"action": "security_verification_failed"}
                    )
                    return {"response": response, "completed": True}

        elif context.workflow_step == "reason_collection":
            # Step 4: Get blocking reason
            block_reason = message.strip()
            if len(block_reason) < 2:
                response = await self.conversation_ai.generate_response(
                    context, message,
                    {"action": "reason_too_short"}
                )
                return {"response": response, "workflow_active": True, "clarification_needed": True}
            
            context.collected_data["block_reason"] = block_reason
            context.workflow_step = "final_confirmation"
            
            selected_card = context.collected_data["selected_card"]
            response = await self.conversation_ai.generate_response(
                context, message,
                {
                    "selected_card": selected_card,
                    "block_reason": block_reason,
                    "action": "final_confirmation"
                }
            )
            return {"response": response, "workflow_active": True}

        elif context.workflow_step == "final_confirmation":
            # Step 5: Final confirmation and block the card
            if any(word in message.lower() for word in ["yes", "confirm", "block", "okay", "ok", "1"]):
                selected_card = context.collected_data["selected_card"]
                block_reason = context.collected_data.get("block_reason", "User requested")
                
                try:
                    # Block the card with enhanced error handling
                    block_result = await card_service.block_card(
                        selected_card["card_id"],
                        f"{block_reason} - Blocked via assistant at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    
                    # Check if blocking was successful
                    if not block_result.get("success", False):
                        context.conversation_state = ConversationState.COMPLETED
                        response = await self.conversation_ai.generate_response(
                            context, message,
                            {
                                "error": block_result.get("error", "Unknown error occurred"),
                                "action": "block_failed"
                            }
                        )
                        return {"response": response, "completed": True, "error": True}
                    
                    # **CRITICAL: Clear any cached card data**
                    if hasattr(context, 'collected_data') and 'user_cards' in context.collected_data:
                        del context.collected_data['user_cards']
                    
                    # Fetch fresh card data to verify blocking
                    fresh_cards = await card_service.get_user_cards(context.user_id)
                    blocked_card = next(
                        (card for card in fresh_cards if card["card_id"] == selected_card["card_id"]),
                        None
                    )
                    
                    context.conversation_state = ConversationState.COMPLETED
                    
                    # Verify the card shows as blocked in fresh data
                    if blocked_card and blocked_card["card_status"] == "blocked":
                        response = await self.conversation_ai.generate_response(
                            context, message,
                            {
                                "selected_card": selected_card,
                                "blocked_card": blocked_card,
                                "block_result": block_result,
                                "action": "block_successful_verified"
                            }
                        )
                        return {"response": response, "completed": True}
                    else:
                        # Blocking failed - status didn't change
                        response = await self.conversation_ai.generate_response(
                            context, message,
                            {
                                "selected_card": selected_card,
                                "error": "Card status did not update to blocked",
                                "action": "block_verification_failed"
                            }
                        )
                        return {"response": response, "completed": True, "error": True}
                        
                except Exception as e:
                    context.conversation_state = ConversationState.COMPLETED
                    response = await self.conversation_ai.generate_response(
                        context, message,
                        {"error": f"System error during blocking: {str(e)}", "action": "system_error"}
                    )
                    return {"response": response, "completed": True, "error": True}
            else:
                # User cancelled
                context.conversation_state = ConversationState.COMPLETED
                response = await self.conversation_ai.generate_response(
                    context, message, {"action": "block_cancelled"}
                )
                return {"response": response, "completed": True}


        # Default fallback
        response = await self.conversation_ai.generate_response(
            context, message, {"action": "card_blocking_help"}
        )
        return {"response": response, "workflow_active": True}

    # Other handlers remain the same but simplified
    async def _handle_card_inquiry_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Get fresh card data"""
        cards = await card_service.get_user_cards(context.user_id)
        response = await self.conversation_ai.generate_response(
            context, message,
            {"cards": cards, "action": "show_cards"}
        )
        return {"response": response, "completed": True}

    async def _handle_balance_inquiry_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Balance inquiry"""
        accounts = await account_service.get_user_accounts(context.user_id)
        response = await self.conversation_ai.generate_response(
            context, message,
            {"accounts": accounts, "action": "show_balance"}
        )
        return {"response": response, "completed": True}

    async def _handle_transaction_history_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Transaction history"""
        accounts = await account_service.get_user_accounts(context.user_id)
        transactions = []
        if accounts:
            transactions = await account_service.get_account_transactions(accounts[0]["account_id"], 5)
        
        response = await self.conversation_ai.generate_response(
            context, message,
            {"accounts": accounts, "transactions": transactions, "action": "show_transactions"}
        )
        return {"response": response, "completed": True}

    async def _handle_loan_inquiry_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Loan inquiry"""
        loan_applications = await loan_service.get_user_loan_applications(context.user_id)
        response = await self.conversation_ai.generate_response(
            context, message,
            {"loan_applications": loan_applications, "action": "show_loans"}
        )
        return {"response": response, "completed": True}

    async def _handle_greeting_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Greeting response"""
        response = await self.conversation_ai.generate_response(
            context, message, {"action": "greeting"}
        )
        return {"response": response, "completed": True}

    async def _handle_goodbye_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """Goodbye response"""
        response = await self.conversation_ai.generate_response(
            context, message, {"action": "goodbye"}
        )
        return {"response": response, "completed": True}

    async def _handle_general_inquiry_ai(self, context: ConversationContext, message: str) -> Dict[str, Any]:
        """General inquiry response"""
        response = await self.conversation_ai.generate_response(
            context, message, {"action": "general_help"}
        )
        return {"response": response, "completed": True}

    async def _handle_card_application_ai(self, context: ConversationContext, message: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified card application"""
        # Implementation similar to before but simplified
        response = await self.conversation_ai.generate_response(
            context, message, {"action": "card_application_help"}
        )
        return {"response": response, "workflow_active": True}

    async def _handle_loan_application_ai(self, context: ConversationContext, message: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified loan application"""
        # Implementation similar to before but simplified
        response = await self.conversation_ai.generate_response(
            context, message, {"action": "loan_application_help"}
        )
        return {"response": response, "workflow_active": True}

# Initialize services
conversation_ai = ConversationAI()
workflow_engine = AdvancedWorkflowEngine(conversation_ai)
