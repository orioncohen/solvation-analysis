"""
solvation.py
An MDAnalysis rmodule for solvation analysis.

Handles the primary functions
"""


# atom selection functions
import warnings
import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import distances
import nglview as nv

# all functions
"get_atom_group, get_n_shells, \
    get_cation_anion_shells, get_closest_n_mol, get_radial_shell, \
    get_counts, get_pair_type, count_dicts"


def visualize(selection):
    mda_view = nv.show_mdanalysis(selection)
    mda_view.add_representation('licorice', selection='Li', color='blue')
    return mda_view.display()


def get_atom_group(u, selection):
    """
    Casts an Atom, AtomGroup, Residue, or ResidueGroup to AtomGroup.

    Parameters
    ----------
        u : Universe
            universe that contains central species
        selection: Atom, AtomGroup, Residue, or ResidueGroup

    Returns
    -------
        AtomGroup

    """
    assert isinstance(selection, (mda.core.groups.Residue,
                                  mda.core.groups.ResidueGroup,
                                  mda.core.groups.Atom,
                                  mda.core.groups.AtomGroup)), \
        "central_species must be one of the preceding types"
    if isinstance(selection, (mda.core.groups.Residue, mda.core.groups.ResidueGroup)):
        selection = selection.atoms
    if isinstance(selection, mda.core.groups.Atom):
        selection = u.select_atoms(f'index {selection.index}')
    return selection


# test this
def get_n_shells(u, central_species, n_shell=2, radius=3, ignore_atoms=None):
    """
    A list containing the nth shell at the nth index. Note that the shells have 0 intersection.
    For example, calling get_n_shells with n_shell = 2 would return: [central_species, first_shell, second_shell].
    This scales factorially so probably don't go over n_shell = 3

    Parameters
    ----------
        u : Universe
            universe that contains central species
        central_species : Atom, AtomGroup, Residue, or ResidueGroup
        n_shell : int
            number of shells to return
        radius : float or int
            radius used to select atoms in next shell
        ignore_atoms : AtomGroup
            these atoms will be ignored

    Returns
    -------
        List[AtomGroups] :
            List of n shells

    """
    if n_shell > 3:
        warnings.warn('get_n_shells scales factorially, very slow')
    central_species = get_atom_group(u, central_species)
    if not ignore_atoms:
        ignore_atoms = u.select_atoms('')


def get_closest_n_mol(u, central_species, n_mol=5, radius=3):
    """
    Returns the closest n molecules to the central species, an array of their resids,
    and an array of the distance of the closest atom in each molecule.

    Parameters
    ----------
        u : Universe
            universe that contains central species
        central_species : Atom, AtomGroup, Residue, or ResidueGroup
        n_mol : int
            The number of molecules to return
        radius : float or int
            an initial search radius to look for closest n mol

    Returns
    -------
        AtomGroup (molecules), np.Array (resids), np.Array (distances)

    """
    central_species = get_atom_group(u, central_species)
    coords = central_species.center_of_mass()
    str_coords = " ".join(str(coord) for coord in coords)
    partial_shell = u.select_atoms(f'point {str_coords} {radius}')
    shell_resids = partial_shell.resids
    if len(np.unique(shell_resids)) < n_mol + 1:
        return get_closest_n_mol(u, central_species, n_mol, radius + 1)
    radii = distances.distance_array(coords, partial_shell.positions, box=u.dimensions)[0]
    ordering = np.argsort(radii)
    ordered_resids = shell_resids[ordering]
    closest_n_resix = np.sort(np.unique(ordered_resids, return_index=True)[1])[0:n_mol + 1]
    str_resids = " ".join(str(resid) for resid in ordered_resids[closest_n_resix])
    full_shell = u.select_atoms(f'resid {str_resids}')
    return full_shell, ordered_resids[closest_n_resix], radii[ordering][closest_n_resix]


def get_radial_shell(u, central_species, radius):
    """
    Returns all molecules with atoms within the radius of the central species. (specifically, within the radius
    of the COM of central species).

    Parameters
    ----------
        u : Universe
            universe that contains central species
        central_species : Atom, AtomGroup, Residue, or ResidueGroup
        radius : float or int
            radius used for atom selection

    Returns
    -------
        full_shell : AtomGroup

    """
    central_species = get_atom_group(u, central_species)
    coords = central_species.center_of_mass()
    str_coords = " ".join(str(coord) for coord in coords)
    partial_shell = u.select_atoms(f'point {str_coords} {radius}')
    full_shell = partial_shell.residues.atoms
    return full_shell




def canvas(with_attribution=True):
    """
    Placeholder function to show example docstring (NumPy format)

    Replace this function and doc string for your own project

    Parameters
    ----------
    with_attribution : bool, Optional, default: True
        Set whether or not to display who the quote is from

    Returns
    -------
    quote : str
        Compiled string including quote and optional attribution
    """

    quote = "The code is but a canvas to our imagination."
    if with_attribution:
        quote += "\n\t- Adapted from Henry David Thoreau"
    return quote


if __name__ == "__main__":
    # Do something if this file is invoked on its own
    print(canvas())
