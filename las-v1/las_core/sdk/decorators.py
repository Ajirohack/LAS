import functools

def command(name: str = None, description: str = None, **kwargs):
    """
    Decorator to mark a method as a LAS command.
    
    Args:
        name: Optional custom name for the command. Defaults to method name.
        description: Optional description. Defaults to docstring.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Attach metadata to the function
        wrapper._is_command = True
        wrapper._command_name = name or func.__name__
        wrapper._command_description = description or func.__doc__
        # Preserve any additional metadata if provided
        if kwargs:
            wrapper._command_metadata = kwargs
        return wrapper
    return decorator
