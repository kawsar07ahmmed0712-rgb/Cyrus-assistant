from config import settings
from core import gemini_engine,promt_controller,memory

api_key = settings.Settings().api_key 
gemini_model = gemini_engine.Gemini_model(api_key)


user_input = input("selct (tutor/coding_assistant/career_helper/interviewer/language_teacher/math_tutor)")
prompt = input("enter prompt")

pb = promt_controller.PromptBuilder(topic=prompt)

def main():
    if user_input == "tutor":
        pb.build("tutor")
    elif user_input == "coding_assistant":
        pb.build("coding_assistant")
    elif user_input == "career_helper":
        pb.build("career_helper")
    elif user_input == "interviewer":
        pb.build("interviewer")
    elif user_input == "language_teacher":
        pb.build("language_teacher")
    elif user_input == "math_tutor":
        pb.build("math_tutor")
    else:
        print("invalid input")
        
    
    result = gemini_model.gemini_model_response(prompt)
    print(result)

    memory.memory(prompt,result)

if __name__ == "__main__":
    main()

