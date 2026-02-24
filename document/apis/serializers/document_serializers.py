from rest_framework import serializers

from common.models.common_type_models import Type
from document.models import Document
from document.services.document_service import create_document


class DocumentUploadRequestSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    type = serializers.PrimaryKeyRelatedField(
        queryset=Type.objects.filter(scope="document"),
        required=False,
        allow_null=True,
        write_only=True,
    )

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        type_obj = validated_data.get("type")
        return create_document(
            user=user,
            file_obj=validated_data["file"],
            type_id=type_obj.id if type_obj else None,
        )


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = [
            "id",
            "filename",
            "original_filename",
            "file_type",
            "file_size_bytes",
            "file_url",
            "type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DocumentUpdateSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(
        queryset=Type.objects.filter(scope="document"),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Document
        fields = ["id", "type"]
        read_only_fields = ["id"]
