from .query_json_to_sql import AGJsonToSQL

#
# Multi level JSON
#
s = AGJsonToSQL("lc", "products_product")
s.select = ['code', 'name', "sales_price"]
s.where = []
s.where_string = "sales_price > 16000"
s.order_by = ['name']
s.up_relations = [
    {
        "schema_name": "lc",
        "table_name": "products_productgroup",
        "select": ["code", "name"],
        "relation": "product_group",
        "where": [
            {
                "name__icontains": 'ba'
            }
        ],
        "where_string": "",
        "up_relations": [
            {
                "schema_name": "lc",
                "table_name": "products_productdomain",
                "select": ["code", "name"],
                "relation": "product_domain",
                "where": [],
                "where_string": "",
                "down_relations": []
            }
        ],
        "down_relations": []
    }
]
s.down_relations = [
    {
        "schema_name": "lc",
        "table_name": "products_barcode",
        "select": ["name"],
        "relation": "product",
        "where": [],
        "where_string": "name LIKE '%e%'",
        "order_by": ['name'],
        "up_relations": [],
        "down_relations": []
    }
]
s.execute()
s.print_sql()

#
# Joins
#
s = AGJsonToSQL("lc", "products_product")
s.select = ['code', 'name', "sales_price", "prodgroup.name"]
s.left_join = [
    {
        "schema_name": "lc",
        "table_name": "products_productgroup",
        "alias": "prodgroup",
        "relation": "product_group"
    }
]
s.where = [
    {
        'sales_price__gt': 6000,
        'sales_price__lte': 10000,
        'prodgroup.name__icontains': 'e'
    },
    {
        'sales_price__gt': 14000,
        'sales_price__lte': 99000
    }
]
s.where_string = "sales_price > 6000"
s.order_by = ['sales_price desc', 'name']
s.execute()
s.print_sql()

#
# Joins - Recursive
#
s = AGJsonToSQL("lc", "products_product")
s.select = ['code', 'name', "sales_price", "prodgroup.name", "proddom.name"]
s.left_join = [
    {
        "schema_name": "lc",
        "table_name": "products_productgroup",
        "alias": "prodgroup",
        "relation": "product_group",
        "inner_join": [
            {
                "schema_name": "lc",
                "table_name": "products_productdomain",
                "alias": "proddom",
                "relation": "product_domain"
            }
        ]
    }
]
s.where = [
    {
        'sales_price__gt': 6000,
        'sales_price__lte': 10000,
        'prodgroup.name__icontains': 'e'
    },
    {
        'sales_price__gt': 14000,
        'sales_price__lte': 99000
    }
]
s.where_string = "proddom.name = 'Other'"
s.order_by = ['sales_price desc', 'name']
s.execute()
s.print_sql()

#
# Group By
#
s = AGJsonToSQL("lc", "products_product")
s.select = ["prodgroup.code", "prodgroup.name"]
s.total = [
    {
        "action": "sum",
        "column": "sales_price",
        "alias": "",
        "having": "> 10000",
        "order_by": "desc"
    },
    {
        "action": "avg",
        "column": "sales_price",
        "alias": "average",
        "having": "",
        "order_by": ""
    },
]
s.left_join = [
    {
        "schema_name": "lc",
        "table_name": "products_productgroup",
        "alias": "prodgroup",
        "relation": "product_group"
    }
]
s.where = [
    {
        "sales_price__gt": 4000,
        "sales_price__lte": 6000
    }
]
s.where_string = ""
s.order_by = ["prodgroup.name"]
s.execute()
s.print_sql()

#
# JSON
#
json_join = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ['code', 'name', "sales_price", "prodgroup.name", "proddom.name"],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "prodgroup",
            "relation": "product_group",
            "inner_join": [
                {
                    "schema_name": "lc",
                    "table_name": "products_productdomain",
                    "alias": "proddom",
                    "relation": "product_domain"
                }
            ]
        }
    ],
    "where": [
        {
            'sales_price__gt': 6000,
            'sales_price__lte': 10000,
            'prodgroup.name__icontains': 'e'
        },
        {
            'sales_price__gt': 14000,
            'sales_price__lte': 99000
        }
    ],
    "where_string": "proddom.name = 'Other'",
    "order_by": ['sales_price desc', 'name']
}

json_total = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ["prodgroup.code", "prodgroup.name"],
    "total": [
        {
            "action": "sum",
            "column": "sales_price",
            "alias": "",
            "having": "> 10000",
            "order_by": "desc"
        },
        {
            "action": "avg",
            "column": "sales_price",
            "alias": "average",
            "having": "",
            "order_by": ""
        },
    ],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "prodgroup",
            "relation": "product_group"
            # "on": "prpr.product_group = prodgroup.id"
        }
    ],
    "where": [
        {
            "sales_price__gt": 4000,
            "sales_price__lte": 6000
        }
    ]
}

json_in_select = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ["prodgroup.code", "prodgroup.name"],
    "total": [
        {
            "action": "sum",
            "column": "sales_price",
            "alias": "",
            "having": "> 10000",
            "order_by": "desc"
        },
        {
            "action": "avg",
            "column": "sales_price",
            "alias": "average",
            "having": "",
            "order_by": ""
        },
    ],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "prodgroup",
            "relation": "product_group"
        }
    ],
    "where": [
        {
            "product_group__in_select": {
                "schema_name": "lc",
                "table_name": "products_productgroup",
                "id_name": "id",
                "where": [
                    {
                        "name__startswith": "A"
                    }
                ],
                "where_string": ""
            }
        }
    ]
}

json_image = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ["code", "name", "image"],
    "host": {
        "url": "localhost:8000",
        "select": [
            "image"
        ]
    }
}

json_multi_level = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ['code', 'name', "sales_price"],
    "where_string": "sales_price > 16000",
    "order_by": ['name'],
    "up_relations": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "select": ["code", "name"],
            "relation": "product_group",
            "where": [
                {
                    "name__icontains": 'ba'
                }
            ],
            "where_string": "",
            "up_relations": [
                {
                    "schema_name": "lc",
                    "table_name": "products_productdomain",
                    "select": ["code", "name"],
                    "relation": "product_domain",
                    "where": [],
                    "where_string": "",
                    "down_relations": []
                }
            ],
            "down_relations": []
        }
    ],
    "down_relations": [
        {
            "schema_name": "lc",
            "table_name": "products_barcode",
            "select": ["name"],
            "relation": "product",
            "where": [],
            "where_string": "name LIKE '%e%'",
            "order_by": ['name'],
            "up_relations": [],
            "down_relations": []
        }
    ]
}

json_down_relations_total = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ["code", "name", "pg.name"],
    "down_relations": [
        {
            "schema_name": "lc",
            "table_name": "customers_customerproduct",
            "select": [
                "cust.code", "cust.name"
            ],
            "total": [
                {
                    "action": "count",
                    "column": "id"
                }
            ],
            "relation": "product",
            "inner_join": [
                {
                    "schema_name": "lc",
                    "table_name": "customers_customer",
                    "alias": "cust",
                    "relation": "customer"
                }
            ],
        }
    ],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "pg",
            "relation": "product_group"
        }
    ]
}

json_down_relation_group_by = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ["code", "name", "pg.name"],
    "down_relations": [
        {
            "schema_name": "lc",
            "table_name": "customers_customerproduct",
            "select": [
                "cust.code", "cust.name"
            ],
            "total": [
                {
                    "action": "count",
                    "column": "id"
                }
            ],
            "relation": "product",
            "inner_join": [
                {
                    "schema_name": "lc",
                    "table_name": "customers_customer",
                    "alias": "cust",
                    "relation": "customer"
                }
            ],
        }
    ],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "pg",
            "relation": "product_group"
        }
    ]
}

json_where = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ['code', 'name', "sales_price", "prodgroup.name"],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "prodgroup",
            "relation": "product_group"
        }
    ],
    "where": [
        {
            'sales_price__gt': 6000,
            'sales_price__lte': 10000,
            'prodgroup.name__icontains': 'e'
        },
        {
            'sales_price__gt': 14000,
            'sales_price__lte': 99000
        }
    ],
    "where_string": "sales_price > 6000",
    "order_by": ["sales_price desc", "name"]
}

json_function = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ['code', 'name', "sales_price", "prodgroup.name"],
    "column_function": [
        {
            "alias": "VAT",
            "formula": "sales_price * 0.25",
            "order_by": "DESC"
        }
    ],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "prodgroup",
            "relation": "product_group"
        }
    ],
    "where": [
        {
            'sales_price__gt': 14000,
            'sales_price__lte': 99000
        }
    ],
    "order_by": ["sales_price desc", "name"]
}

json_function_total = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ['code', 'name', "sales_price", "prodgroup.name"],
    "column_function": [
        {
            "alias": "VAT",
            "formula": "sales_price * 0.25",
            "order_by": "DESC"
        },
        {
            "alias": "cost_price",
            "formula": "sales_price * 0.55"
        }
    ],
    "total": [
        {
            "action": "AVG",
            "column": "sales_price",
            "order_by": "DESC"
        }
    ],
    "left_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "prodgroup",
            "relation": "product_group"
        }
    ],
    "where": [
        {
            'sales_price__gt': 14000,
            'sales_price__lte': 99000
        }
    ],
    "order_by": ["name"]
}

json_window = {
    "schema_name": "lc",
    "table_name": "products_product",
    "select": ['code', 'name', "pg.name", "sales_price"],
    "column_function": [
        {
            "formula": "sales_price * 2",
            "alias": "double_up"
        }
    ],
    "window": [
        {
            "action": "AVG",
            "column": "sales_price",
            "alias": "average_product_group",
            "partition_by": ["pg.name"],
            "order_by": ["code"]
        },
        {
            "action": "rank",
            "column": "",
            "alias": "rank",
            "partition_by": ["pg.name"],
            "order_by": ["code"]
        }
    ],
    "inner_join": [
        {
            "schema_name": "lc",
            "table_name": "products_productgroup",
            "alias": "pg",
            "relation": "product_group"
        }
    ],
    "where_string": "sales_price BETWEEN 1000 AND 1050",
    "order_by": ['pg.name']
}
