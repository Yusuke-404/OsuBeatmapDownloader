import requests, re, argparse, tqdm
from zipfile import ZipFile
from pathlib import Path
from bs4 import BeautifulSoup
from _version import __version__
#import login

def extract_beatmap(save_loc):
	zf_dir = Path('temp/')
	save_dir = Path(save_loc)
	save_dir.mkdir(exist_ok=True)
	b_list = list(zf_dir.iterdir())

	for i in urls_302:
		for osz_f in b_list:
			if i in osz_f.name and osz_f.suffix == '.osz':
				with ZipFile(osz_f, 'r') as zip_f:
					zip_f.extractall(str(save_dir)+'/'+osz_f.name[:-4])

def parse(page):
	soup = BeautifulSoup(page, "html.parser")
	url = requests.utils.unquote(soup.find('a')['href'])
	beatmap_name = re.findall(r' (.*?)&', url)[0]
	return url, beatmap_name

def beatmap(beatmap_id, osu_session, nv, save_loc):
	vid = lambda x : '1' if nv == False else '0'
	url = "https://osu.ppy.sh/beatmapsets/{id}/download?noVideo={video_req}".format(id=beatmap_id, video_req=vid(nv))
	headers = {
		'cookie': 'osu_session={s}'.format(s=osu_session),
		'authority': 'osu.ppy.sh',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
		'referer': 'https://osu.ppy.sh/beatmaps/{id}'.format(id=beatmap_id),
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
	}

	with requests.Session() as s:
		resp1 = s.get(url, headers=headers, allow_redirects=False)

		if resp1.status_code == 302:
			download_url, beatmap_name = parse(resp1.text)
			filename = Path('temp/{bi} {bn}'.format(bi=beatmap_id, bn=beatmap_name))
			if filename.is_file():
				print('{bn} is already Downloaded!'.format(bn=beatmap_name))
				urls_302.append(filename.name)
				return 0
			resp2 = s.get(download_url, headers=headers, stream=True)
			if resp2.status_code == 200:
				try:
					totalSize = int(resp2.headers['Content-Length'])
					with open(filename, 'wb') as f:
						with tqdm.tqdm(total=totalSize, unit='B', unit_scale=True, desc='{}'.format(beatmap_name[:-4]), initial=0, ascii=False) as pbar:
							for data in resp2.iter_content(chunk_size=1024):
								if data:
									f.write(data)
									pbar.update(len(data))
					urls_302.append(filename.name)
				except:
					pass
			else:
				urls_500.append(beatmap_id)
		elif resp1.status_code == 404:
			urls_404.append(beatmap_id)
		else:
			print('{} | Your session expired!'.format(resp1.status_code))
			exit()

def valid_beatmap_url(url):
	if re.match(r'http(s)://osu\.ppy\.sh/beatmapsets/[0-9]+(.*)', url):
		return True
	else:
		return False

def parse_beatmaplist(list):
	parsed_list = []
	for x in list:
		if valid_beatmap_url(x):
			beatmap_id = re.findall(r'[0-9]+', x)[0]
			parsed_list.append(beatmap_id)
		else:
			not_valid_urls.append(x)
	return parsed_list

def beatmapDownloader():
	# Checking session.txt
	s_file = Path('session.txt')
	if s_file.is_file():
		if s_file.stat().st_size != 0:
			osu_session = s_file.read_text().rstrip('\n')
		else:
			printf('session.txt file is empty. Add a session')
	else:
		# login.login()
		# osu_session = s_file.read_text().rstrip('\n')
		print('session.txt file not found!')
		exit()

	temp_dir = Path('temp/')
	temp_dir.mkdir(exist_ok=True)
		
	if args.id or args.url or args.file :
		# if input is beatmap id
		if args.id:
			beatmap_id = args.id
			if re.match(r'[0-9]+', beatmap_id):
				print('Downloading...')
				beatmap(beatmap_id, osu_session, args.video, args.output)
			else:
				print('{} | Not a valid beatmap id'.format(beatmap_id))

		# if input is beatmap url
		if args.url:
			if valid_beatmap_url(args.url):
				beatmap_id = re.findall(r'[0-9]+', args.url)[0]
				print('Downloading...')
				beatmap(beatmap_id, osu_session, args.video, args.output)
			else:
				print('{} | Not a valid beatmap url'.format(args.url))

		# if input is a file containing list of beatmap urls
		if args.file:
			data = args.file.readlines()
			beatmaplist = [x.rstrip() for x in data]
			beatmap_ids = parse_beatmaplist(beatmaplist)
			print('Downloading...\n'+'-'*14)
			for i, beatmap_id in enumerate(beatmap_ids):
				beatmap(beatmap_ids[i], osu_session, args.video, args.output)
	else:
		print('Input beatmap id or beatmap list file!')
		exit()

	# Extract beatmaps after downloading
	# Only extracts newly downloaded maps
	if not args.not_extract and urls_302 != []:
		print('\nExtracting... to {}'.format(args.output))
		extract_beatmap(args.output)
	else:
		print('\nCheck temp directory to see downloaded beatmaps!')

	# List of undownloadable beatmaps
	if urls_404 != [] or urls_500 != [] or not_valid_urls != []:
		print('\nBeatmaps unable to download\n' + '-' * 28)
		if urls_404 != []:
			for i in urls_404:
				print('https://osu.ppy.sh/beatmapsets/{} | Beatmap not found. Check beatmap id or url'.format(i))
		if urls_500 != []:
			for i in urls_500:
				print('https://osu.ppy.sh/beatmapsets/{} | Beatmap unable to download. Check beatmap id or url. Try downloading manually'.format(beatmap_id))
		if not_valid_urls != []:
			for i in not_valid_urls:
				print('{} | Not a valid beatmap url'.format(i))
	print('\nThank you for using osuBeatmapDownloader')


if __name__ == '__main__':
	__version__ = "2.0"
	formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=52)
	parser = argparse.ArgumentParser(formatter_class=formatter)

	parser.add_argument('-id', required=False, type=str, help='Song/Beatmap id')
	parser.add_argument('-u', '--url', required=False, type=str, help='Song/Beatmap url')
	parser.add_argument('-f', '--file', required=False, type=argparse.FileType('r', encoding='UTF-8'), help='Add file containing beatmap ids or urls. Check example.txt')
	parser.add_argument('-o', '--output', required=False, type=str, default='Songs/', help='Folder/Directory to download the beatmaps (default: Songs/)')
	parser.add_argument('-V', '--video', required=False, default=False, action='store_true', help="Download with Video")
	parser.add_argument('-not-extract', required=False, default=False, action='store_true', help="For not extracting .osz/beatmap file")
	parser.add_argument('-v', '--version', action='version', version='%(prog)s v{v}'.format(v=__version__), help="Show Version")

	args = parser.parse_args()

	not_valid_urls = []
	urls_302 = []
	urls_404 = []
	urls_500 = []

	beatmapDownloader()

