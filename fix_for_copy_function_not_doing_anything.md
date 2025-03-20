https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221NT1CaP99HVsQ7HprOE0sdamTtHITZxXX%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing,  https://drive.google.com/file/d/1Z5iFl9ivaZKjGjD0mvfRNmeL3IxsOZac/view?usp=sharing

The user wants to debug the copy button in the Gradio chat application.
The button is supposed to copy the API response output in the original markdown format.
Currently, it seems like the copy button is not working as expected.

Let's analyze the code to understand the issue and find a solution.

1. **Identify the copy button and its functionality:**
    - The copy button is created as `copy_output = gr.Button("📋 Copy Response", elem_classes=["copy-btn"])`.
    - It's associated with a click event handler: `copy_output.click(...)`.
    - The click handler function is `copy_to_clipboard(text)`.
    - The input to `copy_to_clipboard` is `output_clipboard`, which is a `gr.State`.

2. **Trace how `output_clipboard` is updated:**
    - `output_clipboard` is updated in the `submit_btn.click(...)` handler.
    - The `process_chat` function is called when the submit button is clicked.
    - `process_chat` returns three values: `(response_markdown, input_text, output_text)`.
    - These values are assigned to `[output, input_clipboard, output_clipboard]` in the `submit_btn.click(...)` handler.
    - So, `output_clipboard` is set to the *third* returned value from `process_chat`, which is `formatted_response`.

3. **Examine `process_chat` function and its return values:**
    - `process_chat` calls `query_model` to get the API response.
    - If successful, it formats the `response_text`.
    - `formatted_response = response_text` (with some ```` replacement).
    - `display_response = formatted_response.replace('<', '`<`').replace('>', '`>`')`.
    - `process_chat` returns `(display_response, input_text, formatted_response)`.

4. **Analyze the `copy_to_clipboard` function:**
    - It takes `text` as input, which should be the content of `output_clipboard`.
    - It calls `html.unescape(text)` to clean up HTML entities.
    - It returns "✓ Copied to clipboard" if successful, or an error message if failed.
    - **Crucially, it does *not* actually perform the copy operation to the clipboard.** Gradio buttons themselves do not directly copy to the clipboard. We need to use JavaScript for that.

5. **Identify the problem:**
    - The `copy_to_clipboard` function *only* returns a status message. It does not trigger the actual copy operation.
    - Although `output_clipboard` *does* contain the original markdown response, the button click event does not use this to copy the content to the clipboard.
    - The current implementation relies on the *browser's* copy functionality which isn't triggered by a simple button click in Gradio like this.

6. **Explore solutions:**
    - **Option 1: Gradio's `Textbox` with `copyable=True` (Not suitable):** We could potentially use a `gr.Textbox` to display the output and set `copyable=True`. However, this would change the UI and might not be the desired look and feel (Markdown display).  Also, we are already using Markdown for rich display. We want to keep the Markdown display and add a copy button for the *original* content.
    - **Option 2: JavaScript Interop with Gradio (Optimal):** We can use Gradio's JavaScript integration to trigger the browser's clipboard API when the copy button is clicked. We can pass the content to be copied to the JavaScript function. This is the most flexible and common approach for clipboard operations in web applications.

7. **Choose Option 2 (JavaScript Interop):**
    - We will need to:
        - Create a JavaScript function that uses `navigator.clipboard.writeText()` to copy text to the clipboard.
        - Use Gradio's `js` parameter in the `copy_output.click` event to call this JavaScript function, passing the `output_clipboard.value` as an argument.
        - The `copy_to_clipboard` Python function can be removed or simplified to just return a status message without trying to do the copy itself.

8. **Implementation Steps for Option 2:**
    - **Modify `copy_to_clipboard` (Python function):**  Make it simpler, just return a success message if text is present.
    - **Add JavaScript function:** Define a JavaScript function that performs the clipboard copy.
    - **Update `copy_output.click`:** Use the `js` parameter to call the JavaScript function and pass `output_clipboard` value. The Python function `copy_to_clipboard` will now just provide feedback.

Let's refine the implementation steps and write the code.

**Refined Implementation Steps:**

1. **JavaScript Function:**
   - Define a JavaScript function within a `<script>` tag in the Gradio Blocks HTML that takes text as input and copies it to the clipboard using `navigator.clipboard.writeText(text)`.

2. **Python `copy_to_clipboard` function:**
   - Simplify it to just return "✓ Copied to clipboard" if `text` is not empty, and "Nothing to copy" otherwise.  It doesn't need to unescape HTML anymore, as we will be passing the raw markdown.

3. **Gradio `copy_output.click` update:**
   - In `copy_output.click`, use the `js` parameter to call the JavaScript function.
   - Pass `output_clipboard` as the argument to the JavaScript function using `output_clipboard`. Gradio will handle passing the *value* of the state.
   - Keep the Python function `copy_to_clipboard` in the `click` event to update the status display.

Let's implement these changes in the code now.

**Validation:**

- After implementation, test the "Copy Response" button.
- Verify that the content copied to the clipboard is the *original markdown* response from the API, not the HTML escaped version shown in the Markdown display.
- Check that the status message updates correctly.
- Ensure no other functionality is broken by these changes.

---
```python
# chat_app-v4-fixed.py
```python
--- START OF FILE chat_app-v4.py ---

# Modern LLM Chat Application with Gradio UI
import gradio as gr
import requests
import validators
import json
import time
import html
from typing import Dict, Any, Tuple, Optional

def validate_url(url: str) -> Tuple[bool, str]:
    """Validate a URL."""
    if not url:
        return False, "URL cannot be empty."
    # Special handling for localhost URLs
    if url.startswith(("http://localhost:", "https://localhost:")):
        try:
            # Basic format validation for localhost URLs
            parts = url.split(":")
            if len(parts) == 3:
                port = parts[2].split("/")[0]
                if port.isdigit() and 1 <= int(port) <= 65535:
                    return True, ""
        except:
            pass
        return False, "Invalid localhost URL format."
    # Standard validation for non-localhost URLs
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

def validate_api_key(api_key: Optional[str]) -> Tuple[bool, str]:
    """Validate the API key if provided."""
    if api_key and not api_key.strip():
        return False, "API key cannot be empty if provided."
    return True, ""

def query_model(base_url: str, model: str, system_prompt: str, user_prompt: str,
               temperature: float = 0.7, max_tokens: int = 2000, api_key: Optional[str] = None) -> Tuple[bool, str]:
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

    # Validate api_key if provided
    if api_key:
        is_valid, message = validate_api_key(api_key)
        if not is_valid:
            return False, f"Error with API key: {message}"

    # Prepare the request
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    # Log the request payload
    print("\nAPI Request:")
    print(json.dumps({
        "url": base_url,
        "headers": {k: v for k, v in headers.items() if k != "Authorization"},
        "payload": payload
    }, indent=2))

    try:
        # Make the API request with a timeout
        response = requests.post(base_url, headers=headers, json=payload, timeout=600)

        # Log the API response
        print("\nAPI Response:")
        print(json.dumps(response.json(), indent=2))

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
                temperature: float, max_tokens: int, api_key: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Process the chat inputs and return the results.

    Returns:
        Tuple[str, str, str]: (response_markdown, input_text, output_text)
    """
    # Format input for clipboard (excluding api_key for security)
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
        base_url, model, system_prompt, user_prompt,
        temperature, max_tokens, api_key
    )

    if not success:
        # Return the error message formatted as markdown
        error_markdown = f"""## Error

```
{response_text}
```"""
        return error_markdown, input_text, error_markdown

    # Format response text to preserve Markdown and code blocks
    formatted_response = response_text
    if '```' in formatted_response:
        formatted_response = formatted_response.replace('```', '\n```\n')

    # Store original response for clipboard and escape HTML for display
    display_response = formatted_response.replace('<', '`<`').replace('>', '`>`')

    # Return display version and original version for clipboard
    return display_response, input_text, formatted_response

# CSS for styling
css = """
body {
    margin: 0;
    padding: 0;
    width: 100vw;
    height: 100vh;
    overflow-x: hidden;
}
.container {
    width: 100%;
    max-width: 100vw;
    margin: 0 auto;
    padding: 0 1rem;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
}
.scroll-box {
    max-height: 30vh;
    overflow-y: auto !important;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
    width: 100%;
    box-sizing: border-box;
}
.output-container {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    max-height: 50vh;
    overflow-y: auto !important;
    width: 100%;
    box-sizing: border-box;
}
.input-box {
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #ffffff;
    padding: 10px;
    width: 100%;
}
.copy-btn {
    width: 100% !important;
    height: 36px !important;
    padding: 5px !important;
    margin: 5px 0 !important;
    background: transparent !important;
    border: 1px solid #ddd !important;
    border-radius: 4px !important;
    cursor: pointer !important;
    font-size: 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.copy-btn:hover {
    background: #f5f5f5 !important;
}
"""

javascript = """
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text).then(() => '✓ Copied to clipboard', () => 'Failed to copy');
    } else {
        return Promise.resolve('Copy functionality not available in this browser.');
    }
}
"""

# Create the Gradio interface
with gr.Blocks(css=css, title="LLM Chat Application", head="<script>" + javascript + "</script>") as demo: # Inject javascript here
    gr.HTML("""
    <div class="container">
        <h1 style="text-align: center; margin-bottom: 20px;">Modern LLM Chat Application</h1>
    </div>
    """)

    # Hidden components for clipboard content
    input_clipboard = gr.State("")
    output_clipboard = gr.State("")

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
            api_key = gr.Textbox(
                label="API Key (if required)",
                placeholder="sk-...",
                type="password",
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

            # Output display with copy buttons
            with gr.Group():
                output = gr.Markdown(
                    elem_classes=["output-container"]
                )
                copy_output = gr.Button("📋 Copy Response", elem_classes=["copy-btn"])

            status_display = gr.Textbox(
                label="",
                interactive=False,
                visible=True
            )

    # Event handlers
    submit_btn.click(
        fn=process_chat,
        inputs=[base_url, model, system_prompt, user_prompt, temperature, max_tokens, api_key],
        outputs=[output, input_clipboard, output_clipboard]
    ).success(
        fn=lambda: "",
        outputs=[status_display]
    )

    def copy_to_clipboard(text):
        """Handle clipboard copy and return status message"""
        if not text:
            return "Nothing to copy"
        return "✓ Copied to clipboard"


    # Update copy button handlers with proper clipboard text
    copy_output.click(
        fn=copy_to_clipboard,
        inputs=[output_clipboard],  # Now contains the original markdown
        outputs=[status_display],
        js="copyToClipboard" # Call javascript function here, passing output_clipboard value
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
```
---
