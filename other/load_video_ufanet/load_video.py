import ffmpeg

input_url = "http://136.169.226.80/1600746658/tracks-v1/index.fmp4.m3u8?token=e355dad2f2fc455fbd65784c0e348ecf"
output_file = "output.mp4"

try:
    # Загружаем 10 секунд видео
    ffmpeg.input(input_url, t=10, r=30).output(output_file).run()
    print(f"Видео успешно сохранено в файл {output_file}")
except ffmpeg.Error as e:
    print(f"Ошибка при обработке видео: {e}")
