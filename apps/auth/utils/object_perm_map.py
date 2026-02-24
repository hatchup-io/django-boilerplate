from __future__ import annotations

from typing import Dict, List, Type

from django.db.models import Model


def crud_object_perms_map(model: Type[Model]) -> Dict[str, List[str]]:
    """
    Build a standard CRUD permission map for a model.

    This keeps ViewSets short and consistent:
      perms = crud_object_perms_map(Startup)

    Map keys are DRF ViewSet actions.
    Values are lists of full permission strings: "{app_label}.{codename}".
    """

    app = model._meta.app_label
    name = model._meta.model_name
    return {
        "retrieve": [f"{app}.view_{name}"],
        "list": [f"{app}.view_{name}"],
        "update": [f"{app}.change_{name}"],
        "partial_update": [f"{app}.change_{name}"],
        "destroy": [f"{app}.delete_{name}"],
        "*": [f"{app}.view_{name}"],
    }
