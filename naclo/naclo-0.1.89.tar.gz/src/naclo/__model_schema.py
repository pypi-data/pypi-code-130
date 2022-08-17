from schema import Schema, Or


bleach_schema = Schema({
    # Structure data
    'structure_col': str,
    'structure_type': Or('smiles', 'mol'),

    # Target data
    'target_col': str,
    'input_units': Or('mixed', '-log(M)', 'M', 'mM', 'µM', 'uM', 'nM'),
    'output_units': Or('-log(M)', 'M', 'mM', 'µM', 'uM', 'nM'),
    'units_col': str,
    'drop_na_units': bool,

    # Formatting
    'format_settings': {
        'duplicate_compounds': Or('average', 'remove', 'keep'),
        'append_columns': [Or('smiles', 'mol', 'inchi_key', 'mw')],
        'remove_header_chars': str,
        'remove_na_targets': bool
    },

    # Chemistry
    'chem_settings': {
        'neutralize_charge': bool,
        'desalt': bool,
        'fragment_filter': Or('carbon_count', 'atom_count', 'mw', 'none', '')
    }
})
