import os
import cv2
import wget
import time
import telepot
import logging
import platform
import threading
import numpy as np
import pandas as pd
from PIL import Image, ImageFont, ImageDraw


class ImageAdder:
    def __init__(self):
        self.images = []
        self.keywords = []

        self.bot = telepot.Bot("INSERT BOT TOKEN HERE")
        self.chatid = "INSERT CHATID HERE"

    @staticmethod
    def get_computer_details():
        which_os = platform.uname()[0]
        pc_name = platform.uname()[1]
        processor = platform.uname()[4]
        return which_os, pc_name, processor

    @staticmethod
    def create_folder(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def delete_image_files(download_dir):
        for f in os.listdir(download_dir):
            os.remove(os.path.join(download_dir, f))

    @staticmethod
    def excel_extensions(filename):
        df = None
        if filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filename)
        elif filename.endswith('.csv'):
            df = pd.read_csv(filename, sep=',', encoding='utf-8')
        else:
            logging.info("Warning: Unsupported extension")
        return df

    def download_images_from_url(self, excel_file, download_dir, img_column):
        num = 0

        df = self.excel_extensions(excel_file)
        try:
            for index, row in df.iterrows():
                try:
                    num += 1
                    image_file = self.append_images(num)
                    pic = row[img_column]
                    print(f"Downloading: {pic}, Output: {image_file}")
                    # wget.download(url=pic, out=f"{download_dir}\{image_file}")  #  Download links from loop and save to downloads folder

                    download_location = f"{download_dir}\{image_file}"
                    threading.Thread(target=wget.download, args=(pic, download_location)).start()
                    time.sleep(0.1)

                except Exception as e:
                    logging.info(f"Exception in download_images_from_url func, row: {row}, details: {e}")
        except Exception as e:
            print(f"Exception in download_images_from_url (for loop) func, details: {e}")

        # sleep(10)  # Change the value higher for low spec processors

    def append_images(self, num):
        image_file = f"{num}.jpg"
        self.images.append(image_file)
        return image_file

        # for filename in os.listdir(download_dir):
        #     if filename.endswith(".jpg"):
        #         self.images.append(filename)

    def append_keywords(self, excel_file, keyword_column, append_offline=None):
        df = self.excel_extensions(excel_file)
        for index, row in df.iterrows():
            self.keywords.append(row[keyword_column])
            if append_offline:
                self.images.append(row['<pic_url><item>'])

    def _draw_to_image(self, img, keyword, img_filename, savefile_dir, savefile_name):
        try:
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
            # cv2.imwrite(f"{savefile_dir}/{img_filename}", img)
            cv2.imwrite(f"{savefile_dir}/{savefile_name}", img)

        except Exception as e:
            if "cannot open resource" in str(e):
                time.sleep(1)
                self._draw_to_image(img, keyword, img_filename, savefile_dir)
            else:
                logging.info(f"Exception in _draw_to_image func, details: {e}, more details: {img}")

    def send_logfile_to_telegram(self, logger_filename):
        try:
            self.bot.sendDocument(chat_id=self.chatid, document=(open(logger_filename, "rb")))
        except Exception as e:
            if "file must be non-empty" in str(e):
                self.bot.sendMessage(chat_id=self.chatid, text="Theres no error while running the tool, awesome!")
            else:
                self.bot.sendMessage(chat_id=self.chatid, text=f"Error found, details: {e}")

    def send_to_telegram(self, send_to_telegram, type, logger_filename=None, text=None):
        if send_to_telegram:
            if type == "msg":
                self.bot.sendMessage(chat_id=self.chatid, text=text)
            if type == "doc":
                self.send_logfile_to_telegram(logger_filename)

    def main(self):
        t1 = time.time()

        excel_file = 'test-jpg - Copy.xlsx'
        image_column = '<pic_url><item>'
        keyword_column = 'query'

        download_dir = 'downloads'
        savefile_dir = 'savefile'
        logger_filename = 'errors.log'

        send_to_telegram = False  # True if you want to send alerts on telegram, False if you dont want to send alerts
        enable_offline_mode = False  # True if you want to use offline images, False goes otherwise (Excel must use this format: https://i.imgur.com/M0wGMu0.png, https://i.imgur.com/ftF9ERt.png)

        which_os, pc_name, processor = self.get_computer_details()
        self.send_to_telegram(send_to_telegram, "msg", text=f"Process started on: {pc_name}:{processor}, enabled offline mode: {enable_offline_mode}")

        self.create_folder(download_dir)  # Create initial download folder if not exist
        self.create_folder(savefile_dir)  # Create initial savefile folder if not exist
        self.delete_image_files(savefile_dir)  # Delete all files inside savefile folder at start

        excel_length = len(self.excel_extensions(excel_file).index)
        self.send_to_telegram(send_to_telegram, "msg", text=f"Filename: {excel_file}, rows to process: {excel_length}")

        if not enable_offline_mode:
            self.delete_image_files(download_dir)  # Delete all files inside download folder at start
            self.download_images_from_url(excel_file, download_dir, image_column)  # Download all images from links in excel to files, and append images to __init__
        self.append_keywords(excel_file, keyword_column, enable_offline_mode)  # Append keywords to __init__

        num = 0
        for img_filename, keyword in zip(self.images, self.keywords):
            num += 1
            savefile_name = f"{num}.jpg"

            time.sleep(0.1)
            try:
                img_array = cv2.imread(f"{download_dir}\{img_filename}")
                print(f"Procesing: {keyword}, Output: {savefile_name}")
                # self._draw_to_image(img_array, keyword, img_filename, savefile_dir)
                t = threading.Thread(target=self._draw_to_image, args=(img_array, keyword, img_filename, savefile_dir, savefile_name))
                t.start()

            except Exception as e:
                logging.info(f"Exception in main (for_loop) func, details: {e}")
        self.send_to_telegram(send_to_telegram, "doc", logger_filename)

        t2 = time.time()
        print(f"Total time taken: {round(t2 - t1, 2)}s")
        self.send_to_telegram(send_to_telegram, "msg", text=f"Process finished, time taken: {round(t2 - t1, 2)}s")


if __name__ == "__main__":
    logging.basicConfig(
        filename="errors.log",
        filemode="w",
        level=logging.INFO,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    i = ImageAdder()
    i.main()
