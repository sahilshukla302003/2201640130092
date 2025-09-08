import requests

LOG_SERVER_URL = "http://20.244.56.144/evaluation-service/logs"

def Log(stack: str, level: str, package: str, message: str):
    """
    Reusable logging function for backend/frontend apps.

    Parameters:
        stack   : "backend" or "frontend"
        level   : "debug" | "info" | "warn" | "error" | "fatal"
        package : e.g. "controller", "db", "handler", "service"
        message : descriptive log message
    """
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": message,
    }

    try:
        res = requests.post(LOG_SERVER_URL, json=payload, timeout=5)
        if res.status_code == 200:
            return res.json() 
        else:
            return {"error": res.status_code, "details": res.text}
    except Exception as e:
        return {"error": "exception", "details": str(e)}
