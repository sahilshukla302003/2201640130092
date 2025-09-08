from logging_middleware.logger import Log


Log("backend", "error", "handler", "received string, expected bool")
Log("backend", "fatal", "db", "Critical database connection failure.")
Log("backend", "info", "controller", "create_short_url invoked")
