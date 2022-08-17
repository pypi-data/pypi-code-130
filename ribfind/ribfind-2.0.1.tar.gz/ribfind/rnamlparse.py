import sys
from operator import attrgetter
from xml.etree import ElementTree
from ribfind import structures
from ribfind.model import RNAModel, RNAStrand, RNAHelix

# pylint: disable=R0914
def file_parse(filename):
    """Parses an RNAML file and returns an RNAObject (see
    structures.py) describing its secondary structure. Requires a
    standard RNAML file as defined by the RNAML standards that
    contains 2D structure information. RNAML files can be obtained
    directly from the NDB or produced from PDB files by the RNAView
    program.

    """
    try:
        doc = ElementTree.parse(filename)
    except ElementTree.ParseError:
        print("File not found or not valid XML file")
        sys.exit()
    rna = structures.RNAObject()

    def struct_to_list(struct_list):
        struct_list.append(structures.StructObject(title, is_helix, start_pos, end_pos))

    for molecule in doc.findall("molecule"):
        chain_id = int(molecule.attrib["id"])
        rnaml_numbering = range(
            int(molecule.findtext("./sequence/numbering-system/numbering-range/start")),
            int(molecule.findtext("./sequence/numbering-system/numbering-range/end"))
            + 1,
        )
        pdb_numbering = molecule.findtext("./sequence/numbering-table").split()
        for pdb_number in range(len(pdb_numbering) - 1):
            next_pdb_number = pdb_number + 1
            a_list = []
            while pdb_numbering[pdb_number] == pdb_numbering[next_pdb_number]:
                if not pdb_number in a_list:
                    a_list.append(pdb_number)
                a_list.append(next_pdb_number)
                next_pdb_number += 1
            pdb_number = next_pdb_number
            for index, pdb_number in enumerate(a_list):
                pdb_numbering[pdb_number] += chr(65 + index)
        numbering_map = dict(zip(rnaml_numbering, pdb_numbering))
        rna.chains.append(
            structures.ChainObject(
                int(molecule.attrib["id"]),
                int(molecule.find("./sequence/numbering-table").attrib["length"]),
                numbering_map,
            )
        )
        for helix in molecule.findall("./structure/model/str-annotation/helix"):
            title = helix.attrib["id"] + "." + str(chain_id)
            is_helix = True
            start_pos = int(helix.findtext("./base-id-5p/base-id/position"))
            end_pos = int(helix.findtext("./base-id-5p/base-id/position")) + (
                int(helix.findtext("./length")) - 1
            )
            struct_to_list(rna.chains[chain_id - 1].struct_list)
            start_pos = int(helix.findtext("./base-id-3p/base-id/position")) - (
                int(helix.findtext("./length")) - 1
            )
            end_pos = int(helix.findtext("./base-id-3p/base-id/position"))
            struct_to_list(rna.chains[chain_id - 1].struct_list)
        for loop in molecule.findall("./structure/model/str-annotation/single-strand"):
            title = loop.findtext("./segment/seg-name") + "." + str(chain_id)
            is_helix = False
            start_pos = int(loop.findtext("./segment/base-id-5p/base-id/position"))
            end_pos = int(loop.findtext("./segment/base-id-3p/base-id/position"))
            struct_to_list(rna.chains[chain_id - 1].struct_list)
    for helix in doc.find("interactions").findall("./str-annotation/helix"):
        title_append = (
            helix.find("./base-id-5p/base-id/molecule-id").attrib["ref"]
            + "-"
            + helix.find("./base-id-3p/base-id/molecule-id").attrib["ref"]
        )
        title = helix.attrib["id"] + "." + title_append
        chain_id = int(helix.find("./base-id-5p/base-id/molecule-id").attrib["ref"])
        is_helix = True
        start_pos = int(helix.findtext("./base-id-5p/base-id/position"))
        end_pos = int(helix.findtext("./base-id-5p/base-id/position")) + (
            int(helix.findtext("./length")) - 1
        )
        struct_to_list(rna.chains[chain_id - 1].struct_list)
        chain_id = int(helix.find("./base-id-3p/base-id/molecule-id").attrib["ref"])
        start_pos = int(helix.findtext("./base-id-3p/base-id/position")) - (
            int(helix.findtext("./length")) - 1
        )
        end_pos = int(helix.findtext("./base-id-3p/base-id/position"))
        struct_to_list(rna.chains[chain_id - 1].struct_list)
    for chain in rna.chains:
        chain.struct_list.sort(key=attrgetter("start_pos"))
    return rna


def assign_pdb_chains(rna, pdb):
    """Assigns PDB chain id to RNA chains."""
    chain_list = []

    def test_chain(chain):
        for residue in chain.get_list():
            if not residue.get_id()[0] == " ":
                continue
            res_name = residue.get_resname().strip()
            return res_name in ["G", "A", "U", "C"]
        return False

    for pdb_chain in pdb[0].get_list():
        if test_chain(pdb_chain):
            chain_list.append(pdb_chain.get_id())
    i = 0
    for chain in rna.chains:
        chain.pdb_chain = chain_list[i]
        i += 1


def parse_rna_model(rna_file, structure):
    rna = file_parse(rna_file)
    assign_pdb_chains(rna, structure)
    helices = {}
    models = []
    for chain in rna.chains:
        for struct in chain.struct_list:
            start = int(chain.numbering_map[struct.start_pos])
            end = int(chain.numbering_map[struct.end_pos])
            strand = RNAStrand(chain.pdb_chain, start, end + 1)
            if struct.is_helix:
                if helices.get(struct.title) is None:
                    helices[struct.title] = []
                helices[struct.title].append(strand)
            else:
                models.append(strand)
    for helix in helices.values():
        assert len(helix) == 2
        models.append(RNAHelix(helix))
    return RNAModel(models)
