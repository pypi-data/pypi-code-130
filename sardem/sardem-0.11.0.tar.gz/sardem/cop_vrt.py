####
def get_tiles_positions(vrtfile):
    from bs4 import BeautifulSoup
    with open(vrtfile) as f:
        soup = BeautifulSoup(f, "lxml")
    sources = soup.find_all(name="simplesource")
    outs = []
    for ss in sources:
        tile = _get_tile(ss.sourcefilename.text)
        xoff = float(ss.dstrect['xoff'])
        yoff = float(ss.dstrect['yoff'])
        outs.append((tile, xoff, yoff))
    return outs


def _get_tile(text):
    import re
    return ''.join(re.search(r'([NS]\d{2})_00_([EW]\d{3})', text).groups())


def get_offset_tiles(tilename):
    from sardem.download import Tile
    ns, lat, ew, lon = Tile.get_tile_parts(tilename)
    # not sure why the xoffset was shifted by 5
    if ew == "W":
        xoff = (180 - lon) * 3600 - 5
    else:
        xoff = (180 + lon) * 3600 - 5
    if ns == "N":
        yoff = (90 - lat - 1) * 3600 - 0.5
    else:
        yoff = (90 + lat - 1) * 3600 - 0.5

    return xoff, yoff


def g():
    t = get_tiles_positions("sardem/data/copernicus_GLO_30_dem.vrt")


import re
import fileinput
import glob

    
# input: 
# <SourceFilename relativeToVRT="1">DEM_N00_00_E000_00.tif</SourceFilename>
# target:
# <SourceFilename relativeToVRT="0">/vsicurl/https://...E000_00.tif</SourceFilename>
# https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N19_00_W155_00_DEM/Copernicus_DSM_COG_10_N19_00_W155_00_DEM.tif

# # BAD
# /vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N86_00_E168_00/Copernicus_DSM_COG_10_N86_00_E168_00.tif'
# # GOOD
# /vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N19_00_W155_00_DEM/Copernicus_DSM_COG_10_N19_00_W155_00_DEM.tif
# /vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N84_00_E175_00_DEM/Copernicus_DSM_COG_10_N84_00_E175_00_DEM.tif
import sardem.cop_dem

# Converting gustavos tree-vrt to one that works with aws tiles
# needs to delete missing tiles
def gust2(allnames=None, path="testcop/"):
    base = r"DEM_(.*).tif"
    if allnames is None:
        alltiles = sardem.cop_dem.get_tile_list()
        allnames = set([t[22:-4] for t in alltiles])
    template = "/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{n}_DEM/Copernicus_DSM_COG_10_{n}_DEM.tif"
    filelist = glob.glob(path + "[NS]*.vrt")
    len_ss = 7
    for fname in filelist:
        print("Processing", fname)
        with open(fname) as f:
            lines = f.read().splitlines()
        outlines = []
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if "<SimpleSource>" not in line:
                # breakpoint()
                outlines.append(line)
                idx += 1
                continue
            # <SimpleSource>
            #   <SourceFilename relativeToVRT="0">/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N00_00_E040_00_DEM/Copernicus_DSM_COG_10_N00_00_E040_00_DEM.tif</SourceFilename>
            #   <SourceBand>1</SourceBand>
            #   <SourceProperties RasterXSize="3600" RasterYSize="3600" DataType="Float32" BlockXSize="256" BlockYSize="256" />
            #   <SrcRect xOff="0" yOff="0" xSize="3600" ySize="3600" />
            #   <DstRect xOff="0" yOff="32400" xSize="3600" ySize="3600" />
            # </SimpleSource>    
            file_line = lines[idx + 1]
            assert "<SourceFilename" in file_line
            m = re.search(base, file_line)
            tilename = m.group(1)
            if tilename not in allnames:
                # skip this simplesource
                idx += len_ss
                continue
            out = template.format(n=tilename)
            updated = file_line.replace(f"DEM_{tilename}.tif", out)
            updated = updated.replace('relativeToVRT="1\"', 'relativeToVRT="0"')
            outlines.append(line)
            outlines.append(updated)
            outlines.extend(lines[idx + 2:idx + len_ss])
            # breakpoint()
            idx += len_ss
        with open(fname, "w") as f:
            f.write("\n".join(outlines))

#  for f in `ls *vrt`; do gdal_edit.py -a_srs "epsg:4326+3855" $f; done

def grepc(filename, grep_pat):
    with open(filename) as f:
        lines = f.read().splitlines()
    return len([l for l in lines if grep_pat in l])
# S50_E160.vrt
# S50_E060.vrt
# S40_W100.vrt
# S40_W060.vrt
# S40_E160.vrt
# 25
# 25
# S40_W020.vrt
# 1
# S40_E100.vrt
# 31
# 31
# S40_E120.vrt