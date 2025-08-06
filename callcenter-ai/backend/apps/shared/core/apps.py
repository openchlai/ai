"""
Django app configuration for the Murima core application.

This module configures the core app and handles signal registration
for automatic audit logging and system monitoring.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    """
    Configuration for the Murima core application.
    
    This app provides:
    - Abstract base models for consistent data patterns
    - Automatic audit logging via signals
    - System configuration management
    - Error logging and monitoring
    - Common utilities and managers
    """
    
    # App identification
    name = 'apps.shared.core'
    label = 'core'
    verbose_name = _('Murima Core')
    
    # Use BigAutoField for auto-generated primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """
        Initialize the app when Django starts.
        
        This method is called when the app is fully loaded and ready.
        It's the place to register signals, perform startup tasks,
        and configure app-specific behavior.
        """
        # Import and register signals
        self._register_signals()
        
        # Initialize system configuration defaults
        self._initialize_system_defaults()
        
        # Setup logging configuration
        self._setup_logging()
        
        # Validate app dependencies
        self._validate_dependencies()
    
    def _register_signals(self):
        """Register signal handlers for audit logging and monitoring."""
        try:
            # Import signals module to register the signal handlers
            from . import signals
            
            # The signals are automatically registered when the module is imported
            # due to the @receiver decorators
            
            print("Core app: Signal handlers registered successfully")
            
        except Exception as e:
            print(f"Core app: Failed to register signal handlers: {e}")
            # Don't raise the exception as it would prevent Django from starting
    
    def _initialize_system_defaults(self):
        """Initialize default system configurations if they don't exist."""
        try:
            # Import here to avoid circular imports
            from django.db import transaction
            from .models import SystemConfiguration
            
            # Default configurations that should exist in every installation
            default_configs = [
                {
                    'key': 'system_name',
                    'name': 'System Name',
                    'value': 'Murima Platform',
                    'data_type': 'string',
                    'category': 'general',
                    'description': 'Display name for the platform',
                    'is_sensitive': False,
                },
                {
                    'key': 'max_file_upload_size',
                    'name': 'Maximum File Upload Size',
                    'value': 10485760,  # 10MB in bytes
                    'data_type': 'integer',
                    'category': 'file_management',
                    'description': 'Maximum size for file uploads in bytes',
                    'is_sensitive': False,
                },
                {
                    'key': 'session_timeout_minutes',
                    'name': 'Session Timeout (Minutes)',
                    'value': 480,  # 8 hours
                    'data_type': 'integer',
                    'category': 'security',
                    'description': 'User session timeout in minutes',
                    'is_sensitive': False,
                },
                {
                    'key': 'audit_retention_days',
                    'name': 'Audit Log Retention Days',
                    'value': 2555,  # 7 years
                    'data_type': 'integer',
                    'category': 'compliance',
                    'description': 'Number of days to retain audit logs',
                    'is_sensitive': False,
                },
                {
                    'key': 'error_log_retention_days',
                    'name': 'Error Log Retention Days',
                    'value': 90,  # 3 months
                    'data_type': 'integer',
                    'category': 'system',
                    'description': 'Number of days to retain error logs',
                    'is_sensitive': False,
                },
                {
                    'key': 'enable_audit_logging',
                    'name': 'Enable Audit Logging',
                    'value': True,
                    'data_type': 'boolean',
                    'category': 'compliance',
                    'description': 'Whether to enable automatic audit logging',
                    'is_sensitive': False,
                },
                {
                    'key': 'maintenance_mode',
                    'name': 'Maintenance Mode',
                    'value': False,
                    'data_type': 'boolean',
                    'category': 'system',
                    'description': 'Put the system in maintenance mode',
                    'is_sensitive': False,
                },
                {
                    'key': 'api_rate_limit_per_minute',
                    'name': 'API Rate Limit (Per Minute)',
                    'value': 1000,
                    'data_type': 'integer',
                    'category': 'api',
                    'description': 'Maximum API requests per minute per user',
                    'is_sensitive': False,
                },
            ]
            
            # Only create configurations if the table exists (migrations have run)
            if self._table_exists('core_systemconfiguration'):
                with transaction.atomic():
                    for config_data in default_configs:
                        SystemConfiguration.objects.get_or_create(
                            key=config_data['key'],
                            defaults=config_data
                        )
                
                print("Core app: Default system configurations initialized")
        
        except Exception as e:
            print(f"Core app: Failed to initialize default configurations: {e}")
            # Don't raise the exception
    
    def _setup_logging(self):
        """Configure logging for the core app."""
        try:
            import logging
            
            # Get or create logger for core app
            logger = logging.getLogger('murima.core')
            
            # Set default level if not configured
            if not logger.handlers:
                logger.setLevel(logging.INFO)
            
            # Log that core app is ready
            logger.info("Murima Core app initialized successfully")
            
        except Exception as e:
            print(f"Core app: Failed to setup logging: {e}")
    
    def _validate_dependencies(self):
        """Validate that required dependencies are available."""
        try:
            # Check for required Django apps
            from django.apps import apps
            
            required_apps = [
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django_tenants',  # Multi-tenancy support
            ]
            
            missing_apps = []
            for app_name in required_apps:
                try:
                    apps.get_app_config(app_name)
                except LookupError:
                    missing_apps.append(app_name)
            
            if missing_apps:
                print(f"Core app: Missing required dependencies: {', '.join(missing_apps)}")
            else:
                print("Core app: All dependencies validated successfully")
        
        except Exception as e:
            print(f"Core app: Failed to validate dependencies: {e}")
    
    def _table_exists(self, table_name):
        """
        Check if a database table exists.
        Useful for preventing errors during initial migrations.
        """
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables 
                    WHERE table_name = %s
                """, [table_name])
                
                return cursor.fetchone()[0] > 0
        
        except Exception:
            # If we can't check, assume table doesn't exist
            return False
    
    @classmethod
    def get_version(cls):
        """Get the version of the core app."""
        return "1.0.0"
    
    @classmethod
    def get_system_info(cls):
        """Get system information for debugging."""
        import django
        import sys
        import platform
        
        return {
            'core_app_version': cls.get_version(),
            'django_version': django.get_version(),
            'python_version': sys.version,
            'platform': platform.platform(),
            'app_name': cls.name,
            'app_label': cls.label,
        }


# Additional configuration classes for different environments

class CoreDevConfig(CoreConfig):
    """Core app configuration for development environment."""
    
    def ready(self):
        super().ready()
        
        # Development-specific initialization
        self._setup_dev_logging()
        self._create_dev_data()
    
    def _setup_dev_logging(self):
        """Setup enhanced logging for development."""
        import logging
        
        logger = logging.getLogger('murima.core')
        logger.setLevel(logging.DEBUG)
        
        # Add console handler for development
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.debug("Core app: Development logging configured")
    
    def _create_dev_data(self):
        """Create development test data."""
        # This could create test configurations, users, etc.
        # Only run in development
        pass


class CoreProductionConfig(CoreConfig):
    """Core app configuration for production environment."""
    
    def ready(self):
        super().ready()
        
        # Production-specific initialization
        self._setup_production_logging()
        self._validate_security_settings()
    
    def _setup_production_logging(self):
        """Setup production logging configuration."""
        import logging
        
        logger = logging.getLogger('murima.core')
        
        # Ensure INFO level in production
        logger.setLevel(logging.INFO)
        
        logger.info("Core app: Production environment detected")
    
    def _validate_security_settings(self):
        """Validate security settings for production."""
        from django.conf import settings
        
        security_checks = [
            ('DEBUG', False, "DEBUG should be False in production"),
            ('ALLOWED_HOSTS', None, "ALLOWED_HOSTS should be configured"),
        ]
        
        warnings = []
        for setting_name, expected_value, message in security_checks:
            setting_value = getattr(settings, setting_name, None)
            
            if expected_value is not None and setting_value != expected_value:
                warnings.append(message)
            elif expected_value is None and not setting_value:
                warnings.append(message)
        
        if warnings:
            import logging
            logger = logging.getLogger('murima.core')
            for warning in warnings:
                logger.warning(f"Security check: {warning}")


# Export the default configuration
default_app_config = 'apps.shared.core.apps.CoreConfig'