skus = """
query skus($search: SearchFilter!, $limit: Int!, $offset: Int!, $isPointBound: Boolean, $isApproved: Boolean) {
	skus(search: $search, limit: $limit, offset: $offset, isPointBound: $isPointBound, isApproved: $isApproved) {
		total
		skus {
			code
		}
	}
}"""

products = """
query products(
		$search: SearchFilter!
		$limit: Int!
		$offset: Int!
		$cartonID: ID
		$orderID: ID
		$skuID: ID
		$contractID: ID
	) {
		products(
			search: $search
			limit: $limit
			offset: $offset
			isPointBound: false
			skuID: $skuID
			orderID: $orderID
			cartonID: $cartonID
			contractID: $contractID
		) {
			products {
				code
			}
			total
		}
	}
"""