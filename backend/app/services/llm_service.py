import openai
import httpx
import json
from typing import Optional, List
from decouple import config

from app import schemas


class LLMService:
    def __init__(self):
        # Don't initialize with environment keys - use user-provided keys instead
        self.serpapi_key = config("SERPAPI_KEY", default="")
        self.brave_api_key = config("BRAVE_API_KEY", default="")

    async def generate_response(
        self,
        query: str,
        model: str,
        context: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        use_web_search: bool = False,
        api_key: Optional[str] = None
    ) -> schemas.LLMResponse:
        """Generate response using specified LLM with optional web search"""
        
        # Perform web search if requested
        web_context = ""
        sources = []
        if use_web_search:
            search_results = await self._perform_web_search(query)
            web_context = search_results.get("context", "")
            sources = search_results.get("sources", [])

        # Build the prompt
        system_prompt = self._build_system_prompt(custom_prompt, context, web_context)
        
        try:
            if model.startswith("gpt"):
                response = await self._call_openai(system_prompt, query, model, api_key)
            elif model.startswith("gemini"):
                response = await self._call_gemini(system_prompt, query, model, api_key)
            else:
                raise ValueError(f"Unsupported model: {model}")
            
            return schemas.LLMResponse(
                response=response,
                sources=sources,
                model_used=model
            )
            
        except Exception as e:
            return schemas.LLMResponse(
                response=f"Error generating response: {str(e)}",
                sources=[],
                model_used=model
            )

    def _build_system_prompt(
        self,
        custom_prompt: Optional[str],
        context: Optional[str],
        web_context: str
    ) -> str:
        """Build the system prompt with all available context"""
        
        base_prompt = custom_prompt or "You are a helpful AI assistant."
        
        if context or web_context:
            base_prompt += "\n\nAdditional Context:\n"
            
            if context:
                base_prompt += f"Document Context: {context}\n"
            
            if web_context:
                base_prompt += f"Web Search Results: {web_context}\n"
            
            base_prompt += "\nUse this context to provide accurate and relevant responses."
        
        return base_prompt

    async def _call_openai(self, system_prompt: str, query: str, model: str, api_key: Optional[str] = None) -> str:
        """Call OpenAI API"""
        if not api_key:
            raise ValueError("API key is required for OpenAI models. Please provide your API key in the LLM component.")
        
        # Use the provided API key
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content

    async def _call_gemini(self, system_prompt: str, query: str, model: str, api_key: Optional[str] = None) -> str:
        """Call Google Gemini API using direct HTTP requests"""
        if not api_key:
            raise ValueError("API key is required for Gemini models")
        
        # Combine system prompt and query for Gemini
        full_prompt = f"{system_prompt}\n\nUser Query: {query}"
        
        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ]
        }
        
        # Make the API request using the format you provided
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={
                    "Content-Type": "application/json",
                    "X-goog-api-key": api_key
                },
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
            
            result = response.json()
            print(f"Gemini API Response: {result}")
            
            # Extract the text from the response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            raise Exception("Invalid response format from Gemini API")

    async def _perform_web_search(self, query: str) -> dict:
        """Perform web search using available APIs"""
        
        # Try SerpAPI first
        if self.serpapi_key:
            results = await self._search_with_serpapi(query)
            if results:
                return results
        
        # Try Brave API as fallback
        if self.brave_api_key:
            results = await self._search_with_brave(query)
            if results:
                return results
        
        return {"context": "", "sources": []}

    async def _search_with_serpapi(self, query: str) -> Optional[dict]:
        """Search using SerpAPI"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": self.serpapi_key,
                        "engine": "google",
                        "num": 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    organic_results = data.get("organic_results", [])
                    
                    context = ""
                    sources = []
                    
                    for result in organic_results[:5]:
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")
                        link = result.get("link", "")
                        
                        context += f"{title}: {snippet}\n\n"
                        sources.append(link)
                    
                    return {"context": context, "sources": sources}
        
        except Exception as e:
            print(f"SerpAPI search error: {str(e)}")
            return None

    async def _search_with_brave(self, query: str) -> Optional[dict]:
        """Search using Brave Search API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip",
                        "X-Subscription-Token": self.brave_api_key
                    },
                    params={
                        "q": query,
                        "count": 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    web_results = data.get("web", {}).get("results", [])
                    
                    context = ""
                    sources = []
                    
                    for result in web_results:
                        title = result.get("title", "")
                        description = result.get("description", "")
                        url = result.get("url", "")
                        
                        context += f"{title}: {description}\n\n"
                        sources.append(url)
                    
                    return {"context": context, "sources": sources}
        
        except Exception as e:
            print(f"Brave search error: {str(e)}")
            return None
