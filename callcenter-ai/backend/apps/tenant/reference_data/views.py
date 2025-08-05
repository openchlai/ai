from django.contrib.auth import get_user
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
import re

from .models import ReferenceDataType, ReferenceData, ReferenceDataHistory
from .serializers import (
    ReferenceDataTypeSerializer,
    ReferenceDataSerializer,
    ReferenceDataHistorySerializer
)


# -------------------------------
# Reference Data Type Views
# -------------------------------

class ReferenceDataTypeListCreateView(generics.ListCreateAPIView):
    queryset = ReferenceDataType.objects.all()
    serializer_class = ReferenceDataTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'is_tenant_specific', 'is_system_managed']
    ordering = ['name']


class ReferenceDataTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferenceDataType.objects.all()
    serializer_class = ReferenceDataTypeSerializer


# -------------------------------
# Reference Data Views
# -------------------------------

class ReferenceDataListCreateView(generics.ListCreateAPIView):
    queryset = ReferenceData.objects.all()
    serializer_class = ReferenceDataSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tenant', 'data_type', 'is_active']
    search_fields = ['code', 'display_value', 'description']
    ordering_fields = ['sort_order', 'display_value']
    ordering = ['sort_order', 'display_value']


class ReferenceDataDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferenceData.objects.all()
    serializer_class = ReferenceDataSerializer


# -------------------------------
# Reference Data History Views
# -------------------------------

class ReferenceDataHistoryListView(generics.ListAPIView):
    queryset = ReferenceDataHistory.objects.all()
    serializer_class = ReferenceDataHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['reference_data', 'version']
    ordering_fields = ['created_at', 'version']
    ordering = ['-created_at']


class ReferenceDataHistoryDetailView(generics.RetrieveAPIView):
    queryset = ReferenceDataHistory.objects.all()
    serializer_class = ReferenceDataHistorySerializer

import csv, os, logging
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Use DEBUG for development, INFO or WARNING in production

class CSVUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        logger.debug("Received request to upload CSV")

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            logger.warning("No file uploaded in request")
            return Response({'error': 'No file uploaded'}, status=400)

        try:
            file_path = default_storage.save(f'temp/{uploaded_file.name}', uploaded_file)
            logger.info(f"File uploaded and saved at: {file_path}")
            return Response({'file_path': file_path}, status=201)
        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}", exc_info=True)
            return Response({'error': 'Failed to save uploaded file'}, status=500)


from rest_framework.request import Request  # 🔑 Make sure this import is present

from rest_framework.request import Request
from rest_framework.parsers import JSONParser

class CSVProcessView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [JSONParser]

    def post(self, request):
        logger.debug(f"Authorization header: {request.headers.get('Authorization')}")
        logger.debug(f"Authenticated user: {request.user} (is_authenticated={request.user.is_authenticated})")
        logger.debug("Received request to process CSV file")

        file_path = request.data.get('file_path')
        if not file_path:
            logger.warning("Missing file_path in request data")
            return Response({'error': 'Missing file path'}, status=400)

        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        logger.debug(f"Resolved full path: {full_path}")

        if not os.path.exists(full_path):
            logger.error(f"File not found at path: {full_path}")
            return Response({'error': 'File not found'}, status=404)

        created = 0
        user = request.user if request.user.is_authenticated else None

        try:
            with open(full_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                logger.info(f"Read {len(rows)} rows from CSV")

                for i, row in enumerate(rows, start=1):
                    try:
                        logger.debug(f"Processing row {i}: {row}")
                        ReferenceDataType.objects.create(
                            name=row['name'],
                            description=row.get('description', ''),
                            is_tenant_specific=row.get('is_tenant_specific', '').lower() == 'true',
                            is_system_managed=row.get('is_system_managed', '').lower() == 'true',
                            allowed_metadata_keys=[],
                            created_by=user,
                            updated_by=user
                        )
                        created += 1
                    except Exception as e:
                        logger.warning(f"Failed to process row {i}: {e}", exc_info=True)
                        continue
        except Exception as e:
            logger.error(f"Error opening or reading CSV file: {str(e)}", exc_info=True)
            return Response({'error': 'Failed to read or process CSV file'}, status=500)

        logger.info(f"Successfully created {created} records from CSV")
        return Response({'message': f'Processed {created} rows'}, status=200)
