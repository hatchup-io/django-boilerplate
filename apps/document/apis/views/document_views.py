from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.apis.views.common_base_views import HatchupModelViewset
from apps.document.apis.serializers import DocumentSerializer
from apps.document.apis.serializers import DocumentUpdateSerializer
from apps.document.apis.serializers import DocumentUploadRequestSerializer
from apps.document.models import Document


@extend_schema_view(
    list=extend_schema(
        tags=["Documents"],
        summary="List documents",
        description="List documents owned by the current user.",
        responses={200: DocumentSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Documents"],
        summary="Retrieve document",
        description="Retrieve a document by ID (owner only).",
        responses={200: DocumentSerializer()},
    ),
    create=extend_schema(
        tags=["Documents"],
        summary="Upload document",
        description="Upload a document (multipart: file, optional type_id).",
        request=DocumentUploadRequestSerializer,
        responses={201: DocumentSerializer()},
    ),
    update=extend_schema(
        tags=["Documents"],
        summary="Update document",
        request=DocumentUpdateSerializer(),
        responses={200: DocumentSerializer()},
    ),
    partial_update=extend_schema(
        tags=["Documents"],
        summary="Partially update document",
        request=DocumentUpdateSerializer(partial=True),
        responses={200: DocumentSerializer()},
    ),
    destroy=extend_schema(
        tags=["Documents"],
        summary="Delete document",
        description="Delete a document (owner only).",
        responses={204: None},
    ),
)
class DocumentViewSet(HatchupModelViewset):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["type"]
    queryset = Document.objects.all()

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentUploadRequestSerializer
        if self.action in ("update", "partial_update"):
            return DocumentUpdateSerializer
        return DocumentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        doc = serializer.save()
        return Response(DocumentSerializer(doc).data, status=201)
