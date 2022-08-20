import re

from .ascii import asciilator
from .diacritics import ACUTE
from .punctuation import APOSTROPHES, DELIMITERS

vowels_lower_cyr = "аеиіоу"
vowels_upper_cyr = vowels_lower_cyr.upper()
vowels_cyr = vowels_lower_cyr + vowels_upper_cyr

vowels_lower_lat = "aeyiou"
vowels_upper_lat = vowels_lower_lat.upper()
vowels_lat = vowels_lower_lat + vowels_upper_lat

iotted_lower_cyr = "єїюя"
iotted_upper_cyr = iotted_lower_cyr.upper()
iotted_cyr = iotted_lower_cyr + iotted_upper_cyr

iotted_lower_out = "еіуа"
iotted_upper_out = iotted_lower_out.upper()

iotted_lower_lat = "eiua"
iotted_upper_lat = iotted_lower_lat.upper()

iot_lower_cyr = "й"
iot_upper_cyr = iot_lower_cyr.upper()

iot_lower_lat = "j"
iot_upper_lat = iot_lower_lat.upper()

consonants_lower_cyr = "бвдгґжзйклмнпрстфхцчш"
consonants_upper_cyr = consonants_lower_cyr.upper()
consonants_cyr = consonants_lower_cyr + consonants_upper_cyr

consonants_lower_lat = "bvdhgžzjklmnprstfxcčš"
consonants_upper_lat = consonants_lower_lat.upper()
consonants_lat = consonants_lower_lat + consonants_upper_lat

soft_sign_lower_cyr = "ь"
soft_sign_upper_cyr = soft_sign_lower_cyr.upper()
soft_sign_cyr = soft_sign_lower_cyr + soft_sign_upper_cyr

soft_sign_lat = ACUTE * 2

sqcq_lower_cyr = "щ"
sqcq_upper_cyr = sqcq_lower_cyr.upper()
sqcq_cyr = sqcq_lower_cyr + sqcq_upper_cyr

sqcq_lower_lat = "šč"
sqcq_upper_lat = sqcq_lower_lat.upper()

w_cyr = "вВ"
w_lat = "wW"

lower_cyr = (
    vowels_lower_cyr + iotted_lower_cyr + consonants_lower_cyr + sqcq_lower_cyr
)
all_cyr = vowels_cyr + iotted_cyr + consonants_cyr + soft_sign_cyr + sqcq_cyr

abbr = (
    ("ЄІБ", "JeIB"),
    ("ЄАВТ", "JeAVT"),
    ("ЄАЕС", "JeAES"),
    ("ЄАНТК", "JeANTK"),
    ("ЄАР", "JeAR"),
    ("ЄБА", "JeBA"),
    ("ЄБРР", "JeBRR"),
    ("ЄВС", "JeVS"),
    ("ЄГФ", "JeHF"),
    ("ЄДІ", "JeDI"),
    ("ЄДАПС", "JeDAPS"),
    ("ЄДЕБО", "JeDEBO"),
    ("ЄДКІ", "JeDKI"),
    ("ЄДР", "JeDR"),
    ("ЄДРПОУ", "JeDRPOU"),
    ("ЄЕК", "JeEK"),
    ("ЄЕП", "JeEP"),
    ("ЄЕС", "JeES"),
    ("ЄЕСУ", "JeESU"),
    ("ЄК", "JeK"),
    ("ЄКА", "JeKA"),
    ("ЄКВ", "JeKV"),
    ("ЄКП", "JeKP"),
    ("ЄКПЛ", "JeKPL"),
    ("ЄКРН", "JeKRN"),
    ("ЄНП", "JeNP"),
    ("ЄНР", "JeNR"),
    ("ЄОВС", "JeOVS"),
    ("ЄП", "JeP"),
    ("ЄПС", "JePS"),
    ("ЄР", "JeR"),
    ("ЄРДР", "JeRDR"),
    ("ЄРПН", "JeRPN"),
    ("ЄРЦ", "JeRC"),
    ("ЄС", "JeS"),
    ("ЄСВ", "JeSW"),
    ("ЄСВС", "JeSVS"),
    ("ЄСПЛ", "JeSPL"),
    ("ЄУ", "JeU"),
    ("ЄХБ", "JeXB"),
    ("ЄЦ", "JeC"),
    ("ЄЦБ", "JeCB"),
    ("АВМ", "AVM"),
    ("АТВТ", "ATVT"),
    ("БДЮТ", "BDJuT"),
    ("БЮТ", "BJuT"),
    ("ВВ", "WV"),
    ("ВВІР", "VVIR"),
    ("ВВВ", "VVV"),
    ("ВВНЗ", "VVNZ"),
    ("ВВП", "VWP"),
    ("ВВР", "VVR"),
    ("ВГК", "VHK"),
    ("ВГСУ", "VHSU"),
    ("ВД", "VD"),
    ("ВДАІ", "VDAI"),
    ("ВДВ", "VDV"),
    ("ВДЕ", "VĐE"),
    ("ВДНГ", "VDNH"),
    ("ВДПУ", "VDPU"),
    ("ВЗ", "VZ"),
    ("ВЗУН", "VZUN"),
    ("ВК", "VK"),
    ("ВКВ", "VKV"),
    ("ВККС", "VKKS"),
    ("ВККСУ", "VKKSU"),
    ("ВКЛ", "VKL"),
    ("ВМД", "VMD"),
    ("ВМС", "VMS"),
    ("ВМСУ", "VMSU"),
    ("ВМФ", "VMF"),
    ("ВНАУ", "VNAU"),
    ("ВНЗ", "VNZ"),
    ("ВНО", "VNO"),
    ("ВНП", "VNP"),
    ("ВНТ", "VNT"),
    ("ВНТУ", "VNTU"),
    ("ВОІВ", "WOIW"),
    ("ВП", "VP"),
    ("ВПК", "VPK"),
    ("ВПЛ", "VPL"),
    ("ВПС", "VPS"),
    ("ВПУ", "VPU"),
    ("ВР", "VR"),
    ("ВРП", "VRP"),
    ("ВРУ", "VRU"),
    ("ВРХ", "VRX"),
    ("ВРЮ", "VRJu"),
    ("ВС", "VS"),
    ("ВСП", "VSP"),
    ("ВССУ", "VSSU"),
    ("ВСУ", "VSU"),
    ("ВТС", "VTS"),
    ("ВТССУМ", "VTSSUM"),
    ("ВУЦВК", "WUCVK"),
    ("ВЦА", "VCA"),
    ("ВЦВК", "WCVK"),
    ("ВЧ", "VČ"),
    ("ВШ", "VŠ"),
    ("ВЯП", "VJaP"),
    ("ГЛСВ", "HLSV"),
    ("ГеВ", "HeV"),
    ("ДЄС", "DJeS"),
    ("ДБЖ", "ĐBŽ"),
    ("ДВК", "DVK"),
    ("ДВНЗ", "DVNZ"),
    ("ДВП", "DVP"),
    ("ДВС", "DVS"),
    ("ДКВС", "DKVS"),
    ("ДНВП", "DNVP"),
    ("ДНЯЗ", "DNJaZ"),
    ("ДРВ", "DRV"),
    ("ДШВ", "DŠV"),
    ("ДЮСШ", "DJuSŠ"),
    ("ДЮСШОР", "DJuSŠOR"),
    ("ДЮФЛ", "DJuFL"),
    ("ЗЄС", "ZJeS"),
    ("ЗВР", "ZVR"),
    ("ЗВТ", "ZVT"),
    ("КВК", "KVK"),
    ("КВН", "KVN"),
    ("КДЮСШ", "KDJuSŠ"),
    ("КЕКВ", "KEKV"),
    ("КПВВ", "KPWV"),
    ("ЛЄ", "LJe"),
    ("ЛНВ", "LNV"),
    ("МВ", "MV"),
    ("МВК", "MVK"),
    ("МВФ", "MVF"),
    ("МРЕВ", "MREV"),
    ("МСВ", "MSV"),
    ("МФВ", "MFV"),
    ("МеВ", "MeV"),
    ("НАЗЯВО", "NAZJaVO"),
    ("НБСЄ", "NBSJe"),
    ("НБУВ", "NBUV"),
    ("НВК", "NVK"),
    ("НВКГ", "KVKH"),
    ("НВП", "NVP"),
    ("НВР", "NVR"),
    ("НВФ", "NVF"),
    ("НВЦ", "NVC"),
    ("НВЧ", "NVČ"),
    ("НУВГП", "NUVHP"),
    ("ОІЯД", "OIJaD"),
    ("ОАЄ", "OAJe"),
    ("ОБСЄ", "OBSJe"),
    ("ОВД", "OVD"),
    ("ОВК", "OVK"),
    ("ОВП", "OVP"),
    ("ОВТ", "OVT"),
    ("ОГРВ", "OHRV"),
    ("ОДЮСШ", "ODJuSŠ"),
    ("ОКВ", "OKV"),
    ("ПАРЄ", "PARJe"),
    ("ПВ", "PV"),
    ("ПВЗВТ", "PWZVT"),
    ("ПВК", "PVK"),
    ("ПВХ", "PVX"),
    ("ПДВ", "PDV"),
    ("ПДВЛ", "PDVL"),
    ("ПнВК", "PnVK"),
    ("РЄ", "RJe"),
    ("РАВ", "RAV"),
    ("РВ", "RV"),
    ("РВВС", "RVWS"),
    ("РВСП", "RVSP"),
    ("РСЗВ", "RSZV"),
    ("СЄПН", "SJePN"),
    ("СВ", "SV"),
    ("СВГ", "SVH"),
    ("СДЮШО", "SDJuŠO"),
    ("СДЮШОР", "SDJuŠOR"),
    ("СРВ", "SRV"),
    ("СРЮ", "SRJu"),
    ("СТОВ", "STOV"),
    ("СФРЮ", "SFRJu"),
    ("СЧВ", "SČV"),
    ("ТВД", "TVD"),
    ("ТВЗ", "TVZ"),
    ("ТВК", "TVK"),
    ("ТДВ", "TDV"),
    ("ТОВ", "TOV"),
    ("ТПВ", "TPV"),
    ("ТЮГ", "TJuH"),
    ("ТеВ", "TeV"),
    ("ТзОВ", "TzOV"),
    ("УЄФА", "UJeFA"),
    ("УЄЦАВ", "UJeCAV"),
    ("УАВПП", "UAVPP"),
    ("УВВ", "UVV"),
    ("УВК", "UVK"),
    ("УВКБ", "UVKB"),
    ("УВКПЛ", "UVKPL"),
    ("УВП", "UVP"),
    ("УГВ", "UHV"),
    ("УГВК", "UHVK"),
    ("УГВР", "UHVR"),
    ("УМВБ", "UMVB"),
    ("УМВГ", "UMVH"),
    ("УЦОЯО", "UCOJaO"),
    ("ФСВП", "FSVP"),
    ("ХВЄ", "XVJe"),
    ("ХДАВП", "XDAVP"),
    ("ЦВК", "CVK"),
    ("ЦДАВОВ", "CDAVOW"),
    ("ЦДВР", "CDVR"),
    ("ЦДЮТ", "CDJuT"),
    ("ЦМВ", "CMV"),
    ("ЦОВВ", "COVW"),
    ("ЦПКіВ", "CPKiV"),
    ("ЦСЄ", "CSJe"),
    ("ЦСВЯП", "CSVJaP"),
    ("ЧЄ", "ČJe"),
    ("ЧСВВ", "ČSVV"),
    ("ШВЛ", "ŠVL"),
    ("ШВСМ", "ŠVSM"),
    ("ЮВТ", "JuVT"),
    ("ЮНІДО", "JuNIDO"),
    ("ЮНІСЕФ", "JuNISEF"),
    ("ЮНЕП", "JuNEP"),
    ("ЮНЕСКО", "JuNESKO"),
    ("ЮНКТАД", "JuNKTAD"),
    ("ЮНОПС", "JuNOPS"),
    ("ЮНСІТРАЛ", "JuNSITRAL"),
    ("ЮРС", "JuRS"),
    ("ЮУАЕС", "JuUAES"),
    ("ЮФ", "JuF"),
    ("ЯМР", "JaMR"),
    ("еВ", "eV"),
    ("кВ", "kV"),
    ("мВ", "mV"),
    ("мкВ", "mkV"),
    ("облВНО", "oblVNO"),
)
abbr_dot_pattern = (
    r"(?i:(?<=\b)|(?<=\b(г|з|і|к|с))|(?<=\b(ди|за|ін|по|св))|"
    r"(?<=\b(про|сло))|(?<=\b(буль|пере|родо))){0}(?=\.)"
)

w_pattern = (
    r"((?<=\b)|(?<=[_%s])){0}((?=[%s])|(?=[%s])|(?=\W*$)|"
    r"(?=\W*[%s](?:\W|$))|(?=\W+[%s]))"
    % (
        all_cyr,
        consonants_cyr + sqcq_cyr,
        APOSTROPHES,
        DELIMITERS,
        consonants_cyr + sqcq_cyr + iotted_cyr + consonants_lat,
    )
)

apostrophe_pattern = r"(?<=[%s])[%s]{0}" % (all_cyr + w_lat, APOSTROPHES)
iotted_pattern = r"((?<=\b)|(?<=[%s])){0}" % (vowels_cyr + iotted_cyr)
ending_pattern = r"(?=[%s]|\W+[%s]|\W*$)" % (
    lower_cyr + "w",
    lower_cyr + vowels_lat + consonants_lat + w_lat
)
acuted_pattern = r"(?<=[%s]){0}" % (consonants_cyr + sqcq_cyr)

affricate_exclude_patterns = (
    r"(?i:(?<=ме)){0}(?i:((?=заклад)|(?=захис)))",
    r"(?i:(?<=\bро)){0}(?i:(?=зал))",
    r"(?i:((?<=\bбу)|(?<=\bзагоро)|(?<=\bме)|(?<=\bпро))){0}(?i:(?=заг[іо]н))",
    r"(?i:((?<=\bвищеві)|(?<=\bкінові)|(?<=\bлітві)|(?<=\bра)|(?<=\bспецві)))"
    r"{0}(?i:(?=зна[кч]))",
    r"(?i:(?<=епі)){0}(?i:(?=зах[іо]д))",
    r"(?i:(?<=пі)){0}(?i:(?=жи[вw]))",
)
affricate_pattern_1 = r"(?i:(?<=\bпере)){0}(?i:з)(?i:(?=вен|він|вон|ижч))"
affricate_pattern_2 = (
    r"(?i:(?!(?<=\bві)|(?<=\bна)|(?<=\bо)|(?<=\bпере)|(?<=\bпі)|(?<=\bпона)|"
    r"(?<=\bпопі)|(?<=\bпре)|(?<=\bсере)|(?<=\bневі)|(?<=\bнепі)|(?<=\bнапере)"
    r"|(?<=\bопі))){0}"
)

patterns = ()
patterns += (
    (abbr_dot_pattern.format("в"), "v"),
    (abbr_dot_pattern.format("В"), "V"),
)
patterns += tuple((r"\b{0}\b".format(cyr), lat) for cyr, lat in abbr)
patterns += tuple(
    (w_pattern.format(cyr), lat) for cyr, lat in zip(w_cyr, w_lat)
)

patterns += ((sqcq_upper_cyr + ending_pattern, sqcq_lower_lat.title()),)

patterns += tuple(
    (apostrophe_pattern.format(cyr), iot_lower_cyr + out)
    for cyr, out in zip(iotted_lower_cyr, iotted_lower_out)
)
patterns += tuple(
    (apostrophe_pattern.format(cyr) + ending_pattern, iot_upper_cyr + out)
    for cyr, out in zip(iotted_upper_cyr, iotted_lower_out)
)
patterns += tuple(
    (apostrophe_pattern.format(cyr), iot_upper_cyr + out)
    for cyr, out in zip(iotted_upper_cyr, iotted_upper_out)
)

patterns += tuple(
    (iotted_pattern.format(cyr) + ending_pattern, iot_upper_cyr + out)
    for cyr, out in zip(iotted_upper_cyr, iotted_lower_out)
)

patterns += tuple(
    (acuted_pattern.format(cyr), ACUTE + out)
    for cyr, out in zip(iotted_lower_cyr, iotted_lower_out)
)
patterns += tuple(
    (acuted_pattern.format(cyr), ACUTE + out)
    for cyr, out in zip(iotted_upper_cyr, iotted_upper_out)
)

patterns += tuple(
    (pattern.format("д"), "d") for pattern in affricate_exclude_patterns
)
patterns += tuple(
    (pattern.format("Д"), "D") for pattern in affricate_exclude_patterns
)
patterns += (
    (affricate_pattern_1.format("д"), "ƶ"),
    (affricate_pattern_1.format("Д"), "Ƶ"),
)
patterns += (
    (affricate_pattern_2.format("дж"), "đ"),
    (affricate_pattern_2.format("Дж"), "Đ"),
    (affricate_pattern_2.format("дз"), "ƶ"),
    (affricate_pattern_2.format("Дз"), "Ƶ"),
)

table = dict(
    zip(
        vowels_cyr + consonants_cyr + soft_sign_cyr,
        vowels_lat + consonants_lat + soft_sign_lat,
    )
)
table.update(
    {
        cyr: iot_lower_lat + lat
        for cyr, lat in zip(iotted_lower_cyr, iotted_lower_lat)
    }
)
table.update(
    {
        cyr: iot_upper_lat + lat
        for cyr, lat in zip(iotted_upper_cyr, iotted_upper_lat)
    }
)
table[sqcq_lower_cyr] = sqcq_lower_lat
table[sqcq_upper_cyr] = sqcq_upper_lat
table = str.maketrans(table)


def encode(text, no_diacritics=False):
    result = text

    for pattern, repl in patterns:
        result = re.sub(pattern, repl, result)

    result = result.translate(table)

    if no_diacritics:
        result = asciilator(result)

    return result
