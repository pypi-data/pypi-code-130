from johnsnowlabs.abstract_base.lib_resolver import try_import_lib

if try_import_lib('sparknlp_jsl') and try_import_lib('sparknlp'):
    from sparknlp_jsl.annotator import *
    from sparknlp_jsl.base import *
    from sparknlp.base import *
    from sparknlp.annotator import *
    # import sparknlp_jsl.annotator.SentenceEntityResolverModel


else:
    pass
