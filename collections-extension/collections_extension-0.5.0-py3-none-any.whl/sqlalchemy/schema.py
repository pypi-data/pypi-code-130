from contextlib import suppress
from typing import Any, Mapping, Optional, Type

from ..native import Map

__all__ = [

]

with suppress(ImportError):
    from marshmallow import Schema
    from marshmallow_sqlalchemy.schema import SQLAlchemyAutoSchemaMeta, \
        SQLAlchemyAutoSchemaOpts
    from sqlalchemy.ext.declarative import DeclarativeMeta

    from .model import SqlalchemyModelMap


    def _create_schema_meta(
        sqlalchemy_cls: DeclarativeMeta,
        **meta_kwargs: Any,
    ) -> Type:
        """Create class, that will be used as 'Meta' attribute of marshmallow
        schema class (warning, it is not python-style metaclass)."""
        return type(
            f'{sqlalchemy_cls.__name__}SchemaMeta',
            (object,),
            {
                'model': sqlalchemy_cls,
                'include_fk': True,
                **meta_kwargs,
            },
        )


    def _create_schema_class(
        sqlalchemy_cls: DeclarativeMeta,
        **meta_kwargs: Any,
    ) -> SQLAlchemyAutoSchemaMeta:
        """Create schema, based on sqlalchemy declarative model class."""
        return SQLAlchemyAutoSchemaMeta(
            f'{sqlalchemy_cls.__name__}Schema',
            # It doesn`t inherit from ``SQLAlchemyAutoSchema`` marshmallow
            # sqlalchemy class, because this class requires sqlalchemy
            # session, but we have no it.
            (Schema,),
            {
                'OPTIONS_CLASS': SQLAlchemyAutoSchemaOpts,
                'Meta': _create_schema_meta(sqlalchemy_cls, **meta_kwargs),
            },
        )


    class SqlalchemyModelSchemaMap(Map[str, Schema]):
        """Marshmallow schema map for sqlalchemy declarative models."""
        __slots__ = ()

        @classmethod
        def from_sqlalchemy_model_map(
            cls,
            sqlalchemy_model_map: SqlalchemyModelMap,
            schema_kwargs: Optional[Mapping[str, Any]] = None,
            meta_kwargs: Optional[Mapping[str, Any]] = None,
        ) -> 'SqlalchemyModelSchemaMap':
            """Create schema map from existing model map."""
            if schema_kwargs is None:
                schema_kwargs = {}

            if meta_kwargs is None:
                meta_kwargs = {}

            return cls({
                # Instantly initialization of marshmallow schemas.
                key: _create_schema_class(value, **meta_kwargs)(
                    **schema_kwargs,
                )
                for key, value in sqlalchemy_model_map.items()
            })


    __all__.append(SqlalchemyModelSchemaMap.__name__)
