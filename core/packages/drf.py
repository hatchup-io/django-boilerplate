REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.common.configs.classes.common_authentication_classes.HatchupJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_SCHEMA_CLASS": "apps.common.configs.classes.hatchup_auto_schema.HatchupAutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.common.configs.classes.common_paginators_classes.DefaultPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "EXCEPTION_HANDLER": "apps.common.utils.common_exception_handler.hatchup_exception_handler",
    "PAGE_SIZE": 10,
}
