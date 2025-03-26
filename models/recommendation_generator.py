from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

class RecommendationGenerator:
    def __init__(self):
        """Initialize the recommendation generator with LLM components."""
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
        )
        
        self.recommendation_template = """
        Based on the MBTI personality type {mbti_type}, provide personalized recommendations in the following categories:

        1. Music:
        Consider the person's {traits} traits. Suggest specific:
        - Music genres that would resonate with them
        - Artists they might enjoy
        - Specific songs they should try
        
        2. Books:
        Given their personality preferences, recommend:
        - Fiction books that match their interests
        - Non-fiction books that could benefit them
        - Literary genres they might enjoy
        
        3. Movies:
        Based on their personality type, suggest:
        - Movie genres that would appeal to them
        - Specific films they should watch
        - TV shows they might enjoy

        Format each recommendation with a brief explanation of why it suits their personality type.
        Keep the tone conversational and engaging.
        """
        
        self.prompt = PromptTemplate(
            input_variables=["mbti_type", "traits"],
            template=self.recommendation_template
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
        # MBTI type traits mapping
        self.mbti_traits = {
            "ISTJ": "practical, detail-oriented, and traditional",
            "ISFJ": "nurturing, detail-focused, and service-oriented",
            "INFJ": "insightful, creative, and idealistic",
            "INTJ": "analytical, strategic, and independent",
            "ISTP": "logical, practical, and adaptable",
            "ISFP": "artistic, sensitive, and spontaneous",
            "INFP": "idealistic, empathetic, and creative",
            "INTP": "logical, innovative, and analytical",
            "ESTP": "energetic, practical, and spontaneous",
            "ESFP": "enthusiastic, spontaneous, and fun-loving",
            "ENFP": "enthusiastic, creative, and people-oriented",
            "ENTP": "innovative, entrepreneurial, and adaptable",
            "ESTJ": "organized, practical, and traditional",
            "ESFJ": "warm, practical, and people-oriented",
            "ENFJ": "charismatic, idealistic, and people-focused",
            "ENTJ": "strategic, logical, and efficient"
        }
    
    def generate_recommendations(self, mbti_type):
        """Generate personalized recommendations based on MBTI type."""
        if mbti_type not in self.mbti_traits:
            raise ValueError(f"Invalid MBTI type: {mbti_type}")
            
        traits = self.mbti_traits[mbti_type]
        
        # Generate recommendations using LLM
        result = self.chain.run(mbti_type=mbti_type, traits=traits)
        
        return result 