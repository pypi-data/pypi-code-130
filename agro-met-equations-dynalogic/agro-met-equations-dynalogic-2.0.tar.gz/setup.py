# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['AgroMetEquations']

package_data = \
{'': ['*'], 'AgroMetEquations': ['docs/*']}

setup_kwargs = {
    'name': 'agro-met-equations-dynalogic',
    'version': '2.0',
    'description': 'Library for agrometeorological calculation like evapotranspiration, water balance, degree days, water balance ...',
    'long_description': 'Agrometeorological Equations Package\n==========\n##### Library for agrometeorological calculation like evapotranspiration, water balance, degree days, etc\n\n|           |                                                    |\n|-----------|----------------------------------------------------|\n|Authors:   | Bruno Ducraux (bducraux@dynalogic.net)             |\n|           | Mariana Gonçalves dos Reis (mreis@dynalogic.net)   |\n| Based on: | [PyEto](https://github.com/woodcrafty/PyETo)       |\n|           |                                                    |\n\nAbout\n-----------\nThis library was adapted to fit some needs of a private project, \nand I decided to disponibilize as open source since the original project \nthat we used as base is.\n\nAll calculations and formulas were reviewed by the agrometeorologist Mariana Gonçalves dos Reis, based on the documents:\n\n[Conversion factors and general equations applied in agricultural and forest meteorology](https://seer.sct.embrapa.br/index.php/agrometeoros/article/view/26527)\n\n[Evapotranspiration_Equation.pdf](AgroMetEquations/docs/Evapotranspiration_Equation.pdf)\n\nIn case of questions related to the python code, bug fix ...\nplease contact Bruno Ducraux, who is the python developer responsible for the project.\n\nInstallation\n------------\n`pip install agro-met-equations-dynalogic`\n\nUsage\n-----\n\n`from AgroMetEquations import`\n\n# Steps to calculate FAO56\n\n1. Day of year: days_passed_on_current_year()\n2. Solar declination: sol_dec(day_of_year)\n3. Sunset hour angle: sunset_hour_angle(latitude_rad, solar_declination)\n4. Daylight hours: daylight_hours(sunset_hour_angle)\n5. Inverse relative distance between earth and sun: inv_rel_dist_earth_sun(day_of_year)\n6. Extraterrestrial radiation: et_rad(latitude_rad, solar_declination, sunset_hour_angle, inv_rel_dist_earth_sun)\n7. Clear sky radiation: cs_rad(altitude, extraterrestrial_radiation)\n8. Saturation vapour pressure Min: svp_from_t(temperature_min)\n9. Saturation vapour pressure Max: svp_from_t(temperature_max)\n10. Saturation vapour pressure: svp(svp_min, svp_max)\n11. Actual vapour pressure: avp_from_rhmin_rhmax(svp_min, svp_max, relative_humidity_min, relative_humidity_max)\n12. Net outgoing longwave radiation: net_out_lw_rad(temperature_min:kelvin, temperature_max:kelvin, solar_radiation, clear_sky_radiation, actual_vapour_pressure)\n13. Net income solar radiation: net_in_sol_rad(solar_radiation)\n14. Net radiation at the crop surface: net_rad(net_in_sol_rad, net_outgoing_longwave_radiation)\n15. Soil heat flux: soil_heat_flux_by_nightday_period(net_rad)\n16. Latent heat: latent_heat(temperature_mean)\n17. Delta: delta_svp(temperature_mean)\n18. Psychrometric constant: psy_const(atmosphere_pressure, latent_heat)\n19. Wind speed measured at different heights: wind_speed_2m(wind_speed, sensor_height)\n20. FAO56: fao56_penman_monteith(net_rad, temperature_mean, wind_speed, latent_heat, svp, actual_vapour_pressure, delta, psychrometric_constant, soil_heat_flux)\n\n\nTesting\n-------\nTo test the code you need to have pytest installed.\n\n`pip install pytest`\n\nInside the AgroMetEquations folder run the command:\n\n`pytest`\n',
    'author': 'Bruno Ducraux',
    'author_email': 'bducraux@dynalogic.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dynalogic-agtech/dynalogic-agro-met-equations-pkg',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
