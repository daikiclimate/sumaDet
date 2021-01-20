from typing import List
import requests
from bs4 import BeautifulSoup
import sys
from logging import getLogger, StreamHandler, DEBUG, Formatter, INFO
from tqdm import tqdm
from pathlib import Path

OUTPUT_DIR = "./data"
LOG_LEVEL = INFO
URL_BASE = "https://smashwiki.info"
URL_IMAGES = "/カラーバリエーション_(SP)"

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(LOG_LEVEL)
formatter = Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


def get_page_html() -> str:
    try:
        res = requests.get(URL_BASE + URL_IMAGES)
    except:
        logger.error("ページを取得できませんでした。")
        sys.exit(1)
    if res.status_code != 200:
        logger.error("ウェブサイトが正常なステータスコードを返しませんでした。status=%d", res.status_code)
        sys.exit(1)
    logger.debug("ページに接続できました。")
    logger.debug("status = %d", res.status_code)
    html = res.content
    return html


class ImageData:
    def __init__(self, name: str, index: int, url: str):
        self.name = name
        self.index = index
        self.url = url

    def __str__(self):
        return f"ImageData({self.name}-{self.index:03})"


def parse_html(html: str) -> List[ImageData]:
    html = get_page_html()
    soup = BeautifulSoup(html, "html.parser")

    gallery = soup.select_one(".mw-parser-output")

    name = None
    get_list = []

    for child in gallery.contents:
        # print(child.name)
        if child.name == "h2":
            if name is not None:
                logger.warning("%sの画像が見つかりませんでした。", name)
                logger.warning("スキップします。")
            name = child.contents[1].string
            if name in ["備考", "脚注", "外部リンク"]:
                name = None
                continue
            logger.debug("名前を発見: %s", name)

        if child.name == "ul" and name is not None:
            imgs = child.select(
                "li > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1) > img:nth-child(1)"
            )
            if len(imgs) != 8:
                continue
            logger.debug("%sに%d個の画像が見つかりました。", name, len(imgs))
            for i, img in enumerate(imgs):
                imgsrc = img.get("src")
                get_list.append(ImageData(name, i + 1, URL_BASE + imgsrc))
            name = None

    return get_list


def download_and_save(img: ImageData, path: str):
    output_dir = Path(path) / img.name
    if not output_dir.exists():
        logger.debug("%s ディレクトリを作成しました", img.name)
        output_dir.mkdir()
    response = requests.get(img.url)
    logger.debug("%s-%03d を保存しました", img.name, img.index)
    image = response.content
    with open(output_dir / f"{img.index:03}.png", "wb") as file:
        file.write(image)


def main(output_path):
    if not Path(output_path).exists() or not Path(output_path).is_dir():
        logger.error("%s ディレクトリが存在しません。予め作成しておいてください。", output_path)
        sys.exit(1)
    html = get_page_html()
    logger.info("HTMLを取得しました")
    img_list = parse_html(html)
    logger.info("合計%d個の画像が見つかりました。", len(img_list))
    for img in tqdm(img_list):
        download_and_save(img, output_path)
    logger.info("ダウンロードが完了しました。")


if __name__ == "__main__":
    main(OUTPUT_DIR)


# from typing import List
# import requests
# from bs4 import BeautifulSoup
# import sys
# from logging import getLogger, StreamHandler, DEBUG, Formatter, INFO
# from tqdm import tqdm
# from pathlib import Path
#
# OUTPUT_DIR = "./data"
# LOG_LEVEL = INFO
# URL_BASE = "https://smashwiki.info"
# URL_IMAGES = "/カラーバリエーション_(SP)"
#
# logger = getLogger(__name__)
# handler = StreamHandler()
# handler.setLevel(LOG_LEVEL)
# formatter = Formatter("%(levelname)s: %(message)s")
# handler.setFormatter(formatter)
# logger.setLevel(DEBUG)
# logger.addHandler(handler)
# logger.propagate = False
#
#
# def get_page_html() -> str:
#     try:
#         res = requests.get(URL_BASE + URL_IMAGES)
#     except:
#         logger.error("ページを取得できませんでした。")
#         sys.exit(1)
#     if res.status_code != 200:
#         logger.error("ウェブサイトが正常なステータスコードを返しませんでした。status=%d", res.status_code)
#         sys.exit(1)
#     logger.debug("ページに接続できました。")
#     logger.debug("status = %d", res.status_code)
#     html = res.content
#     return html
#
#
# class ImageData:
#     def __init__(self, name: str, index: int, url: str):
#         self.name = name
#         self.index = index
#         self.url = url
#
#     def __str__(self):
#         return f"ImageData({self.name}-{self.index:03})"
#
#
# def parse_html(html: str) -> List[ImageData]:
#     html = get_page_html()
#     soup = BeautifulSoup(html, "html.parser")
#
#     gallery = soup.select_one(".mw-parser-output")
#
#     name = None
#     get_list = []
#
#     for child in gallery.contents:
#         # print(child.name)
#         if child.name == "h2":
#             if name is not None:
#                 logger.warning("%sの画像が見つかりませんでした。", name)
#                 logger.warning("スキップします。")
#             name = child.contents[1].string
#             if name in ["備考", "脚注", "外部リンク"]:
#                 name = None
#                 continue
#             logger.debug("名前を発見: %s", name)
#
#         if child.name == "ul" and name is not None:
#             imgs = child.select(
#                 "li > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1) > img:nth-child(1)"
#             )
#             logger.debug("%sに%d個の画像が見つかりました。", name, len(imgs))
#             for i, img in enumerate(imgs):
#                 imgsrc = img.get("src")
#                 get_list.append(ImageData(name, i + 1, URL_BASE + imgsrc))
#             name = None
#
#     return get_list
#
#
# def download_and_save(img: ImageData, path: str):
#     output_dir = Path(path) / img.name
#     if not output_dir.exists():
#         logger.debug("%s ディレクトリを作成しました", img.name)
#         output_dir.mkdir()
#     response = requests.get(img.url)
#     logger.debug("%s-%03d を保存しました", img.name, img.index)
#     image = response.content
#     with open(output_dir / f"{img.index:03}.png", "wb") as file:
#         file.write(image)
#
#
# def main(output_path):
#     if not Path(output_path).exists() or not Path(output_path).is_dir():
#         logger.error("%s ディレクトリが存在しません。予め作成しておいてください。", output_path)
#         sys.exit(1)
#     html = get_page_html()
#     logger.info("HTMLを取得しました")
#     img_list = parse_html(html)
#     logger.info("合計%d個の画像が見つかりました。", len(img_list))
#     for img in tqdm(img_list):
#         download_and_save(img, output_path)
#     logger.info("ダウンロードが完了しました。")
#
#
# if __name__ == "__main__":
#     main(OUTPUT_DIR)
