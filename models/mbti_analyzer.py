import os
import json
import sys
import time
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from .recommendation_generator import RecommendationGenerator

class MBTIAnalyzer:
    def __init__(self):
        """Initialize the MBTI analyzer with dynamic conversation handling."""
        # Check for OpenAI API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY environment variable is not set.")
            print("Please set it in the .env file or as an environment variable.")
            sys.exit(1)
            
        # Setup OpenAI model
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
        )
        
        # Setup conversation memory
        self.memory = ConversationBufferMemory()
        
        # Setup conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
        # Initialize recommendation generator
        self.recommendation_generator = RecommendationGenerator()
        
        # Conversation state
        self.conversation_started = False
        self.test_complete = False
        self.mbti_result = None
        self.conversation_context = []
        self.current_question = None
        
        # Track dimension coverage
        self.dimension_coverage = {
            'E-I': 0.0,  # Coverage score for E/I dimension
            'S-N': 0.0,  # Coverage score for S/N dimension
            'T-F': 0.0,  # Coverage score for T/F dimension
            'J-P': 0.0   # Coverage score for J/P dimension
        }
        
        # Initial open-ended questions
        self.initial_questions = [
            "Tell me about what energizes you the most in life.",
            "How do you typically approach new situations or challenges?",
            "What's your ideal way to spend a free day?",
            "How do you usually make important decisions?"
        ]
        
        # MBTI dimension descriptions for context
        self.dimension_descriptions = {
            'E-I': {
                'E': "Extraversion - Energy from external world and people",
                'I': "Introversion - Energy from internal reflection and solitude"
            },
            'S-N': {
                'S': "Sensing - Focus on concrete facts and present reality",
                'N': "Intuition - Focus on patterns and future possibilities"
            },
            'T-F': {
                'T': "Thinking - Decisions based on logic and analysis",
                'F': "Feeling - Decisions based on values and harmony"
            },
            'J-P': {
                'J': "Judging - Preference for structure and planning",
                'P': "Perceiving - Preference for flexibility and spontaneity"
            }
        }
        
        # Welcome message
        self.welcome_message = (
            "Hi there! 👋 I'm your MBTI personality test assistant. "
            "Let's have a conversation to understand your personality better. "
            "I'll ask you questions about your preferences and tendencies, "
            "and at the end, I'll provide insights about your personality type "
            "along with personalized recommendations for music, books, and movies! "
            "Are you ready to begin?"
        )
    
    def process_message(self, message):
        """Process user message and return appropriate response."""
        if not message and not self.conversation_started:
            # First interaction, send welcome message
            return self.welcome_message, False, None
        
        if self.test_complete:
            # Test is already complete
            return "Your personality test is already complete! Your MBTI type is " + self.mbti_result, True, self.mbti_result
        
        if not self.conversation_started and "ready" in message.lower():
            # Start the conversation with first question
            self.conversation_started = True
            self.current_question = self.initial_questions[0]
            return self.current_question, False, None
        
        if self.conversation_started:
            # Analyze the response
            analysis = self._analyze_response(message)
            self._update_conversation_context(message, analysis)
            
            # Check if we have enough information
            if self._should_complete_test():
                # Calculate MBTI result
                self._calculate_mbti_result()
                self.test_complete = True
                
                # Generate the result message
                result_message = self._generate_result_message()
                return result_message, True, self.mbti_result
            else:
                # Generate next question
                next_question = self._generate_next_question()
                self.current_question = next_question
                return next_question, False, None
        
        # Default response
        return "I'm not sure how to respond to that. Are you ready to continue our conversation?", False, None
    
    def _analyze_response(self, response):
        """Analyze response for MBTI indicators and update dimension coverage."""
        analysis_prompt = f"""
        Analyze this response in the context of MBTI dimensions:
        
        Previous context: {self._format_conversation_history()}
        Current response: "{response}"
        Current question: "{self.current_question}"
        
        For each MBTI dimension pair (E-I, S-N, T-F, J-P):
        1. Identify relevant indicators
        2. Assess confidence level (0-1)
        3. Extract key themes or patterns
        4. Determine which preference is stronger
        
        Format the response as JSON with the following structure:
        {{
            "dimension_analysis": {{
                "E-I": {{"confidence": float, "preference": "E" or "I", "indicators": []}},
                "S-N": {{"confidence": float, "preference": "S" or "N", "indicators": []}},
                "T-F": {{"confidence": float, "preference": "T" or "F", "indicators": []}},
                "J-P": {{"confidence": float, "preference": "J" or "P", "indicators": []}}
            }},
            "themes": [list of key themes],
            "context_relevance": float
        }}
        """
        
        # Get analysis from LLM
        result = self.conversation.predict(input=analysis_prompt)
        try:
            analysis = json.loads(result)
            self._update_dimension_coverage(analysis)
            return analysis
        except json.JSONDecodeError:
            print("Error parsing analysis result")
            return None
    
    def _generate_next_question(self):
        """Generate a contextual follow-up question based on conversation history."""
        # Determine which dimensions need more coverage
        weak_dimensions = [dim for dim, score in self.dimension_coverage.items() if score < 0.6]
        
        question_prompt = f"""
        Based on the following conversation history:
        {self._format_conversation_history()}
        
        Current dimension coverage:
        {json.dumps(self.dimension_coverage, indent=2)}
        
        Generate a natural follow-up question that:
        1. Feels like a natural continuation of the conversation
        2. Helps gather information about these dimensions: {', '.join(weak_dimensions)}
        3. References previous answers when relevant
        4. Maintains a conversational, friendly tone
        
        The question should:
        - Not feel like a test question
        - Be open-ended
        - Encourage detailed responses
        - Flow naturally from the previous response
        - Not directly ask about personality preferences
        
        Return only the question text, without any additional context or explanation.
        """
        
        # If we have remaining initial questions and low coverage, use them
        if len(self.conversation_context) < len(self.initial_questions):
            return self.initial_questions[len(self.conversation_context)]
        
        # Generate dynamic question
        return self.conversation.predict(input=question_prompt)
    
    def _update_dimension_coverage(self, analysis):
        """Update dimension coverage based on response analysis."""
        if not analysis or 'dimension_analysis' not in analysis:
            return
            
        for dimension, data in analysis['dimension_analysis'].items():
            confidence = data.get('confidence', 0)
            # Update coverage score with diminishing returns
            current_coverage = self.dimension_coverage[dimension]
            self.dimension_coverage[dimension] = min(1.0, current_coverage + (confidence * (1 - current_coverage)))
    
    def _should_complete_test(self):
        """Determine if we have enough information to complete the test."""
        # Check if we have at least 8 responses
        if len(self.conversation_context) < 8:
            return False
            
        # Check if we have good coverage of all dimensions
        return all(score >= 0.8 for score in self.dimension_coverage.values())
    
    def _format_conversation_history(self):
        """Format conversation history for LLM prompts."""
        history = []
        for entry in self.conversation_context[-5:]:  # Last 5 interactions
            history.append(f"Q: {entry.get('question', 'Unknown question')}")
            history.append(f"A: {entry.get('response', 'No response')}")
        return "\n".join(history)
    
    def _update_conversation_context(self, response, analysis):
        """Update conversation context with new response and analysis."""
        self.conversation_context.append({
            'question': self.current_question,
            'response': response,
            'analysis': analysis,
            'timestamp': time.time()
        })
    
    def _calculate_mbti_result(self):
        """Calculate MBTI result based on accumulated conversation analysis."""
        preferences = {
            'E': 0, 'I': 0,
            'S': 0, 'N': 0,
            'T': 0, 'F': 0,
            'J': 0, 'P': 0
        }
        
        # Analyze all responses to determine preferences
        for entry in self.conversation_context:
            analysis = entry.get('analysis', {})
            if 'dimension_analysis' in analysis:
                for dimension, data in analysis['dimension_analysis'].items():
                    if 'preference' in data and 'confidence' in data:
                        pref = data['preference']
                        conf = data['confidence']
                        preferences[pref] += conf
        
        # Determine final type
        result = ""
        result += "E" if preferences['E'] > preferences['I'] else "I"
        result += "S" if preferences['S'] > preferences['N'] else "N"
        result += "T" if preferences['T'] > preferences['F'] else "F"
        result += "J" if preferences['J'] > preferences['P'] else "P"
        
        self.mbti_result = result
    
    def _generate_result_message(self):
        """Generate a detailed result message with explanation and recommendations."""
        mbti_descriptions = {
            "ISTJ": "The Inspector: Practical, fact-minded, and reliable. You value loyalty, hard work, and tradition.",
            "ISFJ": "The Protector: Quiet, caring, and dependable. You're committed to fulfilling your duties and responsibilities.",
            "INFJ": "The Counselor: Insightful, principled, and idealistic. You seek meaning and connection in relationships and work.",
            "INTJ": "The Mastermind: Strategic, innovative, and independent. You have a clear vision and drive for improvement.",
            "ISTP": "The Craftsman: Practical, analytical, and adaptable. You're skilled at understanding how things work.",
            "ISFP": "The Composer: Gentle, sensitive, and artistic. You value personal freedom and expressing yourself authentically.",
            "INFP": "The Healer: Idealistic, empathetic, and creative. You're driven by your personal values and desire to help others.",
            "INTP": "The Architect: Logical, curious, and theoretical. You enjoy abstract thinking and solving complex problems.",
            "ESTP": "The Dynamo: Energetic, pragmatic, and spontaneous. You thrive in dynamic situations and enjoy taking risks.",
            "ESFP": "The Performer: Outgoing, friendly, and enthusiastic. You live in the moment and bring fun to any situation.",
            "ENFP": "The Champion: Imaginative, enthusiastic, and compassionate. You're inspired by possibilities and what could be.",
            "ENTP": "The Visionary: Innovative, resourceful, and intellectually curious. You enjoy theoretical discussions and debates.",
            "ESTJ": "The Supervisor: Organized, practical, and decisive. You value structure, clarity, and following procedures.",
            "ESFJ": "The Provider: Warm, cooperative, and reliable. You're attuned to others' needs and seek to create harmony.",
            "ENFJ": "The Teacher: Charismatic, empathetic, and inspiring. You help others develop and grow to their full potential.",
            "ENTJ": "The Commander: Strategic, ambitious, and assertive. You're driven to lead and implement your vision."
        }
        
        # Get base description
        description = mbti_descriptions.get(self.mbti_result, "Unknown personality type")
        
        # Generate personalized recommendations
        recommendations = self.recommendation_generator.generate_recommendations(self.mbti_result)
        
        # Generate personalized insights based on conversation
        insights_prompt = f"""
        Based on this conversation history:
        {self._format_conversation_history()}
        
        And the determined MBTI type of {self.mbti_result},
        generate 3-4 personalized insights about the person's:
        1. Communication style
        2. Decision-making approach
        3. Energy management
        4. Personal values
        
        Keep the insights specific to what was discussed in the conversation.
        Format each insight as a bullet point.
        """
        
        personal_insights = self.conversation.predict(input=insights_prompt)
        
        # Combine all components
        result_message = f"""
        🎉 Your MBTI Personality Type: {self.mbti_result}

        {description}

        Based on our conversation, here are some personal insights about you:
        {personal_insights}

        🎯 I've also prepared some personalized recommendations just for you:

        {recommendations}

        Remember, these insights and recommendations are suggestions based on our conversation and your personality type. Feel free to explore and discover what resonates with you personally!
        """
        
        return result_message 