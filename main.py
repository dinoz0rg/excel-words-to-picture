import cv2
import os
import wget
import pandas as pd
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import threading
from time import sleep


class ImageAdder:
    def __init__(self):
        self.images = []
        self.keywords = []

    def create_folder(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def delete_image_files(self, download_dir):
        for f in os.listdir(download_dir):
            os.remove(os.path.join(download_dir, f))

    def download_images_from_url(self, excel_file, download_dir):
        num = 0

        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            num += 1
            image_file = self.append_images(num)
            pic = row['<pic_url><item>']
            print(f"Downloading: {pic}, Output: {image_file}")
            wget.download(url=pic, out=f"{download_dir}\{image_file}")  #  Download links from loop and save to downloads folder

        #     download_location = f"{download_dir}\{image_file}"
        #     threading.Thread(target=wget.download, args=(pic, download_location)).start()
        # sleep(2)

    def append_images(self, num):
        image_file = f"{num}.jpg"
        self.images.append(image_file)
        return image_file

        # for filename in os.listdir(download_dir):
        #     if filename.endswith(".jpg"):
        #         self.images.append(filename)

    def append_keywords(self, excel_file):
        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            self.keywords.append(row['query'])

    def _draw_to_image(self, img, keyword, img_filename, savefile_dir):
        fontpath = "./simsun.ttc"
        font = ImageFont.truetype(fontpath, 32)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((20, 20), keyword, font=font, fill=(0, 255, 0, 0))
        img = np.array(img_pil)
        cv2.imshow('img-{}'.format(keyword), img)
        cv2.waitKey(600)
        # Save the file
        cv2.imwrite(f"{savefile_dir}/{img_filename}", img)

    def main(self):
        excel_file = '345(1).xlsx'
        download_dir = 'downloads'
        savefile_dir = 'savefile'

        self.create_folder(download_dir)  # Create initial download folder if not exist
        self.create_folder(savefile_dir)  # Create initial savefile folder if not exist
        self.delete_image_files(download_dir)  # Delete all files inside download folder at start
        self.delete_image_files(savefile_dir)  # Delete all files inside savefile folder at start

        self.download_images_from_url(excel_file, download_dir)  # Download all images from links in excel to files, and append images to __init__
        self.append_keywords(excel_file)  # Append keywords to __init__

        for img_filename, keyword in zip(self.images, self.keywords):
            img_array = cv2.imread(f"{download_dir}\{img_filename}")
            print(f"Procesing: {keyword}, Output: {img_filename}")
            # self._draw_to_image(img_array, keyword, img_filename, savefile_dir)
            t = threading.Thread(target=self._draw_to_image, args=(img_array, keyword, img_filename, savefile_dir))
            t.start()


if __name__ == "__main__":
    i = ImageAdder()
    i.main()