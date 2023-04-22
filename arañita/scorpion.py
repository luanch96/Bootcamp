import exifread
import sys

def main():
    
    archivos = sys.argv[1:]
    
    for archivo in archivos:
        with open(archivo, 'rb') as f:
            tags = exifread.process_file(f)
            
            print("\n")
            print("=" * 30)
            print("Archivo: {}".format(archivo))
            print("=" * 30)
            for tag in tags.keys():
                if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                    print("{}: {}".format(tag, tags[tag]))
            print("=" * 30)

if __name__ == "__main__":
    main()
