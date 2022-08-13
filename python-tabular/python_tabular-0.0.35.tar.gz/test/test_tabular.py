from pytabular import pytabular
from pytabular import localsecret
import pytest
import pandas as pd
from Microsoft.AnalysisServices.Tabular import Database

aas = pytabular.Tabular(localsecret.CONNECTION_STR['FIN 500'])
gen2 = pytabular.Tabular(localsecret.CONNECTION_STR['GEN2TEST'])
testing_parameters = [(aas),(gen2)]
testingtable = 'PyTestTable'

@pytest.mark.parametrize("model",testing_parameters)
def test_connection(model):
	'''
	Does a quick check to the Tabular Class
	To ensure that it can connnect
	'''
	assert model.Server.Connected

@pytest.mark.parametrize("model",testing_parameters)
def test_database(model):
	assert isinstance(model.Database,Database)

@pytest.mark.parametrize("model",testing_parameters)
def test_query(model):
	df = model.Query('EVALUATE {1}')
	assert df.iloc[0]['[Value]'] == 1


def remove_testing_table(model):
	table_check = [table for table in model.Model.Tables.GetEnumerator() if testingtable in table.Name]
	for table in table_check:
		model.Model.Tables.Remove(table)
	model.SaveChanges()

@pytest.mark.parametrize("model",testing_parameters)
def test_pre_table_checks(model):
	remove_testing_table(model)
	assert len([table for table in model.Model.Tables.GetEnumerator()  if testingtable in table.Name]) == 0

@pytest.mark.parametrize("model",testing_parameters)
def test_create_table(model):
	df = pd.DataFrame(data={'col1':[1,2,3],'col2':['four','five','six']})
	assert model.Create_Table(df,testingtable)

@pytest.mark.parametrize("model",testing_parameters)
def test_backingup_table(model):
	model.Backup_Table(testingtable)
	assert len([table for table in model.Model.Tables.GetEnumerator()  if f'{testingtable}_backup' == table.Name]) == 1

@pytest.mark.parametrize("model",testing_parameters)
def test_revert_table(model):
	model.Revert_Table(testingtable)
	assert len([table for table in model.Model.Tables.GetEnumerator()  if f'{testingtable}' == table.Name]) == 1


@pytest.mark.parametrize("model",testing_parameters)
def test_table_removal(model):
	remove_testing_table(model)
	assert len([table for table in model.Model.Tables.GetEnumerator()  if testingtable in table.Name]) == 0

@pytest.mark.parametrize("model",testing_parameters)
def test_bpa(model):
	te2 = pytabular.TE2().EXE_Path
	bpa = pytabular.BPA().Location
	assert model.Analyze_BPA(te2,bpa) 
