import google.generativeai as genai 


class Gemini_model:
    def __init__(self , api_key):
        self.api_key = api_key


    def gemini_model_response(self , prompt):
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        result = response.text
        return result 
    

    
    
