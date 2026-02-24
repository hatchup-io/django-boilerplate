SPECTACULAR_SETTINGS = {
    "TITLE": "Boilerplate API",
    "DESCRIPTION": "Minimal authentication and user base API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "PARSER_WHITELIST": ["rest_framework.parsers.JSONParser"],
    "SERVE_AUTHENTICATION": [
        "apps.common.configs.classes.common_authentication_classes.HatchupJWTAuthentication",
    ],
    "SECURITY": [{"Hatchup_auth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "Hatchup_auth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
        },
    },
}
