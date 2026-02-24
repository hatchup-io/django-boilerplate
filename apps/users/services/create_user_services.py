from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


def create_user(validated_data):
    password = validated_data.get("password")
    email = validated_data.get("email")
    try:
        if User.objects.filter(email=email).exists():
            raise ValidationError("This user already exits.")
        extras = {
            "phone_number": validated_data.get("phone_number", ""),
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
        }
        instance = User.objects.create_user(email=email, password=password, **extras)

    except Exception as e:
        raise ValidationError(str(e))

    return instance
