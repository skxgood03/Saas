from django.template import Library

register = Library()

@ register.simple_tag
def user_space(size):
    if size >= 1024 * 1024 * 1024:
        return "%.2f GB" % (size / (1024 * 1024 * 1024),)
    elif size >= 1024 * 1024:
        return "%.2f MB" % (size / (1024 * 1024 ),)
    elif size >= 1024:
        return "%.2f kB" % (size / 1024,)
    else:
        return "%.d B" % size
