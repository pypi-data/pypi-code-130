# Copyright (c) 2004-2022 WUR, Wageningen
''' vectorise: code for converting all pixels of a raster to polygons'''
from shapefile import Writer
from lmgeo.formats.raster import Raster
from pathlib import Path
from pygeopkg.core.geopkg import GeoPackage
from pygeopkg.core.srs import SRS
from pygeopkg.core.field import Field
from pygeopkg.shared.enumeration import GeometryType, SQLFieldTypes
from pygeopkg.conversion.to_geopkg_geom import make_gpkg_geom_header, point_lists_to_gpkg_polygon
from pygeopkg.shared.constants import SHAPE

rg = None

class Pixel:
    xll = 0.0
    yll = 0.0
    dx = 1.0
    dy = 1.0
    
    def __init__(self, colidx, rowidx):
        self.dx = rg.dx
        self.dy = rg.dy
        self.xll = rg.xll + colidx * self.dx
        self.yll = rg.yll + (rg.nrows - 1 - rowidx) * self.dy
        
def to_shapefile(raster, outputfile, attr_name, *args):
    # Initialise
    global rg
    rg = raster
    result = False
    
    # Check and process input
    if len(args) == 2:
        decimals = int(args[1]) # integer
    if len(args) == 1:
        datatype = args[0] # i or f
        if datatype == 'f': decimals = 2
    else:
        datatype = 'i'
    fp = Path(outputfile).parent
    if not fp.exists(): raise ValueError("Folder for output file %s does not exist!" % fp)
    
    # Last check: is the first argument really a raster?
    if not isinstance(rg, Raster):
        ValueError("Raster expected as first argument but %s detected!" % type(rg))    
    else:
        # We can now go ahead
        try:
            with Writer(str(outputfile)) as w:
                if datatype == 'i':
                    w.field(attr_name, 'N')
                elif datatype == 'f':
                    w.field(attr_name, 'N', decimals)
                
                # Now loop over the rows and columns
                for i in range(rg.nrows):
                    line = rg.next()
                    for k in range(rg.ncols):
                        # Check that we're not dealing with "nodata"
                        if line[k] == rg.nodatavalue: continue
                        
                        # Get the properties of the current pixel p
                        p = Pixel(k, i)
                        coords = [(p.xll,p.yll), (p.xll,p.yll+p.dy), (p.xll+p.dx,p.yll+p.dy), (p.xll+p.dx,p.yll), (p.xll,p.yll)]
                        w.poly([coords])
                        if datatype == 'i': w.record(int(line[k]))
                        else: w.record(float(line[k]))
            
            # We have reached here without problems!
            result = True
            
        except Exception as e:
            print(e)
            raise Exception(e)
        finally:
            return result

def get_first_quoted_str(astr):
    # Gets first string from input string that is found in between double quotes
    result = ""
    if astr.count('"') >= 2: 
        pos = astr.find('"')
        tmpstr = astr[pos+1:]
        pos = tmpstr.find('"')
        result = tmpstr[0:pos]
    return result

''' Shapefile must die, so here the alternative!'''
def to_geopkg(raster, outputfile, attr_name, srs_wkt, *args):
    # Initialise
    global rg
    rg = raster
    result = False    
    
    # Check and process input
    if len(args) == 3:
        coordsys_id = int(args[2]) # e.g. EPSG
    else:
        coordsys_id = 3
    if len(args) == 2:
        authority = str(args[1]) 
        datatype = args[0] # i or f
    elif len(args) == 1:
        authority = 'EPSG'
        datatype = args[0] # i or f
    else:
        datatype = 'i'
        authority = 'EPSG'
    
    try:
        # Create the geopackage
        gpkg = GeoPackage.create(outputfile)
        
        # Create the feature class
        projname = get_first_quoted_str(srs_wkt)
        srs = SRS(projname, authority, coordsys_id, srs_wkt)
        fields = [Field('id', SQLFieldTypes.integer)]
        name = outputfile.stem
        fc = gpkg.create_feature_class(name, srs, fields=fields, shape_type=GeometryType.polygon)
    
        # Create field_names
        field_names = [SHAPE, 'id']
    
        # Generate the geometry header once - it is always the same
        polygon_geom_hdr = make_gpkg_geom_header(fc.srs.srs_id)
        
        # Generate the polygons and attributes
        rings = []
        for i in range(rg.nrows):
            line = rg.next()
            for k in range(rg.ncols):
                # Check that we're not dealing with "nodata"
                if line[k] == rg.nodatavalue: continue                
                
                # Get the properties of the current pixel p and convert them into well known bytes
                p = Pixel(k, i)
                coords = [(p.xll,p.yll), (p.xll,p.yll+p.dy), (p.xll+p.dx,p.yll+p.dy), (p.xll+p.dx,p.yll), (p.xll,p.yll)]            
                ring = [coords]
                wkb = point_lists_to_gpkg_polygon(polygon_geom_hdr, ring)
                rings.append((wkb, int(line[k])))
                
        # Insert all rings
        fc.insert_rows(field_names, rings)
        
        # Finish up
        result = True
    except Exception as e:
        print(e)
    finally:
        return result
