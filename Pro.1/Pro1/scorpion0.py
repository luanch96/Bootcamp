# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    scorpion0.py                                       :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: luisanch <luisanch@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/04/17 12:27:29 by luisanch          #+#    #+#              #
#    Updated: 2023/04/17 12:27:31 by luisanch         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import argparse
from PIL import Image, ExifTags


def print_metadata(image_file):
    with Image.open(image_file) as img:
        print(f"File: {image_file}")
        print(f"Format: {img.format}")
        print(f"Size: {img.size}")
        print(f"Mode: {img.mode}")
        print(f"Creation Time: {os.path.getctime(image_file)}")
        try:
            exif_data = img._getexif()
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal":
                    print(f"Date Taken: {value}")
                else:
                    print(f"{tag}: {value}")
        except AttributeError:
            print("No EXIF data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_files", nargs="+", help="Image files to analyze")
    args = parser.parse_args()

    for image_file in args.image_files:
        if not os.path.isfile(image_file):
            print(f"{image_file} is not a valid file")
            continue
        ext = os.path.splitext(image_file)[1]
        if ext.lower() not in [".jpg", ".jpeg", ".png", ".gif"]:
            print(f"{image_file} is not a valid image file")
            continue
        print_metadata(image_file)
