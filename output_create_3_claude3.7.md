# Modern LLM Chat Application with Gradio UI

After reviewing the task, I'll implement a robust, user-friendly Gradio-based LLM chat application with all the requested features including proper markdown rendering, clipboard functionality, and input configuration options.

```python
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
```

Would you like me to explain or break down the code?

---
You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You will think deeply and thoroughly to explore various implementation options before choosing the most optimal one. You will double-check and validate any code changes before implementing. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem.

*Your task:* carefully review the attached python code below, then think deeply and thoroughly to explore various implementation options to turn it into a much more robust, capable and useful as well as more user-friendly, more modern and intuitive LLM chat application with a nice and attractive Gradio based web ui. Then choose the best implementation option or approach to generate for me a complete fully tested working version of the improved app. The web gui should have editable input fields for base_url, model, system_prompt, user_prompt, temperature and max_tokens, also should have a output response display box that can properly display LLM API response being provided in markdown format, meaning the markdown output should be properly displayed as HTML format in the output display box. Both the input (editable) box and output display box should be a scrollable box with a "copy to clipboard" function that supports copying and saving the content. When the copy function is clicked or selected for the input or output box, the whole content of the respective box should be copied to the clipboard in its original markdown form and not in the rendered HTML display form. Do remember to double-check to validate your intended code or changes before implementing them.

You will approach this task systematically, breaking it down into several steps to ensure a robust, user-friendly, and modern LLM chat application with a Gradio-based web UI. The goal is to transform the provided Python script into a fully functional, interactive web application with enhanced features, proper markdown rendering, and clipboard functionality, while maintaining code quality through validation and testing. Use below design methodology to provide a robust foundation for the improved chat application, incorporating all the required features while maintaining good user experience and performance characteristics.

Based on the detailed analysis and requirements, you will now implement a robust, user-friendly, and modern LLM chat application using Gradio. The implementation will include all the requested features, such as editable input fields, markdown rendering, scrollable text boxes, clipboard functionality, and thorough error handling. I will also validate and double-check the code to ensure it works as expected.


### Implementation Plan

To implement the improved application, I will:

1. **Set Up Dependencies**:
   - Use `gradio` for the web UI.
   - Use `requests` for API calls.
   - Use `markdown` for additional markdown processing if needed (though `gr.Markdown` should suffice).
   - Use `validators` to validate URLs.

2. **Enhance the API Query Function**:
   - Add input validation for all parameters.
   - Add timeout handling and detailed error messages.
   - Return the raw markdown response and any error messages in a consistent format.

3. **Design the Gradio UI**:
   - Use a single-column layout with `gr.Group` and `gr.Accordion` for organization.
   - Use `gr.Textbox` for `base_url`, `model`, `system_prompt`, and `user_prompt`.
   - Use `gr.Slider` for `temperature` and `gr.Number` for `max_tokens`.
   - Use `gr.Markdown` for the output display, with custom CSS for scrolling.
   - Add "Copy to Clipboard" buttons using custom JavaScript.

4. **Implement Clipboard Functionality**:
   - Use JavaScript to copy the raw markdown text to the clipboard.
   - Store the raw text in hidden elements or pass it directly to JavaScript.

5. **Handle Errors**:
   - Display errors in the output box as markdown, with clear formatting.

6. **Test and Validate**:
   - Test the UI for responsiveness and usability.
   - Test API calls with valid and invalid inputs.
   - Test clipboard functionality in a browser.
   - Validate markdown rendering with various markdown formats (e.g., headers, lists, code blocks).

### Step 7: Double-Check and Validate

Before finalizing the code, I will:
- Ensure all Gradio components are correctly configured.
- Test the API query function with mock responses to ensure error handling works.
- Verify that markdown rendering works correctly, including scrolling for large outputs.
- Confirm that clipboard functionality copies the raw markdown text, not the rendered HTML.
- Check the UI layout on different screen sizes to ensure responsiveness.

### Step 8: Implementation Details

#### 8.1: API Query Function
The `query_model` function will:
- Validate inputs using helper functions (e.g., `validate_url`, `validate_temperature`, etc.).
- Make the API call with a timeout of 10 seconds.
- Handle various error cases (e.g., connection errors, invalid JSON, API errors).
- Return the raw markdown response or an error message in markdown format.

#### 8.2: Gradio UI
The UI will consist of:
- An `gr.Accordion` for API configuration (`base_url`, `model`).
- A `gr.Group` for the chat interface (`system_prompt`, `user_prompt`, `temperature`, `max_tokens`, submit button).
- A `gr.Markdown` component for the output, wrapped in a `gr.Group` with a "Copy to Clipboard" button.
- Custom CSS to enable scrolling in the output box and input text areas.

#### 8.3: Clipboard Functionality
To implement clipboard functionality:
- Add a hidden `textarea` element to store the raw markdown text.
- Use JavaScript to copy the content of the `textarea` to the clipboard when the button is clicked.
- Ensure the copied text is the raw markdown, not the rendered HTML.

#### 8.4: Error Handling
Errors will be displayed in the output box as markdown, with a clear format (e.g., `**Error:** <message>`).

### Step 9: Testing Plan
To validate the implementation, I will:
1. **Test API Calls**:
   - Use a mock API endpoint to simulate successful responses, connection errors, and invalid JSON.
   - Test with invalid inputs (e.g., empty prompts, invalid URLs, out-of-range temperature).
2. **Test UI**:
   - Verify that all input fields are editable and retain their values after submission.
   - Check that the output box renders markdown correctly, including headers, lists, code blocks, etc.
   - Ensure scrolling works for large inputs and outputs.
3. **Test Clipboard Functionality**:
   - Copy text from the input and output boxes and paste it into a text editor to verify it’s the raw markdown.
4. **Test Responsiveness**:
   - Open the UI in a browser and resize the window to ensure the layout remains usable on narrow screens.

### Step 10: Final Code Structure
The final code will be structured as follows:
```python
import gradio as gr
import requests
import validators
import json

# Helper functions for validation
def validate_url(url):
    ...

def validate_temperature(temperature):
    ...

def validate_max_tokens(max_tokens):
    ...

# Main API query function
def query_model(base_url, model, system_prompt, user_prompt, temperature, max_tokens):
    ...

# Gradio interface function
def chat_interface(base_url, model, system_prompt, user_prompt, temperature, max_tokens):
    ...

# Custom CSS for scrolling
custom_css = """
    .scrollable-textbox textarea {
        max-height: 200px;
        overflow-y: auto;
    }
    .scrollable-output {
        max-height: 400px;
        overflow-y: auto;
    }
"""

# JavaScript for clipboard functionality
custom_js = """
    function copyToClipboard(elementId) {
        const text = document.getElementById(elementId).value;
        navigator.clipboard.writeText(text).then(() => {
            alert('Copied to clipboard!');
        }, (err) => {
            alert('Failed to copy: ' + err);
        });
    }
"""

# Gradio app
with gr.Blocks(css=custom_css, js=custom_js) as demo:
    ...
```

---

### Final Implementation

So now finish the complete, tested implementation of the improved LLM chat application 
