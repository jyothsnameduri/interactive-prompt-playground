import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIWrapper:
    """
    A wrapper class for OpenAI API interactions.
    This class separates the OpenAI API logic from the UI code.
    """
    
    def __init__(self):
        """Initialize the OpenAI wrapper."""
        # Verify API key is set
        if not client.api_key:
            raise ValueError("OpenAI API key is not set. Please check your .env file.")
    
    def generate_response(self, model, system_prompt, user_prompt, product, 
                         temperature=0.7, max_tokens=150, presence_penalty=0.0, 
                         frequency_penalty=0.0, stop_sequence=None):
        """
        Generate a response from the OpenAI API.
        
        Args:
            model (str): The model to use (e.g., 'gpt-3.5-turbo', 'gpt-4')
            system_prompt (str): The system prompt
            user_prompt (str): The user prompt
            product (str): The product to generate a description for
            temperature (float): Controls randomness (0.0 to 2.0)
            max_tokens (int): Maximum number of tokens to generate
            presence_penalty (float): Penalty for token presence (0.0 to 2.0)
            frequency_penalty (float): Penalty for token frequency (0.0 to 2.0)
            stop_sequence (str): Optional sequence where the API will stop generating
            
        Returns:
            tuple: (response_content, error_message)
                - response_content (str): The generated text if successful, None otherwise
                - error_message (str): Error message if an error occurred, None otherwise
        """
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            # Add product to user prompt
            full_user_prompt = f"{user_prompt} Product: {product}"
            messages.append({"role": "user", "content": full_user_prompt})
            
            # Call OpenAI API with new syntax
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stop=stop_sequence
            )
            
            # Extract and return the response content
            return response.choices[0].message.content, None
            
        except Exception as e:
            # Return error message
            return None, str(e)
    
    def batch_generate(self, model, system_prompt, user_prompt, product,
                      temperatures, max_tokens_values, presence_penalties,
                      frequency_penalties, stop_sequence=None):
        """
        Generate responses for multiple parameter combinations.
        
        Args:
            model (str): The model to use
            system_prompt (str): The system prompt
            user_prompt (str): The user prompt
            product (str): The product to generate a description for
            temperatures (list): List of temperature values to test
            max_tokens_values (list): List of max_tokens values to test
            presence_penalties (list): List of presence_penalty values to test
            frequency_penalties (list): List of frequency_penalty values to test
            stop_sequence (str): Optional stop sequence
            
        Returns:
            list: List of result dictionaries with parameters and responses
        """
        results = []
        
        # Generate all combinations
        for temp in temperatures:
            for max_tok in max_tokens_values:
                for pres_pen in presence_penalties:
                    for freq_pen in frequency_penalties:
                        # Generate response
                        response_content, error = self.generate_response(
                            model=model,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            product=product,
                            temperature=temp,
                            max_tokens=max_tok,
                            presence_penalty=pres_pen,
                            frequency_penalty=freq_pen,
                            stop_sequence=stop_sequence
                        )
                        
                        # Store result
                        if error:
                            result = {
                                "parameters": {
                                    "temperature": temp,
                                    "max_tokens": max_tok,
                                    "presence_penalty": pres_pen,
                                    "frequency_penalty": freq_pen
                                },
                                "error": error
                            }
                        else:
                            result = {
                                "parameters": {
                                    "temperature": temp,
                                    "max_tokens": max_tok,
                                    "presence_penalty": pres_pen,
                                    "frequency_penalty": freq_pen
                                },
                                "response": response_content
                            }
                            
                        results.append(result)
        
        return results
