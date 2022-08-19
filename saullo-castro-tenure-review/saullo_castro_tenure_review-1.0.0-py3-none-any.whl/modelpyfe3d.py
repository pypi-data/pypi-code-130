"""
Interface with PyFE3D (:mod:`saullo_castro_tenure_review.modelpyfe3d`)
======================================================================

.. currentmodule:: saullo_castro_tenure_review.modelpyfe3d

"""
import numpy as np
from scipy.sparse import coo_matrix
from pyNastran.bdf.bdf import read_bdf
from pyfe3d import (BeamC, BeamCData, BeamCProbe, Quad4R, Quad4RData,
        Quad4RProbe, Tria3R, Tria3RData, Tria3RProbe, DOF, INT, DOUBLE)
from pyfe3d.beamprop import BeamProp
from pyfe3d.shellprop_utils import isotropic_plate


def conm2_on_rbe3(mesh, conm2, rbe3):
    assert rbe3.type == 'RBE3'
    assert len(rbe3.dependent_nodes) == 1
    xyz = []
    weights = []
    nids = []
    for weight, Gijs in zip(rbe3.weights, rbe3.Gijs_node_ids):
        for nid in Gijs:
            xyz.append(mesh.nodes[nid].xyz)
            weights.append(weight)
            nids.append(nid)
    weights = np.array(weights)
    rCG = np.mean(xyz, axis=0)
    r_i = xyz - rCG
    r_iXY = r_i.copy()
    r_iXZ = r_i.copy()
    r_iYZ = r_i.copy()

    r_iXY[:, 2] = 0
    r_iXZ[:, 1] = 0
    r_iYZ[:, 0] = 0

    mass = conm2.mass
    I11, I21, I22, I31, I32, I33 = conm2.I

    dnode_id = rbe3.dependent_nodes[0]
    dnode = mesh.nodes[dnode_id]
    r_d = dnode.xyz - rCG
    # NOTE from reference node to CG
    ICG11 = I11 + (r_d[1]**2 + r_d[2]**2)*mass
    ICG22 = I22 + (r_d[0]**2 + r_d[2]**2)*mass
    ICG33 = I33 + (r_d[0]**2 + r_d[1]**2)*mass
    # TODO what about the off-diagonal terms?

    # NOTE assuming no moments applied at RBE3
    # M[DOF*pos+3, DOF*pos+3] += -I11
    # M[DOF*pos+3, DOF*pos+4] += -I21
    # M[DOF*pos+3, DOF*pos+5] += -I31
    # M[DOF*pos+4, DOF*pos+3] += -I21
    # M[DOF*pos+4, DOF*pos+4] += -I22
    # M[DOF*pos+4, DOF*pos+5] += -I32
    # M[DOF*pos+5, DOF*pos+3] += -I31
    # M[DOF*pos+5, DOF*pos+4] += -I32
    # M[DOF*pos+5, DOF*pos+5] += -I33

    # NOTE from CG to independent_nodes

    factor_i = weights/weights.sum()
    I11_i = (ICG11 + mass*(r_i[:, 1]**2 + r_i[:, 2]**2))*factor_i
    I22_i = (ICG22 + mass*(r_i[:, 0]**2 + r_i[:, 2]**2))*factor_i
    I33_i = (ICG33 + mass*(r_i[:, 0]**2 + r_i[:, 1]**2))*factor_i
    mass_i = mass*factor_i
    assert np.isclose(mass_i.sum(), mass)

    # TODO how to treat the off-diagonal terms?

    return nids, mass_i, I11_i, I22_i, I33_i


class ModelPyFE3D(object):
    r"""
    Attributes
    ----------
    TODO

    """
    __slots__ = [
            'ncoords', 'nids', 'nid_pos',
            'elements',
            'list_Quad4R', 'list_Tria3R', 'list_Beam',
            'beamLRProbe',
            'quad4RProbe',
            'tria3RProbe',
            'N',
            'dict_prop',
            'bu', 'bk',
            'KC0', 'M',
            'F',
            'K6ROT',
            ]

    def __init__(self):
        self.K6ROT = 100.

    def read_nastran(self, input_file):
        mesh = read_bdf(input_file, debug=False)
        num_cbeam = 0
        num_cquad4 = 0
        num_ctria3 = 0
        unique_nids = set()
        dict_prop = {}
        self.dict_prop = dict_prop
        for eid, elem in mesh.elements.items():
            unique_nids.update(elem.node_ids)
            if elem.type == 'CBEAM':
                num_cbeam += 1
            if elem.type == 'CQUAD4':
                num_cquad4 += 1
            if elem.type == 'CTRIA3':
                num_ctria3 += 1
            prop = elem.pid_ref
            mat = prop.mid_ref
            if prop.pid not in dict_prop:
                if prop.type == 'PBEAML':
                    if prop.beam_type == 'BAR':
                        dz, dy = prop.dim[0]
                        A = dy * dz
                        Iyy = dz**3*dy/12
                        Izz = dy**3*dz/12
                        a = max(dy, dz)
                        b = min(dy, dz)
                        beta_table = np.asarray([
                            [1.0, 0.141],
                            [1.5, 0.196],
                            [2.0, 0.229],
                            [2.5, 0.249],
                            [3.0, 0.263],
                            [4.0, 0.281],
                            [5.0, 0.291],
                            [6.0, 0.299],
                            [10.0, 0.312],
                            [1e6, 0.333]])
                        beta = np.interp(a/b, beta_table[:, 0], beta_table[:, 1])
                        J = beta*a*b**3
                        Iyz = 0
                        # TODO Iyz for rotated rectangular sections
                        # TODO warping constants not yet supported by pyfe3d
                    elif prop.beam_type == 'BOX':
                        dz, dy, hz, hy = prop.dim[0]
                        A = dy*dz - (dz - 2*hz)*(dy - 2*hy)
                        Iyy = dz**3*dy/12 - (dz - 2*hz)**3*(dy - 2*hy)/12
                        Izz = dy**3*dz/12 - (dy - 2*hy)**3*(dz - 2*hz)/12
                        J = Iyy + Izz #FIXME
                        Iyz = 0
                        # TODO Iyz for rotated rectangular sections
                        # TODO warping constants not yet supported by pyfe3d
                    elif prop.beam_type == 'T':
                        d1, d2, d3, d4 = prop.dim[0]
                        A = d1*d3 + (d2 - d3)*d4
                        Iyy = d1**3*d3/12 + d4**3*(d2 - d3)/12
                        Izz = d3**3*d1/12 + (d2 - d3)**3*d4/12 + (d2 - d3)*d4*(d3/2 + (d2 - d3)/2)**2
                        J = Iyy + Izz #FIXME
                        Iyz = 0
                    elif prop.beam_type == 'L':
                        d1, d2, d3, d4 = prop.dim[0]
                        A = d3*d1 + (d2 - d3)*d4
                        Iyy = d4**3*d2/12 + (d1 - d4)**3*d3/12 + ((d1 - d4)/2 + d4/2)**2
                        Izz = d3**3*d1/12 + (d2 - d3)**3*d4/12 + ((d2 - d3)/2 + d3/2)**2
                        J = Iyy + Izz #FIXME
                        Iyz = 0
                        # TODO
                    p = BeamProp()
                    p.A = A
                    p.E = mat.e
                    scf = 5/6.
                    p.G = scf*mat.e/2/(1+mat.nu)
                    p.Iyy = Iyy
                    p.Izz = Izz
                    p.Iyz = Iyz
                    p.J = J
                    p.intrho = mat.rho*prop.Area()
                    p.intrhoz2 = mat.rho*Iyy
                    p.intrhoy2 = mat.rho*Izz
                    p.intrhoyz = mat.rho*Iyz
                    dict_prop[prop.pid] = p
                elif prop.type == 'PSHELL':
                    p = isotropic_plate(thickness=prop.t, E=mat.e, nu=mat.nu,
                            calc_scf=True, rho=mat.rho)
                    dict_prop[prop.pid] = p
                else:
                    raise NotImplementedError('TODO add more properties')

        beamLRData = BeamCData()
        beamLRProbe = BeamCProbe()
        quad4RData = Quad4RData()
        quad4RProbe = Quad4RProbe()
        tria3RData = Tria3RData()
        tria3RProbe = Tria3RProbe()
        self.beamLRProbe = beamLRProbe
        self.quad4RProbe = quad4RProbe
        self.tria3RProbe = tria3RProbe

        size_KC0 = (beamLRData.KC0_SPARSE_SIZE*num_cbeam +
                    quad4RData.KC0_SPARSE_SIZE*num_cquad4 +
                    tria3RData.KC0_SPARSE_SIZE*num_ctria3)
        size_M = (beamLRData.M_SPARSE_SIZE*num_cbeam +
                  quad4RData.M_SPARSE_SIZE*num_cquad4 +
                  tria3RData.M_SPARSE_SIZE*num_ctria3)
        KC0r = np.zeros(size_KC0, dtype=INT)
        KC0c = np.zeros(size_KC0, dtype=INT)
        KC0v = np.zeros(size_KC0, dtype=DOUBLE)
        Mr = np.zeros(size_M, dtype=INT)
        Mc = np.zeros(size_M, dtype=INT)
        Mv = np.zeros(size_M, dtype=DOUBLE)

        N = DOF*len(unique_nids)
        self.N = N
        print('# number of CBEAM elements:', num_cbeam)
        print('# number of CQUAD4 elements:', num_cquad4)
        print('# number of CTRIA3 elements:', num_ctria3)
        print('# degrees-of-freedom:', N)
        nids = sorted(list(unique_nids))
        nid_pos = dict(zip(nids, np.arange(len(nids))))

        ncoords = np.array([mesh.nodes[nid].xyz for nid in nids])
        ncoords_flatten = ncoords.flatten()
        self.ncoords = ncoords
        self.nids = nids
        self.nid_pos = nid_pos

        # creating elements and populating global stiffness
        self.elements = {}

        init_k_KC0 = 0
        init_k_M = 0

        self.list_Beam = []
        for eid, elem in mesh.elements.items():
            if elem.type != 'CBEAM':
                continue
            n1, n2 = elem.node_ids
            pos1 = nid_pos[n1]
            pos2 = nid_pos[n2]
            beam = BeamC(beamLRProbe)
            beam.eid = eid
            beam.init_k_KC0 = init_k_KC0
            beam.init_k_M = init_k_M
            beam.n1 = n1
            beam.n2 = n2
            beam.c1 = DOF*pos1
            beam.c2 = DOF*pos2
            vec = elem.get_x_g0_defaults()
            beam.update_rotation_matrix(vec[0], vec[1], vec[2], ncoords_flatten)
            beam.update_probe_xe(ncoords_flatten)
            prop = dict_prop[elem.pid]
            beam.update_KC0(KC0r, KC0c, KC0v, prop)
            beam.update_M(Mr, Mc, Mv, prop)
            init_k_KC0 += beamLRData.KC0_SPARSE_SIZE
            init_k_M += beamLRData.M_SPARSE_SIZE
            self.list_Beam.append(beam)
            self.elements[eid] = beam

        self.list_Quad4R = []
        for eid, elem in mesh.elements.items():
            if elem.type != 'CQUAD4':
                continue
            n1, n2, n3, n4 = elem.node_ids
            pos1 = nid_pos[n1]
            pos2 = nid_pos[n2]
            pos3 = nid_pos[n3]
            pos4 = nid_pos[n4]
            r1 = ncoords[pos1]
            r2 = ncoords[pos2]
            r3 = ncoords[pos3]
            prop = dict_prop[elem.pid]
            quad = Quad4R(quad4RProbe)
            quad.alphat = self.K6ROT*1e-6/prop.A66*prop.h
            quad.n1 = n1
            quad.n2 = n2
            quad.n3 = n3
            quad.n4 = n4
            quad.c1 = DOF*nid_pos[n1]
            quad.c2 = DOF*nid_pos[n2]
            quad.c3 = DOF*nid_pos[n3]
            quad.c4 = DOF*nid_pos[n4]
            quad.init_k_KC0 = init_k_KC0
            quad.init_k_M = init_k_M
            quad.update_rotation_matrix(ncoords_flatten)
            quad.update_probe_xe(ncoords_flatten)
            quad.update_KC0(KC0r, KC0c, KC0v, prop)
            quad.update_M(Mr, Mc, Mv, prop)
            init_k_KC0 += quad4RData.KC0_SPARSE_SIZE
            init_k_M += quad4RData.M_SPARSE_SIZE
            self.list_Quad4R.append(quad)
            self.elements[eid] = quad

        self.list_Tria3R = []
        for eid, elem in mesh.elements.items():
            if elem.type != 'CTRIA3':
                continue
            n1, n2, n3 = elem.node_ids
            pos1 = nid_pos[n1]
            pos2 = nid_pos[n2]
            pos3 = nid_pos[n3]
            r1 = ncoords[pos1]
            r2 = ncoords[pos2]
            r3 = ncoords[pos3]
            prop = dict_prop[elem.pid]
            tria = Tria3R(tria3RProbe)
            tria.alphat = self.K6ROT*1e-6/prop.A66*prop.h
            tria.n1 = n1
            tria.n2 = n2
            tria.n3 = n3
            tria.c1 = DOF*nid_pos[n1]
            tria.c2 = DOF*nid_pos[n2]
            tria.c3 = DOF*nid_pos[n3]
            tria.init_k_KC0 = init_k_KC0
            tria.init_k_M = init_k_M
            tria.update_rotation_matrix(ncoords_flatten)
            tria.update_probe_xe(ncoords_flatten)
            tria.update_KC0(KC0r, KC0c, KC0v, prop)
            tria.update_M(Mr, Mc, Mv, prop)
            init_k_KC0 += tria3RData.KC0_SPARSE_SIZE
            init_k_M += tria3RData.M_SPARSE_SIZE
            self.list_Tria3R.append(tria)
            self.elements[eid] = tria


        KC0 = coo_matrix((KC0v, (KC0r, KC0c)), shape=(N, N)).tocsc()
        M = coo_matrix((Mv, (Mr, Mc)), shape=(N, N)).tocsc()
        self.KC0 = KC0
        self.M = M

        # treating concentrated masses

        for conm in mesh.masses.values():
            if conm.cid != 0:
                raise NotImplementedError('TODO')
            if conm.type != 'CONM2':
                raise NotImplementedError('TODO')
            pos = nid_pos.get(conm.nid)
            if pos is None:
                flag = False
                for rbe3 in mesh.rigid_elements.values():
                    if rbe3.dependent_nodes[0] == conm.nid:
                        flag = True
                        break
                if not flag:
                    print(conm.nid)
                    raise NotImplementedError('TODO')
                nids, mass_i, I11_i, I22_i, I33_i = conm2_on_rbe3(mesh, conm, rbe3)
            else:
                nids = [conm.nid]
                mass_i = [conm.mass]
                I11, I21, I22, I31, I32, I33 = conm.I
                I11_i, I22_i, I33_i = [I11], [I22], [I33]

            for nid, mass, I11, I22, I33 in zip(nids, mass_i, I11_i, I22_i, I33_i):
                pos = nid_pos[nid]
                for i in range(3):
                    M[DOF*pos+i, DOF*pos+i] += mass
                # TODO out-of-diagonal terms
                # M[DOF*pos+3, DOF*pos+3] += I11
                # M[DOF*pos+3, DOF*pos+4] += I21
                # M[DOF*pos+3, DOF*pos+5] += I31
                # M[DOF*pos+4, DOF*pos+3] += I21
                # M[DOF*pos+4, DOF*pos+4] += I22
                # M[DOF*pos+4, DOF*pos+5] += I32
                # M[DOF*pos+5, DOF*pos+3] += I31
                # M[DOF*pos+5, DOF*pos+4] += I32
                # M[DOF*pos+5, DOF*pos+5] += I33

        print('# structural matrices created')

        # applying boundary conditions

        self.bu = {}
        self.bk = {}
        for spcid, spclist in mesh.spcs.items():
            bk = np.zeros(N, dtype=bool) # array to store known DOFs
            for spc in spclist:
                if isinstance(spc.components, list):
                    components = spc.components[0]
                else:
                    components = spc.components
                for component in components:
                    component = int(component)-1
                    for nid in spc.node_ids:
                        pos = nid_pos.get(nid)
                        if pos is not None:
                            bk[DOF*pos + component] = True
            bu = ~bk
            self.bu[spcid] = bu
            self.bk[spcid] = bk
        print('# boundary conditions created')

        # reading loads
        self.F = {}
        for loadid, loadlist in mesh.loads.items():
            F = np.zeros(N, dtype=DOUBLE)
            for load in loadlist:
                if load.type == 'PLOAD1': # NOTE load in beam elements
                    nid1, nid2 = load.eid_ref.nodes
                    pos1, pos2 = nid_pos.get(nid1), nid_pos.get(nid2)
                    assert (pos1 is not None) and (pos2 is not None), 'nodes of element %d not found' % load.eid

                    assert load.load_type[-1] != 'E' # NOTE not one of 'FXE', 'FYE', 'FZE', 'MXE', 'MYE', 'MZE'
                    if load.load_type == 'FX':
                        dof = 0
                    elif load.load_type == 'FY':
                        dof = 1
                    elif load.load_type == 'FZ':
                        dof = 2
                    elif load.load_type == 'MX':
                        dof = 3
                    elif load.load_type == 'MY':
                        dof = 4
                    elif load.load_type == 'MZ':
                        dof = 5

                    #if load.scale == 'FR':
                        #force_n1 = (1 - load.x1)*load.p1
                        #force_n2 = (load.x2 - 1)*load.p2
#
                        #force_n2 = (1 - load.x1)*load.p1 + (load.x2 - 1)*load.p2

            bu = ~bk
            self.bu[spcid] = bu
            self.bk[spcid] = bk
        print('# loads created')

        return self


def plot3d_pyvista(model, displ_vec=None, contour_vec=None,
        contour_label='vec', contour_colorscale='coolwarm', background='white'):
    """Plot results using pyvista

    Parameters
    ----------
    displ_vec : array-like
        Nodal displacements to be applied to the nodal coordinates in order to visualize the deformed model.
    contour_vec : array-like
        Nodal or element-wise output to be displayed as a contour plot on top of the undeformed mesh.
        For nodal output, the function expects the order of attr:`.ModelPyFE3D.ncoords`.
        For element-wise output, the function expects the element outputs in the following order of elements:

        - :attr:`ModelPyFE3D.list_Quad4R`
        - :attr:`ModelPyFE3D.list_Tria3R`

    contour_label : str
        Name of contour being displayed.
    contour_colorscale : str
        Name of the colorscale.

    Returns
    -------
    plotter : `pyvista.Plotter` object
        A plotter object that is ready to be modified, or shown with ``plotter.show()``.

    """
    import pyvista as pv

    # NOTE needs ipygany and pythreejs packages (pip install pyvista pythreejs ipygany --upgrade)
    nid_pos = model.nid_pos
    ncoords = model.ncoords

    intensitymode = None
    if contour_vec is not None:
        if len(contour_vec) == len(ncoords):
            intensitymode = 'vertex'
        elif len(contour_vec) == len(model.list_Quad4R) + len(model.list_Tria3R):
            intensitymode = 'cell'
        else:
            raise RuntimeError('coutour_vec must be either a nodal or element output')

    plotter = pv.Plotter(off_screen=False)
    faces_quad = []
    for q in model.list_Quad4R:
        faces_quad.append([4, nid_pos[q.n1], nid_pos[q.n2], nid_pos[q.n3], nid_pos[q.n4]])
    faces_quad = np.array(faces_quad)
    quad_plot = pv.PolyData(ncoords, faces_quad)
    if contour_vec is not None:
        if intensitymode == 'vertex':
            quad_plot[contour_label] = contour_vec
        else:
            quad_plot[contour_label] = contour_vec[:len(model.list_Quad4R)]

        plotter.add_mesh(quad_plot, scalars=contour_label,
                cmap=contour_colorscale, edge_color='black', show_edges=True,
                line_width=1.)
    else:
        plotter.add_mesh(quad_plot, edge_color='black', show_edges=True,
                line_width=1.)
    faces_tria = []
    for t in model.list_Tria3R:
        faces_tria.append([3, nid_pos[t.n1], nid_pos[t.n2], nid_pos[t.n3]])
    faces_tria = np.array(faces_tria)
    tria_plot = pv.PolyData(ncoords, faces_tria)
    if contour_vec is not None:
        if intensitymode == 'vertex':
            tria_plot[contour_label] = contour_vec
        else:
            tria_plot[contour_label] = contour_vec[len(model.list_Quad4R):]
        plotter.add_mesh(tria_plot, scalars=contour_label,
                cmap=contour_colorscale, edge_color='black', show_edges=True,
                line_width=1.)
    else:
        plotter.add_mesh(tria_plot, edge_color='black', show_edges=True,
                line_width=1.)
    if displ_vec is not None:
        quad_plot = pv.PolyData(ncoords + displ_vec, faces_quad)
        plotter.add_mesh(quad_plot, edge_color='red', show_edges=True,
                line_width=1., opacity=0.5)
        tria_plot = pv.PolyData(ncoords + displ_vec, faces_tria)
        plotter.add_mesh(tria_plot, edge_color='red', show_edges=True,
                line_width=1., opacity=0.5)
    plotter.set_background(background)
    plotter.parallel_projection = False
    return plotter


def plot3d_plotly(model, displ_vec=None, contour_vec=None, contour_label='vec',
        contour_colorscale='jet'):
    """Plot results using plotly

    Parameters
    ----------
    displ_vec : array-like
        Nodal displacements to be applied to the nodal coordinates in order to visualize the deformed model.
    contour_vec : array-like
        Nodal or element-wise output to be displayed as a contour plot on top of the undeformed mesh.
        For nodal output, the function expects the order of attr:`.ModelPyFE3D.ncoords`.
        For element-wise output, the function expects the element outputs in the following order of elements:

        - :attr:`ModelPyFE3D.list_Quad4R`
        - :attr:`ModelPyFE3D.list_Tria3R`

    contour_label : str
        Name of contour being displayed.
    contour_colorscale : str
        Name of the colorscale.

    Returns
    -------
    fig : `plotly.graph_objects.Figure` object
        A figure object that is ready to be modified, or shown with ``fig.show()``.

    """
    import plotly.graph_objects as go

    nid_pos = model.nid_pos
    x, y, z = model.ncoords.T

    intensity = None
    intensitymode = None
    if contour_vec is not None:
        if len(contour_vec) == len(x):
            intensitymode = 'vertex'
            intensity = contour_vec
        elif len(contour_vec) == len(model.list_Quad4R) + len(model.list_Tria3R):
            intensitymode = 'cell'
            intensity = np.concatenate((
                np.repeat(contour_vec[:len(model.list_Quad4R)], 2), # NOTE 1 quad = 2 trias in the visualization
                contour_vec[len(model.list_Quad4R):]))
        else:
            raise RuntimeError('coutour_vec must be either a nodal or element output')

    i = []
    j = []
    k = []
    # NOTE visualizing quads as triangles
    for q in model.list_Quad4R:
        # first triangle
        i.append(nid_pos[q.n1])
        j.append(nid_pos[q.n2])
        k.append(nid_pos[q.n4])
        # second triangle
        i.append(nid_pos[q.n2])
        j.append(nid_pos[q.n3])
        k.append(nid_pos[q.n4])
    # trias
    for t in model.list_Tria3R:
        i.append(nid_pos[t.n1])
        j.append(nid_pos[t.n2])
        k.append(nid_pos[t.n3])
    data = []
    mesh3d = go.Mesh3d(x=x,y=y,z=z, i=i, j=j, k=k, intensity=intensity,
            name=contour_label, intensitymode=intensitymode, colorscale=contour_colorscale)
    data.append(mesh3d)

    if displ_vec is not None:
        xdispl = x + displ_vec[:, 0]
        ydispl = y + displ_vec[:, 1]
        zdispl = z + displ_vec[:, 2]
        mesh3d_displ = go.Mesh3d(x=xdispl, y=ydispl, z=zdispl, i=i, j=j, k=k,
                color='lightpink', opacity=0.5)
        data.append(mesh3d_displ)
    layout = go.Layout(
        width=1024,
        height=1024,
        scene = dict(
           aspectmode='data',
           aspectratio=dict(x=1, y=1, z=1),
           )
    )
    fig = go.Figure(data=data, layout=layout)
    return fig
