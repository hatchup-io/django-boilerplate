# App Template

Scaffolding template for new Django apps. New apps live under `apps/` and use the module path `apps.<app_name>`.

## Placeholders

| Placeholder                 | Example | Description                      |
| --------------------------- | ------- | -------------------------------- |
| `{{ app_name }}`            | `items` | Snake_case app name              |
| `{{ entity }}`              | `item`  | Snake_case entity/model name     |
| `{{ Entity }}`              | `Item`  | PascalCase entity name           |
| `{{ Tag }}`                 | `Items` | API tag for drf-spectacular      |
| `{{ camel_case_app_name }}` | `Items` | CamelCase app name for AppConfig |

## Usage

1. Create a new app under `apps/`: run `python manage.py startapp <app_name>` (creates `apps/<app_name>/`), or copy `apps/app_template/` to `apps/<app_name>/`.
2. If using the template: find-replace all placeholders in `.py-tpl` files, then rename `.py-tpl` files to `.py` (strip the `-tpl` suffix).
3. Add the app to `INSTALLED_APPS` in `core/settings.py` as `apps.<app_name>.apps.<Config>` (e.g. `apps.items.apps.ItemsConfig`).
4. Add `path("api/<app_name>/", include("apps.<app_name>.apis.urls"))` in `core/urls.py`.
5. Run `python manage.py makemigrations <app_label>` (app_label is the short name, e.g. `items`).
