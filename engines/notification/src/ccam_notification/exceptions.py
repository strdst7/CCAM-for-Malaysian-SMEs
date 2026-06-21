class NotificationError(Exception): pass
class ChannelError(NotificationError): pass
class TemplateError(NotificationError): pass
class DeliveryError(NotificationError): pass
