import cv2
import os
import wget
import threading
import pandas as pd
import numpy as np
from time import sleep
from PIL import Image, ImageFont, ImageDraw


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

    def excel_extensions(self, filename):
        print(f"Reading file: {filename}")

        df = None
        if filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filename)
        elif filename.endswith('.csv'):
            df = pd.read_csv(filename, sep=',', encoding='utf-8')
        return df

    def download_images_from_url(self, excel_file, download_dir, img_column):
        num = 0

        df = self.excel_extensions(excel_file)
        for index, row in df.iterrows():
            num += 1
            image_file = self.append_images(num)
            pic = row[img_column]
            print(f"Downloading: {pic}, Output: {image_file}")
            # wget.download(url=pic, out=f"{download_dir}\{image_file}")  #  Download links from loop and save to downloads folder

            download_location = f"{download_dir}\{image_file}"
            threading.Thread(target=wget.download, args=(pic, download_location)).start()
        sleep(3)  # Change the value higher for low spec processors

    def append_images(self, num):
        image_file = f"{num}.jpg"
        self.images.append(image_file)
        return image_file

        # for filename in os.listdir(download_dir):
        #     if filename.endswith(".jpg"):
        #         self.images.append(filename)

    def append_keywords(self, excel_file, keyword_column):
        df = self.excel_extensions(excel_file)
        for index, row in df.iterrows():
            self.keywords.append(row[keyword_column])

    def _draw_to_image(self, img, keyword, img_filename, savefile_dir):
        fontpath = "./simsun.ttc"
        font = ImageFont.truetype(fontpath, 32)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)

        # get coords based on boundary
        W, H = img_pil.size
        w, h = draw.textsize(keyword, font=font)

        # add text centered on image
        draw.text(((W - w) / 2, (H - h) / 2), keyword, font=font, fill="white", align='middle')
        img = np.array(img_pil)
        cv2.imshow('img-{}'.format(keyword), img)
        cv2.waitKey(600)

        # Save the file
        cv2.imwrite(f"{savefile_dir}/{img_filename}", img)

    def main(self):
        excel_file = '345(1).xlsx'
        image_column = '<pic_url><item>'
        keyword_column = 'query'

        download_dir = 'downloads'
        savefile_dir = 'savefile'

        self.create_folder(download_dir)  # Create initial download folder if not exist
        self.create_folder(savefile_dir)  # Create initial savefile folder if not exist
        self.delete_image_files(download_dir)  # Delete all files inside download folder at start
        self.delete_image_files(savefile_dir)  # Delete all files inside savefile folder at start

        self.download_images_from_url(excel_file, download_dir, image_column)  # Download all images from links in excel to files, and append images to __init__
        self.append_keywords(excel_file, keyword_column)  # Append keywords to __init__

        for img_filename, keyword in zip(self.images, self.keywords):
            img_array = cv2.imread(f"{download_dir}\{img_filename}")
            print(f"Procesing: {keyword}, Output: {img_filename}")
            # self._draw_to_image(img_array, keyword, img_filename, savefile_dir)
            t = threading.Thread(target=self._draw_to_image, args=(img_array, keyword, img_filename, savefile_dir))
            t.start()



if __name__ == "__main__":
    i = ImageAdder()
    i.main()