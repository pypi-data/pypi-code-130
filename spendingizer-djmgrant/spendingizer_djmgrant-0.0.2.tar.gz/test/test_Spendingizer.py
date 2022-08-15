#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sunday 2 Jan 2022 
@author: Dave Grant
"""
import pytest
from src.spendingizer import LoadStatements , FormatStatements, GetMonths, AddExtraExpenses, SpendAnalysis
statement = "./test/testdata/statements"
emptystatement = "./test/testdata/emptystatements"
catagories = "./test/testdata/Catagories-extended.csv"
extras = "./test/testdata/extra-expenses.csv"

def test_LoadStatements():
    assert round(LoadStatements(statement).Amount.sum(),2) == -1208.10
                                                
def test_LoadStatements_nofiles():
    with pytest.raises(Exception) as excinfo:
        LoadStatements(emptystatement)
    assert str(excinfo.value) == 'no files to process'
    
def test_FormatStatement_other():
    spend = LoadStatements(statement)
    fmt = FormatStatements(spend,catagories)
    assert fmt[(fmt['Category'] == 'Other')].Amount.sum() == 23.97
   
def test_FormatStatement_total_tot():
    spend = LoadStatements(statement)
    fmt = FormatStatements(spend,catagories)
    assert round(fmt['Amount'].sum(),2) == 1208.10

def test_GetMonths_total():
    spend = LoadStatements(statement)
    fmt = FormatStatements(spend,catagories)
    assert len(GetMonths(fmt)) == 3
    
def test_AddExtraExpenses():
    spend = LoadStatements(statement)
    fmt = FormatStatements(spend,catagories)
    fmt = AddExtraExpenses(fmt,extras)
    assert fmt[(fmt['Month'] == '2021-11')].Amount.sum() == 80
    
def test_SpendlyAnalysis():
    spend = LoadStatements(statement)
    fmt = FormatStatements(spend,catagories)
    mts = GetMonths(fmt)
    assert round(SpendAnalysis(fmt,mts)['LQTR'],2) == 1208.10