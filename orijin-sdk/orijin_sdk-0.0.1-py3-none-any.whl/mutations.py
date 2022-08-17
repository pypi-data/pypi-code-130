skuCreate = """
mutation skuCreate($input: UpdateSku!) {
	skuCreate(input: $input) {
		code
		id
	}
}"""

orderCreate = """
mutation orderCreate($input: UpdateOrder!) {
	orderCreate(input: $input) {
		code
		id
	}
}"""

containerCreate = """
mutation containerCreate($input: CreateContainer!) {
	containerCreate(input: $input)
}"""

palletCreate = """
mutation palletCreate($input: CreatePallet!) {
	palletCreate(input: $input)
}"""

cartonCreate = """
mutation cartonCreate($input: CreateCarton!) {
	cartonCreate(input: $input)
}"""

productCreate = """
mutation productCreate($input: UpdateProduct!) {
	productCreate(input: $input) {
		code
		id
	}
}"""
