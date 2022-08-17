import pandas as pd
import numpy as np
import pickle
import shap
import warnings
warnings.filterwarnings('ignore')

class Explain:
    def __init__(self,model):
        self.model=model

    def explain_model(self,X,modality='tabular',model_category=None,X_train=None,explanation_type='shap'):
        if explanation_type=='shap':
            if modality=='tabular':
                # model.fit(X,y)
                keys_list=[]
                values_list=[]
                for d in X:
                    keys_list.append(d['feature_name'])
                    values_list.append(d['feature_value'])
                
                if model_category in ['decision_tree','xgboost','gb','random_forest']:

                    explainer = shap.Explainer(self.model)
                    shap_values =explainer.shap_values(pd.DataFrame([values_list]),check_additivity = False)
                    
                else:
                    explainer = shap.KernelExplainer(self.model.predict, X_train)
                    shap_values = explainer.shap_values(pd.DataFrame([values_list]))
                shap_list=shap_values[0].tolist()
                if type(shap_list[0])==list:
                    shap_list=shap_values[0].tolist()[0]
                res=dict(zip(keys_list, shap_list))
                return res



