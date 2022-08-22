"""This builder simply provides typing for IDE prompting and default input values for a few common queries"""

from enum import Enum

class FilterOption(Enum):
	All = "All"
	Active = "Active"
	Archived = "Archived"
	ProductWithoutOrder = "ProductWithoutOrder"
	ProductWithoutCarton = "ProductWithoutCarton"
	ProductWithoutSKU = "ProductWithoutSKU"
	CartonWithoutPallet = "CartonWithoutPallet"
	PalletWithoutContainer = "PalletWithoutContainer"
	System = "System"
	Blockchain = "Blockchain"
	Pending = "Pending"

class SortByOption(Enum):
	DateCreated = "DateCreated"
	DateUpdated = "DateUpdated"
	Alphabetical = "Alphabetical"

class SortDir(Enum):
	Ascending = "Ascending"
	Descending = "Descending"

class Search:
	search: str | None
	filter: FilterOption | None
	sortBy: SortByOption | None
	sortDir: SortDir | None

	def __init__(
		self,
		search: str = None,
		filter: FilterOption = None,
		sortBy: SortByOption = None,
		sortDir: SortDir = None
	):
		self.search  = search
		self.filter  = filter
		self.sortBy  = sortBy
		self.sortDir = sortDir

def skus(request_fields = "total, skus { id }", search: Search={}, limit: int=100, offset: int=0, isPointBound: bool=None, isApproved: bool=None):
	query = """
query skus($search: SearchFilter!, $limit: Int!, $offset: Int!, $isPointBound: Boolean, $isApproved: Boolean) {{
	skus(search: $search, limit: $limit, offset: $offset, isPointBound: $isPointBound, isApproved: $isApproved) {{
		__typename
		{0}
	}}
}}""".format(request_fields)

	variables = {
		'search': search,
		'limit': limit,
		'offset': offset,
		'isPointBound': isPointBound,
		'isApproved': isApproved,
	}

	return query, variables

def products(request_fields = "total, products { id }", search: Search={}, limit: int=100, offset: int=0, cartonID: int=None, orderID: int=None, skuID: int=None, contractID: int=None):
	query = """
query products(
		$search: SearchFilter!
		$limit: Int!
		$offset: Int!
		$cartonID: ID
		$orderID: ID
		$skuID: ID
		$contractID: ID
	) {{
		products(
			search: $search
			limit: $limit
			offset: $offset
			isPointBound: false
			skuID: $skuID
			orderID: $orderID
			cartonID: $cartonID
			contractID: $contractID
		) {{
			__typename
			{0}
		}}
	}}
""".format(request_fields)

	variables = {
		'search': search,
		'limit': limit,
		'offset': offset,
		'cartonID': cartonID,
		'orderID': orderID,
		'skuID': skuID,
		'contractID': contractID,
	}

	return query, variables