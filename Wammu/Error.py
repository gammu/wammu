import traceback,sys

def Handler(type, value, tback):
    """User friendly error handling """
    print '-------------------- Traceback --------------------'
    traceback.print_exception(type, value, tback)
    print '---------------------------------------------------'
    if type == UnicodeEncodeError:
        print 'Unicode encoding error appeared, see question 1 in FAQ, how to avoid this.'
    else:
        print 'You have probably found a bug. You might help improving this software by sending above text and description how it was cause to michal@cihar.com. Thanks.'
