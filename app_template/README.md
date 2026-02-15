# App Template

Scaffolding template for new Django apps. Replace placeholders when generating a new app.

## Placeholders

| Placeholder                 | Example | Description                      |
| --------------------------- | ------- | -------------------------------- |
| `{{ app_name }}`            | `items` | Snake_case app name              |
| `{{ entity }}`              | `item`  | Snake_case entity/model name     |
| `{{ Entity }}`              | `Item`  | PascalCase entity name           |
| `{{ Tag }}`                 | `Items` | API tag for drf-spectacular      |
| `{{ camel_case_app_name }}` | `Items` | CamelCase app name for AppConfig |

## Usage

1. Copy `app_template/` to a new directory (e.g. `items/`).
2. Find-replace all placeholders in `.py-tpl` files.
3. Rename `.py-tpl` files to `.py` (strip the `-tpl` suffix).
4. Add the app to `INSTALLED_APPS` in `core/settings.py`.
5. Add `path("api/{{ app_name }}/", include("{{ app_name }}.apis.urls"))` in `core/urls.py`.
6. Run `python manage.py makemigrations {{ app_name }}`.
