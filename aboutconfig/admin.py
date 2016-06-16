"""User configuration access via the django admin."""

from django.contrib import admin

from .models import DataType, Config


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    """Django admin for the DataType model."""

    list_display = ('name', 'serializer_class')


class ConfigNamespaceFilter(admin.SimpleListFilter):
    """Key namespace sidebar filter implementation."""

    title = 'namespace'
    parameter_name = 'namespace'


    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        lookups = set(queryset.values_list(
            'key_namespace', flat=True
        ).distinct().iterator())

        return sorted((x, x) for x in lookups)


    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(key_namespace=self.value())


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    """Django admin for the Config model."""

    list_display = ('key', 'value', 'default_value', 'data_type', 'allow_template_use', 'in_cache')
    fields = ('key', 'value', 'data_type', 'default_value', 'allow_template_use')
    readonly_fields = ('default_value',)
    list_filter = ('data_type', 'allow_template_use', ConfigNamespaceFilter)
