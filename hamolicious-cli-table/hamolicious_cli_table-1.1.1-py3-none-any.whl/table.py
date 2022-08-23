from types import FunctionType
from typing import Any
from .aligners import align_data_center
import colorama


class Table:
	def __init__(self, data: list[list[Any]], **kwargs) -> None:
		self.update_data(data)

		self.__margin = ' ' * kwargs.get('margin', 1)
		self.__alignment = kwargs.get('alignment', align_data_center)
		self.__verify_aligner(self.__alignment)
		self.__header_alignment = kwargs.get('header_alignment', align_data_center)
		self.__has_header = kwargs.get('header', False)
		self.__should_add_top = kwargs.get('add_top', False)
		self.__should_add_bottom = kwargs.get('add_bottom', False)

		self.__use_color = kwargs.get('use_color', False)
		self.__header_color_bg = kwargs.get('header_color_bg', colorama.Back.RESET)
		self.__header_color_fg = kwargs.get('header_color_fg', colorama.Fore.LIGHTBLUE_EX)
		self.__odd_row_color_bg = kwargs.get('odd_color_bg', colorama.Back.RESET)
		self.__odd_row_color_fg = kwargs.get('odd_color_fg', colorama.Fore.BLUE)
		self.__even_row_color_bg = kwargs.get('even_color_bg', colorama.Back.RESET)
		self.__even_row_color_fg = kwargs.get('even_color_fg', colorama.Fore.CYAN)

		self.__string = ''
		self.__frozen = False
		self.__lookup = self.__generate_lookup(self.__data)
		self.__has_header_aligner_used = False

	# Internal

	def __color_row(self, data: str, fg: str, bg: str) -> str:
		"""Colors a single row

		Args:
				data (str): a single row as a string
				fg (str): colorama.Fore color
				bg (str): colorama.Back color

		Returns:
				str: colored row
		"""
		if not self.__use_color:
			return data

		return \
			f'{bg}{fg}{data}{colorama.Fore.RESET}{colorama.Back.RESET}'

	def __color_header_row(self, data: str) -> str:
		"""Colors the first row (if header exists)

		Args:
				data (str): a single row as a string

		Returns:
				str: colored row
		"""
		if not self.__use_color:
			return data

		return self.__color_row(data, self.__header_color_fg, self.__header_color_bg)

	def __color_alternating_row(self, data: str, row_index: int) -> str:
		"""Colors odd and even rows with their assigned colors

		Args:
				data (str): a single row of data as a str
				row_index (int): index of the current row within the table

		Returns:
				str: a colored row
		"""
		if not self.__use_color:
			return data

		if row_index % 2 == 0:
			return self.__color_row(data, self.__even_row_color_fg, self.__even_row_color_bg)
		else:
			return self.__color_row(data, self.__odd_row_color_fg, self.__odd_row_color_bg)

	def __color_all_rows(self, data: list[str]) -> list[str]:
		"""Colors the entire table

		Args:
				data (list[str]): rows of the table as strings

		Returns:
				list[str]: colored rows
		"""
		if not self.__use_color:
			return data

		data = data.copy()
		new_data = []

		if self.__has_header:
			new_data.append(
				self.__color_header_row(data.pop(0))
			)

		for row_index, row in enumerate(data):
			new_data.append(
				self.__color_alternating_row(row, row_index)
			)

		return new_data

	def __stringify(self, data: list[list[Any]]) -> list[list[str]]:
		"""Casts every element in the table to string

		Args:
				data (list[list[Any]]): 2d list representing the table

		Returns:
				list[list[str]]: 2d list where every element is a string
		"""
		str_data = []

		for row in data:
			str_data.append(
				list(map(str, row))
			)

		return str_data

	def __get_longest_values(self, data: list[list[str]]) -> list[int]:
		"""Calculates the longest piece of data for each row

		Args:
				data (list[list[str]]): 2d array representing the table

		Returns:
				list[int]: a list of max lengths for each column
		"""
		longest_values = [0 for _ in range(self.__width)]

		for col in range(self.__height):
			for index, cell in enumerate(data[col]):
				current_value = longest_values[index]
				longest_values[index] = max(current_value, len(cell))

		return longest_values

	def __generate_lookup(self, data: list[list[Any]]) -> dict|None:
		"""Generates a lookup table where a heading name corresponds to a column index

		Args:
				data (list[list[Any]]): 2d array representing the table

		Returns:
				dict|None: lookup dict where every key is a table heading, none if no heading exists
		"""
		if self.__has_header is False: return None
		lookup = {}

		for index, heading in enumerate(data[0]):
			lookup[heading] = index

		return lookup

	def __add_top(self, rows: list[str], width: int) -> list[str]:
		"""Adds a top border line to the table

		Args:
			rows (list[str]): list of all rows as strings
			width (int): the width of the table

		Returns:
			list[str]: list of all rows as strings, with a top border
		"""
		if not self.__should_add_top:
			return rows

		top_row = '_' * width

		if self.__has_header:
			return [self.__color_header_row(top_row)] + rows

		return [self.__color_alternating_row(top_row, 0)] + rows

	def __add_bottom(self, rows: list[str], width: int) -> list[str]:
		"""Adds a bottom border line to the table

		Args:
			rows (list[str]): list of all rows as strings
			width (int): the width of the table

		Returns:
			list[str]: list of all rows as strings, with a bottom border
			"""
		if not self.__should_add_bottom:
				return rows

		bottom = '-' * width
		return rows + [self.__color_alternating_row(bottom, len(rows))]

	def __verify_aligner(self, alignment: list[FunctionType]|FunctionType) -> bool:
		"""Verifies the passed in alignment

		Args:
			alignment (list[FunctionType] | FunctionType): alignment list of functions or function

		Raises:
			TypeError: If the list length is not the same as the width of the table
			TypeError: If the list does not contain functions
			TypeError: if the argument is not a function

		Returns:
			bool: True if all is well
		"""
		if type(alignment) is list:
			if len(alignment) != self.__width:
				raise TypeError('alignment of type list must be of length "len(row)"')

			for elem in alignment:
				if type(elem) is not FunctionType:
					raise TypeError('alignment of type list must only contain FunctionType\'s')
		else:
			if not (type(alignment) is FunctionType):
				raise TypeError('alignment not of type list must be a FunctionType')

		return True

	def __get_aligner(self, column_index: int) -> FunctionType:
		"""Gets the current alignment function

		Args:
			column_index (int): index into the row

		Returns:
			FunctionType: alignment function
		"""
		if self.__has_header and not self.__has_header_aligner_used:
			self.__has_header_aligner_used = True
			return self.__header_alignment

		if type(self.__alignment) is list:
			return self.__alignment[column_index]

		return self.__alignment

	# Public

	def is_frozen(self) -> bool:
		"""Checks if the table needs to be frozen before printing

		Returns:
				bool: is the table frozen
		"""
		return self.__frozen

	def sort_by(self, column: str|int, key=None, reverse=False) -> None:
		"""Sorts the table by the values of a column

		Args:
				column (str | int): name of row (str) or index of row (int)
				key (Callable, optional): sorting key. Defaults to a simple value sort.
				reverse (bool, optional): reverses the sorting algorithm. Defaults to False.

		Raises:
				TypeError: If column of type str is passed in when no header exists
				ValueError: When a column of type str is passed in when no such header name exists
		"""
		if not self.__has_header and type(column) is str:
			raise TypeError('Lookup of type "str" is not supported for headerless tables')

		self.__frozen = False

		index = None
		if type(column) is int : index = column
		if type(column) is str : index = self.__lookup.get(column)

		if index is None : raise ValueError(f'Heading "{column}" does not exist')

		if key is None:
			key = lambda row : row[index]

		header = []
		if self.__has_header:
			header = self.__data.pop(0)

		self.__data.sort(key=key, reverse=reverse)

		if self.__has_header:
			self.__data = [header] + self.__data

	def update_data(self, new_data: list[list[Any]]) -> None:
		"""Changes the data that the table has

		Args:
				new_data (list[list[Any]]): 2d array representing the table
		"""
		self.__data = new_data
		self.__width = len(self.__data[0])
		self.__height = len(self.__data)
		self.__string = ''
		self.__frozen = False
		self.__has_header_aligner_used = False

	def freeze(self) -> None:
		"""Compiles the given data into a string for quick displaying
		"""
		if self.__height == 0 : return
		data = self.__stringify(self.__data)

		rows = []
		longest_values = self.__get_longest_values(data)

		for row in data:
			temp = []
			for cell_index, cell in enumerate(row):
				aligned_cell = self.__get_aligner(cell_index)(cell, longest_values[cell_index])
				temp.append(
					f'{self.__margin}{aligned_cell}{self.__margin}'
				)
			rows.append(f'|{"|".join(temp)}|')
			alignment = self.__alignment

		colored_rows = self.__color_all_rows(rows)
		colored_rows = self.__add_top(colored_rows, len(rows[0]))
		colored_rows = self.__add_bottom(colored_rows, len(rows[0]))

		self.__string = '\n'.join(colored_rows)
		self.__frozen = True

	def display(self) -> None:
		"""Prints the table
		"""
		if not self.__frozen: return 'Freeze the data first'
		print(self.__string)

	def __repr__(self) -> str:
		"""Returns the table in string form

		Returns:
				str: the table in string form
		"""
		if not self.__frozen: return 'Freeze the data first'
		return self.__string

