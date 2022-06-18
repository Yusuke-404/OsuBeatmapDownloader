import urllib3, re, argparse
from pathlib import Path
import login

def beatmap(beatmap_id, osu_session, no_video, save_location='Songs/'):
	vid = lambda x : '1' if no_video == False else '0'
	url = "https://osu.ppy.sh/beatmapsets/{id}/download?noVideo={video_req}".format(id=beatmap_id, video_req=vid(no_video))

	headers = {
		'cookie': 'osu_session={s}'.format(s=osu_session),
		'authority': 'osu.ppy.sh',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
		'referer': 'https://osu.ppy.sh/beatmaps/{id}'.format(id=beatmap_id),
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
	}

	http = urllib3.PoolManager()
	r = http.request('GET', url, headers=headers)

	if r.status == 200:
		filename = re.findall(r'"(.*?)"', r.headers['Content-Disposition'])[0]
	elif r.status == 404:
		print('{} | Beatmap not found, check beatmap id or url | https://osu.ppy.sh/beatmapsets/{id}'.format(r.status, id=beatmap_id))
		exit()
	else:
		print('{} | Your session expired!'.format(r.status))
		exit()

	temp_dir = Path("temp/")
	temp_dir.mkdir(exist_ok=True)
	file = Path(str(temp_dir)+'/'+filename)
	print(filename)
	if file.is_file():
		file.unlink()
	file.write_bytes(r.data)

def valid_beatmap_url(url):
	if re.match(r'http(s)://osu\.ppy\.sh/beatmapsets/[0-9]+', url):
		return True

def parse_beatmaplist(list):
	parsed_list = []
	for x in list:
		if valid_beatmap_url(x):
			beatmap_id = re.findall(r'[0-9]+', x)[0]
			parsed_list.append(beatmap_id)
	return parsed_list

def beatmapDownloader():
	s_file = Path('./session.txt')
	if s_file.is_file():
		if is_file.stat().st_size != 0:
			osu_session = s_file.read_text().rstrip('\n')
	else:
		# login.login()
		# osu_session = s_file.read_text().rstrip('\n')
		print('session.txt file not found!')
		exit()
		
	if args.id or args.file:
		if args.id:
			beatmap_id = args.id
			beatmap(beatmap_id)
		if args.file:
			data = args.file.readlines()
			beatmaplist = [x.rstrip() for x in data]
			beatmap_ids = parse_beatmaplist(beatmaplist)
			print(beatmap_ids)
			for beatmap_id in beatmap_ids:
				beatmap(beatmap_id, osu_session, args.video, args.output)
	else:
		print('Input beatmap id or beatmap list file!')


if __name__ == '__main__':
	formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=52)
	parser = argparse.ArgumentParser(formatter_class=formatter)

	parser.add_argument('-id', required=False, type=str, help='Song/Beatmap id')
	parser.add_argument('-u', '--url', required=False, type=str, help='Song/Beatmap url')
	parser.add_argument('-f', '--file', required=False, type=argparse.FileType('r', encoding='UTF-8'), help='Add file containing beatmap ids or urls. Check example.txt')
	parser.add_argument('-o', '--output', required=False, type=str, default='Songs/', help='Folder/Directory to download the beatmaps (default: Songs/)')
	parser.add_argument('-V', '--video', required=False, default=False, action='store_true', help="Download with Video")
	parser.add_argument('-e0', required=False, default=False, action=argparse.BooleanOptionalAction, help="For not extracting .osz file")

	args = parser.parse_args()

	beatmapDownloader()

