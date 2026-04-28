from __future__ import annotations

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Sequence(lambda n: f"100000{n:04d}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "pass1234")
        user = model_class(*args, **kwargs)
        user.set_password(password)
        user.save()
        return user
