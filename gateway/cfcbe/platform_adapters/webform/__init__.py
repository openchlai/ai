from platform_adapters.adapter_factory import AdapterFactory
from platform_adapters.webform.webform_adapter import WebformAdapter

# Register the webform adapter
AdapterFactory.register_adapter('webform', WebformAdapter)