from . import input_types

def skuCreate(input: input_types.UpdateSku={}, request_fields = "id"):
	mutation = """
mutation skuCreate($input: UpdateSku!) {{
	skuCreate(input: $input) {{
		__typename
		{0}
	}}
}}""".format(request_fields)

	variables = {'input': input}

	return mutation, variables


def orderCreate(input: input_types.UpdateOrder={}, request_fields = "id"):

	mutation = """
mutation orderCreate($input: UpdateOrder!) {{
	orderCreate(input: $input) {{
		__typename
		{0}
	}}
}}""".format(request_fields)

	variables = {'input': input}

	return mutation, variables


def containerCreate(input: input_types.CreateContainer={}, request_fields = "id"):
	
	mutation = """
mutation containerCreate($input: CreateContainer!) {{
	containerCreate(input: $input) {{
		__typename
		{0}
	}}
}}""".format(request_fields)

	variables = {'input': input}

	return mutation, variables


def palletCreate(input: input_types.CreatePallet={}, request_fields = "id"):
	
	mutation = """
mutation palletCreate($input: CreatePallet!) {{
	palletCreate(input: $input) {{
		__typename
		{0}
	}}
}}""".format(request_fields)

	variables = {'input': input}

	return mutation, variables


def cartonCreate(input: input_types.CreateCarton={}, request_fields = "id"):
	
	mutation = """
mutation cartonCreate($input: CreateCarton!) {{
	cartonCreate(input: $input) {{
		__typename
		{0}
	}}
}}""".format(request_fields)

	variables = {'input': input}

	return mutation, variables


def productCreate(input: input_types.UpdateProduct={}, request_fields = "id"):
	mutation = """
mutation productCreate($input: UpdateProduct!) {{
	productCreate(input: $input) {{
		__typename
		{0}
	}}
}}""".format(request_fields)
	variables = {'input': input}

	return mutation, variables