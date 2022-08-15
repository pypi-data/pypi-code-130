""" Main code of the package, contains all production network models in the 
library.

We adopt the following common notation:
* T is the number of time steps of the simulation.
* N is the number of firms in the network (i.e. the number of nodes).
* P is the vector of production of each firm.
* D is the vector of total demand faced by each firm.
* C is the vector of final consumption faced by each firm.
* C_a is the realised consumption vector (actual consumption)
* F is the vector of final demand faced by each firm that is not consumption.
* S is the vector of inventories held by each firm.
* O is the matrix of orders faced by each firm from all other firms.
* Z is the vector of intermediate consumption between firms.
* A is the matrix of technical coefficients of production.
* p_cap is the vector of production capacity of each firm for each t.

An important note on the implied direction of the matrices:
* Z(i, j) represents the consumption of firm j of good produces by i therefore 
the flow of goods is i -> j
* S(i, j) represents the stock of the production of i held by firm j to be 
consistent with Z
* A(i, j) represents the minimal quantity of product i needed by j to produce 
one unit of its output.
* O(i, j) represents the orders faced by i due to j

The first dimension of these arrays will be time if it is relevant. 

"""

import numpy as np
from numba import njit
from numpy.random import default_rng
import scipy.sparse as sp
from .lib import faster_dot


class SimEngine:
    def __init__(self, T, N, rationing_type='proportional', dtype=np.float64):
        """ This class is the common engine for the simulation of different 
        models in this package. It collect different methods that apply to all 
        models.

        :param T: Number of time steps in the simulation.
        :type T: int
        :param N: Number of firms in the network.
        :type N: int
        """
        self.T = T
        self.N = N
        self.rationing_type = rationing_type

    def demand_rationing(self, o, p, c):
        """ Computes the demand rationing according to the specified method 
        set by rationing_type. 
        """
        # Check input dimensions
        if o.shape != (self.N, self.N):
            raise ValueError('Intermediate orders is not a NxN matrix.')
        if p.shape != (self.N,):
            raise ValueError('Production is not a N-length vector.')
        if c.shape != (self.N,):
            raise ValueError('Consumption is not a N-length vector.')

        # Ensure all entries are positive
        if np.any(o < 0) or np.any(p < 0) or np.any(c < 0):
            raise ValueError(
                'Negative orders, production, or demand is not allowed.')

        # Select algorithm
        if self.rationing_type == "proportional":
            z, c_a = self.prop_rationing(o, p, c)   
        elif self.rationing_type == "mixed_proportional":
            z, c_a = self.mixed_prop_rationing(o, p, c)
        elif self.rationing_type == "mixed_priority":
            z, c_a = self.mixed_priority_rationing(o, p, c, random=False)
        elif self.rationing_type == "priority":
            z, c_a = self.priority_rationing(o, p, c, random=False)
        elif self.rationing_type == "rnd_mixed_priority":
            z, c_a = self.mixed_priority_rationing(o, p, c, random=True)
        elif self.rationing_type == "rnd_priority":
            z, c_a = self.priority_rationing(o, p, c, random=True)
        else:
            raise ValueError('Demand rationing type not recognised.')

        # Some sanity checks
        if np.any(c_a < 0):
            raise ValueError('Negative final consumption')
        if not np.allclose(z.sum(axis=1) + c_a, p):
            raise ValueError(
                'Final and intermediate demand do not match production')

        return z, c_a
        
    @staticmethod
    def prop_rationing(o, p, c):
        """ Given a production level return the actual final demand and 
        intermediate one in proportion to their relative sizes.

        :param o: Orders matrix (NxN)
        :type o: numpy.ndarray
        :param p: Production vector (N)
        :type p: numpy.ndarray
        :param c: Consumprion vector (N)
        :type c: numpy.ndarray
        """
        # Compute total demand of each firm
        d = c + o.sum(axis=1)

        # Compute satisfiable ratio
        ind = d != 0
        r = np.zeros(p.shape, dtype=p.dtype)
        r[ind] = np.where(p[ind]/d[ind] > 1, 1, p[ind]/d[ind]) 

        # Fill results
        z = o * r[np.newaxis].T
        c_a = c * r 

        return z, c_a

    @staticmethod
    def mixed_prop_rationing(o, p, c):
        """ Given a production level demand is met proportionally to its size 
        but firm-to-firm orders are prioritized over final demand.
        
        :param o: Orders matrix (NxN)
        :type o: numpy.ndarray
        :param p: Production vector (N)
        :type p: numpy.ndarray
        :param c: Consumprion vector (N)
        :type c: numpy.ndarray
        """

        d_firms = o.sum(axis=1)
        ratio = np.where(p/d_firms > 1, 1, p/d_firms)
        z = o * ((ratio)[np.newaxis].T)
        c_a = p-z.sum(axis=1)

        return z, c_a

    @staticmethod
    def cumsum_stop(o, o_order, cap):
        z = np.zeros(len(o))
        sum_n = 0
        for i in range(len(o)):
            sum_n += o[o_order[i]]
            place = o_order[i]
            z[place] = o[o_order[i]]
            if (i == 0) and (o[o_order[i]] > cap):
                left = cap
                z[place] = left
                break
            else:
                if (sum_n > cap):
                    left = cap - np.cumsum(
                        o[o_order[0:i]])[len(np.cumsum(o[o_order[0:i]]))-1]
                    place = o_order[i]
                    z[place] = left
                    break
        return z

    @staticmethod
    def mixed_priority_rationing(o, p, c, random=False):
        """ Given a production level demand is met in order of sizes (largest 
        first) but firm-to-firm orders are prioritized over final demand. If 
        random is set to true, the order of the priority is randomized.
        
        :param o: Orders matrix (NxN)
        :type o: numpy.ndarray
        :param p: Production vector (N)
        :type p: numpy.ndarray
        :param c: Consumprion vector (N)
        :type c: numpy.ndarray
        :param random: randomization toggle
        :type random: boolean
        """
        z = []
        for zz in range(o.shape[0]):
            order_vec = o[zz, :]
            ordered_o = np.flip(np.argsort(order_vec))
            if random:
                random.shuffle(ordered_o)
            else:
                ordered_o = np.flip(np.argsort(order_vec))
            z.append(SimEngine.cumsum_stop(order_vec, ordered_o, p[zz]))

        z = np.stack(z, axis=0)   
        c_a = p - z.sum(axis=1) 
        
        return z, c_a

    @staticmethod
    def priority_rationing(o, p, c, random=False):
        """ Given a production level demand is met in order of sizes (largest 
        first) including final demand. If random is set to true, the order of 
        the priority is randomized.
        
        :param o: Orders matrix (NxN)
        :type o: numpy.ndarray
        :param p: Production vector (N)
        :type p: numpy.ndarray
        :param c: Consumprion vector (N)
        :type c: numpy.ndarray
        :param random: randomization toggle
        :type random: boolean
        """
        z = []
        dem_sat = []
        for zz in range(o.shape[0]):
            order_vec = o[zz, :]
            order_vec = np.append(order_vec, c[zz])
            ordered_o = np.flip(np.argsort(order_vec))
            if random:
                random.shuffle(ordered_o)
            else:
                ordered_o = np.flip(np.argsort(order_vec))
            res = SimEngine.cumsum_stop(order_vec, ordered_o, p[zz])
            dem_sat.append(res[:(o.shape[0])])
            z.append(res[:(o.shape[0])]) 

        z = np.stack(z, axis=0)     
        c_a = p - z.sum(axis=1)
        
        return z, c_a


class ARIO(SimEngine):
    def __init__(self, T, N, A, n, tau, p_cap, rationing_type='proportional', 
                 dtype=np.float64):
        """ This class implements the ARIO network model by Hallegatte et al 
        as described in the Henriet et al. Journal of Economic Dynamics & 
        Control 36 (2012) 150–167 paper.

        :param T: Number of time steps in the simulation.
        :type T: int
        :param N: Number of firms in the network.
        :type N: int
        :param A: Technical coefficients matrix (NxN).
        :type A: numpy.ndarray
        :param n: Inventory target time of each firm (N).
        :type n: numpy.ndarray 
        :param tau: Inventory adjustment speed of each firm (N).
        :type tau: numpy.ndarray 
        :param p_cap: Production capacity of each firm (N).
        :type p_cap: numpy.ndarray 
        :param dtype: Sets data type of all arrays, by default np.float64.
        :type dtype: numpy.dtype
        :return: ARIO model object
        :rtype: ARIO object

        """
        self.T = T
        self.N = N
        self.rationing_type = rationing_type
        self.dtype = dtype

        # Check that A adheres to correct shape
        if A.shape != (self.N, self.N):
            raise ValueError('A must a NxN array.')
        self.A = A 

        # Check that n adheres to correct shape
        if n.size != self.N:
            raise ValueError('n must an array of N elements.')
        if n.shape != (self.N,):
            n = n.reshape((self.N,))
        self.n = n

        # Check that tau adheres to correct shape
        if tau.size != self.N:
            raise ValueError('tau must an array of N elements.')
        if tau.shape != (self.N,):
            tau = tau.reshape((self.N,))
        self.tau = tau

        # Check that p_cap adheres to correct shape
        if p_cap.size != self.N:
            raise ValueError('p_cap must an array of N elements.')
        if p_cap.shape != (self.N,):
            p_cap = p_cap.reshape((self.N,))
        self.p_cap = p_cap

    def simulate(self, s0, C, p_shock=None):
        """ Simulate model over all time steps given initial conditions and 
        exogenous factors.

        :param s0: Initial inventories of each firm (N).
        :type s0: numpy.ndarray
        :param C: Final demand faced by each firm at each time-step (TxN).
        :type C: numpy.ndarray
        :param p_shock: Production shock as a percentage of p_cap (TxN).
        :type p_shock: numpy.ndarray
        """

        # Check that C adheres to correct shape
        if C.shape != (self.T, self.N):
            raise ValueError('C must a TxN array.')
        self.C = C

        # Check that p_shock is either None or correct shape
        if p_shock is not None:
            if p_shock.shape != (self.T, self.N):
                raise ValueError('p_shock must a TxN array.')

            # Ensure that the shock values are between zero and one
            if np.any(p_shock > 1) or np.any(p_shock < 0):
                raise ValueError('p_shock elements must be in [0, 1].')

        self.p_shock = p_shock

        # Check that s0 adheres to correct shape
        if s0.shape != (self.N, self.N):
            raise ValueError('s0 must an array of NxN elements.')

        # Initialize inventory array
        self.S = np.zeros((self.T, self.N, self.N), dtype=self.dtype)
        self.S[0, :] = s0

        # Initialise production array
        self.P = np.zeros((self.T, self.N), dtype=self.dtype)

        # Initialize orders array
        self.O = np.zeros((self.T, self.N, self.N), dtype=self.dtype)

        # Initialize intermediate consumption array
        self.Z = np.zeros((self.T, self.N, self.N), dtype=self.dtype)

        # Initialize demand array
        self.D = np.zeros((self.T, self.N), dtype=self.dtype)

        # Initialize actual consumption array
        self.C_a = np.zeros((self.T, self.N), dtype=self.dtype)

        for t in range(self.T):
            print('\x1b[K', 't=', t, end='\r')

            # Compute intermediate demand faced by firms
            self.set_intermediate_demand(t)

            # Compute total demand faced by firms
            self.set_total_demand(t)

            # Compute production level
            self.set_production_level(t)

            # Compute demand rationing
            self.Z[t, :], self.C_a[t, :] = self.demand_rationing(
                self.O[t, :], self.P[t, :], self.C[t, :])

            # Compute demand rationing
            self.set_inventories(t)

    def set_intermediate_demand(self, t):
        """ This functions sets the update of the orders matrix O for time step
         t.
            
        :param t: The current time step index.
        :type t: int
        """
        # Set previous demand
        if t > 0:
            D_prev = self.D[t - 1, :]
        else:
            D_prev = np.linalg.inv(np.eye(self.N) - self.A).dot(self.C[0, :])

        # Compute optimal inventory level
        S_opt = self.S[0, :]

        # Compute new orders
        self.O[t, :] = self.A * D_prev + (S_opt - self.S[t, :]) / self.tau
        self.O[t, :][self.O[t, :] < 0] = 0

    def set_total_demand(self, t):
        """ This functions sets the update of the total demand D for time step 
        t.
            
        :param t: The current time step index.
        :type t: int
        """
        self.D[t, :] = self.C[t, :] + self.O[t, :].sum(axis=1) 

    def set_production_level(self, t):
        """ This functions computes the production level P for each firm for 
        time step t.
            
        :param t: The current time step index.
        :type t: int
        """
        # Compute production input capacity according to the standard Leontief
        with np.errstate(divide='ignore', invalid='ignore'):
            p_inp = self.S[t, :] / self.A
        p_inp = np.nanmin(p_inp, axis=0)
  
        # Get current production capacity
        if self.p_shock is not None:
            p_cap_t = self.p_cap * (1 - self.p_shock[t, :])
        else:
            p_cap_t = self.p_cap

        # Determine output level
        self.P[t, :] = np.minimum(np.minimum(p_cap_t, p_inp), self.D[t, :])
        
    def set_inventories(self, t):
        """ This functions updates the inventories for the next iteration.
            
        :param t: The current time step index.
        :type t: int
        """
        if t < self.T - 1:
            S_next = self.S[t, :] + self.Z[t, :] - self.A * self.P[t, :]
            S_next[S_next < 0] = 0
            self.S[t + 1, :] = S_next
        

class PerBak():
    """ Per Bak et al. (1992) model of inventory and production dynamics.

    This model has a very simple 'cylindrical' topology where each firm has 
    two suppliers and two customers, unless the customer is the final consumer 
    in which case it is just one. Production is discrete and oscillates 
    between zero and the maximum value of two.
    """
    def __init__(self, L, T, S=None):
        """ Initialize model with number of simulation steps T and number of 
        layers L. The initial inventories can be set, or will be assumed full. 
        Note that the number of firms is given by L^2. 
        """
        # Number of layers
        self.L = L

        # Iteration steps
        self.T = T

        # Inventories
        self.S = np.ones((T, L, L), dtype='u1') 
        if S is not None:
            if not isinstance(S, np.ndarray):
                raise ValueError(
                    'Initial inventories S must be a numpy array.')

            if S.shape != (self.L, self.L):
                raise ValueError(
                    'Initial inventories S must have dimensions (L, L).')

            self.S[0, :, :] = S

        # Sales (Demand is met)
        self.D = np.zeros((T, L, L), dtype='u1') 

        # Production
        self.P = np.zeros((T, L, L), dtype='u1') 

    def set_final_demand(self, p=None, C=None):
        """ Set final consumption affecting firms. 

        If p is not set by the user then the default value is given as in the 
        paper. It is also possible to pass directly a final demand vector for 
        all times.
        """

        if p is None:
            p = self.L**(-2/3)

        if C is None:
            rng = default_rng()
            demand = rng.random(size=(self.T, self.L)) < p
            self.C = demand.astype('u1')
        else:
            if not isinstance(C, np.ndarray):
                raise ValueError('Final demand C must be a numpy array.')

            if C.shape != (self.T, self.L):
                raise ValueError('Final demand C must have dimensions (T, L).')

            self.C = C

    def simulate(self):
        if not hasattr(self, 'C'):
            self.set_final_demand()

        self.D[:, 0, :] = self.C
        self._simulate(self.S, 
                       self.D, 
                       self.P, 
                       self._production, 
                       self._inventories,
                       self.T,
                       self.L)

    @staticmethod
    @njit
    def _production(x, s):
        if x == 1:
            if s == 0:
                return 0
            elif s == 1:
                return 0
            else:
                return 2
        else:
            if s == 0:
                return 0
            elif s == 1:
                return 2
            else:
                return 2

    @staticmethod
    @njit
    def _inventories(x, s):
        if x == 1:
            if s == 0:
                return 1
            elif s == 1:
                return 0
            else:
                return 1
        else:
            if s == 0:
                return 0
            elif s == 1:
                return 1
            else:
                return 0

    @staticmethod
    @njit
    def _simulate(S, D, P, f_p, f_s, T, L):
        for t in range(T):
            for i in range(L):
                for j in range(L):
                    P[t, i, j] = f_p(S[t, i, j], D[t, i, j])
                    if t + 1 < T:
                        S[t + 1, i, j] = f_s(S[t, i, j], D[t, i, j])
                    if i + 1 < L:
                        D[t, i + 1, j] += P[t, i, j] / 2
                        D[t, i + 1, (j + 1) % L] += P[t, i, j] / 2


class GeneralizedPerBak():
    """ An adaptation of the Per Bak et al. (1992) model of inventory and 
    production dynamics on a general supply network.

    In this model the interaction topology can be arbitrarily set through the 
    matrix A, and the final demand can affect all nodes. Production is still 
    discrete and oscillates between zero and the maximum value which is given 
    by the number of customers. All firms are assumed to connect to the final 
    consumer. There is no rationing necessary.
    """
    def __init__(self, N, T, A, B=None, S=None, P_cap=None):
        """ Initialize model with the number of firms N, the adjacency matrix 
        A, and the number of simulation steps T. Optionally one can set an 
        initial inventory vector S and specify which firms are connected to the
         final consumer through B.
        """
        # Number of firms
        self.N = N

        # Iteration steps
        self.T = T

        # Adjacency matrix
        if not (isinstance(A, np.ndarray) or isinstance(A, sp.spmatrix)):
            raise ValueError('Adjacency matrix must be a numpy array or a '
                             'sparse matrix.')
        if A.shape != (N, N):
            raise ValueError('Adjacency matrix must have dimensions (N, N).')

        self.A = sp.csc_matrix(A.astype(bool))

        # Final consumer adjacency vector
        if B is None:
            self.B = np.ones(self.N, dtype=bool)
        else:
            if not isinstance(B, np.ndarray):
                raise ValueError('Final consumer connection vector B must '
                                 'be a numpy array.')
            if len(B) != self.N:
                raise ValueError('Final consumer connection vector B must '
                                 'have N elements.')

            self.B = B != 0

        # Get max production values
        if P_cap is None:
            self.P_cap = self.A.dot(np.ones(N)) + self.B
        else:
            if not isinstance(P_cap, np.ndarray):
                raise ValueError('Production capacity P_cap must be a numpy '
                                 'array.')
            if len(P_cap) != self.N:
                raise ValueError('Production capacity P_cap vector must '
                                 'have N elements.')
            if np.any(P_cap < self.A.dot(np.ones(N)) + self.B):
                raise ValueError('Rationing currently not supported.')

            self.P_cap = P_cap

        # Determine optimal memory size based on P_cap
        p_max = np.max(self.P_cap)
        if p_max < 2**8:
            self.dtype = 'u1'
        elif p_max < 2**16:
            self.dtype = 'u2'
        elif p_max < 2**32:
            self.dtype = 'u4'
        elif p_max < 2**64:
            self.dtype = 'u8'
        else:
            raise ValueError('Max production requires more than 64 bits.')

        # Set correct dtype
        self.P_cap = self.P_cap.astype(self.dtype)

        # Inventories (initialized to capacity minus demand)
        self.S = np.empty((T, N), dtype=self.dtype) 
        self.S[0, self.P_cap != 0] = self.P_cap - 1

        if S is not None:
            if not isinstance(S, np.ndarray):
                raise ValueError(
                    'Initial inventories S must be a numpy array.')

            if len(S) != self.N:
                raise ValueError(
                    'Initial inventories S must have N elements.')

            self.S[0, :] = S.astype(self.dtype)

        # Sales (Demand is met)
        self.D = np.zeros((T, N), dtype=self.dtype) 

        # Production
        self.P = np.zeros((T, N), dtype=self.dtype) 

    def set_final_demand(self, p=None, C=None):
        """ Set final consumption affecting firms. 

        If p is not set by the user then the default value is given as in the 
        paper. It is also possible to pass directly a final demand vector for 
        all times.
        """

        if C is None:
            if p is None:
                p = np.sqrt(self.N)**(-2/3)

            rng = default_rng()      
            demand = rng.random(size=(self.T, np.sum(self.B))) < p
            self.C = np.zeros((self.T, self.N), dtype=self.dtype)
            self.C[:, self.B] = demand.astype(self.dtype)
            
        else:
            if not isinstance(C, np.ndarray):
                raise ValueError('Final demand C must be a numpy array.')

            if C.shape != (self.T, self.N):
                raise ValueError('Final demand C must have dimensions (T, N).')

            if np.any(C[:, self.B == 0]):
                raise ValueError('Some firms that are not connected to the '
                                 'final consumer (through B) have been set to '
                                 'face some final demand.') 

            self.C = C.astype(self.dtype)

    def simulate(self, max_iter=None):
        """ Simulate model over all times given initial conditions and demand.
        """
        if not hasattr(self, 'C'):
            self.set_final_demand()

        if max_iter is None:
            max_iter = self.N

        for t in range(self.T):
            print('\x1b[K', 't=', t, end='\r')

            # Compute equilibrium demand
            self.D[t, :] = self._next_step(self.S[t, :], 
                                           self.C[t, :],
                                           self.A.indices,
                                           self.A.indptr,
                                           self.A.data,
                                           self.D.dtype, 
                                           max_iter)

            # Update production
            self.P[t, :] = self.P_cap * (self.D[t, :] > self.S[t, :])
            if t + 1 < self.T:
                self.S[t+1, :] = self.P[t, :] + self.S[t, :] - self.D[t, :]

    @staticmethod
    @njit
    def _next_step(s_t, c_t, A_ind, A_ptr, A_dat, dtype, max_iter):
        n = 0
        d_t = c_t
        while n <= max_iter:
            n += 1

            # Find where production is necessary
            y_tilde = d_t > s_t

            # Compute update in demand
            d_next = faster_dot(A_ind, A_ptr, A_dat, y_tilde, dtype) + c_t
            
            if np.all(d_t == d_next): 
                return d_t
            else:
                d_t = d_next
