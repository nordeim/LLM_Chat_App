You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You will think deeply and thoroughly to explore various implementation options before choosing the most optimal one. You will double-check and validate any code changes before implementing. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem.

*Your task:* carefully review the attached python code below, then think deeply and thoroughly to explore various implementation options to turn it into a much more robust, capable and useful as well as more user-friendly, more modern and intuitive LLM chat application with a nice and attractive Gradio based web ui. Then choose the best implementation option or approach to generate for me a complete fully tested working version of the improved app. The web gui should have editable input fields for base_url, model, system_prompt, user_prompt, temperature and max_tokens, also should have a output response display box that can properly display LLM API response being provided in markdown format, meaning the markdown output should be properly displayed as HTML format in the output display box. Both the input (editable) box and output display box should be a scrollable box with a "copy to clipboard" function that supports copying and saving the content. When the copy function is clicked or selected for the input or output box, the whole content of the respective box should be copied to the clipboard in its original markdown form and not in the rendered HTML display form. Do remember to double-check to validate your intended code or changes before implementing them.

```python
import requests
import json
from datetime import datetime

def query_model(prompt, system_prompt=None, temperature=0.15):
    """
    Query the deployed Mistral model.
    
    Args:
        prompt (str): The user prompt to send to the model
        system_prompt (str, optional): System prompt to guide model behavior
        temperature (float, optional): Sampling temperature (default: 0.15)
        
    Returns:
        dict: The model's response
    """
    # Current date for system prompt
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Default system prompt if none provided
    if system_prompt is None:
        system_prompt = f"""You are Mistral Small 3.1, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.
You power an AI assistant called Le Chat.
Your knowledge base was last updated on 2023-10-01.
The current date is {today}.

When you're not sure about some information, you say that you don't have the information and don't make up anything.
If the user's question is not clear, ambiguous, or does not provide enough context for you to accurately answer the question, you do not try to answer it right away and you rather ask the user to clarify their request (e.g. "What are some good restaurants around me?" => "Where are you?" or "When is the next flight to Tokyo" => "Where do you travel from?").
You are always very attentive to dates, in particular you try to resolve dates (e.g. "yesterday" is {yesterday}) and when asked about information at specific dates, you discard information that is at another date. 
You follow these instructions in all languages, and always respond to the user in the language they use or request.
Next sections describe the capabilities that you have.

# WEB BROWSING INSTRUCTIONS

You cannot perform any web search or access internet to open URLs, links etc. If it seems like the user is expecting you to do so, you clarify the situation and ask the user to copy paste the text directly in the chat.

# MULTI-MODAL INSTRUCTIONS

You have the ability to read images, but you cannot generate images. You also cannot transcribe audio files or videos.
You cannot read nor transcribe audio files or videos."""
    
    # API endpoint (adjust if your server is on a different host/port)
    url = "http://localhost:8000/v1/chat/completions"
    
    # Prepare the request payload
    payload = {
        "model": "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    
    # Send the request to the server
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Return the processed response
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status {response.status_code}", "details": response.text}

# Example usage
if __name__ == "__main__":
    user_prompt = "Explain how large language models work"
    response = query_model(user_prompt)
    
    # Extract and print the model's response
    try:
        model_response = response["choices"][0]["message"]["content"]
        print("Model response:")
        print(model_response)
    except KeyError:
        print("Unexpected response format:", response)
        
---
