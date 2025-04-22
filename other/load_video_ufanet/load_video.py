import ffmpeg

input_url = "http://136.169.226.80/1600746658/tracks-v1/index.fmp4.m3u8?token=c833bffff87b44029484688bd5721b59"
output_file = "output.mp4"

# Загружаем 10 секунд видео
ffmpeg.input(input_url, t=600).output(output_file).run()
