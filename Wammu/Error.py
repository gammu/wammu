import traceback,sys

def Handler(type, value, tback):
    """User friendly error handling """
    print '-------------------- Traceback --------------------'
    traceback.print_exception(type, value, tback)
    print '---------------------------------------------------'
    print 'You have probably found a bug. You might help improving this software by sending above text and description how it was cause to michal@cihar.com. Thanks.'
