"""
Conversation Manager with LLM Integration
Handles intelligent conversations using Claude or GPT-4
"""

import json
from typing import List, Dict, Optional, Callable
from datetime import datetime
import logging
from anthropic import Anthropic
import openai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Conversation message"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = datetime.now()
    metadata: Dict = {}


class ConversationContext(BaseModel):
    """Conversation context and state"""
    conversation_id: str
    customer_id: Optional[str] = None
    messages: List[Message] = []
    metadata: Dict = {}
    functions_called: List[str] = []
    sentiment: Optional[str] = None


class FunctionDefinition(BaseModel):
    """Function that AI can call"""
    name: str
    description: str
    parameters: Dict
    function: Callable


class ConversationManager:
    """
    Manages conversations with LLM integration
    Supports Claude and GPT-4
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        provider: str = "anthropic",  # 'anthropic' or 'openai'
        system_prompt: Optional[str] = None
    ):
        """
        Initialize conversation manager
        
        Args:
            api_key: API key for LLM provider
            model: Model name
            provider: 'anthropic' or 'openai'
            system_prompt: System instructions
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.functions: Dict[str, FunctionDefinition] = {}
        
        # Initialize client
        if provider == "anthropic":
            self.client = Anthropic(api_key=api_key)
        elif provider == "openai":
            openai.api_key = api_key
            self.client = openai
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for customer service"""
        return """You are a helpful AI customer service assistant. Your role is to:

1. Greet customers warmly and professionally
2. Understand their needs and questions
3. Provide accurate information
4. Use available functions to look up information or take actions
5. Be concise but friendly in your responses
6. Ask clarifying questions when needed
7. Transfer to human agent if unable to help

Always:
- Be polite and professional
- Keep responses brief (2-3 sentences max)
- Confirm important actions before executing
- Maintain conversation context

Never:
- Make promises you can't keep
- Share confidential information
- Get argumentative with customers
"""
    
    def register_function(
        self,
        name: str,
        description: str,
        parameters: Dict,
        function: Callable
    ):
        """
        Register a function that AI can call
        
        Args:
            name: Function name
            description: What the function does
            parameters: JSON schema for parameters
            function: Callable function
        """
        self.functions[name] = FunctionDefinition(
            name=name,
            description=description,
            parameters=parameters,
            function=function
        )
        logger.info(f"Registered function: {name}")
    
    async def generate_response(
        self,
        context: ConversationContext,
        user_message: str
    ) -> tuple[str, Dict]:
        """
        Generate AI response to user message
        
        Args:
            context: Conversation context
            user_message: User's message
            
        Returns:
            (response_text, function_results)
        """
        # Add user message to context
        context.messages.append(Message(
            role="user",
            content=user_message
        ))
        
        # Generate response based on provider
        if self.provider == "anthropic":
            response, functions_used = await self._claude_response(context)
        elif self.provider == "openai":
            response, functions_used = await self._openai_response(context)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Add assistant response to context
        context.messages.append(Message(
            role="assistant",
            content=response
        ))
        
        return response, functions_used
    
    async def _claude_response(
        self,
        context: ConversationContext
    ) -> tuple[str, Dict]:
        """Generate response using Claude"""
        try:
            # Prepare messages
            messages = [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in context.messages
                if msg.role in ['user', 'assistant']
            ]
            
            # Prepare tools if functions registered
            tools = []
            if self.functions:
                tools = [
                    {
                        "name": func.name,
                        "description": func.description,
                        "input_schema": func.parameters
                    }
                    for func in self.functions.values()
                ]
            
            # Call Claude API
            if tools:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=self.system_prompt,
                    messages=messages,
                    tools=tools
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=self.system_prompt,
                    messages=messages
                )
            
            # Handle tool calls
            functions_used = {}
            response_text = ""
            
            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                elif block.type == "tool_use":
                    # Execute function
                    func_name = block.name
                    func_args = block.input
                    
                    if func_name in self.functions:
                        logger.info(f"Executing function: {func_name}")
                        try:
                            result = await self.functions[func_name].function(**func_args)
                            functions_used[func_name] = result
                            context.functions_called.append(func_name)
                        except Exception as e:
                            logger.error(f"Function execution error: {e}")
                            functions_used[func_name] = {"error": str(e)}
            
            return response_text.strip(), functions_used
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return "I'm having trouble processing that. Could you rephrase?", {}
    
    async def _openai_response(
        self,
        context: ConversationContext
    ) -> tuple[str, Dict]:
        """Generate response using OpenAI"""
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            messages.extend([
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in context.messages
                if msg.role in ['user', 'assistant']
            ])
            
            # Prepare functions
            functions = []
            if self.functions:
                functions = [
                    {
                        "name": func.name,
                        "description": func.description,
                        "parameters": func.parameters
                    }
                    for func in self.functions.values()
                ]
            
            # Call OpenAI API
            if functions:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    functions=functions,
                    function_call="auto"
                )
            else:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            
            # Handle function calls
            functions_used = {}
            message = response.choices[0].message
            
            if message.function_call:
                func_name = message.function_call.name
                func_args = json.loads(message.function_call.arguments)
                
                if func_name in self.functions:
                    logger.info(f"Executing function: {func_name}")
                    try:
                        result = await self.functions[func_name].function(**func_args)
                        functions_used[func_name] = result
                        context.functions_called.append(func_name)
                    except Exception as e:
                        logger.error(f"Function execution error: {e}")
                        functions_used[func_name] = {"error": str(e)}
            
            response_text = message.content or ""
            return response_text.strip(), functions_used
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm having trouble processing that. Could you rephrase?", {}
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            'positive', 'negative', or 'neutral'
        """
        # Simple keyword-based sentiment (could use ML model)
        positive_words = ['thank', 'great', 'excellent', 'perfect', 'happy', 'love']
        negative_words = ['problem', 'issue', 'broken', 'angry', 'upset', 'hate', 'terrible']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'


# ============================================
# Example Function Definitions
# ============================================

async def lookup_order(order_id: str) -> Dict:
    """Look up order status"""
    # Simulate database lookup
    return {
        "order_id": order_id,
        "status": "In Transit",
        "expected_delivery": "Tomorrow",
        "tracking_number": "1Z999AA1234567890"
    }


async def check_business_hours() -> Dict:
    """Check business hours"""
    return {
        "monday_friday": "9:00 AM - 6:00 PM",
        "saturday": "10:00 AM - 4:00 PM",
        "sunday": "Closed",
        "current_status": "Open"
    }


async def schedule_appointment(date: str, time: str, service: str) -> Dict:
    """Schedule an appointment"""
    return {
        "confirmed": True,
        "appointment_id": "APT-12345",
        "date": date,
        "time": time,
        "service": service
    }


# ============================================
# Example Usage
# ============================================

async def main():
    """Example conversation"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize manager
    manager = ConversationManager(
        api_key=os.getenv("CLAUDE_API_KEY"),
        provider="anthropic"
    )
    
    # Register functions
    manager.register_function(
        name="lookup_order",
        description="Look up order status by order ID",
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID"
                }
            },
            "required": ["order_id"]
        },
        function=lookup_order
    )
    
    manager.register_function(
        name="check_business_hours",
        description="Check business operating hours",
        parameters={"type": "object", "properties": {}},
        function=check_business_hours
    )
    
    # Create conversation context
    context = ConversationContext(
        conversation_id="conv-123",
        customer_id="cust-456"
    )
    
    # Simulate conversation
    print("=== Customer Service AI Demo ===\n")
    
    queries = [
        "Hi, I need help with my order",
        "My order number is ORD-12345",
        "When will it arrive?",
        "What are your business hours?"
    ]
    
    for query in queries:
        print(f"Customer: {query}")
        
        response, functions = await manager.generate_response(context, query)
        
        print(f"AI: {response}")
        
        if functions:
            print(f"Functions called: {list(functions.keys())}")
        
        print()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
