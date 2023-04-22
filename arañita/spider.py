# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    spider.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ivromero <ivromero@student.42urduliz.co    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/04/18 23:50:15 by ivromero          #+#    #+#              #
#    Updated: 2023/04/22 16:43:14 by ivromero         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import requests
import argparse
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


parser = argparse.ArgumentParser(description='Programa Spider')
parser.add_argument("url", type=str, help="URL a inspeccionar")
parser.add_argument("-r", action='store_true',
					help="descargar imágenes recursivamente")
parser.add_argument(
	"-l", type=int, help="profundidad máxima para descarga recursiva (por defecto: 5)", default=5)
parser.add_argument(
	"-p", type=str, help="directorio de salida (por defecto: ./data/)", default="./data/")

extensiones = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]


def descargar_imagen(url, directorio, url_html):
	"""
	Función para descargar una imagen de una URL y guardarla en un directorio específico.
	"""
	url_parseada = urlparse(url_html)
	url_base = f"{url_parseada.scheme}://{url_parseada.netloc}"
	if url.startswith("/"):
		url = url_base + url
	elif not url.startswith("http"):
		url = url_base + "/" + url
		print(url)

	nombre_archivo = url.split("/")[-1]
	ruta_archivo = os.path.join(directorio, nombre_archivo)
	
	try:
		with open(ruta_archivo, 'wb') as f:
			respuesta = requests.get(url)
			f.write(respuesta.content)
	except Exception as e:
		print(f"Se produjo un error al descargar el archivo: {e}")


def obtener_url_absoluta_imagen(url_relativa, url_base):
	"""
	Función para convertir una URL relativa de una imagen (/imgs/xxx.jpg) en una URL absoluta (http://www.42urduliz.com/imgs/xxx.jpg).
	"""
	url_relativa_parseada = urlparse(url_relativa)
	url_base_parseada = urlparse(url_base)
	ruta_absoluta = url_base_parseada.scheme + "://" + \
		url_base_parseada.netloc + url_relativa_parseada.path
	return ruta_absoluta


def inspeccionar_pagina(url, nivel, max_nivel, directorio, ya_visitadas=[]):
	"""
	Función para inspeccionar una página web y descargar todas las imágenes.
	"""
	if nivel > max_nivel or not isinstance(url, str) or not url:
		return
	if  url.startswith("#") or url.startswith("mailto:"):
		return

	if url in ya_visitadas:
		return
	else:
		ya_visitadas.append(url)

	print("***************************************************************")
	print(F"({nivel}) {url}")
	print("***************************************************************")
	if not url.startswith("http") and nivel == 0:
		max_nivel = 0
		try:
			with open(url) as archivo:
				html = archivo.read()
		except FileNotFoundError as e:
			print("No se puede encontrar el archivo: " + url)
			return

	else:
		try:
			respuesta = requests.get(url)
			html = respuesta.content
		except requests.exceptions.RequestException as e:
			print(f"[ERROR] No se pudo hacer solicitud a {url}: {str(e)}")
			return
	#print(html)
	soup = BeautifulSoup(html, 'html.parser')
	
	for img in soup.find_all('img'):
		src_img = img.get('src')
		if src_img:
			extensión = os.path.splitext(src_img)[1]
			if extensión in extensiones:
				print(F"[+] Descargando {src_img} en {directorio}")
				descargar_imagen(src_img, directorio, url)

	for div in soup.find_all('div'):
		bg_img = div.get('style')
		if bg_img and 'background-image' in bg_img:
			src_bg_img = re.search('url\((.*?)\)', bg_img).group(1)
			extensión = os.path.splitext(src_bg_img)[1]
			if extensión in extensiones:
				print(F"[+] Descargando {src_bg_img} en {directorio}")
				descargar_imagen(src_bg_img, directorio, url)

	for url in soup.find_all('a'):
		src_a = url.get('href')
		inspeccionar_pagina(src_a, nivel+1, max_nivel, directorio, ya_visitadas)


def main():
	args = parser.parse_args()
	if not os.path.exists(args.p):
		os.makedirs(args.p)
	inspeccionar_pagina(args.url, 0, args.l, args.p)

if __name__ == "__main__":
	main()
