import Wammu
import wx
import gammu
import traceback,sys

def Handler(type, value, tback):
    """User friendly error handling """
    print '--------------------- Version ---------------------'
    print 'Python       %s' % sys.version.split()[0]
    print 'wxPython     %s' % wx.VERSION_STRING
    print 'Wammu        %s' % Wammu.__version__
    print 'python-gammu %s' % gammu.Version()[1]
    print 'Gammu        %s' % gammu.Version()[0]
    print '-------------------- Traceback --------------------'
    traceback.print_exception(type, value, tback)
    print '---------------------------------------------------'
    if type == UnicodeEncodeError:
        print 'Unicode encoding error appeared, see question 1 in FAQ, how to solve this.'
        print
    print 'You have probably found a bug. You might help improving this software by'
    print 'sending above text and description how it was caused to michal@cihar.com.'
