"""Calculate Kolmogorov-Smirnov's Statistics on two groups of cells, testing whether their expression distributions for a given gene list are significantly different.
"""
# imports
from scipy.stats import ks_2samp
from pandas import DataFrame
import sys

def stats(adata, group_column, group_mutant, group_normal, gene_list = [], layer = None):
    """Calculate Kolmogorov-Smirnov's Statistics on two groups of cells for a given list of genes.

    Parameters
    ----------
    adata: anndata object
        Object containing single cell RNA-seq data.
    group_column: string
        A column in adata.obs containing group labels.
    group_mutant: string
        Name of the first group.
    group_normal: string
        Name of the second group.
    gene_list: list
        List of gene to perform statistical analysis on.
    layer: string
        Name of the adata layer to be used for calculation. Default is None. If default adata.X will be used for calculation.

    Returns
    -------
    table: DataFrame object (pandas)
        Index is the same as gene_list. Columns correspond to 1) KS statistic number, 2) p-value. If the KS statistic is small or the p-value is high, then we cannot reject the null hypothesis in favor of the alternative.
    """

    if len(gene_list) == 0:
        sys.exit('Please provide a non-empty gene_list parameter!')

    adata = adata[:,gene_list]
    table = DataFrame(index=gene_list)

    if not layer:
        table['ks-stat'] = 0
        table['ks-pval'] = 1
    else:
        table['ks-stat' + '_' + layer] = 0
        table['ks-pval' + '_' + layer] = 1

    for gene in gene_list:
        d1 = adata[adata.obs[group_column] == group_mutant]
        d2 = adata[adata.obs[group_column] == group_normal]
        if not layer:
            d1 = d1.to_df()[gene]
            d2 = d2.to_df()[gene]
        else: 
            d1 = d1.to_df(layer = layer)[gene]
            d2 = d2.to_df(layer = layer)[gene]

        ks = ks_2samp(d1, d2)

        if not layer:
            table.loc[gene, 'ks-stat'] = ks[0]
            table.loc[gene, 'ks-pval'] = ks[1]
        else:
            table.loc[gene, 'ks-stat' + '_' + layer] = ks[0]
            table.loc[gene, 'ks-pval' + '_' + layer] = ks[1]

    return(table)

# run when file is directly executed
if __name__ == '__main__':
    from .adata import dummy
    # create a dummy anndata object
    adata = dummy()
    gene_list = ['Gene_0', 'Gene_1', 'Gene_2']
    table = stats(adata, 'cell_type', 'Monocyte', 'B', gene_list = gene_list, layer = 'log_transformed')
    print(table)