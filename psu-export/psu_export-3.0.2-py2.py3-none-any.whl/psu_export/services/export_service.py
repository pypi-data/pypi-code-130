import boto3
from psu_base.services import utility_service, error_service
from django.apps import apps
from psu_base.classes.Log import Log
import pandas
import io
from datetime import datetime
from django.db import connection, connections
from psu_export.models import ExportApp, ExportModel, ExportField

log = Log()

# Completely ignore some framework models
ignored_apps = [
    'admin', 'contenttypes', 'auth', 'sessions', 'messages',
    'staticfiles', 'django_cas_ng', 'crequest', 'sass_processor'
]


def prepare_export():
    """Make sure all apps, models, and fields have been defined in the database"""
    new_apps = []
    new_models = []
    new_fields = []

    current_app = utility_service.get_app_code().lower()
    sub_apps = utility_service.sub_apps()
    sub_apps = [x.lower() for x in list(sub_apps.keys())] if sub_apps else []

    # For all installed apps...
    for app, models in apps.all_models.items():

        # Completely ignore some framework models
        if app in ignored_apps:
            continue

        try:
            # Get or create app definition
            app_definition = ExportApp.get(app)
            if not app_definition:

                # Is this iteration for the current app (rather than a re-usable or sub-app)
                is_this_app = app == current_app

                # Is this iteration for a sub-application of the current app?
                is_sub_app = app in sub_apps

                # Which S3 app directory should the file be exported to?
                if is_sub_app:
                    export_app_code = app
                else:
                    export_app_code = current_app

                app_definition = ExportApp()
                app_definition.app_code = app
                app_definition.export_app = export_app_code
                app_definition.save()
                new_apps.append(app)

            # For each model in the app
            for mm in models:
                model_instance = apps.get_model(f"{app}.{mm}")

                # Get or create model definition
                model_definition = ExportModel.find(app_definition, mm)
                if not model_definition:
                    model_definition = ExportModel()
                    model_definition.app = app_definition
                    model_definition.name = mm
                    model_definition.save()
                    new_models.append(f"{app}.{mm}")

                # Determine the longest field name in this model
                # This is used for suggested Oracle column names
                field_list = model_instance._meta.fields
                # log.debug(f"###### FIELD LIST: {field_list}")
                field_names = [ff.db_column or ff.name for ff in field_list]
                longest_name = max([len(x) for x in field_names])
                # Determine the max length of the model name that can be used as part of column name
                model_name_limit = 30 - longest_name - 1  # -1 for an underscore
                # Minimum 5 characters of table name
                if model_name_limit < 5:
                    model_name_limit = 5  # column name will be truncated in suggested cognos name

                # For each field in the model
                for ff in field_list:

                    # Gather some field data (helpful to the Cognos team)
                    field_name = ff.db_column or ff.name
                    field_definition = ExportField.find(model_definition, field_name)
                    if not field_definition:
                        data_type = ff.db_type(connection)
                        key = ff.related_model.__name__ if ff.is_relation else None
                        if key:
                            key = f"Foreign Key to {key}"
                        elif field_name == "id":
                            key = "Primary Key"

                        stage_type = "varchar2(255)"
                        composite_type = data_type
                        if data_type == "text":
                            stage_type = "varchar2(4000)"
                            composite_type = "varchar2(4000)"
                        elif data_type in ["bool", "boolean"]:
                            composite_type = "varchar2(5)"
                        elif data_type in ('integer', 'bigint', 'bigserial'):
                            composite_type = 'number'
                        elif data_type == "datetime":
                            composite_type = 'date'

                        data_format = None
                        if data_type == "date":
                            data_format = "YYYY-MM-DD"
                        elif data_type == "datetime" or "timestamp" in data_type:
                            data_format = "YYYY-MM-DD HH24:MI:SS.FFFFFF"

                        # Save default field data
                        field_definition = ExportField()
                        field_definition.model = model_definition
                        field_definition.name = field_name
                        field_definition.data_type = data_type
                        field_definition.key = key
                        field_definition.suggested_cognos_name = f"{mm[:model_name_limit]}_{field_name}".upper()[:30]
                        field_definition.suggested_cognos_stage_type = stage_type
                        field_definition.suggested_cognos_type = composite_type
                        field_definition.description = ff.help_text
                        field_definition.format_data = data_format
                        field_definition.export_enabled = False
                        field_definition.save()
                        new_fields.append(f"{app}.{mm}.{ff}")
        except Exception as ee:
            error_service.record(ee, app)

    if new_apps:
        log.info(f"New applications: {len(new_apps)}")
    if new_models:
        log.info(f"New models: {len(new_models)}")
    if new_fields:
        field_log = "\n".join(new_fields)
        log.info(f"New fields: {len(new_fields)}\n{field_log}")


def get_export_map():
    prepare_export()
    return export_models(audit_mode=True)


def export_models(audit_mode=False):
    """
    Export all models (as defined by settings)

    In audit mode, returns a list of models that would be exported (but does not do the export)
    """
    log.trace({'audit_mode': audit_mode})
    results = {}

    # Map all existing data, and all data to be exported
    data_definitions = {}
    export_definitions = {}

    # For all installed apps...
    for app, models in apps.all_models.items():

        # Completely ignore some framework models
        if app in ignored_apps:
            continue

        # Only export defined applications
        app_definition = ExportApp.get(app)
        if not app_definition:
            log.warning(f"Undefined application is not being exported: {app}")
            results[app] = "Export not defined"
            continue

        if not app_definition.export_enabled:
            results[app] = "Export not enabled"
            continue

        results[app] = {}
        log.info(f"Exporting models for {app}")

        for mm in models:
            model_definition = ExportModel.find(app_definition, mm)
            if not model_definition:
                log.warning(f"Undefined model is not being exported: {mm}")
                results[app][mm] = "Ignored"
                continue
            if not app_definition.export_enabled:
                results[app][mm] = "Skipped"
                continue

            results[app][mm] = {"export_path": None, "fields": None}

            if not audit_mode:
                export_file_path = export_model(model_definition)
                if export_file_path:
                    results[app][mm]["export_path"] = export_file_path
                    results[app][mm]["fields"] = [x.name for x in model_definition.fields() if x.export_enabled]
                else:
                    results[app][mm] = "ERROR"

            else:
                results[app][mm] = [x.name for x in model_definition.fields() if x.export_enabled]

        # Create an export of the datamodel (for cognos team mapping)
        if not audit_mode:
            columns = [
                "AWS Table", "AWS Field", "AWS Data Type",
                "Field", "Stage Format", "Composite Table Format",
                "Key(s)", "Description", "Format"
            ]
            data = []
            last_model = None

            def auto_export_date_definition():
                return [
                    last_model,
                    "cognos_export_date",
                    "datetime",
                    f"{last_model.upper()}_EXPORT_DATE",
                    "varchar2(255)",
                    "date",
                    None,
                    "Timestamp of the data export",
                    "YYYY-MM-DD HH24:MI:SS.FFFFFF",
                ]

            fields = ExportField.objects.select_related("model").select_related("model__app").filter(
                model__app__export_app=app,
                export_enabled=True, model__export_enabled=True, model__app__export_enabled=True
            ).order_by("model__app__app_code", "model__name", "id")
            for ff in fields:
                if not last_model:
                    last_model = ff.model.name
                elif last_model != ff.model.name:
                    data.append(auto_export_date_definition())
                    data.append(["", "", "", "", "", "", "", "", ""])
                last_model = ff.model.name

                data.append([
                    ff.model.name,
                    ff.name,
                    ff.data_type,
                    ff.suggested_cognos_name,
                    ff.suggested_cognos_stage_type,
                    ff.suggested_cognos_type,
                    ff.key,
                    ff.description,
                    ff.format_data,
                ])
            data.append(auto_export_date_definition())

            # Write the file to S3
            env = utility_service.get_environment().lower()
            file_path = f'{app}/{env}/data_model.csv'
            export_path = _create_s3_file(file_path, data, columns)
            if export_path:
                results[app]["data_model_definition"] = export_path

    return results


def export_model(model_definition):
    """
    Example: model_name='dual_credit.IdentityCrisis'
    """
    log.trace([model_definition])
    try:
        export_app_code = model_definition.app.export_app
        model_name = f"{model_definition.app.app_code}.{model_definition.name}"
        model_instance = apps.get_model(model_name)
        model_fields = model_instance._meta.fields
        columns = [x.db_column or x.name for x in model_fields]

        enabled_fields = model_definition.enabled_fields()
        enabled_field_names = [x.name for x in enabled_fields]
        columns = [x for x in columns if x in enabled_field_names]

        # Add an export_date
        cognos_export_date = datetime.now()
        columns.append("cognos_export_date")

        data = []
        for result in model_instance.objects.all():
            row_data = []
            for field in model_fields:
                field_name = field.name

                # If only exporting certain fields, and this is not one of them
                if field_name not in columns:
                    continue

                field_value = getattr(result, field.name)

                # If field is empty, no processing needed
                if not field_value:
                    val = field_value

                # If field is a relation, and is mapped by a single key
                elif field.is_relation and field.to_fields and len(field.to_fields) == 1 and field.to_fields[0]:
                    val = getattr(field_value, field.to_fields[0])

                # If field is a relation, and mapped by multiple keys
                elif field.is_relation and field.to_fields and len(field.to_fields) > 1:
                    val = [getattr(field_value, x) for x in field.to_fields]

                # If field is relation with unknown key, assume 'id'
                elif field.is_relation and hasattr(field_value, 'id'):
                    val = getattr(field_value, 'id')

                # Otherwise, use raw field data
                else:
                    val = field_value

                # Add to this row's data
                row_data.append(val)

            # Append cognos_export_date to each row
            row_data.append(cognos_export_date)

            # Add to the full data-set
            data.append(row_data)

        # Create an in-memory file to be returned as attachment
        env = utility_service.get_environment().lower()
        # Modify model name for a better file name
        if '.' in model_name:
            pp = model_name.split('.')
            model_name = pp[len(pp)-1]
        model_name = utility_service.decamelize(model_name)
        file_name = f'{model_name}.csv'.lower()
        file_path = f'{export_app_code}/{env}/{file_name}'

        return _create_s3_file(file_path, data, columns)

    except Exception as ee:
        error_service.record(ee, model_definition)
        return False


def _create_s3_file(file_path, data, columns):
    # Create an in-memory file to be returned as attachment
    response = io.StringIO()
    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    # Write data in CSV format
    df = pandas.DataFrame(data, columns=columns)
    df.to_csv(response, index=False)

    response.seek(0)
    response.seek(0)

    # Save to S3
    status = _export_to_s3(file_path, response.read())
    log.info(f"{file_path} S3 Upload Status:\n{status}\n")
    if status['ResponseMetadata']['HTTPStatusCode'] == 200:
        return file_path
    else:
        return None


def _get_credentials():
    try:
        required_role = 'arn:aws:iam::921749119607:role/psu-bi-export-vpc-campus'
        session_name = 'Django-BI-Export'
        access_key = utility_service.get_setting('BI_EXPORT_ACCESS_KEY')
        secret_key = utility_service.get_setting('BI_EXPORT_SECRET_KEY')
        sts = boto3.client('sts', region_name='us-west-2', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        sts_response = sts.assume_role(RoleArn=required_role, RoleSessionName=session_name)
        credentials = sts_response.get('Credentials')
        return credentials.get('AccessKeyId'), credentials.get('SecretAccessKey'), credentials.get('SessionToken')
    except Exception as ee:
        error_service.record(ee, 'Unable to get S3 credentials')
        return None, None, None


def _get_s3_resource():
    try:
        key, secret, sid = _get_credentials()
        if key and secret and sid:
            return boto3.resource(
                's3', region_name='us-west-2', aws_access_key_id=key, aws_secret_access_key=secret, aws_session_token=sid
            )
    except Exception as ee:
        error_service.record(ee, 'Unable to get S3 resource')
    return None


def _export_to_s3(export_path, file_content):
    """
    https://stackoverflow.com/questions/40336918/how-to-write-a-file-or-data-to-an-s3-object-using-boto3
    https://stackoverflow.com/questions/15029666/exporting-items-from-a-model-to-csv-django-python
    """
    s3 = _get_s3_resource()
    bucket_name = 'psu-bi-export.wdt.pdx.edu'
    return s3.Object(bucket_name, export_path).put(Body=file_content)

    # {
    #     'ResponseMetadata': {
    #         'RequestId': 'B2068FBF555F437B',
    #         'HostId': 'JkyniuhAyL462cPy10VEbbE+pgdvMChht5+aZi1w2ni+Vg3O3rd+qWffPitosm+knODVQQpkj0U=',
    #         'HTTPStatusCode': 200,
    #         'HTTPHeaders': {
    #             'x-amz-id-2': 'JkyniuhAyL462cPy10VEbbE+pgdvMChht5+aZi1w2ni+Vg3O3rd+qWffPitosm+knODVQQpkj0U=',
    #             'x-amz-request-id': 'B2068FBF555F437B',
    #             'date': 'Tue, 19 Jan 2021 23:35:03 GMT',
    #             'etag': '"b10a8db164e0754105b7a99be72e3fe5"',
    #             'content-length': '0',
    #             'server': 'AmazonS3'
    #         },
    #         'RetryAttempts': 0
    #     },
    #     'ETag': '"b10a8db164e0754105b7a99be72e3fe5"'
    # }
