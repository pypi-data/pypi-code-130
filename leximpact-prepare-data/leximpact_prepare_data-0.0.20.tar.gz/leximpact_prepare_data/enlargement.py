# AUTOGENERATED! DO NOT EDIT! File to edit: ../notebooks/retraitement_erfs-fpr/modules/enlarge_fake.ipynb.

# %% auto 0
__all__ = ["enlarge"]

# %% ../notebooks/retraitement_erfs-fpr/modules/enlarge_fake.ipynb 3
import pandas as pd


# %% ../notebooks/retraitement_erfs-fpr/modules/enlarge_fake.ipynb 6
def enlarge(erfs_r, N):

    # On décide de doubler le nombre d'individus, i.e. de foyers fiscaux
    erfs_true = erfs_r.copy(deep=True)
    erfs_fake = erfs_r.copy(deep=True)

    # Ajout d'une colonne pour repérer les individus que l'on ajoute
    erfs_true["fake_id"] = 0  # People are not fake <=> fake_id == 0
    erfs_fake["fake_id"] = 1  # People are fake <=> fake_id == 1

    # On concatène les dataframes à la suite N fois
    nb_de_ff_uniques = erfs_r["idfoy"].nunique()
    max_idfoy = max(erfs_r["idfoy"]) + 1

    # print(nb_de_ff_uniques, "nom", max(erfs_r["idfoy"]))

    erfs_enlarged = erfs_true.copy(deep=True).reset_index(drop=True)

    for i in range(2, N + 1):
        # On update l'ID des foyers fiscaux en gardant la même composition
        erfs_fake_i = erfs_fake.copy(deep=True)
        erfs_fake_i["idfoy"] = (
            erfs_fake["idfoy"] + (i - 1) * max_idfoy
        )  # Pour être sûr d'attribuer des idfoy distincts même s'ils ne se suivent pas tous
        erfs_fake_i["idfam"] = erfs_fake["idfam"] + (i - 1) * max_idfoy
        erfs_fake_i["idmen"] = erfs_fake["idmen"] + (i - 1) * max_idfoy
        erfs_enlarged = pd.concat([erfs_enlarged, erfs_fake_i])

    erfs_enlarged.reset_index(drop=True, inplace=True)

    # On divise les poids par N
    erfs_enlarged["wprm"] = erfs_enlarged["wprm"] / N

    # On vérifie qu'on a toujours le même total de poids
    print(
        "Poids avant enlargment : ",
        erfs_r["wprm"].sum(),
        ", Poids après : ",
        erfs_enlarged["wprm"].sum(),
        "Soit une différence de : ",
        100
        * (erfs_enlarged["wprm"].sum() - erfs_r["wprm"].sum())
        / erfs_r["wprm"].sum(),
        " %",
    )

    # On check
    nb_de_ff_uniques_final = erfs_enlarged["idfoy"].nunique()
    # print(nb_de_ff_uniques_final, "nom", max(erfs_enlarged["idfoy"]))

    print("Nombre final d'individus : ", len(erfs_enlarged))
    print("Nombre d'individus ajoutés' : ", erfs_enlarged["fake_id"].sum())
    print(
        "On a bien multiplié par ",
        nb_de_ff_uniques_final / nb_de_ff_uniques,
        "le nombre de foyers dans notre base",
    )
    print(
        "On a bien multiplié par ",
        len(erfs_enlarged) / len(erfs_r),
        " le nombre d'individus dans notre base",
    )

    return erfs_enlarged
