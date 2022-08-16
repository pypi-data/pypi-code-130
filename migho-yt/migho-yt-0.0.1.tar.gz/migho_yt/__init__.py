from pytube import YouTube
import os


def info(url):
	s = YouTube(url=url)
	ff = {'title': s.title,'description': s.description, 'views': s.views, 'video photo': s.thumbnail_url,'rate': s.rating, 'channel id': s.channel_id, 'date': s.publish_date, 'video_long': s.length, 'video id': s.video_id}
	return ff
#get_info(url='https://youtube.com/shorts/014Y_t5fPp4?feature=share')

def mp4(url,storage):
	if storage==None:
		path = './migho_down'
		try:
			print('im starting ✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n___________________________')
			s = YouTube(url)
			s.streams.filter(progressive=True,file_extension='mp4')
			s.streams.get_highest_resolution().download()
			
			print('done✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n')
		except:
			print('im starting ✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n')
			s = YouTube(url)
			s.streams.filter(progressive=True,file_extension='mp4')
			s.streams.get_highest_resolution().download(path)
			print('done✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n')
				
	else:
		try:
			print('im starting ✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n___________________________')
			s = YouTube(url)
			s.streams.filter(progressive=True,file_extension='mp4')
			s.streams.get_highest_resolution().download(storage)
			os.system('clear')
			print('done✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n')
		except:
			print('The storage not found')

def mp3(url, path):
	print('im starting ✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n___________________________')
	if path==None:
		s = YouTube(url)
		s.streams.filter(only_audio=True).first().download()
		name = str(s.title)
		if '#' in name:
			new = name.replace('#','')
			os.rename(f'{str(new)}.mp4',f'{new}.mp3')
			print('done')
			quit()
		else:
			os.rename(f'{str(s.title)}.mp4',new)
	else:
		try:
			s = YouTube(url)
			s.streams.filter(only_audio=True).first().download(path)
			name = str(s.title)
			if '#' in name:
				new = name.replace('#','')
				os.rename(f'{str(new)}.mp4',f'{new}.mp4')
				os.system('clear')
				print('done✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n')
				quit()
			else:
				
				os.rename(f'{str(s.title)}.mp4',new)
				os.system('clear')
				print('done✓ \n\n__________\n\n My Telegram : https://t.me/R3ZOO \n\n')
		except:
			print('done1')