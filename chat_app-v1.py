# Modern LLM Chat Application with Gradio UI
import gradio as gr
import requests
import validators
import json
import time
from typing import Dict, Any, Tuple, Optional

def validate_url(url: str) -> Tuple[bool, str]:
    """Validate a URL."""
    if not url:
        return False, "URL cannot be empty."
    if not validators.url(url):
        return False, "Invalid URL format."
    return True, ""

def validate_temperature(temperature: float) -> Tuple[bool, str]:
    """Validate the temperature parameter."""
    if temperature < 0:
        return False, "Temperature must be >= 0."
    if temperature > 2:
        return False, "Temperature must be <= 2."
    return True, ""

def validate_max_tokens(max_tokens: int) -> Tuple[bool, str]:
    """Validate the max_tokens parameter."""
    if max_tokens < 1:
        return False, "Max tokens must be >= 1."
    if max_tokens > 32000:  # Using a sensible upper limit
        return False, "Max tokens must be <= 32000."
    return True, ""

def query_model(base_url: str, model: str, system_prompt: str, user_prompt: str, 
               temperature: float = 0.7, max_tokens: int = 2000) -> Tuple[bool, str]:
    """
    Query an LLM model via API with error handling.
    
    Returns:
        Tuple[bool, str]: (success, response_text)
            - success: Whether the query was successful
            - response_text: The response or error message
    """
    # Validate base_url
    is_valid, message = validate_url(base_url)
    if not is_valid:
        return False, f"Error with base_url: {message}"
    
    # Validate model
    if not model.strip():
        return False, "Error: Model name cannot be empty."
    
    # Validate prompts
    if not user_prompt.strip():
        return False, "Error: User prompt cannot be empty."
    
    # Validate temperature
    is_valid, message = validate_temperature(temperature)
    if not is_valid:
        return False, f"Error with temperature: {message}"
    
    # Validate max_tokens
    is_valid, message = validate_max_tokens(max_tokens)
    if not is_valid:
        return False, f"Error with max_tokens: {message}"
    
    # Prepare the request
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        # Make the API request with a timeout
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the JSON response
        result = response.json()
        
        # Extract the content from the response
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                content = result["choices"][0]["message"]["content"]
                return True, content
            else:
                error_msg = "Unexpected API response format. Could not find 'message.content' in the response."
                return False, error_msg
        else:
            error_msg = "Unexpected API response format. Could not find 'choices' in the response."
            return False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. The server took too long to respond."
        return False, error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "Connection error. Could not connect to the server."
        return False, error_msg
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error occurred: {str(e)}"
        return False, error_msg
    except json.JSONDecodeError:
        error_msg = "Could not parse the API response as JSON."
        return False, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        return False, error_msg

def process_chat(base_url: str, model: str, system_prompt: str, user_prompt: str, 
                temperature: float, max_tokens: int) -> Tuple[str, str, str]:
    """
    Process the chat inputs and return the results.
    
    Returns:
        Tuple[str, str, str]: (response_markdown, input_text, output_text)
    """
    # Format input for clipboard
    input_text = f"""Base URL: {base_url}
Model: {model}
Temperature: {temperature}
Max Tokens: {max_tokens}

System Prompt:
{system_prompt}

User Prompt:
{user_prompt}"""
    
    # Query the model
    success, response_text = query_model(
        base_url, model, system_prompt, user_prompt, temperature, max_tokens
    )
    
    if not success:
        # Return the error message formatted as markdown
        error_markdown = f"""## Error

{response_text}"""
        return error_markdown, input_text, error_markdown
    
    # Return the response text (already in markdown format)
    return response_text, input_text, response_text

# JavaScript for clipboard functionality
js_code = """
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Return a message to indicate success
    return "Copied to clipboard!";
}
"""

# CSS for styling
css = """
.container {
    max-width: 950px;
    margin: auto;
}
.scroll-box {
    max-height: 300px;
    overflow-y: auto !important;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
}
.output-container {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    max-height: 500px;
    overflow-y: auto !important;
}
.input-box {
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #ffffff;
    padding: 10px;
}
.copy-btn {
    margin-top: 10px;
}
pre {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
}
code {
    font-family: monospace;
    background-color: #f0f0f0;
    padding: 2px 4px;
    border-radius: 3px;
}
"""

# Create the Gradio interface
with gr.Blocks(css=css, js=js_code, title="LLM Chat Application") as demo:
    gr.HTML("""
    <div class="container">
        <h1 style="text-align: center; margin-bottom: 20px;">Modern LLM Chat Application</h1>
    </div>
    """)
    
    # Hidden components for clipboard content
    input_clipboard = gr.State("")
    output_clipboard = gr.State("")
    clipboard_status = gr.State("")
    
    with gr.Group(elem_classes=["container"]):
        with gr.Accordion("API Configuration", open=True):
            with gr.Row():
                base_url = gr.Textbox(
                    label="Base URL",
                    placeholder="https://api.openai.com/v1/chat/completions",
                    value="https://api.openai.com/v1/chat/completions",
                    elem_classes=["input-box"]
                )
                model = gr.Textbox(
                    label="Model",
                    placeholder="gpt-3.5-turbo",
                    value="gpt-3.5-turbo",
                    elem_classes=["input-box"]
                )
        
        with gr.Group():
            system_prompt = gr.Textbox(
                label="System Prompt",
                placeholder="You are a helpful assistant.",
                value="You are a helpful assistant.",
                lines=3,
                elem_classes=["scroll-box", "input-box"]
            )
            
            user_prompt = gr.Textbox(
                label="User Prompt",
                placeholder="Enter your message here...",
                lines=5,
                elem_classes=["scroll-box", "input-box"]
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    temperature = gr.Slider(
                        label="Temperature",
                        minimum=0.0,
                        maximum=2.0,
                        step=0.1,
                        value=0.7
                    )
                
                with gr.Column(scale=1):
                    max_tokens = gr.Number(
                        label="Max Tokens",
                        value=2000,
                        precision=0
                    )
            
            submit_btn = gr.Button("Submit", variant="primary")
    
        # Output display and copy functionality
        gr.HTML('<div class="container"><h3>Response:</h3></div>')
        output = gr.Markdown(elem_classes=["output-container"])
        
        with gr.Row():
            copy_input_btn = gr.Button("Copy Input to Clipboard", elem_classes=["copy-btn"])
            copy_output_btn = gr.Button("Copy Output to Clipboard", elem_classes=["copy-btn"])
            status_display = gr.Textbox(label="", elem_classes=["copy-status"], visible=True)
    
    # Event handlers
    submit_result = submit_btn.click(
        fn=process_chat,
        inputs=[base_url, model, system_prompt, user_prompt, temperature, max_tokens],
        outputs=[output, input_clipboard, output_clipboard]
    )
    
    # Copy input to clipboard
    def copy_text(text):
        return f"Copied to clipboard successfully!"
    
    copy_input_btn.click(
        fn=copy_text,
        inputs=[input_clipboard],
        outputs=[status_display],
        js="(text) => { copyToClipboard(text); return 'Input copied to clipboard!'; }"
    )
    
    copy_output_btn.click(
        fn=copy_text,
        inputs=[output_clipboard],
        outputs=[status_display],
        js="(text) => { copyToClipboard(text); return 'Output copied to clipboard!'; }"
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
