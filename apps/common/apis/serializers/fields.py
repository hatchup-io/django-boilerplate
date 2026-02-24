# Standard library imports
import base64
import csv
from decimal import Decimal, InvalidOperation
from uuid import uuid4

# Django imports
from django.core.files.base import ContentFile

# Third-party imports
import magic
import six
from djmoney.money import Money
from rest_framework import serializers


class MoneySerializerField(serializers.Field):
    """
    DRF field that accepts money as:
    - String "amount currency" (e.g. "1000000.00 USD")
    - Number (uses default_currency, e.g. 1000000.00)
    - Dict {"amount": "100", "currency": "USD"}
    Returns a Money instance for model assignment.
    """

    default_error_messages = {
        "invalid": 'A valid money value is required (e.g. "100.00 USD" or a number).',
    }

    def __init__(self, default_currency="USD", **kwargs):
        self.default_currency = default_currency
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data is None:
            return None
        if isinstance(data, Money):
            return data
        if isinstance(data, (int, float)):
            try:
                amount = Decimal(str(data))
            except (InvalidOperation, ValueError):
                self.fail("invalid")
            return Money(amount=amount, currency=self.default_currency)
        if isinstance(data, six.string_types):
            data = data.strip()
            if not data:
                return None
            parts = data.split(None, 1)
            try:
                amount = Decimal(parts[0])
            except (InvalidOperation, ValueError):
                self.fail("invalid")
            currency = parts[1] if len(parts) > 1 else self.default_currency
            return Money(amount=amount, currency=currency)
        if isinstance(data, dict):
            amount_str = data.get("amount")
            currency = data.get("currency", self.default_currency)
            if amount_str is None:
                self.fail("invalid")
            try:
                amount = Decimal(str(amount_str))
            except (InvalidOperation, ValueError):
                self.fail("invalid")
            return Money(amount=amount, currency=currency)
        self.fail("invalid")

    def to_representation(self, value):
        if value is None:
            return None
        if isinstance(value, Money):
            return f"{value.amount} {value.currency}"
        return value


class Base64FileField(serializers.FileField):
    """
    A Django REST framework field for handling file uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    This version supports images, PDF, Excel, and CSV files.
    """

    default_error_messages = {
        "empty_string": "Upload failed. Please upload a valid file.",
        "invalid_file": "Upload failed. Please upload a valid file.",
        "unsupported_file_type": "Unsupported file type. Please upload a valid file type (image, pdf, excel, csv).",
    }

    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the string is empty
            if data == "":
                self.fail("empty_string")
            # Check if the base64 string is in the "data:" format
            if "data:" in data and ";base64," in data:
                # Break out the header from the base64 content
                header, data = data.split(";base64,")

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_file")

            # Generate file name:
            file_name = str(uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = f"{file_name}.{file_extension}"

            # Return as a ContentFile object
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64FileField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        """
        Determines the file extension based on the file type.
        Now supports image, PDF, Excel, and CSV.
        """
        file_type = magic.from_buffer(decoded_file, mime=True)

        if file_type.startswith("image"):
            ext = file_type.split("/", 1)[-1].lower()
            if ext == "jpeg":
                ext = "jpg"
            if not ext:
                self.fail("unsupported_file_type")
            extension = ext

        elif file_type == "application/pdf":
            extension = "pdf"

        elif file_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]:
            extension = (
                "xlsx"
                if file_type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else "xls"
            )

        elif file_type in ("text/csv", "application/csv"):
            extension = "csv"

        elif file_type == "text/plain":
            try:
                sample = decoded_file[:4096].decode("utf-8", errors="ignore")
                if (
                    "," in sample or ";" in sample or "\t" in sample
                ) and csv.Sniffer().sniff(sample):
                    extension = "csv"
                else:
                    self.fail("unsupported_file_type")
            except Exception:
                self.fail("unsupported_file_type")

        else:
            self.fail("unsupported_file_type")

        return extension
