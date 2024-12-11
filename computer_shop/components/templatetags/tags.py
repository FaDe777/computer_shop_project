from django import template

register = template.Library()

@register.simple_tag()
def count(obj, request, choice):
    if choice == 'likes':
        return obj.likes.filter(pk=request.user.id).exists()
    return obj.dislikes.filter(pk=request.user.id).exists()

@register.simple_tag()
def multiple(x,y):
    a = int("".join(str(x).split())) * y
    return '{0:,}'.format(a).replace(',', ' ')

@register.filter()
def get(obj,key):
    return obj.get(key,'')