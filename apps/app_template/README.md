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

## Layout

```
apps/<app_name>/
  apis/
    serializers/<entity>_serializers.py
    views/<entity>_viewsets.py
    urls.py
  models/<app_name>_<entity>_models.py
  services/<app_name>_services.py        # business logic; raise apps.common.exceptions.*
  configs/constants/<app_name>_enums.py  # TextChoices / IntegerChoices live here
  admin/<entity>_admin.py
  tests/
    factories.py                          # factory_boy factories
    test_<entity>_apis.py                 # pytest smoke tests
  apps.py
  migrations/
```

This matches the per-app layout described in `docs/CONVENTIONS.md`.

## Usage

1. Create the app under `apps/`: either run `python manage.py startapp <app_name>` (the project's overridden `startapp` command places it under `apps/<app_name>/`), or copy `apps/app_template/` to `apps/<app_name>/`.
2. If using the template directly: find-replace all placeholders in `.py-tpl` files, then rename `.py-tpl` files to `.py` (strip the `-tpl` suffix).
3. Add the app to `INSTALLED_APPS` in `core/settings.py` as `apps.<app_name>.apps.<Config>` (e.g. `apps.items.apps.ItemsConfig`).
4. Add `path("api/<app_name>/", include("apps.<app_name>.apis.urls"))` in `core/urls.py`.
5. Run `python manage.py makemigrations <app_label>` (e.g. `items`) and `python manage.py migrate`.
6. Run `uv run pytest apps/<app_name>` to verify the scaffolded smoke tests pass.
