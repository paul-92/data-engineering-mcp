class DataEngineeringMCPError(ValueError):
    """Base error returned by the domain layer."""


class TableNotFoundError(DataEngineeringMCPError): pass
class ColumnNotFoundError(DataEngineeringMCPError): pass
class AmbiguousColumnError(DataEngineeringMCPError): pass
class RelationshipNotFoundError(DataEngineeringMCPError): pass
class PathNotFoundError(DataEngineeringMCPError): pass
class InvalidWorkbookError(DataEngineeringMCPError): pass
class NoValidWorksheetError(InvalidWorkbookError): pass
class MissingHeaderError(InvalidWorkbookError): pass
class InvalidFilterError(DataEngineeringMCPError): pass
class ForbiddenSQLOperationError(DataEngineeringMCPError): pass
