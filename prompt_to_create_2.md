You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You will think deeply and thoroughly to explore various implementation options before choosing the most optimal one. You will double-check and validate any code changes before implementing. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem.

*Your task:* carefully review the attached python code below, then think deeply and thoroughly to explore various implementation options to turn it into a much more robust, capable and useful as well as more user-friendly, more modern and intuitive LLM chat application with a nice and attractive Gradio based web ui. Then choose the best implementation option or approach to generate for me a complete fully tested working version of the improved app. The web gui should have editable input fields for base_url, model, system_prompt, user_prompt, temperature and max_tokens, also should have a output response display box that can properly display LLM API response being provided in markdown format, meaning the markdown output should be properly displayed as HTML format in the output display box. Both the input (editable) box and output display box should be a scrollable box with a "copy to clipboard" function that supports copying and saving the content. When the copy function is clicked or selected for the input or output box, the whole content of the respective box should be copied to the clipboard in its original markdown form and not in the rendered HTML display form. Do remember to double-check to validate your intended code or changes before implementing them.

You will approach this task systematically, breaking it down into several steps to ensure a robust, user-friendly, and modern LLM chat application with a Gradio-based web UI. The goal is to transform the provided Python script into a fully functional, interactive web application with enhanced features, proper markdown rendering, and clipboard functionality, while maintaining code quality through validation and testing. Use below design methodology to provide a robust foundation for the improved chat application, incorporating all the required features while maintaining good user experience and performance characteristics.

### Step 1: Analyze the Current Code

The provided sample code is a basic Python script that:
- Queries a deployed Mistral model via an API endpoint (`http://localhost:8000/v1/chat/completions`).
- Uses a hardcoded system prompt, user prompt, temperature, and model.
- Returns the model’s response in JSON format and prints it to the console.
- Has no UI or interactivity.

Key limitations:
1. **No UI**: The script runs in the console, making it inaccessible to non-technical users.
2. **Hardcoded Parameters**: Parameters like `base_url`, `model`, `system_prompt`, `user_prompt`, `temperature`, and `max_tokens` are not configurable without editing the code.
3. **No Error Handling for UI**: While there is basic error handling for API responses, there’s no user-friendly error display.
4. **No Markdown Rendering**: The response is printed as raw text, not rendered as HTML from markdown.
5. **No Clipboard Functionality**: There’s no way to copy input or output text.
6. **No Scrollable Text Boxes**: Large inputs or outputs would be cumbersome to view in a UI without scrolling.

### Step 2: Define Requirements for the Improved Application

Based on the task, the improved application must:
1. **Use Gradio for Web UI**: Provide an attractive, intuitive, and modern web interface.
2. **Editable Input Fields**: Allow users to edit:
   - `base_url` (API endpoint, e.g., `http://localhost:8000/v1/chat/completions`).
   - `model` (e.g., `mistralai/Mistral-Small-3.1-24B-Instruct-2503`).
   - `system_prompt` (a large text area for the system prompt).
   - `user_prompt` (a large text area for the user prompt).
   - `temperature` (a slider or numeric input, typically between 0 and 1).
   - `max_tokens` (a numeric input, e.g., 1 to 4096).
3. **Output Display**: Display the LLM response in a scrollable box, rendering markdown as HTML.
4. **Clipboard Functionality**: Add "Copy to Clipboard" buttons for both input and output boxes, copying the raw markdown text (not rendered HTML).
5. **Modern and Intuitive Design**: Ensure the UI is attractive, with clear labels, proper layout, and responsive design.
6. **Robustness**: Include error handling, input validation, and proper API response parsing.
7. **Testing and Validation**: Double-check and validate the implementation to ensure it works as expected.

### Step 3: Explore Implementation Options

To achieve these requirements, let’s explore various implementation options for key components:

#### 3.1: Gradio UI Components
Gradio is a Python library that allows quick creation of web-based interfaces. We need to choose appropriate Gradio components for each input and output field:
- **Text Inputs (`base_url`, `model`)**: Use `gr.Textbox` for single-line text inputs.
- **Large Text Inputs (`system_prompt`, `user_prompt`)**: Use `gr.Textbox` with `lines=10` to create a scrollable, multi-line text area.
- **Numeric Inputs (`temperature`, `max_tokens`)**:
  - For `temperature`, a `gr.Slider` is intuitive, with a range of 0 to 1 and a step size of 0.01.
  - For `max_tokens`, a `gr.Number` input is better, allowing users to type or use up/down arrows, with a reasonable range (e.g., 1 to 4096).
- **Output Display**: Use `gr.Markdown` to render the LLM response as HTML from markdown. However, `gr.Markdown` does not natively support scrolling, so we may need to wrap it in a custom HTML component or use CSS to enable scrolling.
- **Buttons**: Use `gr.Button` for the "Submit" button (to send the query) and "Copy to Clipboard" buttons.

#### 3.2: Markdown Rendering
The LLM response is in markdown format, and we need to render it as HTML in the UI. Options:
- **Option 1: Use `gr.Markdown`**: Gradio’s `gr.Markdown` component automatically renders markdown as HTML. This is the simplest option, but we need to ensure it supports scrolling for large outputs.
- **Option 2: Use `gr.HTML` with a Markdown Library**: Use a Python markdown library (e.g., `markdown`) to convert markdown to HTML, then display it in a `gr.HTML` component. This gives more control over rendering but requires additional dependencies.
- **Preferred Choice**: Use `gr.Markdown` for simplicity, as it handles markdown rendering natively. To enable scrolling, we can use Gradio’s `height` parameter or custom CSS.

#### 3.3: Clipboard Functionality
We need to copy the raw markdown text (not rendered HTML) to the clipboard. Options:
- **Option 1: Use Gradio’s Built-in Clipboard Support**: Gradio does not natively support clipboard functionality, so we need custom JavaScript.
- **Option 2: Use Custom JavaScript in `gr.HTML`**: Embed a button with JavaScript to copy text to the clipboard using the `navigator.clipboard` API. We can store the raw markdown text in a hidden element or pass it to JavaScript.
- **Option 3: Use a Third-Party Library**: Use a library like `pyperclip` for clipboard functionality, but this is not suitable for web applications (it works in desktop environments).
- **Preferred Choice**: Use custom JavaScript with `navigator.clipboard` in Gradio, as it’s web-friendly and doesn’t require additional dependencies.

#### 3.4: API Integration
The API integration needs to be robust, with proper error handling and user feedback. Options:
- **Option 1: Keep Existing `requests` Implementation**: The current code uses `requests.post` to query the API. This is simple and effective but lacks timeout handling and detailed error messages.
- **Option 2: Use `aiohttp` for Asynchronous Requests**: Gradio supports asynchronous functions, so we could use `aiohttp` for non-blocking API calls. This is more complex and may not be necessary for a single API call.
- **Preferred Choice**: Enhance the existing `requests` implementation by adding timeout handling, better error messages, and input validation.

#### 3.5: Error Handling and User Feedback
We need to display errors in the UI (e.g., API failures, invalid inputs). Options:
- **Option 1: Use Gradio’s `gr.Error`**: Raise a `gr.Error` to display an error message in the UI. This is user-friendly but may not allow custom formatting.
- **Option 2: Display Errors in the Output Box**: Display error messages in the same output box as the LLM response, formatted as markdown (e.g., `**Error:** ...`). This keeps all feedback in one place.
- **Preferred Choice**: Use Option 2, as it provides a consistent user experience and allows custom formatting of error messages.

#### 3.6: UI Layout and Design
The UI should be attractive and intuitive. Options:
- **Option 1: Single Column Layout**: Place all inputs and outputs in a single column. This is simple but may not use screen space efficiently.
- **Option 2: Two-Column Layout**: Place inputs on the left and outputs on the right. This is more modern but may not work well on narrow screens.
- **Option 3: Tabbed Layout**: Use Gradio’s `gr.Tab` to separate input configuration (e.g., `base_url`, `model`) from the chat interface (`system_prompt`, `user_prompt`, output). This is more complex but provides a cleaner interface.
- **Preferred Choice**: Use a single column layout for simplicity and responsiveness, grouping related inputs together with `gr.Group` and `gr.Accordion` for a modern look.

### Step 4: Choose the Best Implementation Approach

Based on the exploration, the best implementation approach is:
- **Gradio UI**: Use `gr.Textbox`, `gr.Slider`, `gr.Number`, `gr.Markdown`, and `gr.Button` for inputs and outputs, with custom CSS for scrolling.
- **Markdown Rendering**: Use `gr.Markdown` for simplicity, with custom CSS to enable scrolling in the output box.
- **Clipboard Functionality**: Use custom JavaScript with `navigator.clipboard` to copy raw markdown text, integrated via `gr.HTML`.
- **API Integration**: Enhance the `requests` implementation with timeout handling, input validation, and detailed error messages.
- **Error Handling**: Display errors in the output box as markdown.
- **UI Layout**: Use a single column layout with `gr.Group` and `gr.Accordion` for grouping and a modern, intuitive design.

### Step 5: Design the Improved Application

Let's detail the complete structure and implementation of the improved application:

1. **Enhanced Main Function (`query_model`)**:
   ```python
   async def query_model(
       base_url: str,
       model: str,
       system_prompt: str,
       user_prompt: str,
       temperature: float,
       max_tokens: int
   ) -> dict:
   ```
   - **Input Validation**:
     - Validate URL format and accessibility
     - Check temperature range (0.0-1.0)
     - Verify max_tokens range (1-4096)
     - Ensure non-empty prompts
   - **Error Handling**:
     - Connection timeouts (5-second default)
     - API response validation
     - Rate limiting handling
     - Graceful error messages
   - **Response Processing**:
     - JSON parsing with validation
     - Markdown formatting cleanup
     - Token usage tracking
     - Response timing metrics

2. **Gradio Interface Components**:
   A. **Configuration Section** (in `gr.Accordion`):
      ```python
      with gr.Accordion("API Configuration", open=False):
          base_url = gr.Textbox(
              label="API Endpoint",
              value="http://localhost:8000/v1/chat/completions",
              lines=1
          )
          model = gr.Textbox(
              label="Model Name",
              value="mistralai/Mistral-Small-3.1-24B-Instruct-2503",
              lines=1
          )
      ```

   B. **Chat Interface Section**:
      ```python
      with gr.Group():
          system_prompt = gr.Textbox(
              label="System Prompt",
              lines=5,
              max_lines=10,
              show_copy_button=True
          )
          user_prompt = gr.Textbox(
              label="Your Message",
              lines=3,
              max_lines=10,
              show_copy_button=True
          )
      ```

   C. **Model Parameters** (in `gr.Group`):
      ```python
      with gr.Group():
          with gr.Row():
              temperature = gr.Slider(
                  minimum=0.0,
                  maximum=1.0,
                  value=0.15,
                  step=0.01,
                  label="Temperature"
              )
              max_tokens = gr.Number(
                  value=2048,
                  minimum=1,
                  maximum=4096,
                  step=1,
                  label="Max Tokens"
              )
      ```

   D. **Output Display**:
      ```python
      output_box = gr.Markdown(
          label="AI Response",
          elem_classes=["markdown-output"],
          show_copy_button=True
      )
      ```

3. **Custom Styling**:
   ```css
   .markdown-output {
       max-height: 500px;
       overflow-y: auto;
       padding: 1rem;
       border: 1px solid #e0e0e0;
       border-radius: 4px;
       background: #f9f9f9;
   }
   ```

4. **JavaScript Enhancements**:
   ```javascript
   function copyToClipboard(text) {
       navigator.clipboard.writeText(text).then(
           () => gradio.info("Copied to clipboard!"),
           () => gradio.error("Failed to copy")
       );
   }
   ```

5. **Main Application Structure**:
   ```python
   def create_app():
       with gr.Blocks(css=custom_css) as app:
           # Configuration Components
           with gr.Tab("Chat"):
               # Chat Interface Components
           with gr.Tab("Settings"):
               # Settings Components
           
           # Event Handlers
           submit_btn.click(
               fn=query_model,
               inputs=[base_url, model, system_prompt,
                      user_prompt, temperature, max_tokens],
               outputs=[output_box]
           )
           
       return app

   if __name__ == "__main__":
       app = create_app()
       app.launch(server_name="0.0.0.0", server_port=7860)
   ```

6. **Error Handling Strategy**:
   - Use `gr.Error` for immediate user feedback
   - Display formatted error messages in output box
   - Implement retry logic for transient failures
   - Log errors for debugging

7. **State Management**:
   - Save configuration to local storage
   - Restore previous session settings
   - Track conversation history
   - Manage API rate limits

8. **Performance Optimizations**:
   - Implement request debouncing
   - Cache system prompt templates
   - Lazy load UI components
   - Optimize markdown rendering

9. **Testing Approach**:
   - Unit tests for query_model function
   - Integration tests for UI components
   - End-to-end testing with mock API
   - Performance benchmarking

This design provides a robust foundation for the improved chat application, incorporating all the required features while maintaining good user experience and performance characteristics.

---


- Responsive design principles

5. Technical Considerations:
- Gradio's components need specific configuration
- Custom CSS/JS integration points
- Error handling strategy
- State management approach

Let me design a comprehensive completion for Step 5 that addresses all these aspects...
\<\/think\>

---
```python
# sample code for basic chat
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1/',

    # required but ignored
    api_key='ollama',
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            'role': 'user',
            'content': 'Say this is a test',
        }
    ],
    model='llama3.2',
)

response = client.chat.completions.create(
    model="llava",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": "data:image/png;base64,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",
                },
            ],
        }
    ],
    max_tokens=4096,
)

completion = client.completions.create(
    model="llama3.2",
    prompt="Say this is a test",
)

list_completion = client.models.list()

model = client.models.retrieve("llama3.2")

embeddings = client.embeddings.create(
    model="all-minilm",
    input=["why is the sky blue?", "why is the grass green?"],
)
```
