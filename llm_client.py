import os
from openai import OpenAI
# from groq import Groq
from dotenv import load_dotenv

# ============================================================================
# ALTERNATIVE PROVIDER IMPORTS (uncomment the one you want to use)
# ============================================================================
# --- Groq (free tier available at https://console.groq.com) ---
# from groq import Groq
#
# --- Anthropic (https://console.anthropic.com) ---
# import anthropic
#
# --- Google Gemini (free tier at https://aistudio.google.com/apikey) ---
# import google.generativeai as genai
# ============================================================================

load_dotenv()

class LLMClient:
    """
    Unified LLM client that supports multiple providers.
    
    Default: OpenAI
    To switch providers, uncomment the relevant import above and 
    change the 'provider' parameter, e.g.:
        client = LLMClient(provider="groq")
        client = LLMClient(provider="anthropic")
        client = LLMClient(provider="google")
    """
    
    def __init__(self, provider="openai"):
        self.provider = provider
        
        # --- OpenAI (default) ---
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # --- Groq ---
        # Groq uses the same API format as OpenAI, making it a drop-in replacement.
        # Uncomment the Groq import at the top of this file, then uncomment below:
        #
        elif provider == "groq":
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # --- Anthropic ---
        # Anthropic uses a different API format (messages API with system as a parameter).
        # Uncomment the anthropic import at the top, then uncomment below:
        #
        # elif provider == "anthropic":
        #     self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # --- Google Gemini ---
        # Google uses a completely different SDK (google-generativeai).
        # Uncomment the genai import at the top, then uncomment below:
        #
        # elif provider == "google":
        #     genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        #     self.client = genai  # We'll use genai.GenerativeModel() in get_completion
        
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose from: openai, groq, anthropic, google")

    def get_completion(self, prompt, model=None, temperature=0.7, max_tokens=500, 
                       system_message=None, stop=None):
        """
        Get a completion from the LLM.
        
        Args:
            prompt (str): The user prompt.
            model (str): Model name. If None, uses provider default.
            temperature (float): Sampling temperature (0.0 - 1.0).
            max_tokens (int): Maximum tokens in response.
            system_message (str): Optional system prompt for persona/instructions.
            stop (list[str]): Optional stop sequences.
        
        Returns:
            str or None: The completion text, or None on error.
        """
        if model is None:
            model = self._get_default_model()
        
        try:
            # --- OpenAI / Groq ---
            # Both OpenAI and Groq use the same chat completions API format.
            # If using Groq, the only difference is the model name.
            if self.provider in ("openai", "groq"):
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})
                
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if stop:
                    kwargs["stop"] = stop
                    
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            
            # --- Anthropic ---
            # Anthropic uses a different structure: system is a top-level parameter,
            # and max_tokens is required.
            #
            # elif self.provider == "anthropic":
            #     kwargs = {
            #         "model": model,
            #         "max_tokens": max_tokens,
            #         "temperature": temperature,
            #         "messages": [{"role": "user", "content": prompt}],
            #     }
            #     if system_message:
            #         kwargs["system"] = system_message
            #     if stop:
            #         kwargs["stop_sequences"] = stop
            #     response = self.client.messages.create(**kwargs)
            #     return response.content[0].text
            
            # --- Google Gemini ---
            # Google Gemini uses a completely different SDK pattern.
            # Note: Gemini handles system instructions differently (via model config).
            #
            # elif self.provider == "google":
            #     generation_config = {
            #         "temperature": temperature,
            #         "max_output_tokens": max_tokens,
            #     }
            #     if stop:
            #         generation_config["stop_sequences"] = stop
            #     
            #     model_kwargs = {}
            #     if system_message:
            #         model_kwargs["system_instruction"] = system_message
            #     
            #     gemini_model = self.client.GenerativeModel(
            #         model_name=model,
            #         generation_config=generation_config,
            #         **model_kwargs
            #     )
            #     response = gemini_model.generate_content(prompt)
            #     return response.text
            
        except Exception as e:
            print(f"Error getting completion from {self.provider}: {e}")
            return None

    def get_chat_completion(self, messages, model=None, temperature=0.7, 
                            max_tokens=500, tools=None, stop=None):
        """
        Get a chat completion using a full messages list.
        Useful for multi-turn conversations and tool/function calling.
        
        Args:
            messages (list[dict]): List of {"role": "...", "content": "..."} dicts.
            model (str): Model name. If None, uses provider default.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum tokens in response.
            tools (list[dict]): Optional tool definitions (OpenAI function calling format).
            stop (list[str]): Optional stop sequences.
        
        Returns:
            The raw response message object (for tool_calls inspection), or None on error.
        """
        if model is None:
            model = self._get_default_model()
            
        try:
            # --- OpenAI / Groq ---
            if self.provider in ("openai", "groq"):
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if tools:
                    kwargs["tools"] = tools
                if stop:
                    kwargs["stop"] = stop
                    
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message
            
            # --- Anthropic ---
            # Anthropic tool calling uses a different format. See:
            # https://docs.anthropic.com/en/docs/build-with-claude/tool-use
            #
            # elif self.provider == "anthropic":
            #     system = None
            #     filtered_messages = []
            #     for msg in messages:
            #         if msg["role"] == "system":
            #             system = msg["content"]
            #         else:
            #             filtered_messages.append(msg)
            #     kwargs = {
            #         "model": model,
            #         "max_tokens": max_tokens,
            #         "temperature": temperature,
            #         "messages": filtered_messages,
            #     }
            #     if system:
            #         kwargs["system"] = system
            #     if tools:
            #         kwargs["tools"] = [
            #             {
            #                 "name": t["function"]["name"],
            #                 "description": t["function"]["description"],
            #                 "input_schema": t["function"]["parameters"],
            #             }
            #             for t in tools
            #         ]
            #     response = self.client.messages.create(**kwargs)
            #     return response
            
        except Exception as e:
            print(f"Error in chat completion from {self.provider}: {e}")
            return None

    def _get_default_embedding_model(self):
        """Return the default embedding model for the current provider."""
        defaults = {
            "openai": "text-embedding-3-small",
            "groq": "all-MiniLM-L6-v2",  # local model when using Groq (Groq has no working embedding API)
        }
        return defaults.get(self.provider, "text-embedding-3-small")

    def _get_groq_embedding_model(self):
        """Lazy-load sentence-transformers for local embeddings when provider is Groq."""
        if not hasattr(self, "_groq_embedding_model"):
            try:
                from sentence_transformers import SentenceTransformer
                model_name = self._get_default_embedding_model()
                self._groq_embedding_model = SentenceTransformer(model_name)
            except ImportError:
                raise ImportError(
                    "For embeddings with provider='groq', install: pip install sentence-transformers"
                )
        return self._groq_embedding_model

    def get_embedding(self, text, model=None):
        """
        Get an embedding vector for the text.
        
        OpenAI: text-embedding-3-small (default), via API.
        Groq: local sentence-transformers (all-MiniLM-L6-v2) — Groq has no embedding API.
        Google has embeddings via a different method (see commented code).
        """
        if model is None:
            model = self._get_default_embedding_model()
        try:
            text = text.replace("\n", " ")
            
            if self.provider == "openai":
                from openai import OpenAI
                openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                return openai_client.embeddings.create(
                    input=[text], model=model
                ).data[0].embedding
            elif self.provider == "groq":
                # Groq does not offer a working embeddings API; use local model instead.
                st = self._get_groq_embedding_model()
                embedding = st.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            
            # --- Google Gemini Embeddings ---
            #
            # elif self.provider == "google":
            #     result = self.client.embed_content(
            #         model="models/text-embedding-004",
            #         content=text
            #     )
            #     return result["embedding"]
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None

    def _get_default_model(self):
        """Return the default model for the current provider."""
        defaults = {
            "openai": "gpt-3.5-turbo",
            "groq": "llama-3.3-70b-versatile",
            # "anthropic": "claude-sonnet-4-20250514",
            # "google": "gemini-2.0-flash",
        }
        return defaults.get(self.provider, "gpt-3.5-turbo")