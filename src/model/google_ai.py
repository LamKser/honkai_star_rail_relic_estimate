from openai import OpenAI


class GoogleAI:
    def __init__(self, api_key, url):
        self.client = OpenAI(
            api_key = api_key,
            base_url = url
        )
        

    def generate(self, prompt_system, prompt_user, model_name):
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": prompt_system
                },
                {
                    "role": "user",
                    "content": prompt_user
                }
            ],
            model = model_name
        )
        return response
