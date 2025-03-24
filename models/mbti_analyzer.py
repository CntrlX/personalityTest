import os
import json
import sys
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

class MBTIAnalyzer:
    def __init__(self):
        """Initialize the MBTI analyzer with questions and Langchain components."""
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
        
        # MBTI test state
        self.current_question_index = 0
        self.user_responses = []
        self.test_complete = False
        self.mbti_result = None
        
        # Load MBTI questions
        self.questions = self._load_questions()
        
        # Initialize dimension scores
        self.scores = {
            "E": 0, "I": 0,
            "S": 0, "N": 0,
            "T": 0, "F": 0,
            "J": 0, "P": 0
        }
        
        # Welcome message
        self.welcome_message = (
            "Hi there! 👋 I'm your MBTI personality test assistant. "
            "I'll ask you a series of questions to determine your personality type. "
            "Please answer honestly - there are no right or wrong answers. "
            "Are you ready to begin?"
        )
    
    def _load_questions(self):
        """Load MBTI questions from a predefined list."""
        return [
            {
                "question": "Do you prefer spending time with a large group of friends or having deep conversations with just a few close friends?",
                "dimension": {"large group": "E", "few close friends": "I"}
            },
            {
                "question": "When making decisions, do you tend to follow your heart or rely on logical analysis?",
                "dimension": {"heart": "F", "logical analysis": "T"}
            },
            {
                "question": "Do you prefer having a structured plan or being spontaneous and flexible?",
                "dimension": {"structured plan": "J", "spontaneous": "P"}
            },
            {
                "question": "Are you more interested in concrete facts and details or exploring ideas and possibilities?",
                "dimension": {"facts and details": "S", "ideas and possibilities": "N"}
            },
            {
                "question": "In social situations, do you tend to initiate conversations or wait for others to approach you?",
                "dimension": {"initiate conversations": "E", "wait for others": "I"}
            },
            {
                "question": "When solving problems, do you rely more on past experiences or consider innovative approaches?",
                "dimension": {"past experiences": "S", "innovative approaches": "N"}
            },
            {
                "question": "Do you prefer to have things decided and settled or keep your options open?",
                "dimension": {"decided and settled": "J", "options open": "P"}
            },
            {
                "question": "Is it more important to you that something is fair and just, or that harmony is maintained?",
                "dimension": {"fair and just": "T", "harmony": "F"}
            },
            {
                "question": "Do you find it energizing to be the center of attention or do you prefer to observe from the sidelines?",
                "dimension": {"center of attention": "E", "observe": "I"}
            },
            {
                "question": "Do you pay more attention to the immediate practical needs or focus on future possibilities?",
                "dimension": {"immediate practical needs": "S", "future possibilities": "N"}
            },
            {
                "question": "When giving criticism, are you straightforward and objective or tactful and supportive?",
                "dimension": {"straightforward": "T", "tactful": "F"}
            },
            {
                "question": "Do you prefer to work on multiple projects simultaneously or focus on one project until completion?",
                "dimension": {"multiple projects": "P", "one project": "J"}
            },
            {
                "question": "After a long day, would you rather attend a social event or spend quiet time alone?",
                "dimension": {"social event": "E", "quiet time alone": "I"}
            },
            {
                "question": "Are you more likely to trust your experience or rely on your intuition?",
                "dimension": {"experience": "S", "intuition": "N"}
            },
            {
                "question": "Is it more important that a decision feels right emotionally or makes logical sense?",
                "dimension": {"feels right emotionally": "F", "makes logical sense": "T"}
            },
            {
                "question": "Do you prefer to have detailed step-by-step instructions or just a general direction?",
                "dimension": {"detailed instructions": "J", "general direction": "P"}
            },
            {
                "question": "Do you usually express your emotions openly or keep them to yourself?",
                "dimension": {"express openly": "E", "keep to yourself": "I"}
            },
            {
                "question": "Are you more comfortable with routine and familiar situations or do you seek new experiences?",
                "dimension": {"routine": "S", "new experiences": "N"}
            },
            {
                "question": "When resolving a conflict, do you focus more on finding the logical solution or maintaining relationships?",
                "dimension": {"logical solution": "T", "maintaining relationships": "F"}
            },
            {
                "question": "Do you prefer to plan your activities in advance or decide spontaneously?",
                "dimension": {"plan in advance": "J", "decide spontaneously": "P"}
            }
        ]
    
    def process_message(self, message):
        """Process user message and return appropriate response."""
        if not message and self.current_question_index == 0:
            # First interaction, send welcome message
            return self.welcome_message, False, None
        
        if self.test_complete:
            # Test is already complete
            return "Your personality test is already complete! Your MBTI type is " + self.mbti_result, True, self.mbti_result
        
        if self.current_question_index == 0 and "ready" in message.lower():
            # User is ready to start
            response = self.questions[0]["question"]
            self.current_question_index += 1
            return response, False, None
        
        if self.current_question_index > 0 and self.current_question_index <= len(self.questions):
            # Process the answer to the previous question
            self._analyze_response(message, self.current_question_index - 1)
            
            # Check if we have more questions
            if self.current_question_index < len(self.questions):
                response = self.questions[self.current_question_index]["question"]
                self.current_question_index += 1
                return response, False, None
            else:
                # No more questions, calculate result
                self._calculate_mbti_result()
                self.test_complete = True
                
                # Generate the result message
                result_message = self._generate_result_message()
                return result_message, True, self.mbti_result
        
        # Default response
        return "I'm not sure how to respond to that. Are you ready to continue with the personality test?", False, None
    
    def _analyze_response(self, response, question_index):
        """Analyze user response to a question and update scores."""
        question = self.questions[question_index]
        dimension_options = question["dimension"]
        
        # Add response to history
        self.user_responses.append({
            "question": question["question"],
            "response": response
        })
        
        # Use LLM to determine which dimension is stronger in the response
        prompt = f"""
        Analyze the following response to the question: "{question['question']}"
        
        Response: "{response}"
        
        Based on the response, determine if it aligns more with:
        Option 1: {list(dimension_options.keys())[0]} (maps to {list(dimension_options.values())[0]})
        Option 2: {list(dimension_options.keys())[1]} (maps to {list(dimension_options.values())[1]})
        
        Only reply with either "{list(dimension_options.values())[0]}" or "{list(dimension_options.values())[1]}".
        """
        
        result = self.conversation.predict(input=prompt)
        
        # Update score based on the dimension identified
        if list(dimension_options.values())[0] in result:
            self.scores[list(dimension_options.values())[0]] += 1
        elif list(dimension_options.values())[1] in result:
            self.scores[list(dimension_options.values())[1]] += 1
    
    def _calculate_mbti_result(self):
        """Calculate the final MBTI result based on accumulated scores."""
        result = ""
        
        # E vs I
        result += "E" if self.scores["E"] > self.scores["I"] else "I"
        
        # S vs N
        result += "S" if self.scores["S"] > self.scores["N"] else "N"
        
        # T vs F
        result += "T" if self.scores["T"] > self.scores["F"] else "F"
        
        # J vs P
        result += "J" if self.scores["J"] > self.scores["P"] else "P"
        
        self.mbti_result = result
    
    def _generate_result_message(self):
        """Generate a detailed result message with explanation."""
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
        
        # Dimension explanation
        dimensions = {
            "E": "Extraversion: You gain energy from interacting with others and the external world.",
            "I": "Introversion: You gain energy from internal reflection and solitude.",
            "S": "Sensing: You focus on concrete facts and present realities.",
            "N": "Intuition: You focus on patterns, possibilities, and future potential.",
            "T": "Thinking: You make decisions based on logic and objective analysis.",
            "F": "Feeling: You make decisions based on values and how they affect people.",
            "J": "Judging: You prefer structure, planning, and resolving matters definitively.",
            "P": "Perceiving: You prefer flexibility, spontaneity, and keeping options open."
        }
        
        # Build the result message
        message = f"🎉 Your MBTI personality type is: {self.mbti_result}\n\n"
        message += f"**{self.mbti_result}: {mbti_descriptions.get(self.mbti_result, '')}**\n\n"
        
        message += "**Your Preferences:**\n"
        for letter in self.mbti_result:
            message += f"- {dimensions.get(letter, '')}\n"
        
        message += "\n**Dimension Scores:**\n"
        message += f"- Extraversion (E): {self.scores['E']} vs Introversion (I): {self.scores['I']}\n"
        message += f"- Sensing (S): {self.scores['S']} vs Intuition (N): {self.scores['N']}\n"
        message += f"- Thinking (T): {self.scores['T']} vs Feeling (F): {self.scores['F']}\n"
        message += f"- Judging (J): {self.scores['J']} vs Perceiving (P): {self.scores['P']}\n\n"
        
        message += "Remember that personality types are not definitive labels, but tools for understanding yourself better. Your preferences may change over time or in different contexts."
        
        return message 