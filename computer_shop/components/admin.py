from django.contrib import admin
from .models import *
from specs.models import Spec


class OrderItemInline(admin.TabularInline):
    model = OrderItem

class SpecsTabularInline(admin.TabularInline):
    model = Spec
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        product_id = request.resolver_match.kwargs.get('object_id')
        if product_id:
            product = Components.objects.get(id=product_id)
            if db_field.name == 'category':
                kwargs['queryset'] = Category.objects.filter(id=product.cat.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]



@admin.register(Components)
class ComponentsAdmin(admin.ModelAdmin):
    inlines = [SpecsTabularInline]


admin.site.register(Category)
admin.site.register(UserCustom)
admin.site.register(ComponentImages)
admin.site.register(Reviews)
admin.site.register(Reply)
admin.site.register(Notifications)
admin.site.register(Order, OrderAdmin)
