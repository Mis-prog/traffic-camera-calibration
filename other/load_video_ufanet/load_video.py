# import requests
# import os
#
# html = requests.get('http://maps.ufanet.ru/ufa').text
# index_for_token = html.find("перекрёсток Карла Маркса - Свердлова")
# print(index_for_token)
# ttemp = html[index_for_token-800:index_for_token + 800]
# print(ttemp)
# index_for_token = ttemp.find("marker.token = ")
# ttemp = ttemp[index_for_token:index_for_token + len("marker.token = 8314d794f6cc4620ae02fb62ef4163b2") + 1].split(
#     "marker.token = ")[1][1:]
# playlist = "http://136.169.226.59/1600746658/tracks-v1/index.fmp4.m3u8?token=" + ttemp
# print(playlist)
# videoLink = os.path.dirname(playlist) + '/'

import ffmpeg

input_url = "http://136.169.226.80/1600746658/tracks-v1/index.fmp4.m3u8?token=89421cab65a94ce99d2ef99798bb0896"
output_file = "output.mp4"

# Загружаем 10 секунд видео
ffmpeg.input(input_url, t=10).output(output_file).run()