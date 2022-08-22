from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from psu_base.classes.Log import Log
from psu_export.services import export_service
from psu_scheduler.decorators import scheduled_job
from psu_base.decorators import require_authority
from psu_base.services import utility_service, message_service, error_service
from psu_export.models import ExportApp, ExportModel, ExportField

log = Log()


def export_status(request):
    """
    Configure what gets exported
    """
    log.trace()
    export_service.prepare_export()

    # Check for existence of access and secret keys (boolean only)
    access_key = bool(utility_service.get_setting('BI_EXPORT_ACCESS_KEY'))
    secret_key = bool(utility_service.get_setting('BI_EXPORT_SECRET_KEY'))

    apps = ExportApp.objects.all()

    return render(
        request, 'psu_export/export_status.html', {
            'apps': apps,
            'access_key': access_key,
            'secret_key': secret_key,
        }
    )


@scheduled_job()
def export_models(request):
    """
    Export all models (as configured in settings)
    """
    log.trace()
    return JsonResponse(export_service.export_models())


@require_authority("~SuperUser")
def set_app_export(request):
    """
    Enable or Disable exporting for an app
    """
    log.trace()
    app_definition = ExportApp.get(request.POST.get("app_id"))
    if not app_definition:
        message_service.post_error("Application was not found")
        return HttpResponseForbidden()

    enabled = request.POST.get("enabled", "N") == "Y"
    app_definition.export_enabled = enabled
    app_definition.save()

    return render(
        request, 'psu_export/_app_definition.html', {
            'app_definition': app_definition,
        }
    )


@require_authority("~SuperUser")
def set_model_export(request):
    """
    Enable or Disable exporting for a model
    """
    log.trace()
    model_definition = ExportModel.get(request.POST.get("model_id"))
    if not model_definition:
        message_service.post_error("Model was not found")
        return HttpResponseForbidden()

    enabled = request.POST.get("enabled", "N") == "Y"
    model_definition.export_enabled = enabled
    model_definition.save()

    return render(
        request, 'psu_export/_model_definition.html', {
            'model_definition': model_definition,
        }
    )


@require_authority("~SuperUser")
def set_field_export(request):
    """
    Enable or Disable exporting for a field
    """
    log.trace()
    field_definition = ExportField.get(request.POST.get("field_id"))
    if not field_definition:
        message_service.post_error("Field was not found")
        return HttpResponseForbidden()

    enabled = request.POST.get("enabled", "N") == "Y"
    field_definition.export_enabled = enabled
    field_definition.save()

    return render(
        request, 'psu_export/_field_definition.html', {
            'field_definition': field_definition,
        }
    )


@require_authority("~SuperUser")
def set_field_property(request):
    """
    Update a property of a field_definition
    """
    log.trace()
    field_definition = ExportField.get(request.POST.get("field_id"))
    if not field_definition:
        message_service.post_error("Field was not found")
        return HttpResponseForbidden()

    prop = request.POST.get("prop")
    value = request.POST.get("value")
    if prop in ["model", "export_enabled"] or not hasattr(field_definition, prop):
        message_service.post_error("Invalid property was specified")

    else:
        try:
            setattr(field_definition, prop, value)
            field_definition.save()
            return HttpResponse('success')
        except Exception as ee:
            error_service.unexpected_error(f"Invalid value for {prop}", ee)

    return HttpResponseForbidden()
