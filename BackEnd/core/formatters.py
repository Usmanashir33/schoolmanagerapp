def format_serializer_errors(errors):
    formatted = {}
    for field, messages in errors.items():
        formatted[field] = str(messages[0])
    return formatted