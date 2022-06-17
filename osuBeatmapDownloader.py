import urllib3, re

song_id = '1740003'
no_video = '1'
osu_session = ""
headers = {
        'cookie': 'osu_session={s}'.format(s=osu_session),
        'authority': 'osu.ppy.sh',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'referer': 'https://osu.ppy.sh/beatmaps/{id}'.format(id=song_id),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }

url = "https://osu.ppy.sh/beatmapsets/{id}/download?noVideo={video_req}".format(id=song_id, video_req=no_video)
print(url)

http = urllib3.PoolManager()
r = http.request('GET', url, headers=headers)
data = r.data

filename = re.findall('"(.*)"', r.headers['Content-Disposition'])[0]
print(filename)

with open(filename, 'xb') as file:
    file.write(data)