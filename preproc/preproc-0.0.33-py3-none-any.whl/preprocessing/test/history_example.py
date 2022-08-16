scaler_history_ex = list(
    [ 
      [ 
        {
            "name" : "MinMaxScaler",
            "columnName" : "tenure",
            "orgMax" : 178.0,
            "orgMin" : 1.0,
        }, 
        {
            "name" : "MinMaxScaler",
            "columnName" : "MonthlyCharges",
            "orgMax" : 118.75,
            "orgMin" : 23.45,
        }
      ],
      [
        {
            "name" : "StandardScaler",
            "columnName" : "tenure",
            "orgMean" : 33.02685050798258,
            "orgStdDev" : 24.826860637095507,
        }
      ],
      [
        {
            "name" : "RobustScaler",
            "columnName" : "TotalCharges",
            "q25" : 586.8375000000001,
            "q50" : 2139.1499999999996,
            "q75" : 4528.0
        }
      ],
      [
        {
            "name" : "LogScaler",
            "columnName" : "TotalCharges",
        }
      ],
      [
        {
            "name" : "ExpScaler",
            "columnName" : "MonthlyCharges",
        }
      ],
      [
        {
            "name" : "BoxCoxTransform",
            "columnName" : "SeniorCitizen",
        }
      ],
    ]
)

outlier_history_ex = list(
    [ # 히스토리 전처리 단
        [ # 컬럼 단
            { 
                'name': 'Carling',
                'columnName': 'tenure',
                'newColumn': ['tenure_carling'],
                'q25': 9.0, 
                'q50': 30.0, 
                'q75': 56.0, 
                'lower': -78.1, 
                'upper': 138.1, 
                'outlierN': 4
            }
        ],
        [
            {
                'name': 'Carling',
                'columnName': 'tenure', 
                'q25': 9.0, 
                'q50': 30.0, 
                'q75': 56.0, 
                'lower': -78.1, 
                'upper': 138.1, 
                'outlierN': 4
            },
            {
                'name': 'Carling',
                'columnName': 'MonthlyCharges', 
                'q25': 9.0, 
                'q50': 30.0, 
                'q75': 56.0, 
                'lower': -78.1, 
                'upper': 138.1, 
                'outlierN': 4
            }
        ],
        [
            {
                'name': 'Tukey',
                'columnName': 'tenure', 
                'newColumn': ['tenure_tukey'], 
                'q25': 9.0, 
                'q50': 30.0, 
                'q75': 56.0, 
                'lower': -61.5, 
                'upper': 126.5, 
                'outlierN': 5
            }
        ],
        [
            {
                'name': 'Tukey',
                'columnName': 'tenure', 
                'q25': 9.0, 
                'q50': 30.0, 
                'q75': 56.0, 
                'lower': -61.5, 
                'upper': 126.5, 
                'outlierN': 5
            }
        ],
        [
            {
                'name': 'ESD',
                'columnName': 'tenure', 
                'newColumn': ['tenure_ESD'], 
                'orgMean': 33.02685050798258, 
                'stddev': 24.826860637095507, 
                'cutoff': 74.48058191128652, 
                'lower': -41.45373140330394, 
                'upper': 107.5074324192691, 
                'outlierN': 5
            }
        ],
        [
            {
                'name': 'ESD',
                'columnName': 'tenure', 
                'orgMean': 33.02685050798258, 
                'stddev': 24.826860637095507, 
                'cutoff': 74.48058191128652, 
                'lower': -41.45373140330394, 
                'upper': 107.5074324192691, 
                'outlierN': 5
            }
        ],
    ]
)

categorical_history_ex = list(
    [ # 히스토리 전처리 단
        [ # 컬럼 단
            {
                'name': 'LabelEncoder',
                'columnName': 'Contract', 
                'num_label': [0, 1, 2], 
                'label': ['Month-to-month', 'One year', 'Two year'], 
                'newColumn': ['Contract_LabelEncoder']
            }
        ],
        [
            {
                'name': 'OneHotEncoder',
                'columnName': 'Contract', 
                'label': ['Month-to-month', 'One year', 'Two year'], 
                'newColumn': ['Contract_Month-to-month', 'Contract_One year', 'Contract_Two year']
            }
        ],
    ]
)

fillmissing_history_ex = list(
    [ # 히스토리 전처리 단
        [ # 컬럼 단
            {
                'name': 'FillMissing',
                'columnName': 'gender', 
                'fillVal': None, 
                'nanVals': None, 
                'descriptive': -1, 
                'treatedMissingN': 1, 
                'remainedMissingN': 0
            }
        ],
        [
            {
                'name': 'FillMissing', 
                'columnName': 'tenure', 
                'fillVal': 10, 
                'nanVals': None, 
                'descriptive': -1, 
                'treatedMissingN': 1, 
                'remainedMissingN': 0
            },
        ],
        [
            {
                'name': 'FillMissing',
                'columnName': 'tenure', 
                'fillVal': None, 
                'nanVals': None, 
                'descriptive': 2, 
                'treatedMissingN': 0, 
                'method': 'mode', 
                'remainedMissingN': 0
            }
        ],
    ]
)
