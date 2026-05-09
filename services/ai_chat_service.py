import os
import httpx
from pydantic import BaseModel

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = "You are AgriSen AI Assistant, an expert in agriculture. Provide clear helpful answers to farming questions including crops, fertilizers, irrigation, soil and pest management. If asked about the platform, explain its features. IMPORTANT: Strictly refuse to answer any questions that are NOT related to agriculture, farming, crops, or the AgriSen platform. If a user asks a non-agricultural question, your response must be exactly: 'Please ask questions related to agriculture or farming.'"

async def get_ai_response(user_message: str) -> str:
    # Handle missing API key gracefully by simulating a fallback immediately
    if not OPENROUTER_API_KEY:
        print("XCI API KEY MISSING -> Triggering fallback.")
        return _get_fallback_response(user_message)
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "agrisen-app",
        "X-Title": "AgriSen AI Assistant"
    }
    
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "top_p": 0.9
    }
    
    try:
        print(f"\n[AI Chat] Sending request to OpenRouter API... Model: {payload['model']}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            
            # Print raw response before parsing
            print(f"[AI Chat] Raw Response Status: {response.status_code}")
            try:
                raw_json = response.json()
                print(f"[AI Chat] Raw JSON Response:\n{raw_json}")
            except Exception as json_err:
                print(f"[AI Chat] Could not parse raw response as JSON: {json_err}")
                
            response.raise_for_status()
            data = response.json()
            
            print("[AI Chat] Full API Response:", data)
            
            choice = data.get("choices", [{}])[0]
            
            content = (
                choice.get("message", {}).get("content")
                or choice.get("text")
                or ""
            )
            
            if content:
                content = content.strip()
            
            print("[AI Chat] Extracted Content:", content)
            
            # Trigger fallback only if the response content is truly empty 
            if not content or len(content.strip()) == 0:
                print("[AI Chat] Empty response → fallback triggered")
                return _get_fallback_response(user_message)
                
            return content
    except Exception as e:
        print(f"[AI Chat] XCI AI Assistant Request Error: {e} -> Triggering fallback.")
        return _get_fallback_response(user_message)

def _get_fallback_response(user_message: str) -> str:
    message_lower = user_message.lower()
    
    if "crop" in message_lower:
        return "Our crop recommendation system predicts the best crop using soil nutrients (N, P, K), pH level, rainfall, humidity and temperature."
    elif "fertilizer" in message_lower:
        return "Our fertilizer suggestion feature recommends fertilizers based on crop type, soil nutrients and environmental conditions."
    else:
        return "I am currently unable to access the AI service, but I can still help explain farming concepts and how to use this application."
