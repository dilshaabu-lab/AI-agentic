import math

def calculator(expression):
    """
    Evaluates a mathematical expression.
    """
    try:
        # Security: restrict available globals/locals
        allowed_names = {"math": math, "abs": abs, "round": round, "min": min, "max": max}
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Use of '{name}' is not allowed")
        return eval(code, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

def web_search(query):
    """
    Mock web search tool.
    Returns simulated search results for demo purposes.
    """
    print(f"[Tool: Web Search] Searching for: {query}")
    mock_db = {
        "weather": "The weather in San Francisco is 65F and sunny.",
        "stock": "AAPL is trading at $185.32, up 0.5%.",
        "president": "The current president of the United States is Joe Biden.",
        "course": "The Applied Agentic AI Systems course covers RAG, Agents, and Multi-Agent systems.",
        "revenue": "Q2 revenue was $1.2M. Q3 revenue was $1.5M."
    }
    
    # Simple keyword matching for mock results
    results = []
    for key, value in mock_db.items():
        if key in query.lower():
            results.append(value)
            
    if not results:
        return "No specific results found. Try simpler keywords."
        
    return "\n".join(results)

def send_email(to, subject, body):
    """
    Mock email sender.
    """
    print(f"[Tool: Email] Sending email to {to}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return "Email sent successfully"