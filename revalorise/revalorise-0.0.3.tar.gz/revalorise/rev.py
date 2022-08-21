class RevaloriseJr:
	"""
    Class revalorise is
    a data that associated with Revalorise
    Including Webpages, Youtube, and Social
    Accounts

    Example :
    % -----------------------
    rev = revalorise()
	rev.show_name()
	rev.show_youtube()
	rev.show_github()
	rev.about_me()
	rev.show_art()
	% -----------------------
	"""

	def __init__(self):
		self.name = 'revalorise'
		self.page = 'https://www.facebook.com'

	def show_name(self):
		print(f'Hello, my name is {self.name}')

	def show_youtube(self):
		print('https://www.youtube.com')

	def show_github(self):
		print('https://github.com/Revalorise')

	def about_me(self):
		text = """
		-------------------------------------------------------
        Hello! it's me Rev, I am the developer of this package.
        I'm currently studying Python with various online source.
        -------------------------------------------------------
		"""
		print(text)

	def show_art(self):
		text = """
		     ___________________
			 | _______________ |
			 | |XXXXXXXXXXXXX| |
			 | |Rev inbound! | |
			 | |..../>       | |
			 | |Probably not.| |
			 | |XXXXXXXXXXXXX| |
			 |_________________|
			     _[_______]_
			 ___[___________]___
			|         [_____] []|__
			|         [_____] []|  \\__
			L___________________J     \\ \\___\\/
			 ___________________      /\
			/###################\\    (__)
		"""
		print(text)


if __name__ == '__main__':
	rev = RevaloriseJr()
	rev.show_name()
	rev.show_youtube()
	rev.show_github()
	rev.about_me()
	rev.show_art()