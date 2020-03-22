"""User configuration access via the django admin."""

from typing import TYPE_CHECKING, List, Tuple

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls.resolvers import RegexPattern

from .constants import CONFIG_ADMIN_TYPE_QUERY_KEY
from .forms import ConfigAdminForm
from .models import Config, DataType


if TYPE_CHECKING:
    from django.db.models import QuerySet


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    """Django admin for the DataType model."""

    list_display = ("name", "serializer_class")


class ConfigNamespaceFilter(admin.SimpleListFilter):
    """Key namespace sidebar filter implementation."""

    title = "namespace"
    parameter_name = "namespace"

    def lookups(self, request: HttpRequest, model_admin: "ConfigAdmin") -> List[Tuple[str, str]]:
        queryset = model_admin.get_queryset(request)
        lookups = set(queryset.values_list("key_namespace", flat=True).distinct().iterator())

        return sorted((x, x) for x in lookups)

    def queryset(self, request: HttpRequest, queryset: "QuerySet[Config]") -> "QuerySet[Config]":
        if self.value() is None:
            return queryset

        return queryset.filter(key_namespace=self.value())


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    """Django admin for the Config model."""

    list_display = ("key", "value", "default_value", "data_type", "allow_template_use", "in_cache")
    list_filter = ("data_type", "allow_template_use", ConfigNamespaceFilter)
    search_fields = ("key",)
    form = ConfigAdminForm

    class Media:
        js = ("aboutconfig/config_admin.js",)

    @staticmethod
    def fetch_field_view(request: HttpRequest) -> HttpResponse:
        """Fetches the HTML required for rendering the given type of value."""

        try:
            data_type = DataType.objects.get(pk=request.GET[CONFIG_ADMIN_TYPE_QUERY_KEY])
        except (DataType.DoesNotExist, ValueError, TypeError, KeyError):
            raise Http404()

        try:
            attrs = {"id": request.GET["id"]}
        except KeyError:
            return HttpResponseBadRequest()

        current_value = request.GET.get("value", "")

        try:
            config = Config.objects.get(pk=request.GET["config_pk"])
        except (DataType.DoesNotExist, ValueError, TypeError, KeyError):
            config = Config(key="x", key_namespace="x")

        config.data_type = data_type
        config.value = current_value

        try:
            config.full_clean()
        except ValidationError:
            current_value = ""

        widget = data_type.get_widget_class()(**data_type.widget_args)
        return JsonResponse({"content": widget.render("value", current_value, attrs=attrs)})

    def get_urls(self) -> List[RegexPattern]:
        """Get custom admin endpoints."""

        return [
            url(
                r"^fetch-value-field-html",
                self.admin_site.admin_view(self.fetch_field_view),
                name="ac-fetch-value-field",
            )
        ] + super().get_urls()
