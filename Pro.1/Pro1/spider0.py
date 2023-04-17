# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    spider0.py                                         :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: luisanch <luisanch@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/04/17 11:59:59 by luisanch          #+#    #+#              #
#    Updated: 2023/04/17 12:05:41 by luisanch         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def download_image(url, directory):
    response = requests.get(url)
    filename = os.path.join(directory, os.path.basename(urlparse(url).path))
    with open(filename, "wb") as f:
        f.write(response.content)


def spider(url, recursion=False, recursion_depth=3, print_info=False, save_images=False):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    protocol = parsed_url.scheme
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    img_tags = soup.find_all("img")
    image_urls = [img["src"] for img in img_tags]

    if save_images:
        directory = os.path.join(os.getcwd(), domain)
        os.makedirs(directory, exist_ok=True)

    for image_url in image_urls:
        if not image_url.startswith("http"):
            image_url = urljoin(url, image_url)
        if save_images:
            download_image(image_url, directory)
    
    if recursion and recursion_depth > 0:
        links = soup.find_all("a")
        link_urls = [link.get("href") for link in links]
        for link_url in link_urls:
            if not link_url.startswith("http"):
                link_url = urljoin(url, link_url)
            if domain in link_url:
                if print_info:
                    print(f"Processing {link_url}")
                spider(link_url, recursion=True, recursion_depth=recursion_depth - 1, print_info=print_info, save_images=save_images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to spider")
    parser.add_argument("-r", "--recursion", help="Process links recursively", action="store_true")
    parser.add_argument("-l", "--recursion-depth", help="Depth of recursion", type=int, default=3)
    parser.add_argument("-p", "--print-info", help="Print links and images being processed", action="store_true")
    parser.add_argument("-S", "--save-images", help="Save images to subdirectory", action="store_true")
    args = parser.parse_args()

    spider(args.url, recursion=args.recursion, recursion_depth=args.recursion_depth, print_info=args.print_info, save_images=args.save_images)

