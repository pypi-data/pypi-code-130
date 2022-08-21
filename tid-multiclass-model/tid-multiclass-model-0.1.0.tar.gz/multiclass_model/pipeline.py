from config.core import config
from feature_engine.encoding import OrdinalEncoder
from feature_engine.selection import DropFeatures
from processing.data_manager import load_json
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline, make_pipeline, make_union

from multiclass_model.config.core import config
from multiclass_model.custom_functions import custom_functions as cf

TypeEnt_number_maps = load_json(file_name=config.app_config.json_file_TypeEnt)
regex_to_use = load_json(file_name=config.app_config.json_file_regexs)
gbc_parameters = load_json(file_name=config.app_config.json_file_gbc_paramters)

feature_pipeline = Pipeline(
    [
        (
            "NumberOfItemsInDescription_ready",
            cf.get_items_in_description(
                variables=config.model_config.single_text_column,
                new_variable_names=config.model_config.items_in_description_name,
            ),
        ),
        (
            "GetKeyWord_prepro",
            cf.get_keywords_from_description(
                variables=config.model_config.double_text_column,
                new_variable_names=config.model_config.keywords_and_company,
                keywords=[regex_to_use["keywords_rx"], regex_to_use["type_company_rx"]],
            ),
        ),
        (
            "TimeDate_features",
            cf.get_date_features(
                variables=config.model_config.single_text_column,
                date_regex=regex_to_use["dates_rx"],
                year_regex=regex_to_use["year_rx"],
                moth_regex=regex_to_use["month_rx"],
            ),
        ),
        (
            "splitter",
            cf.splitter(
                variables=config.model_config.split_features,
                new_variable_names=config.model_config.split_features_names,
            ),
        ),
        (
            "GCL_Code-cardinal-ordering",
            OrdinalEncoder(
                encoding_method="ordered", variables=config.model_config.ordinal_encode
            ),
        ),
        (
            "TypeEnt_number_map_modes",
            cf.Mapper(
                variables=config.model_config.mapper_encode,
                mappings=TypeEnt_number_maps,
            ),
        ),
        (
            "drop_features",
            DropFeatures(features_to_drop=config.model_config.drop_features),
        ),
        (
            "Fill_na",
            cf.Custom_Fillna(
                variables=config.model_config.fillna_features, fill_value=0
            ),
        ),
    ]
)

category_prediction_pipeline = make_pipeline(
    *feature_pipeline, OneVsRestClassifier(GradientBoostingClassifier(**gbc_parameters))
)
