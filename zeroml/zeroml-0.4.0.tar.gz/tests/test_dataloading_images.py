from zeroml.dataloading.image.datasets import ImageClfAlbuDataset
from zeroml.dataloading.image.transforms import build_training_transform


def test_build_training_transform():
    transform = build_training_transform(224, model=None, augment='noaug')
    transform = build_training_transform(224, model='resnet18', augment='noaug')

    list(transform)
    list(transform)


def test_clf_albu_dataset(create_image_test_dataframe):

    df, base_path = create_image_test_dataframe

    transform = build_training_transform(224, model=None, augment='noaug')

    ds = ImageClfAlbuDataset(
        df, base_path=base_path, transform=transform, file_column='file_names', label_column='labels'
    )

    image, label = ds[5]

    assert label == 5
