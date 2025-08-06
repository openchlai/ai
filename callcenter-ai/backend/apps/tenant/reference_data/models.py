from django.db import models
from django.core.cache import cache
from django.core.validators import validate_slug
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from crum import get_current_user



from django.contrib.postgres.fields import ArrayField
from jsonschema import validate as jsonschema_validate

from apps.shared.core.models import BaseModel
# from tenants.models import Tenant  # Uncomment if needed for type hints

# -- Utility Function ------------------------------------------------------

def get_public_tenant():
    """Helper function to get the public tenant"""
    # return Tenant.objects.filter(schema_name='public').first()
    pass  # Implement appropriately


from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
import re

# If UserTrackingModel is your audit trail base

class ReferenceDataType(BaseModel):
    """
    Defines all possible reference data types in the system.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique name identifier (e.g., 'product_categories')")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Human-readable description")
    )
    is_tenant_specific = models.BooleanField(
        default=False,
        help_text=_("Customizable per tenant")
    )
    is_system_managed = models.BooleanField(
        default=False,
        help_text=_("Managed by system code")
    )
    allowed_metadata_keys = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text=_("Allowed metadata keys")
    )
    validation_schema = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Validation schema")
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(is_system_managed=True) | models.Q(is_tenant_specific=False),
                name="no_system_managed_tenant_specific"
            )
        ]

    def clean(self):
        if self.is_system_managed:
            if not re.match(r'^[a-z_]+$', self.name):
                raise ValidationError("System-managed names must be lowercase with underscores")
            if not self.allowed_metadata_keys:
                raise ValidationError("System-managed types require allowed_metadata_keys")

    def __str__(self):
        return f"{self.name} (Tenant specific: {self.is_tenant_specific}, System managed: {self.is_system_managed})"


# -- Reference Data --------------------------------------------------------

class ReferenceData(BaseModel):
    """
    Represents a reference data value (e.g., category, type, status).
    """
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='reference_data'
    )
    data_type = models.ForeignKey(
        ReferenceDataType,
        on_delete=models.PROTECT,
        related_name='entries',
        help_text=_("Type of reference data this entry belongs to")
    )
    code = models.CharField(
        max_length=50,
        help_text=_("Unique code identifier within this data type and tenant")
    )
    display_value = models.CharField(
        max_length=255,
        help_text=_("Human-readable display value")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of this entry")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this entry is active and available for use")
    )
    sort_order = models.IntegerField(
        default=0,
        help_text=_("Sort order for display purposes")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional attributes specific to this entry")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text=_("Parent entry for hierarchical data")
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text=_("Version number for optimistic concurrency control")
    )

    class Meta:
        verbose_name = _("Reference Data")
        verbose_name_plural = _("Reference Data")
        unique_together = [['tenant', 'data_type', 'code']]
        ordering = ['data_type', 'sort_order', 'display_value']
        indexes = [
            models.Index(fields=['tenant', 'data_type', 'is_active']),
            models.Index(fields=['tenant', 'data_type', 'code']),
        ]

    def __str__(self):
        return f"{self.data_type.name}: {self.display_value} ({self.code})"

    def clean(self):
        # Validate metadata keys
        if self.data_type.allowed_metadata_keys:
            for key in self.metadata.keys():
                if key not in self.data_type.allowed_metadata_keys:
                    raise ValidationError(
                        _(f"Metadata key '{key}' is not allowed for this data type.")
                    )

        # Validate metadata schema
        if self.data_type.validation_schema:
            try:
                jsonschema_validate(self.metadata, self.data_type.validation_schema)
            except Exception as e:
                raise ValidationError(_(f"Metadata validation error: {str(e)}"))

        # Validate tenant restriction
        if not self.data_type.is_tenant_specific and self.tenant != get_public_tenant():
            raise ValidationError(
                _("This data type is not tenant-specific and can only be used for the public tenant.")
            )

    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
        self.full_clean()
        super().save(*args, **kwargs)
        cache_key = f"ref_data_{self.tenant.id}_{self.data_type.name}"
        cache.delete(cache_key)

    def delete(self, *args, **kwargs):
        cache_key = f"ref_data_{self.tenant.id}_{self.data_type.name}"
        cache.delete(cache_key)
        super().delete(*args, **kwargs)


# -- Reference Data History ------------------------------------------------

class ReferenceDataHistory(BaseModel):
    """
    Tracks changes to reference data for audit purposes.
    """
    reference_data = models.ForeignKey(
        ReferenceData,
        on_delete=models.CASCADE,
        related_name='history'
    )
    version = models.PositiveIntegerField()
    change_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Reason for the change")
    )
    changed_fields = models.JSONField()
    previous_state = models.JSONField()

    class Meta:
        verbose_name = _("Reference Data History")
        verbose_name_plural = _("Reference Data Histories")
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.reference_data} - v{self.version}"
