from typing import Dict, Type, Optional
from django.conf import settings
from .base_adapter import BaseAdapter

class AdapterFactory:
    """
    Factory for creating platform-specific adapters.
    
    This factory maintains a registry of available platform adapters
    and instantiates the appropriate adapter based on the platform name.
    """
    
    # Registry of platform adapters
    _adapters: Dict[str, Type[BaseAdapter]] = {}
    
    # Cache of adapter instances
    _adapter_instances: Dict[str, BaseAdapter] = {}
    
    @classmethod
    def register_adapter(cls, platform: str, adapter_class: Type[BaseAdapter]) -> None:
        """
        Register a new adapter for a platform.
        
        Args:
            platform: String identifier for the platform
            adapter_class: Class that implements BaseAdapter
        """
        platform = platform.lower()
        if not issubclass(adapter_class, BaseAdapter):
            raise TypeError(f"Adapter class must inherit from BaseAdapter: {adapter_class.__name__}")
        
        cls._adapters[platform] = adapter_class
    
    @classmethod
    def get_adapter(cls, platform: str) -> BaseAdapter:
        """
        Get an adapter instance for the specified platform.
        
        Args:
            platform: String identifier for the platform
            
        Returns:
            An instance of the appropriate adapter
            
        Raises:
            ValueError: If the platform is not supported
        """
        platform = platform.lower()
        
        # Check if we have an instance already
        if platform in cls._adapter_instances:
            return cls._adapter_instances[platform]
        
        # Get the adapter class
        if platform not in cls._adapters:
            raise ValueError(f"Unsupported platform: {platform}")
        
        adapter_class = cls._adapters[platform]
        
        # Create an instance
        adapter = adapter_class()
        
        # Cache the instance
        cls._adapter_instances[platform] = adapter
        
        return adapter
    
    @classmethod
    def get_available_platforms(cls) -> list:
        """
        Get a list of all registered platforms.
        
        Returns:
            List of platform identifiers
        """
        return list(cls._adapters.keys())
    
    @classmethod
    def get_adapter_config(cls, platform: str) -> dict:
        """
        Get configuration for a specific platform adapter.
        
        Args:
            platform: String identifier for the platform
            
        Returns:
            Configuration dictionary for the platform
        """
        platform = platform.lower()
        
        # Get platform configs from settings
        platform_configs = getattr(settings, 'PLATFORM_CONFIGS', {})
        
        # Return platform-specific config or empty dict if not found
        return platform_configs.get(platform, {})
    
    @classmethod
    def init_adapters(cls) -> None:
        """
        Initialize all registered adapters.
        
        This method is called during app startup to ensure
        all platform adapters are registered.
        """
        # Import adapter modules to trigger registration
        # This is intentionally empty and will be populated
        # in the actual implementation to avoid circular imports
        pass


# Import all adapter classes to register them
# These imports will be added as adapters are implemented
# from .whatsapp.whatsapp_adapter import WhatsAppAdapter
# from .messenger.messenger_adapter import MessengerAdapter
# from .email.email_adapter import EmailAdapter