from _kymoknot_bindings import ffi, lib
import numpy as np

from . import knotentry
from . import searchtype


#closure types
CL_NONE = "None"
CL_RING = "Ring"
CL_BRIDGE = "Bridge"
CL_QHULL = "Qhull"
CL_QHULLHYB = "Hybrid"
CL_RADIAL = "Radial"
CL_STOCHASTIC = "Stochastic"

CLOSURES = [
    "None",
    "Ring",
    "Bridge",
    "Qhull",
    "Hybrid",
    "Radial",
    "Stochastic",
]


INP_RING = "Ring"
INP_LINEAR = "Linear"


class UndefinedSearch(Exception):
    pass


class UndefinedInputType(Exception):
    pass


class SearchNotRequested(Exception):
    pass


class SearchAlreadyPerformed(Exception):
    pass


def read_file(filename):

    res = None

    fd = open(filename, encoding="utf8")

    while fd:
        lines_nr = fd.readline()
        lines_nr.strip()

        try:
            lines_nr = int(lines_nr)
        except ValueError:
            break

        res = np.empty((lines_nr, 3), dtype=np.float64)

        for i in range(lines_nr):
            line = fd.readline()
            line = line.split()
            for j in range(3):
                res[i][j] = float(line[j])

        yield res

    fd.close()
    return res


def chains_to_str(
        chains,
        precision="{:.6f}"
        ):
    """

    Writes a string representing all chains.
    The string written on a file can be taken as an input file for searches.

    :param chains: iterable of chains to be written in output
    :type chains: [nd.array]
    :return: a string repesenting all chains
    :rtype: str
    """

    res = []
    for c in chains:

        res.append("{:d}".format(c.shape[0]))
        for i in range(c.shape[0]):
            numbers = [precision.format((x)) for x in c[i]]
            res.append(" ".join(numbers))

    res = "\n".join(res)
    return res


class KymoKnotSearch(object):

    #for the complete list of parameters,
    #check the search_config_t structure in
    #kymoknot_bindings.h
    def __init__(
            self,
            **kwargs
            #search_type=[KymoKnotSearch.BU],
            #seed=None,
            #closure_type=KymoKnotClose.CL_QHULLHYB,
            #close_subchain=KymoKnotClose.CL_QHULLHYB,
            #arc_start=None,
            #arc_end=None,
            #fname_prev_search=None,
            #max_stride=None,
            #f_max_stride=None,
            #memlen=None,
            #print_conf=None,
            ):

        self.args = kwargs
        self.param = None

        return


    def prepare_config(self):
        
        """
        Initializes the struct search_config_t that will store the parameters for the knot searches.
        Input and output parameters are, respectively, taken from a class Attribute and set to a class Attributes.
        When needed, fields are converted.

        The output class Attribute is a python object representi a pointer to struct search_config_t 
        to be passed to the C search functions.
        
        input: self.args
        output: self.param

        """

        self.param = ffi.new("search_config_t *")
        lib.init_search_config(self.param)

        #Default value, should match the one defined in kymoknot_bindings
        if "search_type" not in self.args.keys():
            self.args["search_type"] = [searchtype.SearchType.BU]

        for a in self.args:

            if a == "closure_type":
                tmp = self.args["closure_type"]
                if tmp in CLOSURES:
                    tmp = tmp.encode("ascii")
                    setattr(self.param, a, tmp)

            elif a == "close_subchain":
                tmp = self.args["close_subchain"]
                if tmp in CLOSURES:
                    tmp = tmp.encode("ascii")
                    setattr(self.param, a, tmp)

            elif a == "search_type":
                tmp = searchtype.encode_search_type(self.args["search_type"])
                setattr(self.param, a, tmp)

            elif hasattr(self.param, a):
                setattr(self.param, a, self.args[a])

        return


    def _create_data_entry(
            self,
            p_data,
            start=None,
            end=None,
            seed=None,
            ):
        
        """
        Creates the struct search_data_entry_t that will store the coordinates of one chain and the 
        per-chain search parameters (i.e.: when the search on the chain should be restricted from a start
        and an end coordinate).

        :param data: the numpy array representing the coordinates with shape (3, <coordinates number>)
        :type data: numpy.array
        :return: the python object representing the pointer to the search_data_entry_t structure
        :rtype: <ffi pointer>
        """

        res = ffi.new("search_data_entry_t *")
        res.len = p_data.shape[0]

        data = p_data.reshape(-1)
        res.mat = ffi.cast("double * ", data.ctypes.data)

        if start is not None:
            res.arc_start = start

        if end is not None:
            res.arc_end = end

        return res


    def _prepare_data(self, data):
        """
        Creates the struct search_data_t that will store the che coordinates of all the chains.
        When data is the string representing the path of the chains file, 
        its value is set in the search_config_t structure.

        :param data: an iterable containing numpy.array or a string
        :type data: <iterable> or str
        :return: the python object representing the pointer to the search_data_t structure to be used in the C method call 
                 or the object representing a C NULL pointer to be used when passing the chain file path
        :rtype: <ffi pointer>

        """

        res = None

        if isinstance(data, str):

            #print(f"data: {data}")

            #make sure to keep a reference to avoid garbage collection deallocation
            self.filename = ffi.new("char []", data.encode("ascii"))
            self.param.chain_file_path = self.filename
            res = ffi.NULL

        else:
            res = ffi.new("search_data_t *")

            self.des = ffi.new("search_data_entry_t * []", len(data))

            res.len = len(data)
            res.entries = self.des

            self.data_entries = []
            for idx, chain in enumerate(data):

                de = self._create_data_entry(chain)
                res.entries[idx] = de

                #Needed to keep a refenence alive, otherwise python will garbage collect
                #the data entry or some of its substructures
                self.data_entries.append(de)

        return res


    def _parse_search_retval_entry(self, knts):
        """

        Parses the struct reporting the knots founded in the chain.

        :param knts: cdata pointer to stuct of type search_retval_entry_t
        :type knts: <cdata>
        :return: A list of KnotEntry
        :rtype: list[KnotEntry]
        """

        res = []
        for i in range(knts.len):
            ke = knotentry.create_entry(knts.entries[i])
            res.append(ke)

        return res


    def _parse_result(self, search_res):
        """

        Parses the result struct for each chain.

        :param search_res: cdata pointer to stuct of type search_retval_ll_t
        :type search_res: <cdata 'struct search_retval_ll_t *' >
        :return: A dict<SearchType -> lists[KnotEntry]>
        :rtype: list[list[KnotEntry]]
        """

        searches = list(searchtype.SearchType)
        res = {}

        i = 0
        ll_node = ffi.cast("search_retval_llnode_t *", search_res.head)
        while ll_node != ffi.NULL:

            for j in searches:

                entry = ffi.cast("search_retval_entry_t *", ll_node.sres[j.value])
                if entry != ffi.NULL:

                    knts = self._parse_search_retval_entry(entry)

                    src_res = res.get(j, [])
                    src_res.append(knts)
                    res[j] = src_res

            ll_node = ll_node.next
            i = i + 1

        return res


    def search(self, data, input_type, seed=None):
        """

        Takes a list of chains and searchs knots on them.
        The list of chains can be passed as the path of a file contaning the chains or an iterable
        of numpy arrays.
        When the data parameters gets a string (the file path), the chain file is opened 
        and parsed by the C code.

        :param data: an iterable containing numpy.array or a string
        :type data: <iterable> or str
        :param input_type: a const indicating whether data is a linear or a ring chain
        :type input_type: <string> with value INP_RING or INP_LINEAR
        :param seed: an integer to be taken as the seed for the random number generator.
                     If not specified, the seed passed as init parameter is taken.
        :type seed: int
        :returns: a list of all knots found for each chain
        :rtype: list of list of KnotEntry
        """

        self.prepare_config()

        if seed is not None:
            self.param.seed = seed

        search_data = self._prepare_data(data)
        #print(search_data)

        if search_data != ffi.NULL:
            if input_type == INP_RING:
                search_res = lib.KymoKnot_ring(self.param, search_data)

            elif input_type == INP_LINEAR:
                search_res = lib.KymoKnot_linear(self.param, search_data)

            else:
                raise UndefinedInputType

        else:
            if input_type == INP_RING:
                search_res = lib.KymoKnot_ring_file(self.param)

            elif input_type == INP_LINEAR:
                search_res = lib.KymoKnot_linear_file(self.param)

            else:
                raise UndefinedInputType


        res = self._parse_result(search_res)
        #res = KymoKnotSearchResult(tmp, self.args["search_type"])

        lib.free_search_retval(search_res)
        return res


#class KymoKnotSearchResult(object):
#
#
#    def __init__(self, res_dict, searches):
#        self.searches = searches
#        self.result = res_dict
#        return
#
#
#    def get_result(self, search_type):
#
#        if search_type not in self.searches:
#            raise SearchNotRequested
#
#        res = self.result.get(search_type)
#        return res


#class KymoKnotClose(KymoKnotSearch):
#
#    def __init__(self):
#        return
#
#
#    def _parse_close_retval_entry(self, cr_entry):
#
#        res = np.empty((cr_entry.len, 3), dtype=np.float64)
#        for i in range(cr_entry.len):
#            tmp = ffi.addressof(cr_entry.coord, i*3)
#            buf = ffi.buffer(tmp, 24)
#            res[i] = np.frombuffer(buf, np.float64, 3)
#
#        return res
#
#
#    def _parse_result(self, data):
#
#        res = []
#        for i in range(data.len):
#            cr_entry = ffi.addressof(data.entries, i)
#            tmp = self._parse_close_retval_entry(cr_entry)
#            res.append(tmp)
#
#        return res
#
#
#    def close(self, data):
#
#        close_data = self._prepare_data(data)
#
#        cl_retval = lib.KymoKnot_close(close_data)
#
#        res = self._parse_result(cl_retval)
#
#        lib.free_close_retval(cl_retval)
#
#        return res
#
#
