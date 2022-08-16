import argparse

from .dataframe import create_dataframe
from .train_test_split import data_split, dataset


def get_args():
    """
    Get arguments from command line
    """
    parser = argparse.ArgumentParser(
        description="Split the dataset into train and test set"
    )
    parser.add_argument("--path", type=str, help="path to the dataset")
    parser.add_argument("--method", type=str, default="kfold", help="split ratio")
    parser.add_argument("--save", action="store_true", help="save the dataframe")
    parser.add_argument("--nsplit", type=int, default=10, help="number of folds")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument(
        "--splitsize",
        type=float,
        default=0.98,
        help="If method is not kfold, this is the split ratio",
    )
    return parser.parse_args()


class PrepareDataset:
    """
    Prepare the dataset for train, validation and test.

    Usage:
    >>> from bpc.dataset import PrepareDataset
    >>> dataset = PrepareDataset()
    >>> dataset.prepare_data(path='path/to/dataset', method='kfold', save=True)
    """
    @staticmethod
    def prepare_data(
        path: str,
        method: str,
        save: bool = False,
        nsplits: int = 10,
        seed: int = 42,
        splitsize: float = 0.98,
    ) -> None:
        """
        Prepare the dataset

        Args:
            path (str): path to the dataset
            method (str): split method
            save (bool): save the dataframe
            nsplits (int): number of folds
            seed (int): random seed
            splitsize (float): split ratio

        Returns:
            train_dataset(pd.DataFrame): train dataset
            val_dataset(pd.DataFrame): validation dataset
            test_dataset(pd.DataFrame): test dataset

        Usage:
            >>> from bpc import prepare_data
            >>> train_dataset, val_dataset, test_dataset = prepare_data(
            ...     path='path/to/dataset',
            ...     method='kfold',
            ...     save=True,
            ...     nsplits=10,
            ...     seed=42,
            ...     splitsize=0.98,
            ... )

        """
        df = create_dataframe(path, save=save)
        train_data, val_data, test_data = data_split(
            df, method=method, nsplits=nsplits, seed=seed, splitsize=splitsize
        )
        for p, df in zip(["train", "val", "test"], [train_data, val_data, test_data]):
            dataset(p, df)
        print("[INFO] Done")


if __name__ == "__main__":
    args = get_args()
    PrepareDataset.prepare_data(args.path, args.method, args.save, args.nsplit, args.seed, args.splitsize)
    print("[INFO] Done")
