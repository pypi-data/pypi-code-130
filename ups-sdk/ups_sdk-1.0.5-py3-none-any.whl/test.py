from typing import List, Optional
from UPS_SDK.main import TrackType, UPSApi
from UPS_SDK.models import ActivityItem


ACCESS_LICENSE_NUMBER = "0D9B373178F57052"
USER_ID = "BUZV"
PASSWORD = "Falkel.2021"

api = UPSApi(ACCESS_LICENSE_NUMBER, USER_ID, PASSWORD)


tracking_numbers = ['1Z89RA790455452605', '1Z89RA790455240898', '1Z89RA790455997269', '1Z89RA790455315834', '1Z89RA790455891784', '1Z89RA790455219877', '1Z89RA790457072709', '1Z89RA790455879888', '1Z89RA790457185490', '1Z89RA790455829468', '1Z89RA790456292652', '1Z89RA790455553443', '1Z89RA790455572459', '1Z89RA790457785565', '1Z89RA790455445319', '1Z89RA790457461397', '1Z89RA790456443828', '1Z89RA790457425248', '1Z89RA790457595583', '1Z89RA790455637513', '1Z89RA790455111723', '1Z89RA790456909343', '1Z89RA790457583934', '1Z89RA790455889215', '1Z89RA790456407779', '1Z89RA790457607739', '1Z89RA790457233366', '1Z89RA790455571209', '1Z89RA790455459635', '1Z89RA790457101141', '1Z89RA790457492407', '1Z89RA790456352355', '1Z89RA790455663575', '1Z89RA790455121169', '1Z89RA790455493197', '1Z89RA790457463680', '1Z89RA790455555674', '1Z89RA790456592506', '1Z89RA790456897295', '1Z89RA790457871533', '1Z89RA790455327527', '1Z89RA790457800136', '1Z89RA790457113692', '1Z89RA790457200123', '1Z89RA790457269711', '1Z89RA790456592908', '1Z89RA790455361418', '1Z89RA790457209964', '1Z89RA790457068278', '1Z89RA790455445748', '1Z89RA790455693257', '1Z89RA790456273619', '1Z89RA790456069591', '1Z89RA790456052858', '1Z89RA790455748233', '1Z89RA790456204185', '1Z89RA790455256336', '1Z89RA790456729841', '1Z89RA790455153107', '1Z89RA790456813866', '1Z89RA790455412032', '1Z89RA790455988028', '1Z89RA790457493004', '1Z89RA790457966066', '1Z89RA790457101669', '1Z89RA790455625811', '1Z89RA790456504324', '1Z89RA790456681893', '1Z89RA790457341918', '1Z89RA790456432287', '1Z89RA790455753307', '1Z89RA790456321647', '1Z89RA790457853053', '1Z89RA790457317794', '1Z89RA790457173949', '1Z89RA790457536084', '1Z89RA790456252472', '1Z89RA790457427988', '1Z89RA790457072950', '1Z89RA790456777763', '1Z89RA790455890098', '1Z89RA790457416178', '1Z89RA790455452801', '1Z89RA790457680374', '1Z89RA790455205999', '1Z89RA790455220383', '1Z89RA790456778048', '1Z89RA790457596420', '1Z89RA790456324439', '1Z89RA790456418016', '1Z89RA790457632729', '1Z89RA790455806312', '1Z89RA790456888732', '1Z89RA790455724071', '1Z89RA790456660629', '1Z89RA790457140635', '1Z89RA790457476587', '1Z89RA790457944688', '1Z89RA790455573458', '1Z89RA790455393509', '1Z89RA790457738295', '1Z89RA790456372226', '1Z89RA790456276670', '1Z89RA790455952539', '1Z89RA790455734195', '1Z89RA790455650212', '1Z89RA790455784579', '1Z89RA790455693408', '1Z89RA790455542142', '1Z89RA790456648527', '1Z89RA790455854118', '1Z89RA790457558266', '1Z89RA790456466241', '1Z89RA790456564822', '1Z89RA790455153554', '1Z89RA790457728779', '1Z89RA790455902397', '1Z89RA790456394364', '1Z89RA790456972784', '1Z89RA790455794442', '1Z89RA790457493657', '1Z89RA790455196839', '1Z89RA790455425680', '1Z89RA790455338766', '1Z89RA790457073959', '1Z89RA790455137170', '1Z89RA790456119269', '1Z89RA790456294007', '1Z89RA790455821635', '1Z89RA790455029233', '1Z89RA790456370844', '1Z89RA790455975194', '1Z89RA790456997678', '1Z89RA790455986815', '1Z89RA790456894403', '1Z89RA790457357581', '1Z89RA790455905572', '1Z89RA790455974864', '1Z89RA790455158791', '1Z89RA790455893228', '1Z89RA790455454050', '1Z89RA790455581627', '1Z89RA790455507243', '1Z89RA790457153729', '1Z89RA790457414947', '1Z89RA790457979016', '1Z89RA790455327063', '1Z89RA790456901387', '1Z89RA790457033537', '1Z89RA790455015113', '1Z89RA790455531092', '1Z89RA790455574206', '1Z89RA790457554108', '1Z89RA790456594157', '1Z89RA790456493033', '1Z89RA790456226492', '1Z89RA790456481135', '1Z89RA790456121121', '1Z89RA790457849488', '1Z89RA790457043160', '1Z89RA790455773474', '1Z89RA790457246996', '1Z89RA790456601371', '1Z89RA790456593756', '1Z89RA790455062661', '1Z89RA790457762642', '1Z89RA790457194506', '1Z89RA790455579292', '1Z89RA790457793903', '1Z89RA790455434616', '1Z89RA790457198548', '1Z89RA790455146562', '1Z89RA790457030718', '1Z89RA790457417088', '1Z89RA790455710595', '1Z89RA790456708980', '1Z89RA790455453855', '1Z89RA790456053802', '1Z89RA790456970964', '1Z89RA790457486745', '1Z89RA790457354691', '1Z89RA790457512975', '1Z89RA790455845075', '1Z89RA790457513287', '1Z89RA790456354308', '1Z89RA790457494254', '1Z89RA790456805437', '1Z89RA790455137330', '1Z89RA790457073708', '1Z89RA790455590466', '1Z89RA790457140877', '1Z89RA790457198511', '1Z89RA790456456921', '1Z89RA790455064936', '1Z89RA790455389274', '1Z89RA790457560888', '1Z89RA790456625328', '1Z89RA790455122891', '1Z89RA790455302919', '1Z89RA790456685184', '1Z89RA790455574457', '1Z89RA790455754557', '1Z89RA790456191341', '1Z89RA790456167314', '1Z89RA790456061875', '1Z89RA790456049773', '1Z89RA790455555361', '1Z89RA790455317421', '1Z89RA790457254601', '1Z89RA790455351465', '1Z89RA790457343390', '1Z89RA790455053788', '1Z89RA790456685826', '1Z89RA790456035448', '1Z89RA790455694658', '1Z89RA790457283419', '1Z89RA790455267495', '1Z89RA790456241886', '1Z89RA790456550346', '1Z89RA790456983147', '1Z89RA790455630029', '1Z89RA790455999794', '1Z89RA790455507565', '1Z89RA790456654805', '1Z89RA790455994904', '1Z89RA790455759516', '1Z89RA790456527747', '1Z89RA790456263915', '1Z89RA790456746322', '1Z89RA790457033975', '1Z89RA790457309025', '1Z89RA790457177927', '1Z89RA790457298083', '1Z89RA790457969527', '1Z89RA790457595618', '1Z89RA790457074958', '1Z89RA790455351590', '1Z89RA790456023666', '1Z89RA790457166180', '1Z89RA790457595690', '1Z89RA790455162133', '1Z89RA790455989983', '1Z89RA790457854856', '1Z89RA790456203640', '1Z89RA790455545934', '1Z89RA790455042129', '1Z89RA790455394759', '1Z89RA790457574033', '1Z89RA790456899766', '1Z89RA790455018334', '1Z89RA790456955105', '1Z89RA790455135869', '1Z89RA790456563896', '1Z89RA790456710271', '1Z89RA790455858178', '1Z89RA790457655946', '1Z89RA790455414227', '1Z89RA790456011848', '1Z89RA790457310237', '1Z89RA790456347816', '1Z89RA790455077833', '1Z89RA790456055051', '1Z89RA790455095000', '1Z89RA790457795152', '1Z89RA790455112464', '1Z89RA790456276447', '1Z89RA790455784391', '1Z89RA790457922880', '1Z89RA790456655608', '1Z89RA790455244410', '1Z89RA790455172211', '1Z89RA790455095402', '1Z89RA790457370771', '1Z89RA790456134788', '1Z89RA790457555358', '1Z89RA790457502637', '1Z89RA790456355558', '1Z89RA790455294474', '1Z89RA790456420290', '1Z89RA790457238585', '1Z89RA790456038427', '1Z89RA790456290529', '1Z89RA790455114533', '1Z89RA790457718673', '1Z89RA790456674721', '1Z89RA790455450732', '1Z89RA790456540017', '1Z89RA790455039544', '1Z89RA790457680267', '1Z89RA790456731963', '1Z89RA790455582386', '1Z89RA790457195756', '1Z89RA790455868569', '1Z89RA790457958833', '1Z89RA790456287999', '1Z89RA790455172097', '1Z89RA790455832347', '1Z89RA790456528317', '1Z89RA790455575456', '1Z89RA790455995501', '1Z89RA790455522379', '1Z89RA790455575205', '1Z89RA790456216190', '1Z89RA790455460043', '1Z89RA790457898925', '1Z89RA790457320511', '1Z89RA790457075706', '1Z89RA790455880545', '1Z89RA790456026930', '1Z89RA790455906688', '1Z89RA790455154357', '1Z89RA790456955301', '1Z89RA790457176115', '1Z89RA790455688067', '1Z89RA790457716362', '1Z89RA790457548240', '1Z89RA790455004161', '1Z89RA790455424145', '1Z89RA790455573207', '1Z89RA790457853606', '1Z89RA790456322413']


def get_activities(tracking_number: str) -> List[Optional[ActivityItem]]:
    package = api.get_package(tracking_number, TrackType.ByTrackingNumber)

    if package.Shipment.ShipTo.Address.CountryCode == "US":
        activities = package.Shipment.Package.get_US_activities
        filtered_activities = []
        for activity in activities:
            if activity.description == "Import Scan" or activity.description == "Location Scan":
                pass
            else:
                filtered_activities.append(activity.json())
        return filtered_activities   
    return []


activities = get_activities("1Z89RA790456552719")

print(activities)