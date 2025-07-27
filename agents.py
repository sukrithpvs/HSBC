from typing import Dict, Any
from services import workflow_engine
from datetime import datetime

class BankingConversationAgent:
    def __init__(self):
        self.workflow_engine = workflow_engine

    async def process_message(self, user_id: str, message: str, session_id: str) -> Dict[str, Any]:
        """Main entry point for AI-powered conversation processing"""
        try:
            # Process through the AI-enhanced workflow engine
            response = await self.workflow_engine.handle_conversation(user_id, message, session_id)
            
            # Get current context for additional metadata
            context = self.workflow_engine.conversation_ai.contexts.get(session_id)
            
            return {
                "response": response["response"],
                "intent": response.get("intent"),
                "workflow_active": response.get("workflow_active", False),
                "completed": response.get("completed", False),
                "context_switched": response.get("context_switched", False),
                "clarification_needed": response.get("clarification_needed", False),
                "ai_confidence": context.ai_confidence if context else 0.0,
                "current_state": context.conversation_state.value if context else "idle",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Agent Error: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your request. Could you please try rephrasing your question? Error: {str(e)}",
                "completed": True,
                "error": True,
                "timestamp": datetime.now().isoformat()
            }

    async def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get current conversation context for debugging/monitoring"""
        context = self.workflow_engine.conversation_ai.contexts.get(session_id)
        if context:
            return {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "current_intent": context.current_intent.value if context.current_intent else None,
                "conversation_state": context.conversation_state.value,
                "workflow_step": context.workflow_step,
                "collected_data": context.collected_data,
                "conversation_length": len(context.conversation_history),
                "interruption_stack_size": len(context.interruption_stack)
            }
        return {}

    async def reset_conversation(self, session_id: str) -> bool:
        """Reset conversation context"""
        if session_id in self.workflow_engine.conversation_ai.contexts:
            del self.workflow_engine.conversation_ai.contexts[session_id]
            return True
        return False

# Global agent instance
banking_agent = BankingConversationAgent()
