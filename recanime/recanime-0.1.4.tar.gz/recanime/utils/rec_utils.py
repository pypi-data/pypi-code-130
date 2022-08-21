import os
import pickle


from recanime.schema.user import ExistedUserAttributesVector


DATA_INPUT_DIR = os.getenv("DATA_INPUT_DIR", default='./data')


def get_existed_user_attributes_vector() -> ExistedUserAttributesVector:
    with open(DATA_INPUT_DIR + "/user_with_vector_dict.pickle", 'rb') as f:
        user_with_vector_dict = pickle.load(f)

    with open(DATA_INPUT_DIR + "/genre_index_mapping.pickle", 'rb') as f:
        genre_index_mapping = pickle.load(f)

    return ExistedUserAttributesVector(
        user_ids=user_with_vector_dict['user_id'],
        user_attributes_vector=user_with_vector_dict['genre_vector'],
        attribute_map_to_vector_position=genre_index_mapping["genre2genre_idx"],
        vector_position_map_to_attribute=genre_index_mapping["genre_idx2genre"]
    )
