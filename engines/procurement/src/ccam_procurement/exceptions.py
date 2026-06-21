class ProcurementError(Exception):
    pass

class AdapterError(ProcurementError):
    pass

class POGenerationError(ProcurementError):
    pass

class SupplierNotFoundError(ProcurementError):
    pass
