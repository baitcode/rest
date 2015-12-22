from .response import ErrorResponse

UNAUTHENTICATED = 'E001'
UNAUTHORIZED = 'E002'

METHOD_NOT_IMPLEMENTED = 'E003'
PARAMETER_REQUIRED = 'E004'
REQUEST_VALIDATION_FAILED = 'E005'
INTERNAL_SERVER_ERROR = 'E006'
INSUFFICIENT_PERMISSIONS = 'E007'
INTERNAL_API_ERROR = 'E013'

# TODO MOVE TO DIFFERENT PLACE
OBJECT_NOT_FOUND_ERROR = 'E008'
EMPTY_UPDATE = 'E014'
OBJECT_ALREADY_EXISTS_ERROR = 'E015'
UNAUTHORIZED_MODEL_ACCESS_RESPONSE = 'E016'

NotImplementedResponse = ErrorResponse.build_new(
    METHOD_NOT_IMPLEMENTED,
    u'Resource {resource} has no {method} method',
    501,
)

UnauthenticatedResponse = ErrorResponse.build_new(
    UNAUTHENTICATED,
    u'You must be authenticated to access {resource} resource.',
    401
)

UnauthorizedResponse = ErrorResponse.build_new(
    UNAUTHORIZED,
    u'You have no permission to access {resource}.',
    403
)

ParameterRequiredResponse = ErrorResponse.build_new(
    PARAMETER_REQUIRED,
    u'{location} parameter {name} is required.',
    400
)

RequestValidationFailedResponse = ErrorResponse.build_new(
    REQUEST_VALIDATION_FAILED,
    u'Parameter {parameter} is invalid. {message}',
    400
)

EmptyRequestResponse = ErrorResponse.build_new(
    EMPTY_UPDATE,
    u'Update is empty',
    400
)

InsufficientPermissionsResponse = ErrorResponse.build_new(
    INSUFFICIENT_PERMISSIONS,
    u'Insufficient permissions. {message}.',
    403
)

InternalServerErrorResponse = ErrorResponse.build_new(
    INTERNAL_SERVER_ERROR,
    u'Server is out of order. Sorry for inconveniences.',
    500
)

ObjectNotFoundErrorResponse = ErrorResponse.build_new(
    OBJECT_NOT_FOUND_ERROR,
    u'{object_type} with id {id} was not found.',
    404
)

UnauthorizedModelAccessResponse = ErrorResponse.build_new(
    UNAUTHORIZED_MODEL_ACCESS_RESPONSE,
    u'Insufficient permissions. You have cannot access {model} {id}.',
    403
)

ObjectAlreadyExistsErrorResponse = ErrorResponse.build_new(
    OBJECT_ALREADY_EXISTS_ERROR,
    u'{object_type} already exists',
    400,
)
