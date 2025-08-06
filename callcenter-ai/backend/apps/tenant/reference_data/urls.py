from django.urls import include, path
from .views import (
    # ReferenceDataTypeCSVImport,
    ReferenceDataTypeListCreateView,
    ReferenceDataTypeDetailView,
    ReferenceDataListCreateView,
    ReferenceDataDetailView,
    ReferenceDataHistoryListView,
    ReferenceDataHistoryDetailView,
    # ReferenceDataTypeCSVImport,
    CSVUploadView,  # Added import for CSVUploadView
    CSVProcessView,  # Added import for CSVProcessView
)

app_name = "reference_data"

urlpatterns = [
    # Reference Data Types
    path(
        "types/",
        ReferenceDataTypeListCreateView.as_view(),
        name="type-list",
    ),
    path(
        "types/<uuid:pk>/",
        ReferenceDataTypeDetailView.as_view(),
        name="type-detail",
    ),

    # Reference Data Entries
    path(
        "entries/",
        ReferenceDataListCreateView.as_view(),
        name="entry-list",
    ),
    path(
        "entries/<uuid:pk>/",
        ReferenceDataDetailView.as_view(),
        name="entry-detail",
    ),

    # Reference Data History
    path(
        "history/",
        ReferenceDataHistoryListView.as_view(),
        name="history-list",
    ),
    path(
        "history/<uuid:pk>/",
        ReferenceDataHistoryDetailView.as_view(),
        name="history-detail",
    ),
    
    # path('import-csv/', ReferenceDataTypeCSVImport, name='import_reference_data_csv'),
    path('import-csv-upload/', CSVUploadView.as_view(), name='csv-upload'),
    path('import-csv-process/', CSVProcessView.as_view(), name='csv-process'),

]
