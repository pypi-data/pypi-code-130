class Jay:
	"""
	คลาส Jay คือ
	ข้อมูลที่เกี่ยวข้องกับ เจย์
	ประกอบด้วยชื่อเพจ
	ชื่อช่องยูทูป
	
	Example
	# -------------------
	jay = Jay()
	jay.show_name()
	jay.show_youtube()
	jay.show_page()
	jay.about()
	jay.show_art()
	# -------------------
	"""
	def __init__(self):
		self.name = 'เจย์'
		self.page = 'https://www.facebook.com'

	def show_name(self):
		print('สวัสดีฉันชื่อ {}'.format(self.name))

	def show_youtube(self):
		print('Youtube: https://youtube.com')

	def show_page(self):
		print('FB Page: {}'.format(self.page))

	def about(self):
		text = """
		--------------------------------------------
		สวัสดีจ้า นี่คือเจย์เอง เป็นนักเรียนเพจ 'ลุงวิศวกร สอนคำนวณ'
		สามารถติดตามฉันได้เลย ท่านจะได้เห็นผลงานเกี่ยวกับ
		เกมที่ถูกเขียนขึ้นด้วยโปรแกรม Python
		--------------------------------------------"""
		print(text)

	def show_art(self):
		text = """
		      _=====_                               _=====_
		     / _____ \\                             / _____ \\
		   +.-'_____'-.---------------------------.-'_____'-.+
		  /   |     |  '.        S O N Y        .'  |  _  |   \\
		 / ___| /|\\ |___ \\                     / ___| /_\\ |___ \\
		/ |      |      | ;  __           _   ; | _         _ | ;
		| | <---   ---> | | |__|         |_:> | ||_|       (_)| |
		| |___   |   ___| ;SELECT       START ; |___       ___| ;
		|\\    | \\|/ |    /  _     ___      _   \\    | (X) |    /|
		| \\   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
		|  '-.______.-' /       \\ANALOG/       \\  '-._____.-'   |
		|               |       |------|       |                |
		|              /\\       /      \\       /\\               |
		|             /  '.___.'        '.___.'  \\              |
		|            /                            \\             |
		 \\          /                              \\           /
		  \\________/                                \\_________/
                    		PS2 CONTROLLER
		"""
		print(text)


if __name__ == '__main__':
	jay = Jay()
	jay.show_name()
	jay.show_youtube()
	jay.show_page()
	jay.about()
	jay.show_art()