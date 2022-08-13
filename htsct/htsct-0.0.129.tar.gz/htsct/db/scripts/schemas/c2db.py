from typing import Union

from pydantic import BaseModel


class C2db(BaseModel):
    ID: int
    Formula: Union[str, None] = None
    Material_class: Union[str, None] = None
    Space_group: Union[str, None] = None
    Magnetic: Union[str, None] = None
    Heat_of_formation: Union[float, None] = None
    Band_gap: Union[float, None] = None
    Crystal_type: Union[str, None] = None
    two_dimension_plasma_frequency_x: Union[float, None] = None
    two_dimension_plasma_frequency_y: Union[float, None] = None
    First_class_material: Union[str, None] = None
    Calculator: Union[str, None] = None
    Anisotropic_exchange_out_of_plane: Union[str, None] = None
    Area_of_unit_cell: Union[float, None] = None
    Band_gap_G0W0: Union[float, None] = None
    Band_gap_HSE06: Union[float, None] = None
    Topology: Union[str, None] = None
    Conduction_band_effective_mass_direction_1: Union[float, None] = None
    Conduction_band_effective_mass_direction_2: Union[float, None] = None
    Cond_band_minimum: Union[float, None] = None
    Conduction_band_minimum_G0W0: Union[float, None] = None
    Conduction_band_minimum_HSE06: Union[float, None] = None
    DOS_at_ef: Union[float, None] = None
    DOS_at_ef_no_soc: Union[float, None] = None
    Dir_band_gap: Union[float, None] = None
    Direct_band_gap_G0W0: Union[float, None] = None
    Direct_band_gap_HSE06: Union[float, None] = None
    Dir_gap_wo_soc: Union[float, None] = None
    Energy_above_convex_hull: Union[float, None] = None
    Exc_bind_energy: Union[float, None] = None
    Fermi_level: Union[float, None] = None
    Gap_wo_soc: Union[float, None] = None
    Magnetic_anisotropy_z_x: Union[float, None] = None
    Magnetic_anisotropy_z_y: Union[float, None] = None
    Magnetic_easy_axis: Union[str, None] = None
    Magnetic_moment: Union[float, None] = None
    Magnetic_state: Union[str, None] = None
    Material_has_inversion_symmetry: Union[str, None] = None
    Material_unique_ID: Union[str, None] = None
    Maximum_force: Union[float, None] = None
    Maximum_stress: Union[float, None] = None
    Maximum_value_of_S_z_at_magnetic_sites: Union[float, None] = None
    Minimum_eigenvalue_of_Hessian: Union[float, None] = None
    Monolayer_reported_DOI: Union[str, None] = None
    Nearest_neighbor_exchange_coupling: Union[float, None] = None
    Charge: Union[float, None] = None
    Number_of_atoms: Union[float, None] = None
    Number_of_nearest_neighbors: Union[float, None] = None
    n_spins: Union[float, None] = None
    Out_of_plane_dipole_along_plus_z_axis: Union[float, None] = None
    Path_to_collection_folder: Union[str, None] = None
    PBC: Union[str, None] = None
    Phonon_dynamic_stability_lowOrHigh: Union[str, None] = None
    Point_group: Union[str, None] = None
    Related_COD_id: Union[str, None] = None
    Unique_ID: Union[str, None] = None
    Related_ICSD_id: Union[str, None] = None
    Single_ion_anisotropy_out_of_plane: Union[float, None] = None
    Soc_total_energy_x_direction: Union[float, None] = None
    Soc_total_energy_y_direction: Union[float, None] = None
    Soc_total_energy_z_direction: Union[float, None] = None
    Space_group_number: Union[int, None] = None
    Speed_of_sound_x: Union[float, None] = None
    Speed_of_sound_y: Union[float, None] = None
    Static_interband_polarizability_x: Union[float, None] = None
    Static_interband_polarizability_y: Union[float, None] = None
    Static_interband_polarizability_z: Union[float, None] = None
    Static_lattice_polarizability_x: Union[float, None] = None
    Static_lattice_polarizability_y: Union[float, None] = None
    Static_lattice_polarizability_z: Union[float, None] = None
    Static_total_polarizability_x: Union[float, None] = None
    Static_total_polarizability_y: Union[float, None] = None
    Static_total_polarizability_z: Union[float, None] = None
    Stiffness_dynamic_stability_lowOrHigh: Union[str, None] = None
    Stiffness_tensor_11_component: Union[float, None] = None
    Stiffness_tensor_12_component: Union[float, None] = None
    Stiffness_tensor_13_component: Union[float, None] = None
    Stiffness_tensor_21_component: Union[float, None] = None
    Stiffness_tensor_22_component: Union[float, None] = None
    Stiffness_tensor_23_component: Union[float, None] = None
    Stiffness_tensor_31_component: Union[float, None] = None
    Stiffness_tensor_32_component: Union[float, None] = None
    Stiffness_tensor_33_component: Union[float, None] = None
    Stoichiometry: Union[str, None] = None
    Mass: Union[float, None] = None
    Thermodynamic_stability_level: Union[float, None] = None
    Age: Union[str, None] = None
    Energy: Union[float, None] = None
    Unique_identifier: Union[str, None] = None
    Username: Union[str, None] = None
    Vacuum_level: Union[float, None] = None
    Vacuum_level_difference: Union[float, None] = None
    Valence_band_effective_mass_direction_1: Union[float, None] = None
    Valence_band_effective_mass_direction_2: Union[float, None] = None
    Valence_band_maximum_G0W0: Union[float, None] = None
    Valence_band_maximum_HSE06: Union[float, None] = None
    Volume: Union[float, None] = None
    Work_function_avg_if_finite_dipole: Union[float, None] = None
    cif: Union[str, None] = None

    class Config:
        orm_mode = True


class C2dbQuery(BaseModel):
    id: Union[str, None] = None,
    skip: int = 0,
    limit: int = 100,
    min_band_gap: Union[float, None] = None,
    max_band_gap: Union[float, None] = None

    class Config:
        orm_mode = True


class C2dbResponseModel(BaseModel):
    id: str
    status: str
    code: int
    formula: Union[str, None] = None

    class Config:
        orm_mode = True
