from sklearn.model_selection import train_test_split

from scoringmodel.config.core import config
from scoringmodel.pipeline import feature_pipeline, modeling
from scoringmodel.processing.data_manager import load_dataset, save_model


def run_training() -> None:
    """Train the model."""
    data = load_dataset(file_name=config.app_config.training_data_file)
    data = feature_pipeline(data)

    x_train, x_valid, y_train, y_valid = train_test_split(
        data[config.model_config.features],
        data[config.model_config.target],
        test_size=config.model_config.test_size,
        random_state=config.model_config.random_state
    )

    model = modeling(x_train, x_valid, y_train, y_valid)

    save_model(model_to_persist=model)

    return model


if __name__ == "__main__":
    run_training()