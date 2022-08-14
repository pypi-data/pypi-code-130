# ------------------------------------------------------------
# NQPV_la.py
#
# linear algebra tools needed in this verifier
# ------------------------------------------------------------

from .tools import err

import numpy as np

EPS = 1e-7

error_info = ""
silent = False

def complex_norm(c):
    return np.sqrt(c * np.conj(c)).real

def check_unity(m, m_id):
    '''
    check whether tensor m is unitary
    m: tensor of shape (2,2,...,2), with the row indices in front of the column indices
    '''
    global error_info, silent

    if len(m.shape) % 2 == 1:
        error_info += err("Error: The dimension of '" + m_id + "' is invalid for an unitary.\n\n", silent)
        return False

    for dim in m.shape:
        if dim != 2:
            error_info += err("Error: The dimension of '" + m_id + "' is invalid for an unitary.\n\n", silent)
            return False
    
    # calculate the dim for matrix
    dim_m = 2**(len(m.shape)//2)
    matrix = m.reshape((dim_m, dim_m))

    # check the maximum of U^dagger @ U - I
    zero_check = (matrix @ np.transpose(np.conj(matrix))) - np.eye(dim_m)
    diff = np.sqrt(complex_norm(np.max(zero_check)))
    if diff > EPS:
        error_info += err("Error: '" + m_id + "' is not an unitary matrix.\n\n", silent)
        return False
    return True

def check_hermitian_predicate(m, m_id):
    '''
    check whether tensor m is hermitian and 0 <= m <= I
    m: tensor of shape (2,2,...,2), with the row indices in front of the column indices
    '''
    global error_info, silent
    if len(m.shape) % 2 == 1:
        error_info += err("Error: The dimension of '" + m_id + "' is invalid for an Hermitian operator.\n\n", silent)
        return False

    for dim in m.shape:
        if dim != 2:
            error_info += err("Error: The dimension of '" + m_id + "' is invalid for an Hermitian operator.\n\n", silent)
            return False
    
    # calculate the dim for matrix
    dim_m = 2**(len(m.shape)//2)
    matrix = m.reshape((dim_m, dim_m))

    # check the maximum of U^dagger @ U - I
    zero_check = matrix - np.transpose(np.conj(matrix))
    diff = np.sqrt(complex_norm(np.max(zero_check)))
    if diff > EPS:
        error_info += err("Error: '" + m_id + "' is not an Hermitian operator.\n\n", silent)
        return False

    # check 0 <= matrix <= I
    e_vals = np.linalg.eigvals(matrix)
    if np.any(e_vals < 0 - EPS) or np.any(e_vals > 1 + EPS):
        error_info += err("Error: The requirement 0 <= '" + m_id + "' <= I is not satisfied.\n\n", silent)
        return False
        
    return True


def check_measure(m, m_id):
    '''
    check whether tensor m is a valid measurement
    m: tensor of shape (2,2,...,2), with the row indices in front of the column indices. 
        The first index of m corresponds to measurement result 0 or 1.
    '''
    global error_info, silent
    if len(m.shape) % 2 == 0:
        error_info += err("Error: The dimension of '" + m_id + "' is invalid for a measurement.\n\n", silent)
        return False

    for dim in m.shape:
        if dim != 2:
            error_info += err("Error: The dimension of '" + m_id + "' is invalid for a measurement.\n\n", silent)
            return False
    
    # calculate the dim for matrix
    dim_m = 2**((len(m.shape)-1)//2)

    # pick out M0 and M1
    m0 = m[0].reshape((dim_m, dim_m))
    m1 = m[1].reshape((dim_m, dim_m))

    # check the maximum of U^dagger @ U - I
    zero_check = (m0.conj().transpose() @ m0 + m1.conj().transpose() @ m1) - np.eye(dim_m)
    diff = np.sqrt(complex_norm(np.max(zero_check)))
    if diff > EPS:
        error_info += err("Error: '" + m_id + "' does not satisfy the normalization requirement of a measurement.\n\n", silent)
        return False
    return True
    
def eye_tensor(qubitn):
    '''
    return the identity matrix of 'qubitn' qubits, in the form of a (2,2,2,...) tensor, row indices in the front.
    '''
    return np.eye(2**qubitn).reshape((2,)*qubitn*2)

def hermitian_contract(qvar: list, H, qvar_act : list, M):
    '''
    conduct the transformation M.H.M^dagger and return the result hermitian operator
    qvar: name sequence of qubits in H
    qvar_act: name sequence of qubits in M

    Note: the operators H and M should have been checked already

    [index sequence of tensor H (and M)]

            qvar == [q1, q2, q3, ... , qn]

              n  n+1 n+2 n+3     2n-2 2n-1
              |   |   |   |  ...  |   |
             ---------------------------
            | q1  q2  q3     ...      qn|
             ---------------------------
              |   |   |   |  ...  |   |
              0   1   2   3      n-2 n-1

    '''
    nH = len(qvar)
    nM = len(qvar_act)
    # decide the indices for contraction. note that M^dagger is accessed by its conjugate and the same index list iM_ls
    iM_ls = list(range(nM, 2*nM))
    iH_left_ls = [qvar.index(v) for v in qvar_act]
    iH_right_ls = [i + nH for i in iH_left_ls]

    # decide the rearrangements, since the standard rearrangement is not what we want
    count_rem_MH = 0
    count_rem_HMd = nH
    rearrange_MH = []
    rearrange_HMd = []
    for i in range(nH):
        if i in iH_left_ls:
            rearrange_MH.append(2*nH-nM + qvar_act.index(qvar[i]))
        else:
            rearrange_MH.append(count_rem_MH)
            count_rem_MH += 1
        if i + nH in iH_right_ls:
            rearrange_HMd.append(2*nH-nM + qvar_act.index(qvar[i - nH]))
        else:
            rearrange_HMd.append(count_rem_HMd)
            count_rem_HMd += 1

    rearrange_MH = rearrange_MH + list(range(nH - nM, 2*nH - nM))
    rearrange_HMd = list(range(nH)) + rearrange_HMd

    # conduct the contraction and rearrange the indices
    temp1 = np.tensordot(H, M, (iH_left_ls, iM_ls)).transpose(rearrange_MH)
    temp2 = np.tensordot(temp1, np.conjugate(M), (iH_right_ls, iM_ls)).transpose(rearrange_HMd)
    return temp2

def dagger(M):
    '''
    for a tensor M with shape (2,2,2,...), return M^dagger
    Note: M should have been already checked
    '''
    nM = len(M.shape)//2
    trans = list(range(nM, nM*2)) + list(range(0, nM))
    return np.conjugate(M).transpose(trans)
    

def hermitian_init(qvar: list, H, qvar_init: list):
    '''
    initialize hermitian operator H at variables 'qvar_init'
    '''
    P0 = np.array([[1., 0.],
                    [0., 0.]])
    P1 = np.array([[0., 0.],
                    [1., 0.]])
    # initialize all the variables in order
    tempH = H
    for var in qvar_init:
        a = hermitian_contract(qvar, tempH, [var], P0)
        b = hermitian_contract(qvar, tempH, [var], P1)
        tempH = a + b
    
    return tempH

def tensor_to_matrix(t):
    nM = len(t.shape)//2
    ndim = 2**nM
    return t.reshape((ndim, ndim))


def hermitian_extend(qvar: list, H, qvar_H: list):
    '''
    extend the given hermitian operator, according to all variables qvar, and return
    '''
    nAll = len(qvar)
    nH = len(qvar_H)
    m_I = eye_tensor(nAll - nH)

    temp = np.tensordot(H, m_I, ([],[]))

    # rearrange the indices
    count_ext = 0
    r_left = []
    r_right = []
    for i in range(nAll):
        if qvar[i] in qvar_H:
            pos = qvar_H.index(qvar[i])
            r_left.append(pos)
            r_right.append(nH + pos)
        else:
            r_left.append(2*nH + count_ext)
            r_right.append(nAll + nH + count_ext)
            count_ext += 1
    
    return temp.transpose(r_left + r_right)
