from pathlib import Path
import urllib.request
import urllib
import imghdr
import posixpath
import re
import hashlib
from io import BytesIO
from PIL import Image
import io

'''
Python api to download image form Bing.
Author: Jeremiah Korreck (korreckj328@gmail.com) [Fork]
        Guru Prasad (g.gaurav541@gmail.com) [Original]
'''


def image_to_byte_array(image: Image) -> bytes:
    print('creating bytesio object')
    img_byte_array = io.BytesIO()
    print('saving image to bytes object')
    image.save(img_byte_array, format="PNG")
    img_byte_array = img_byte_array.getvalue()
    return img_byte_array


def resize(img, size):
    print('size is: ' + str(size))
    if size != 'none':
        print('resize is not none ... resizing')
        assert (type(size) == tuple)
        print('size is valid')
        print('bytes to image')
        img = Image.open(io.BytesIO(img))
        print('resizing')
        img = img.resize(size=size, resample=Image.LANCZOS)
        print('image resized')
    else:
        print('no need to resize image')
    return img


class Bing:
    def __init__(self, query, limit, output_dir, adult, timeout, filter='', size='none', verbose=True):
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filter = filter
        self.verbose = verbose
        self.seen = set()
        self.hash_list = []
        self.size = size

        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        print('Size: ' + str(self.size))

        # self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        self.page_counter = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                                      'AppleWebKit/537.11 (KHTML, like Gecko) '
                                      'Chrome/23.0.1271.64 Safari/537.11',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive'}

    def get_filter(self, shorthand):
        if shorthand == "line" or shorthand == "linedrawing":
            return "+filterui:photo-linedrawing"
        elif shorthand == "photo":
            return "+filterui:photo-photo"
        elif shorthand == "clipart":
            return "+filterui:photo-clipart"
        elif shorthand == "gif" or shorthand == "animatedgif":
            return "+filterui:photo-animatedgif"
        elif shorthand == "transparent":
            return "+filterui:photo-transparent"
        else:
            return ""

    def save_image(self, image, file_path):
        with open(str(file_path), 'wb') as f:
            f.write(image)

    def save_hashes(self, file_path):
        with open(str(file_path), 'w') as f:
            hash_str: str = ""
            for h in self.hash_list:
                h = h + ","
                hash_str += h
            f.write(hash_str)

    def load_hashes(self):
        try:
            with open(self.output_dir.joinpath("hash_table.csv"), 'r') as f:
                hash_str = f.read()
            if hash_str != "":
                self.hash_list = hash_str.split(',')
        except:
            print("No hash table found assuming first run for this query")

    def download_image(self, link, size):
        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                file_type = "jpg"

            if self.verbose:
                # Download the image
                print("[%] Downloading Image #{} from {}".format(self.download_count, link))

            request = urllib.request.Request(link, None, self.headers)
            image = urllib.request.urlopen(request, timeout=self.timeout).read()
            print('resizing ... ')
            image = resize(image, size=self.size)
            if self.size != 'none':
                print('transitioning back to byte array ...')
                image = image_to_byte_array(image)
            print('done')
            if not imghdr.what(None, image):
                print('[Error]Invalid image, not saving {}\n'.format(link))
                raise ValueError('Invalid image, not saving {}\n'.format(link))
            print('hashing image ... ')
            try:
                new_hash = hashlib.sha1(image).hexdigest()
            except:
                exit(-1)
            print('complete')

            if new_hash not in self.hash_list:
                self.hash_list.append(new_hash)
                self.save_image(image,
                                self.output_dir.joinpath("{}.{}".format(str(new_hash), 'png')))
                self.download_count += 1
                if self.verbose:
                    print("[%] File Downloaded !\n")

        except Exception as e:
            self.download_count -= 1
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    def run(self):
        self.load_hashes()
        while self.download_count < self.limit:
            if self.verbose:
                print('\n\n[!!]Indexing page: {}\n'.format(self.page_counter + 1))
            # Parse the page source and download pics
            request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
                          + '&first=' + str(self.page_counter) + '&count=' + str(self.limit) \
                          + '&adlt=' + self.adult + '&qft=' + (
                              '' if self.filter is None else self.get_filter(self.filter))
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf8')
            if html == "":
                print("[%] No more images are available")
                break
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
            if self.verbose:
                print("[{}][%] Indexed {} Images on Page {}.".format(self.query, len(links), self.page_counter + 1))
                print("\n===============================================\n")

            for link in links:
                if self.download_count < self.limit and link not in self.seen:
                    self.seen.add(link.replace(" ", "%20"))
                    self.download_image(link.replace(" ", "%20"), size=self.size)

            self.page_counter += 1
        self.save_hashes(self.output_dir.joinpath("hash_table.csv"))
        print("\n\n[%] Done. Downloaded {} images.".format(self.download_count))
