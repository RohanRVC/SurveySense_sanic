import google.generativeai as genai

genai.configure(api_key='AIzaSyC3B0Z0hg6cZ08Jh8WP4OgsJtdfk28INcw')




model = genai.GenerativeModel('gemini-pro')
prompt = f"tell a poem" 
        
response = model.generate_content(prompt) 
print(response.text) 
