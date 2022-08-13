# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_geo.ipynb (unless otherwise specified).

__all__ = ['country_bounding_boxes', 'dict2json', 'Region', 'RegionST']

# Cell
import rasterio
import numpy as np
import pandas as pd
import json

# Cell
# extracted from http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip
# under public domain terms
country_bounding_boxes = {
    'AF': ('Afghanistan', (60.5284298033, 29.318572496, 75.1580277851, 38.4862816432)),
    'AO': ('Angola', (11.6400960629, -17.9306364885, 24.0799052263, -4.43802336998)),
    'AL': ('Albania', (19.3044861183, 39.624997667, 21.0200403175, 42.6882473822)),
    'AE': ('United Arab Emirates', (51.5795186705, 22.4969475367, 56.3968473651, 26.055464179)),
    'AR': ('Argentina', (-73.4154357571, -55.25, -53.628348965, -21.8323104794)),
    'AM': ('Armenia', (43.5827458026, 38.7412014837, 46.5057198423, 41.2481285671)),
    'AQ': ('Antarctica', (-180.0, -90.0, 180.0, -63.2706604895)),
    'TF': ('Fr. S. and Antarctic Lands', (68.72, -49.775, 70.56, -48.625)),
    'AU': ('Australia', (113.338953078, -43.6345972634, 153.569469029, -10.6681857235)),
    'AT': ('Austria', (9.47996951665, 46.4318173285, 16.9796667823, 49.0390742051)),
    'AZ': ('Azerbaijan', (44.7939896991, 38.2703775091, 50.3928210793, 41.8606751572)),
    'BI': ('Burundi', (29.0249263852, -4.49998341229, 30.752262811, -2.34848683025)),
    'BE': ('Belgium', (2.51357303225, 49.5294835476, 6.15665815596, 51.4750237087)),
    'BJ': ('Benin', (0.772335646171, 6.14215770103, 3.79711225751, 12.2356358912)),
    'BF': ('Burkina Faso', (-5.47056494793, 9.61083486576, 2.17710778159, 15.1161577418)),
    'BD': ('Bangladesh', (88.0844222351, 20.670883287, 92.6727209818, 26.4465255803)),
    'BG': ('Bulgaria', (22.3805257504, 41.2344859889, 28.5580814959, 44.2349230007)),
    'BS': ('Bahamas', (-78.98, 23.71, -77.0, 27.04)),
    'BA': ('Bosnia and Herz.', (15.7500260759, 42.65, 19.59976, 45.2337767604)),
    'BY': ('Belarus', (23.1994938494, 51.3195034857, 32.6936430193, 56.1691299506)),
    'BZ': ('Belize', (-89.2291216703, 15.8869375676, -88.1068129138, 18.4999822047)),
    'BO': ('Bolivia', (-69.5904237535, -22.8729187965, -57.4983711412, -9.76198780685)),
    'BR': ('Brazil', (-73.9872354804, -33.7683777809, -34.7299934555, 5.24448639569)),
    'BN': ('Brunei', (114.204016555, 4.007636827, 115.450710484, 5.44772980389)),
    'BT': ('Bhutan', (88.8142484883, 26.7194029811, 92.1037117859, 28.2964385035)),
    'BW': ('Botswana', (19.8954577979, -26.8285429827, 29.4321883481, -17.6618156877)),
    'CF': ('Central African Rep.', (14.4594071794, 2.2676396753, 27.3742261085, 11.1423951278)),
    'CA': ('Canada', (-140.99778, 41.6751050889, -52.6480987209, 83.23324)),
    'CH': ('Switzerland', (6.02260949059, 45.7769477403, 10.4427014502, 47.8308275417)),
    'CL': ('Chile', (-75.6443953112, -55.61183, -66.95992, -17.5800118954)),
    'CN': ('China', (73.6753792663, 18.197700914, 135.026311477, 53.4588044297)),
    'CI': ('Ivory Coast', (-8.60288021487, 4.33828847902, -2.56218950033, 10.5240607772)),
    'CM': ('Cameroon', (8.48881554529, 1.72767263428, 16.0128524106, 12.8593962671)),
    'CD': ('Congo (Kinshasa)', (12.1823368669, -13.2572266578, 31.1741492042, 5.25608775474)),
    'CG': ('Congo (Brazzaville)', (11.0937728207, -5.03798674888, 18.4530652198, 3.72819651938)),
    'CO': ('Colombia', (-78.9909352282, -4.29818694419, -66.8763258531, 12.4373031682)),
    'CR': ('Costa Rica', (-85.94172543, 8.22502798099, -82.5461962552, 11.2171192489)),
    'CU': ('Cuba', (-84.9749110583, 19.8554808619, -74.1780248685, 23.1886107447)),
    'CY': ('Cyprus', (32.2566671079, 34.5718694118, 34.0048808123, 35.1731247015)),
    'CZ': ('Czech Rep.', (12.2401111182, 48.5553052842, 18.8531441586, 51.1172677679)),
    'DE': ('Germany', (5.98865807458, 47.3024876979, 15.0169958839, 54.983104153)),
    'DJ': ('Djibouti', (41.66176, 10.9268785669, 43.3178524107, 12.6996385767)),
    'DK': ('Denmark', (8.08997684086, 54.8000145534, 12.6900061378, 57.730016588)),
    'DO': ('Dominican Rep.', (-71.9451120673, 17.598564358, -68.3179432848, 19.8849105901)),
    'DZ': ('Algeria', (-8.68439978681, 19.0573642034, 11.9995056495, 37.1183806422)),
    'EC': ('Ecuador', (-80.9677654691, -4.95912851321, -75.2337227037, 1.3809237736)),
    'EG': ('Egypt', (24.70007, 22.0, 36.86623, 31.58568)),
    'ER': ('Eritrea', (36.3231889178, 12.4554157577, 43.0812260272, 17.9983074)),
    'ES': ('Spain', (-9.39288367353, 35.946850084, 3.03948408368, 43.7483377142)),
    'EE': ('Estonia', (23.3397953631, 57.4745283067, 28.1316992531, 59.6110903998)),
    'ET': ('Ethiopia', (32.95418, 3.42206, 47.78942, 14.95943)),
    'FI': ('Finland', (20.6455928891, 59.846373196, 31.5160921567, 70.1641930203)),
    'FJ': ('Fiji', (-180.0, -18.28799, 180.0, -16.0208822567)),
    'FK': ('Falkland Is.', (-61.2, -52.3, -57.75, -51.1)),
    'FR': ('France', (-54.5247541978, 2.05338918702, 9.56001631027, 51.1485061713)),
    'GA': ('Gabon', (8.79799563969, -3.97882659263, 14.4254557634, 2.32675751384)),
    'GB': ('United Kingdom', (-7.57216793459, 49.959999905, 1.68153079591, 58.6350001085)),
    'GE': ('Georgia', (39.9550085793, 41.0644446885, 46.6379081561, 43.553104153)),
    'GH': ('Ghana', (-3.24437008301, 4.71046214438, 1.0601216976, 11.0983409693)),
    'GN': ('Guinea', (-15.1303112452, 7.3090373804, -7.83210038902, 12.5861829696)),
    'GM': ('Gambia', (-16.8415246241, 13.1302841252, -13.8449633448, 13.8764918075)),
    'GW': ('Guinea Bissau', (-16.6774519516, 11.0404116887, -13.7004760401, 12.6281700708)),
    'GQ': ('Eq. Guinea', (9.3056132341, 1.01011953369, 11.285078973, 2.28386607504)),
    'GR': ('Greece', (20.1500159034, 34.9199876979, 26.6041955909, 41.8269046087)),
    'GL': ('Greenland', (-73.297, 60.03676, -12.20855, 83.64513)),
    'GT': ('Guatemala', (-92.2292486234, 13.7353376327, -88.2250227526, 17.8193260767)),
    'GY': ('Guyana', (-61.4103029039, 1.26808828369, -56.5393857489, 8.36703481692)),
    'HN': ('Honduras', (-89.3533259753, 12.9846857772, -83.147219001, 16.0054057886)),
    'HR': ('Croatia', (13.6569755388, 42.47999136, 19.3904757016, 46.5037509222)),
    'HT': ('Haiti', (-74.4580336168, 18.0309927434, -71.6248732164, 19.9156839055)),
    'HU': ('Hungary', (16.2022982113, 45.7594811061, 22.710531447, 48.6238540716)),
    'ID': ('Indonesia', (95.2930261576, -10.3599874813, 141.03385176, 5.47982086834)),
    'IN': ('India', (68.1766451354, 7.96553477623, 97.4025614766, 35.4940095078)),
    'IE': ('Ireland', (-9.97708574059, 51.6693012559, -6.03298539878, 55.1316222195)),
    'IR': ('Iran', (44.1092252948, 25.0782370061, 63.3166317076, 39.7130026312)),
    'IQ': ('Iraq', (38.7923405291, 29.0990251735, 48.5679712258, 37.3852635768)),
    'IS': ('Iceland', (-24.3261840479, 63.4963829617, -13.609732225, 66.5267923041)),
    'IL': ('Israel', (34.2654333839, 29.5013261988, 35.8363969256, 33.2774264593)),
    'IT': ('Italy', (6.7499552751, 36.619987291, 18.4802470232, 47.1153931748)),
    'JM': ('Jamaica', (-78.3377192858, 17.7011162379, -76.1996585761, 18.5242184514)),
    'JO': ('Jordan', (34.9226025734, 29.1974946152, 39.1954683774, 33.3786864284)),
    'JP': ('Japan', (129.408463169, 31.0295791692, 145.543137242, 45.5514834662)),
    'KZ': ('Kazakhstan', (46.4664457538, 40.6623245306, 87.3599703308, 55.3852501491)),
    'KE': ('Kenya', (33.8935689697, -4.67677, 41.8550830926, 5.506)),
    'KG': ('Kyrgyzstan', (69.464886916, 39.2794632025, 80.2599902689, 43.2983393418)),
    'KH': ('Cambodia', (102.3480994, 10.4865436874, 107.614547968, 14.5705838078)),
    'KR': ('S. Korea', (126.117397903, 34.3900458847, 129.468304478, 38.6122429469)),
    'KW': ('Kuwait', (46.5687134133, 28.5260627304, 48.4160941913, 30.0590699326)),
    'LA': ('Laos', (100.115987583, 13.88109101, 107.564525181, 22.4647531194)),
    'LB': ('Lebanon', (35.1260526873, 33.0890400254, 36.6117501157, 34.6449140488)),
    'LR': ('Liberia', (-11.4387794662, 4.35575511313, -7.53971513511, 8.54105520267)),
    'LY': ('Libya', (9.31941084152, 19.58047, 25.16482, 33.1369957545)),
    'LK': ('Sri Lanka', (79.6951668639, 5.96836985923, 81.7879590189, 9.82407766361)),
    'LS': ('Lesotho', (26.9992619158, -30.6451058896, 29.3251664568, -28.6475017229)),
    'LT': ('Lithuania', (21.0558004086, 53.9057022162, 26.5882792498, 56.3725283881)),
    'LU': ('Luxembourg', (5.67405195478, 49.4426671413, 6.24275109216, 50.1280516628)),
    'LV': ('Latvia', (21.0558004086, 55.61510692, 28.1767094256, 57.9701569688)),
    'MA': ('Morocco', (-17.0204284327, 21.4207341578, -1.12455115397, 35.7599881048)),
    'MD': ('Moldova', (26.6193367856, 45.4882831895, 30.0246586443, 48.4671194525)),
    'MG': ('Madagascar', (43.2541870461, -25.6014344215, 50.4765368996, -12.0405567359)),
    'MX': ('Mexico', (-117.12776, 14.5388286402, -86.811982388, 32.72083)),
    'MK': ('Macedonia', (20.46315, 40.8427269557, 22.9523771502, 42.3202595078)),
    'ML': ('Mali', (-12.1707502914, 10.0963607854, 4.27020999514, 24.9745740829)),
    'MM': ('Myanmar', (92.3032344909, 9.93295990645, 101.180005324, 28.335945136)),
    'ME': ('Montenegro', (18.45, 41.87755, 20.3398, 43.52384)),
    'MN': ('Mongolia', (87.7512642761, 41.5974095729, 119.772823928, 52.0473660345)),
    'MZ': ('Mozambique', (30.1794812355, -26.7421916643, 40.7754752948, -10.3170960425)),
    'MR': ('Mauritania', (-17.0634232243, 14.6168342147, -4.92333736817, 27.3957441269)),
    'MW': ('Malawi', (32.6881653175, -16.8012997372, 35.7719047381, -9.23059905359)),
    'MY': ('Malaysia', (100.085756871, 0.773131415201, 119.181903925, 6.92805288332)),
    'NA': ('Namibia', (11.7341988461, -29.045461928, 25.0844433937, -16.9413428687)),
    'NC': ('New Caledonia', (164.029605748, -22.3999760881, 167.120011428, -20.1056458473)),
    'NE': ('Niger', (0.295646396495, 11.6601671412, 15.9032466977, 23.4716684026)),
    'NG': ('Nigeria', (2.69170169436, 4.24059418377, 14.5771777686, 13.8659239771)),
    'NI': ('Nicaragua', (-87.6684934151, 10.7268390975, -83.147219001, 15.0162671981)),
    'NL': ('Netherlands', (3.31497114423, 50.803721015, 7.09205325687, 53.5104033474)),
    'NO': ('Norway', (4.99207807783, 58.0788841824, 31.29341841, 80.6571442736)),
    'NP': ('Nepal', (80.0884245137, 26.3978980576, 88.1748043151, 30.4227169866)),
    'NZ': ('New Zealand', (166.509144322, -46.641235447, 178.517093541, -34.4506617165)),
    'OM': ('Oman', (52.0000098, 16.6510511337, 59.8080603372, 26.3959343531)),
    'PK': ('Pakistan', (60.8742484882, 23.6919650335, 77.8374507995, 37.1330309108)),
    'PA': ('Panama', (-82.9657830472, 7.2205414901, -77.2425664944, 9.61161001224)),
    'PE': ('Peru', (-81.4109425524, -18.3479753557, -68.6650797187, -0.0572054988649)),
    'PH': ('Philippines', (117.17427453, 5.58100332277, 126.537423944, 18.5052273625)),
    'PG': ('Papua New Guinea', (141.000210403, -10.6524760881, 156.019965448, -2.50000212973)),
    'PL': ('Poland', (14.0745211117, 49.0273953314, 24.0299857927, 54.8515359564)),
    'PR': ('Puerto Rico', (-67.2424275377, 17.946553453, -65.5910037909, 18.5206011011)),
    'KP': ('N. Korea', (124.265624628, 37.669070543, 130.780007359, 42.9853868678)),
    'PT': ('Portugal', (-9.52657060387, 36.838268541, -6.3890876937, 42.280468655)),
    'PY': ('Paraguay', (-62.6850571357, -27.5484990374, -54.2929595608, -19.3427466773)),
    'QA': ('Qatar', (50.7439107603, 24.5563308782, 51.6067004738, 26.1145820175)),
    'RO': ('Romania', (20.2201924985, 43.6884447292, 29.62654341, 48.2208812526)),
    'RU': ('Russia', (-180.0, 41.151416124, 180.0, 81.2504)),
    'RW': ('Rwanda', (29.0249263852, -2.91785776125, 30.8161348813, -1.13465911215)),
    'SA': ('Saudi Arabia', (34.6323360532, 16.3478913436, 55.6666593769, 32.161008816)),
    'SD': ('Sudan', (21.93681, 8.61972971293, 38.4100899595, 22.0)),
    'SS': ('S. Sudan', (23.8869795809, 3.50917, 35.2980071182, 12.2480077571)),
    'SN': ('Senegal', (-17.6250426905, 12.332089952, -11.4678991358, 16.5982636581)),
    'SB': ('Solomon Is.', (156.491357864, -10.8263672828, 162.398645868, -6.59933847415)),
    'SL': ('Sierra Leone', (-13.2465502588, 6.78591685631, -10.2300935531, 10.0469839543)),
    'SV': ('El Salvador', (-90.0955545723, 13.1490168319, -87.7235029772, 14.4241327987)),
    'SO': ('Somalia', (40.98105, -1.68325, 51.13387, 12.02464)),
    'RS': ('Serbia', (18.82982, 42.2452243971, 22.9860185076, 46.1717298447)),
    'SR': ('Suriname', (-58.0446943834, 1.81766714112, -53.9580446031, 6.0252914494)),
    'SK': ('Slovakia', (16.8799829444, 47.7584288601, 22.5581376482, 49.5715740017)),
    'SI': ('Slovenia', (13.6981099789, 45.4523163926, 16.5648083839, 46.8523859727)),
    'SE': ('Sweden', (11.0273686052, 55.3617373725, 23.9033785336, 69.1062472602)),
    'SZ': ('Swaziland', (30.6766085141, -27.2858794085, 32.0716654803, -25.660190525)),
    'SY': ('Syria', (35.7007979673, 32.312937527, 42.3495910988, 37.2298725449)),
    'TD': ('Chad', (13.5403935076, 7.42192454674, 23.88689, 23.40972)),
    'TG': ('Togo', (-0.0497847151599, 5.92883738853, 1.86524051271, 11.0186817489)),
    'TH': ('Thailand', (97.3758964376, 5.69138418215, 105.589038527, 20.4178496363)),
    'TJ': ('Tajikistan', (67.4422196796, 36.7381712916, 74.9800024759, 40.9602133245)),
    'TM': ('Turkmenistan', (52.5024597512, 35.2706639674, 66.5461503437, 42.7515510117)),
    'TL': ('East Timor', (124.968682489, -9.39317310958, 127.335928176, -8.27334482181)),
    'TT': ('Trinidad and Tobago', (-61.95, 10.0, -60.895, 10.89)),
    'TN': ('Tunisia', (7.52448164229, 30.3075560572, 11.4887874691, 37.3499944118)),
    'TR': ('Turkey', (26.0433512713, 35.8215347357, 44.7939896991, 42.1414848903)),
    'TW': ('Taiwan', (120.106188593, 21.9705713974, 121.951243931, 25.2954588893)),
    'TZ': ('Tanzania', (29.3399975929, -11.7209380022, 40.31659, -0.95)),
    'UG': ('Uganda', (29.5794661801, -1.44332244223, 35.03599, 4.24988494736)),
    'UA': ('Ukraine', (22.0856083513, 44.3614785833, 40.0807890155, 52.3350745713)),
    'UY': ('Uruguay', (-58.4270741441, -34.9526465797, -53.209588996, -30.1096863746)),
    'US': ('United States', (-171.791110603, 18.91619, -66.96466, 71.3577635769)),
    'UZ': ('Uzbekistan', (55.9289172707, 37.1449940049, 73.055417108, 45.5868043076)),
    'VE': ('Venezuela', (-73.3049515449, 0.724452215982, -59.7582848782, 12.1623070337)),
    'VN': ('Vietnam', (102.170435826, 8.59975962975, 109.33526981, 23.3520633001)),
    'VU': ('Vanuatu', (166.629136998, -16.5978496233, 167.844876744, -14.6264970842)),
    'PS': ('West Bank', (34.9274084816, 31.3534353704, 35.5456653175, 32.5325106878)),
    'YE': ('Yemen', (42.6048726743, 12.5859504257, 53.1085726255, 19.0000033635)),
    'ZA': ('South Africa', (16.3449768409, -34.8191663551, 32.830120477, -22.0913127581)),
    'ZM': ('Zambia', (21.887842645, -17.9612289364, 33.4856876971, -8.23825652429)),
    'ZW': ('Zimbabwe', (25.2642257016, -22.2716118303, 32.8498608742, -15.5077869605)),
}

# Cell
def dict2json(data:dict, file):
    "Writes json file from dict"
    with open(file, 'w') as f:
        f.write(json.dumps(data))

class Region():
    """Defines a geographical region with a name, a bounding box and the pixel size"""
    def __init__(self, name:str, bbox:list, pixel_size:float):
        self.name = name
        self.bbox = rasterio.coords.BoundingBox(*bbox) # left, bottom, right, top
        self.pixel_size = pixel_size

    @property
    def width(self):
        "Width of the region"
        return int(np.round(np.abs(self.bbox.left-self.bbox.right)/self.pixel_size))

    @property
    def height(self):
        "Height of the region"
        return int(np.round(np.abs(self.bbox.top-self.bbox.bottom)/self.pixel_size))

    @property
    def transform(self):
        "Rasterio Affine transform of the region"
        return rasterio.transform.from_bounds(*self.bbox, self.width, self.height)

    @property
    def shape(self):
        "Shape of the region (height, width)"
        return (self.height, self.width)

    def coords(self, offset='ul'):
        "Computes longitude and latitude arrays given a shape and a rasterio Affine transform"
        rxy = rasterio.transform.xy
        ys, xs = map(range, self.shape)
        return (np.array(rxy(self.transform, [0]*len(xs), xs, offset=offset)[0]),
                np.array(rxy(self.transform, ys, [0]*len(ys), offset=offset)[1]))

    @classmethod
    def load(cls, file):
        "Loads region information from json file"
        with open(file, 'r') as f:
            args = json.load(f)
        return cls(args['name'], args['bbox'], args['pixel_size'])

    def export(self, file):
        """Exports region information to json file"""
        dict2json(self.__dict__, file)

    def __repr__(self):
        return '\n'.join([f'{i}: {o}' for i, o in self.__dict__.items()]) + '\n'


class RegionST(Region):
    "Defines a region in space and time with a name, a bounding box and the pixel size."
    def __init__(self, name:str, bbox:list, pixel_size:float, time_start:str=None,
                 time_end:str=None, time_freq:str='D', time_margin:int=0):
        self.name = name
        self.bbox = rasterio.coords.BoundingBox(*bbox) # left, bottom, right, top
        self.pixel_size = pixel_size
        self.time_start = pd.Timestamp(str(time_start))
        self.time_end = pd.Timestamp(str(time_end))
        self.time_margin = time_margin
        self.time_freq = time_freq

    @property
    def times(self):
        "Property that computes the date_range for the region."
        tstart = self.time_start - pd.Timedelta(days=self.time_margin)
        tend = self.time_end + pd.Timedelta(days=self.time_margin)
        return pd.date_range(tstart, tend, freq=self.time_freq)

    @classmethod
    def load(cls, file, time_start=None, time_end=None):
        "Loads region information from json file"
        with open(file, 'r') as f:
            args = json.load(f)
        if time_start is None:
            time_start = args['time_start']
        if time_end is None:
            time_end = args['time_end']
        return cls(args['name'], args['bbox'], args['pixel_size'],
                   time_start, time_end)