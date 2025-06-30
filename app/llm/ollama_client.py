import ollama
import os
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variable to define the default model
# Users can set this to their preferred (and downloaded) DeepSeek model
# e.g., "deepseek-r1:8b", "deepseek-r1:7b", "deepseek-r1:1.5b"
# For testing in environments without a powerful GPU, a smaller model might be specified.
DEFAULT_OLLAMA_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "orca-mini:latest")
# Using orca-mini as a fallback default because it's small and quick for testing basic connectivity.
# Users will be instructed to set DEFAULT_OLLAMA_MODEL to their chosen DeepSeek model.

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

_ollama_client = None
_ollama_available_check_done = False
_ollama_is_actually_available = False

def get_default_model_name() -> str:
    """Returns the configured default Ollama model name."""
    return DEFAULT_OLLAMA_MODEL

def _get_client() -> ollama.Client | None:
    """Initializes and returns the Ollama client, checking for availability."""
    global _ollama_client, _ollama_available_check_done, _ollama_is_actually_available

    if not _ollama_available_check_done:
        try:
            temp_client = ollama.Client(host=OLLAMA_HOST, timeout=5) # Short timeout for check
            # Try a lightweight command to see if Ollama is responsive and has models
            temp_client.list()
            _ollama_client = temp_client # Use this client if check is successful
            _ollama_is_actually_available = True
            logger.info(f"Successfully connected to Ollama at {OLLAMA_HOST}. Service is available.")
            # Check if the default model is present
            try:
                _ollama_client.show(DEFAULT_OLLAMA_MODEL)
                logger.info(f"Default model '{DEFAULT_OLLAMA_MODEL}' is available in Ollama.")
            except ollama.ResponseError as e:
                if e.status_code == 404:
                    logger.warning(
                        f"Default model '{DEFAULT_OLLAMA_MODEL}' not found in Ollama. "
                        f"Please pull it with 'ollama pull {DEFAULT_OLLAMA_MODEL}'. "
                        f"Falling back to listing available models for generation if any."
                    )
                else:
                    logger.warning(f"Could not verify default model '{DEFAULT_OLLAMA_MODEL}': {e.error}")

        except Exception as e:
            logger.warning(
                f"Ollama service not available at {OLLAMA_HOST} or other error: {e}. "
                "LLM generation will be skipped or use mocked responses if not in production."
            )
            _ollama_is_actually_available = False
        _ollama_available_check_done = True

    return _ollama_client if _ollama_is_actually_available else None

def OLLAMA_IS_AVAILABLE() -> bool:
    """
    Checks if the Ollama service is available by attempting a connection.
    Caches the result after the first check.
    """
    if not _ollama_available_check_done:
        _get_client() # This will perform the check and set the flag
    return _ollama_is_actually_available

def generate_text(
    prompt: str,
    model_name: str = None,
    system_prompt: str = None,
    temperature: float = 0.7,
    stream: bool = False # Added stream parameter
) -> str | None:
    """
    Generates text using a model served by a local Ollama instance.

    Args:
        prompt: The user's prompt.
        model_name: The name of the model to use (e.g., "deepseek-r1:8b", "orca-mini").
                    Defaults to DEFAULT_OLLAMA_MODEL.
        system_prompt: An optional system message to guide the model's behavior.
        temperature: The generation temperature (0.0 to 1.0). Higher is more creative.
        stream: Whether to stream the response (not fully utilized by this wrapper returning full string yet).

    Returns:
        The generated text as a string, or None if an error occurs or Ollama is unavailable.
    """
    client = _get_client()
    if not client:
        logger.warning("Ollama client not available. Skipping text generation.")
        return None

    actual_model_name = model_name if model_name else DEFAULT_OLLAMA_MODEL

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        logger.info(f"Sending request to Ollama model '{actual_model_name}' with prompt: '{prompt[:100]}...'")
        response = client.chat(
            model=actual_model_name,
            messages=messages,
            stream=stream, # Pass stream argument
            options={"temperature": temperature} if temperature is not None else None,
        )

        if stream:
            full_response = ""
            for chunk in response: # response is an iterator if stream=True
                if 'message' in chunk and 'content' in chunk['message']:
                    full_response += chunk['message']['content']
            logger.info("Streamed response received from Ollama.")
            return full_response
        else: # Not streaming
            if isinstance(response, dict) and 'message' in response and 'content' in response['message']:
                logger.info("Response received from Ollama.")
                return response['message']['content']
            else:
                logger.error(f"Unexpected response structure from Ollama: {response}")
                return None

    except ollama.ResponseError as e:
        logger.error(f"Ollama API ResponseError for model '{actual_model_name}': {e.error} (Status: {e.status_code})")
        if e.status_code == 404:
            logger.error(
                f"Model '{actual_model_name}' not found. "
                f"Please ensure it's pulled via 'ollama pull {actual_model_name}'."
            )
        return None
    except Exception as e:
        logger.error(f"Error during Ollama request for model '{actual_model_name}': {e}")
        return None

# --- Test functions ---
def _test_ollama_connection_and_models():
    """For direct testing of this module."""
    logging.info("--- Testing Ollama Connection and Model Availability ---")

    if OLLAMA_IS_AVAILABLE():
        logger.info("Ollama service is reported as available.")
        client = _get_client()
        try:
            models = client.list()
            logger.info(f"Available Ollama models: {[m['name'] for m in models.get('models', [])]}")

            # Check for the default model specifically
            default_model = get_default_model_name()
            try:
                client.show(default_model)
                logger.info(f"Default model '{default_model}' is present.")
            except ollama.ResponseError as e:
                if e.status_code == 404:
                    logger.warning(f"Default model '{default_model}' NOT FOUND. Please run: ollama pull {default_model}")
                else:
                    logger.error(f"Error checking default model '{default_model}': {e}")

        except Exception as e:
            logger.error(f"Could not list models or perform show: {e}")
    else:
        logger.warning("Ollama service is reported as NOT available. Skipping further tests.")

def _test_generate_text_function():
    """For direct testing of the generate_text function."""
    logging.info("\n--- Testing generate_text Function ---")
    if not OLLAMA_IS_AVAILABLE():
        logger.warning("Ollama not available, generate_text will be skipped for live test.")
        # Example of mocked response for CI/dev environments without Ollama
        logger.info("Mocked generate_text response: This is a mocked summary for testing.")
        return

    # Use a small, commonly available model for this test if the default (DeepSeek) might not be present
    # However, we'll try the configured DEFAULT_OLLAMA_MODEL first.
    test_model = get_default_model_name()
    logger.info(f"Attempting generation with model: {test_model}")

    # Simple prompt
    prompt1 = "What is the main purpose of Python programming language? Be concise."
    system_prompt1 = "You are a helpful assistant that provides brief answers."
    response1 = generate_text(prompt1, model_name=test_model, system_prompt=system_prompt1, temperature=0.5)
    if response1:
        logger.info(f"Response for '{prompt1}':\n{response1}")
    else:
        logger.error(f"Failed to get response for '{prompt1}' with model '{test_model}'.")

    # Test streaming (if you want to see it in action here)
    prompt2 = "List three benefits of using local LLMs."
    logger.info(f"\nTesting streamed generation with prompt: '{prompt2}' using model '{test_model}'")

    full_streamed_response = ""
    # Need to call client.chat directly to iterate over stream if generate_text doesn't expose it
    # Or adapt generate_text to yield chunks when stream=True
    # For simplicity, let's call client.chat here for a direct stream test
    client = _get_client()
    if client:
        try:
            stream_response_iter = client.chat(
                model=test_model,
                messages=[{'role': 'user', 'content': prompt2}],
                stream=True,
                options={"temperature": 0.5}
            )
            logger.info("Streamed response:")
            for chunk in stream_response_iter:
                content = chunk['message']['content']
                print(content, end='', flush=True)
                full_streamed_response += content
            print("\nStream finished.") # Newline after stream
            if not full_streamed_response:
                 logger.warning("Streamed response was empty.")
        except Exception as e:
            logger.error(f"Error during streamed generation test: {e}")
    else:
        logger.warning("Ollama client not available for streamed test.")


if __name__ == "__main__":
    # This allows direct testing of the client.
    # In a real environment, Ollama service should be running.
    # The user would need to `ollama serve` and `ollama pull <model_name>`

    # Set a more verbose logging for direct testing if needed
    # logging.getLogger().setLevel(logging.DEBUG)
    # logging.getLogger("ollama").setLevel(logging.DEBUG)

    _test_ollama_connection_and_models()
    _test_generate_text_function()

    # Example of how to use the availability check
    # if OLLAMA_IS_AVAILABLE():
    #     print("\nOllama is available, proceeding with LLM tasks.")
    # else:
    #     print("\nOllama not available, LLM tasks will be skipped or mocked.")
    #     print(f"To use LLM features, ensure Ollama is running at {OLLAMA_HOST} and you have pulled a model like '{DEFAULT_OLLAMA_MODEL}'.")
