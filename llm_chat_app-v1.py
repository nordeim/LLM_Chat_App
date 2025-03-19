# LLM Chat Application with Gradio UI
import requests
import json
import time
import gradio as gr
from datetime import datetime, timedelta

# Constants for default values
DEFAULT_BASE_URL = "http://localhost:8000/v1"
DEFAULT_MODEL = "mistralai/Mistral-Small-3.1-24B-Instruct-2503"
DEFAULT_TEMPERATURE = 0.15
DEFAULT_MAX_TOKENS = 4096
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def get_default_system_prompt():
    """Generate a default system prompt with current date."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    return f"""You are an AI assistant powered by a large language model.
Your knowledge base was last updated in 2023.
The current date is {today}.

When you're not sure about some information, you say that you don't have the information and don't make up anything.
If the user's question is not clear, ambiguous, or does not provide enough context for you to accurately answer the question, you do not try to answer it right away and you rather ask the user to clarify their request.
You are always very attentive to dates, in particular you try to resolve dates (e.g. "yesterday" is {yesterday}) and when asked about information at specific dates, you discard information that is at another date. 
You follow these instructions in all languages, and always respond to the user in the language they use or request."""

def query_llm(
    user_prompt, 
    base_url=DEFAULT_BASE_URL, 
    model=DEFAULT_MODEL,
    system_prompt=None, 
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=DEFAULT_MAX_TOKENS,
    chat_history=None
):
    """
    Query an LLM model with improved error handling and configurability.
    
    Args:
        user_prompt (str): The user prompt to send to the model
        base_url (str): Base URL for the API endpoint
        model (str): Model identifier to use
        system_prompt (str, optional): System prompt to guide model behavior
        temperature (float): Sampling temperature
        max_tokens (int): Maximum number of tokens to generate
        chat_history (list, optional): List of previous message dicts
        
    Returns:
        tuple: (success (bool), response (dict or str))
    """
    try:
        # Convert parameters to appropriate types
        temperature = float(temperature)
        max_tokens = int(max_tokens)
    except (ValueError, TypeError):
        return False, "Invalid parameters: temperature must be a float and max_tokens must be an integer"
    
    # Default system prompt if none provided
    if not system_prompt:
        system_prompt = get_default_system_prompt()

    # API endpoint
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    
    # Prepare messages
    messages = []
    
    # Add system message
    messages.append({"role": "system", "content": system_prompt})
    
    # Add chat history if provided
    if chat_history:
        messages.extend(chat_history)
    
    # Add the current user message
    messages.append({"role": "user", "content": user_prompt})
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Send the request with retries
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                endpoint, 
                headers=headers, 
                data=json.dumps(payload),
                timeout=60  # Add timeout to prevent hanging
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = f"Request failed with status {response.status_code}: {response.text}"
                # If we've reached max retries, return the error
                if attempt == MAX_RETRIES - 1:
                    return False, error_msg
                # Otherwise, wait and retry
                time.sleep(RETRY_DELAY)
        except Exception as e:
            error_msg = f"Error during API call: {str(e)}"
            # If we've reached max retries, return the error
            if attempt == MAX_RETRIES - 1:
                return False, error_msg
            # Otherwise, wait and retry
            time.sleep(RETRY_DELAY)
    
    # This should not be reached, but just in case
    return False, "Max retries exceeded with no successful response"

def extract_message_content(chat_history):
    """
    Extract message content from Gradio chat history for API calls.
    
    Args:
        chat_history (list): List of tuples from Gradio chatbot
        
    Returns:
        list: Messages in the format expected by the API
    """
    messages = []
    for sender, content in chat_history:
        # Skip system messages
        if sender == "System":
            continue
        
        role = "user" if sender == "User" else "assistant"
        messages.append({"role": role, "content": content})
    
    return messages

def on_submit(
    user_message, 
    chat_history, 
    base_url, 
    model, 
    system_prompt, 
    temperature, 
    max_tokens
):
    """Process user message and get response from the LLM."""
    if not user_message.strip():
        return "", chat_history, None
    
    # Add user message to chat history
    chat_history = chat_history + [("User", user_message)]
    
    # Extract messages for API call
    messages = extract_message_content(chat_history)
    
    # Call the API
    success, response = query_llm(
        user_prompt=user_message,
        base_url=base_url,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        chat_history=messages[:-1]  # Exclude the last message as it's sent separately
    )
    
    # Process the response
    assistant_response = None
    if success:
        try:
            assistant_response = response["choices"][0]["message"]["content"]
            chat_history = chat_history + [("Assistant", assistant_response)]
        except (KeyError, IndexError) as e:
            error_msg = f"Error parsing API response: {str(e)}\nResponse: {json.dumps(response, indent=2)}"
            chat_history = chat_history + [("System", f"⚠️ {error_msg}")]
    else:
        # Handle error case
        chat_history = chat_history + [("System", f"⚠️ {response}")]
    
    return "", chat_history, assistant_response

def format_chat_history(chat_history):
    """Format chat history for display."""
    formatted = []
    for sender, message in chat_history:
        formatted.append(f"## {sender}\n\n{message}\n")
    
    return "\n".join(formatted)

def create_gradio_interface():
    """Create and launch the Gradio interface for the LLM chat application."""
    
    # Custom CSS for styling
    css = """
    .container { max-width: 1200px; margin: auto; }
    .message pre { background-color: #f6f8fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
    .message code { font-family: monospace; background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; }
    .markdown-area { border: 1px solid #ddd; border-radius: 4px; padding: 10px; }
    """
    
    with gr.Blocks(css=css, title="LLM Chat Application") as demo:
        gr.Markdown("# LLM Chat Application")
        
        # State variables
        last_response = gr.State(None)
        
        with gr.Row():
            # Left column: Chat interface
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=500,
                    render_markdown=True,
                    elem_classes="message",
                    show_copy_button=True
                )
                
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Type your message here...",
                        label="Message",
                        lines=3,
                    )
                    submit_btn = gr.Button("Send", variant="primary")
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat")
            
            # Right column: Settings
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("## API Settings")
                    
                    base_url = gr.Textbox(
                        label="API Base URL",
                        placeholder="Enter API base URL",
                        value=DEFAULT_BASE_URL,
                    )
                    
                    model = gr.Textbox(
                        label="Model",
                        placeholder="Enter model identifier",
                        value=DEFAULT_MODEL,
                    )
                
                with gr.Group():
                    gr.Markdown("## Model Parameters")
                    
                    system_prompt = gr.Textbox(
                        label="System Prompt",
                        placeholder="Enter system instructions...",
                        lines=5,
                        value=get_default_system_prompt(),
                    )
                    
                    temperature = gr.Slider(
                        label="Temperature",
                        minimum=0.0,
                        maximum=2.0,
                        step=0.01,
                        value=DEFAULT_TEMPERATURE,
                    )
                    
                    max_tokens = gr.Number(
                        label="Max Tokens",
                        value=DEFAULT_MAX_TOKENS,
                        precision=0,
                    )
        
        # Last response display area for copying in markdown format
        with gr.Accordion("Last Response (Markdown)", open=True):
            response_textbox = gr.TextArea(
                label="Response (for copying)",
                placeholder="The response will appear here",
                lines=10,
                max_lines=30,
                interactive=False,
                elem_classes="markdown-area"
            )
            copy_response_btn = gr.Button("Copy Response")
        
        # Chat history export
        with gr.Accordion("Export Chat History", open=False):
            chat_history_textbox = gr.TextArea(
                label="Complete Chat History",
                placeholder="Chat history will appear here",
                lines=15,
                max_lines=50,
                interactive=False,
            )
            export_btn = gr.Button("Update Export")
        
        # Event handlers
        submit_btn.click(
            on_submit,
            inputs=[
                user_input, chatbot, base_url, model, 
                system_prompt, temperature, max_tokens
            ],
            outputs=[user_input, chatbot, last_response],
        ).then(
            lambda resp: resp if resp else "No response yet",
            inputs=[last_response],
            outputs=[response_textbox],
        )
        
        user_input.submit(
            on_submit,
            inputs=[
                user_input, chatbot, base_url, model, 
                system_prompt, temperature, max_tokens
            ],
            outputs=[user_input, chatbot, last_response],
        ).then(
            lambda resp: resp if resp else "No response yet",
            inputs=[last_response],
            outputs=[response_textbox],
        )
        
        clear_btn.click(
            lambda: ("", [], None),
            outputs=[user_input, chatbot, last_response],
        ).then(
            lambda: "No response yet",
            outputs=[response_textbox],
        ).then(
            lambda: "No chat history",
            outputs=[chat_history_textbox],
        )
        
        # Export chat history
        export_btn.click(
            format_chat_history,
            inputs=[chatbot],
            outputs=[chat_history_textbox],
        )
        
        # Copy functionality using Gradio's built-in clipboard feature
        copy_response_btn.click(
            lambda x: x, 
            inputs=[response_textbox],
            outputs=[]
        )

    return demo

# Main application
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(share=False)
