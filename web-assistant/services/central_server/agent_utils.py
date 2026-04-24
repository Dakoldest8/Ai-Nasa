import logging

def format_agent_response(text, handoff=False, escalated=False):
    return {
        "reply": text,        # ✅ frontend expects this
        "response": text,     # (keep for backwards compatibility)
        "handoff": handoff,
        "escalated": escalated
    }

def safe_llm_call(llm_function, *args, **kwargs):
    try:
        return llm_function(*args, **kwargs)
    except Exception as e:
        logging.error(f"LLM call failed: {e}")
        return "Sorry, I couldn't process that request."
