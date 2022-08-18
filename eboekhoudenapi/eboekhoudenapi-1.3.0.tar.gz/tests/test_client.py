import pytest
import os

from eboekhoudenapi import Client, Mutatie, MutatieRegel

USERNAME = os.environ["USERNAME"]
SECURITY_CODE_1 = os.environ["SECURITY_CODE_1"]
SECURITY_CODE_2 = os.environ["SECURITY_CODE_2"]


def get_client():
    return Client(
        username=USERNAME,
        security_code_1=SECURITY_CODE_1,
        security_code_2=SECURITY_CODE_2,
    )


def get_mutatie():
    amount_excl = 20
    amount_incl = 20 / 100 * 121
    vat = amount_excl / 100 * 21

    mutatie_regels = [
        MutatieRegel(
            bedrag_invoer=str(amount_incl),
            bedrag_excl_btw=str(amount_excl),
            bedrag_btw=str(vat),
            bedrag_incl_btw=str(amount_incl),
            btw_code="HOOG_VERK_21",
            btw_percentage="21",
            tegenrekening_code="8002",
        ),
        MutatieRegel(
            bedrag_invoer=str(amount_incl * 2),
            bedrag_excl_btw=str(amount_excl * 2),
            bedrag_btw=str(vat * 2),
            bedrag_incl_btw=str(amount_incl * 2),
            btw_code="HOOG_VERK_21",
            btw_percentage="21",
            tegenrekening_code="8003",
        ),
    ]

    return Mutatie(
        soort="FactuurVerstuurd",
        datum="2021-01-01",
        rekening="1300",
        relatie_code="036",
        factuurnummer="test-1231241246",
        omschrijving="Automatisch import via api",
        betalingstermijn="14",
        inexbtw="IN",
        mutatie_regels=mutatie_regels,
    )


def test_client():
    get_client()


def test_mutatie_export():
    mutatie = get_mutatie()

    result = mutatie.export()


def test_mutatie():
    mutatie = get_mutatie()
    client = get_client()

    res = client.add_mutatie(mutatie=mutatie)
    print(res)
