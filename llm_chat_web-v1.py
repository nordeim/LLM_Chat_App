# A modern Gradio-based LLM chat application with all the requested features. Transform a simple API querying script into a fully-featured web application.
import gradio as gr
import requests
import json
import time

def query_llm(base_url, model, system_prompt, user_prompt, temperature=0.7, max_tokens=2048):
    """
    Query the LLM API with the given parameters.
    
    Args:
        base_url (str): The base URL of the API endpoint
        model (str): The model name to use
        system_prompt (str): The system prompt
        user_prompt (str): The user prompt
        temperature (float): The temperature parameter (0.0-1.0)
        max_tokens (int): Maximum number of tokens to generate
        
    Returns:
        str: The API response content or error message
    """
    try:
        # Input validation
        if not base_url:
            return "**Error:** API endpoint URL cannot be empty."
        if not model:
            return "**Error:** Model name cannot be empty."
        
        # Validate temperature range
        try:
            temperature = float(temperature)
            if not 0.0 <= temperature <= 1.0:
                return "**Error:** Temperature must be between 0.0 and 1.0."
        except ValueError:
            return "**Error:** Temperature must be a valid number between 0.0 and 1.0."
        
        # Validate max_tokens
        try:
            max_tokens = int(max_tokens)
            if max_tokens < 1:
                return "**Error:** Max tokens must be at least 1."
        except ValueError:
            return "**Error:** Max tokens must be a valid integer."
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            base_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30  # Add timeout for robustness
        )
        
        response.raise_for_status()  # Raise exception for bad status codes
        result = response.json()
        
        # Extract the assistant's message from the response
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0]:
                return result["choices"][0]["message"]["content"]
            else:
                return "**Error:** Unexpected API response format. Missing 'message' field."
        else:
            return "**Error:** Unexpected API response format. Missing 'choices' field."
    
    except requests.exceptions.RequestException as e:
        return f"**Error:** API request failed: {str(e)}"
    except json.JSONDecodeError:
        return "**Error:** Failed to parse API response as JSON."
    except Exception as e:
        return f"**Error:** An unexpected error occurred: {str(e)}"

def create_llm_chat_app():
    """
    Creates a Gradio-based web UI for the LLM chat application.
    """
    # Default values
    DEFAULT_SYSTEM_PROMPT = "You are a helpful, knowledgeable, and precise assistant. Provide accurate, factual, and concise responses."
    DEFAULT_USER_PROMPT = "Hello! Can you help me with a question?"
    
    # Create Gradio interface
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        # Custom CSS for styling
        gr.HTML("""
        <style>
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .output-box { height: 500px; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px; padding: 15px; background-color: #f9f9f9; }
            .input-box { border: 1px solid #ddd; border-radius: 8px; }
            .feedback { color: green; font-size: 0.8em; margin-left: 10px; }
            .copy-btn { margin-top: 5px; }
            
            /* Custom code block styling in markdown output */
            .output-box pre { background-color: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .output-box code { font-family: 'Courier New', monospace; }
            
            /* Add some spacing between elements */
            .gradio-container .prose { margin-bottom: 1rem; }
            
            /* Make the interface more modern */
            .gradio-container button.primary { background-color: #4f46e5; }
            .gradio-container button.secondary { background-color: #e5e7eb; color: #111827; }
        </style>
        
        <script>
        // Function to copy text to clipboard
        function copyTextToClipboard(text) {
            // Create a temporary textarea element
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.setAttribute('readonly', '');
            textarea.style.position = 'absolute';
            textarea.style.left = '-9999px';
            document.body.appendChild(textarea);
            
            // Select and copy the text
            textarea.select();
            document.execCommand('copy');
            
            // Clean up
            document.body.removeChild(textarea);
            
            // Return a message for user feedback
            return "Copied!";
        }
        </script>
        """)
        
        # Header
        gr.HTML("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="margin-bottom: 5px;">LLM Chat Application</h1>
            <p>Interact with AI models through a user-friendly interface</p>
        </div>
        """)
        
        # API Configuration section
        with gr.Accordion("API Configuration", open=True):
            with gr.Row():
                base_url = gr.Textbox(
                    label="API Endpoint",
                    value="http://localhost:8000/v1/chat/completions",
                    placeholder="Enter the API endpoint URL",
                    lines=1
                )
                model = gr.Textbox(
                    label="Model Name",
                    value="mistralai/Mistral-Small-3.1-24B-Instruct-2503",
                    placeholder="Enter the model name",
                    lines=1
                )
            
            with gr.Row():
                temperature = gr.Slider(
                    label="Temperature",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.01,
                    info="Controls creativity (0 = deterministic, 1 = more random)"
                )
                max_tokens = gr.Number(
                    label="Max Tokens",
                    value=2048,
                    minimum=1,
                    maximum=4096,
                    step=1,
                    info="Maximum response length"
                )
        
        # Prompt inputs
        with gr.Group():
            # System Prompt
            gr.HTML("<h3>System Prompt</h3>")
            system_prompt = gr.Textbox(
                value=DEFAULT_SYSTEM_PROMPT,
                placeholder="Instructions for the AI...",
                lines=5,
                max_lines=15,
                elem_classes=["input-box"],
                show_label=False
            )
            
            # System prompt copy functionality
            with gr.Row():
                system_copy_btn = gr.Button("Copy System Prompt", elem_classes=["copy-btn"], variant="secondary", size="sm")
                system_copy_feedback = gr.Textbox(
                    value="", 
                    elem_classes=["feedback"], 
                    show_label=False,
                    interactive=False
                )
            
            # User Prompt
            gr.HTML("<h3>User Prompt</h3>")
            user_prompt = gr.Textbox(
                value=DEFAULT_USER_PROMPT,
                placeholder="Your message to the AI...",
                lines=5,
                max_lines=15,
                elem_classes=["input-box"],
                show_label=False
            )
            
            # User prompt copy functionality
            with gr.Row():
                user_copy_btn = gr.Button("Copy User Prompt", elem_classes=["copy-btn"], variant="secondary", size="sm")
                user_copy_feedback = gr.Textbox(
                    value="", 
                    elem_classes=["feedback"], 
                    show_label=False,
                    interactive=False
                )
        
        # Submit button and status indicator
        with gr.Row():
            submit_btn = gr.Button("Submit Query", variant="primary")
            status = gr.Textbox(
                label="Status", 
                value="Ready",
                interactive=False
            )
        
        # Response section
        with gr.Group():
            gr.HTML("<h3>Response</h3>")
            
            # Markdown output display
            output = gr.Markdown(
                value="*Response will appear here after submission.*",
                elem_classes=["output-box"],
                elem_id="response-markdown"
            )
            
            # Raw response textarea (hidden) for clipboard functionality
            raw_response = gr.Textbox(visible=False)
            
            # Response copy functionality
            with gr.Row():
                response_copy_btn = gr.Button("Copy Response", elem_classes=["copy-btn"], variant="secondary")
                response_copy_feedback = gr.Textbox(
                    value="", 
                    elem_classes=["feedback"], 
                    show_label=False,
                    interactive=False
                )
        
        # Functions for copy operations
        def copy_text(text):
            """Helper function for copy operations"""
            if not text:
                return "Nothing to copy!"
            return "Copied!"
        
        # Copy button event handlers
        system_copy_btn.click(
            fn=copy_text,
            inputs=[system_prompt],
            outputs=[system_copy_feedback],
            _js="copyTextToClipboard"
        )
        
        user_copy_btn.click(
            fn=copy_text,
            inputs=[user_prompt],
            outputs=[user_copy_feedback],
            _js="copyTextToClipboard"
        )
        
        response_copy_btn.click(
            fn=copy_text,
            inputs=[raw_response],
            outputs=[response_copy_feedback],
            _js="copyTextToClipboard"
        )
        
        # Submit function with progress handling
        def submit_query(base_url, model, system_prompt, user_prompt, temperature, max_tokens):
            # Update status immediately
            yield "Querying the LLM...", "", ""
            
            try:
                # Call the API
                response = query_llm(base_url, model, system_prompt, user_prompt, temperature, max_tokens)
                
                # Store the raw response for clipboard
                yield "Query complete!", response, response
            except Exception as e:
                error_message = f"**Error:** {str(e)}"
                yield f"Error: {str(e)}", error_message, error_message
        
        # Connect the submit button to the query function
        submit_btn.click(
            fn=submit_query,
            inputs=[base_url, model, system_prompt, user_prompt, temperature, max_tokens],
            outputs=[status, output, raw_response]
        )
        
        # Instructions accordion
        with gr.Accordion("Instructions & Examples", open=False):
            gr.Markdown("""
            ## How to Use This Application
            
            This chat application allows you to interact with Large Language Models through a local or remote API.
            
            ### Quick Start:
            
            1. **Configure the API**:
               - Enter the API endpoint (e.g., `http://localhost:8000/v1/chat/completions`)
               - Specify the model name (e.g., `mistralai/Mistral-Small-3.1-24B-Instruct-2503`)
            
            2. **Set Parameters**:
               - Adjust temperature (0-1): Lower values make responses more deterministic, higher values more creative
               - Set max tokens (1-4096): Controls the maximum response length
            
            3. **Enter Prompts**:
               - **System Prompt**: Instructions for the AI's behavior and context
               - **User Prompt**: Your specific question or request
            
            4. **Submit and Review**:
               - Click Submit to send the query
               - Review the response in the output box
               - Use copy buttons to save prompts or responses
            
            ### Example Prompts:
            
            **System Prompt Example:**
            ```
            You are a helpful, knowledgeable assistant with expertise in science and technology. 
            Provide accurate, factual responses with examples where appropriate.
            ```
            
            **User Prompt Example:**
            ```
            Can you explain how nuclear fusion works and why it's difficult to achieve on Earth?
            ```
            """)
    
    return demo

# Create and launch the app
if __name__ == "__main__":
    app = create_llm_chat_app()
    app.launch()
