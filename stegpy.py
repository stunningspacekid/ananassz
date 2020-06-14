# pip3 install opencv-python numpy tqdm
import cv2
import numpy as np
import tqdm


START_KEY = "_START_"
STOP_KEYim = "_STOPim_"
STOP_KEYtxt = "_STOPtxt_"


class Decoder:
    def __init__(self, input_img=None, output_img=None):
        self.input_img = input_img
        self.output_img = output_img

    def _to_bin_(self, data):
        """Convert `data` to binary format as string"""
        if isinstance(data, str):
            return ''.join([ format(ord(i), "08b") for i in data ])
        elif isinstance(data, bytes) or isinstance(data, np.ndarray):
            return [ format(i, "08b") for i in data ]
        elif isinstance(data, int) or isinstance(data, np.uint8):
            return format(data, "08b")
        else:
            raise TypeError("Type not supported.")

    def encode(self, secret_text, secret_img=None):
        if not self.output_img:
            exit('No output image')
        elif not self.input_img:
            exit('No input image')
        elif not secret_text and secret_img:
            exit('No valid data')
        # read the image
        image = cv2.imread(self.input_img)
        secret_data = ""
        # open ans prepare img
        if secret_img:
            with open(secret_img, 'rb') as f:
                img_data = f.read()
            secret_data += START_KEY + str(img_data) + STOP_KEYim
            print("[*] Image bytes:", len(secret_data))
        # prepare text
        if secret_text:
            text = START_KEY + secret_text + STOP_KEYtxt
            secret_data += text
            print("[*] Text bytes:", len(text))
        # maximum bytes to encode
        n_bytes = image.shape[0] * image.shape[1] * 3 // 8
        print("[*] Maximum bytes to encode:", n_bytes)
        if len(secret_data) > n_bytes:
            raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
        print("[*] Encoding data...")
        # add stopping criteria
        data_index = 0
        # convert data to binary
        binary_secret_data = self._to_bin_(secret_data)
        # size of data to hide
        data_len = len(binary_secret_data)
        # processing image
        for row in image:
            for pixel in row:
                # convert RGB values to binary format
                r, g, b = self._to_bin_(pixel)
                # modify the least significant bit only if there is still data to store
                if data_index < data_len:
                    # least significant red pixel bit
                    pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)
                    data_index += 1
                if data_index < data_len:
                    # least significant green pixel bit
                    pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)
                    data_index += 1
                if data_index < data_len:
                    # least significant blue pixel bit
                    pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)
                    data_index += 1
                # if data is encoded, early stopping
                if data_index >= data_len:
                    break
        # save the output image (encoded image)
        cv2.imwrite(self.output_img, image)
        print("[*] Encoded success!")

    def decode(self):
        if not self.output_img:
            exit('No output image')
        print("[+] Decoding...")
        # read the image
        image = cv2.imread(self.output_img)
        binary_data = ""
        for row in tqdm.tqdm(image):
            for pixel in row:
                r, g, b = self._to_bin_(pixel)
                binary_data += r[-1]
                binary_data += g[-1]
                binary_data += b[-1]
        # split by 8-bits
        all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]

        # convert from bits to characters
        decoded_data = ""
        results = [None, None]
        for byte in tqdm.tqdm(all_bytes):
            if decoded_data[-len(START_KEY):] == START_KEY:
                decoded_data = ""
            decoded_data += chr(int(byte, 2))
            if decoded_data[-len(STOP_KEYim):] == STOP_KEYim:
                results[0] = decoded_data[:-len(STOP_KEYim)]
            elif decoded_data[-len(STOP_KEYtxt):] == STOP_KEYtxt:
                results[1] = decoded_data[:-len(STOP_KEYtxt)]
        if not results[0] and not results[1]:
            exit("Can't decode")
        if results[0]:
            with open('decoded.jpg', 'wb') as f:
                f.write(eval(results[0]))
            print("[+] Decoded image:", 'decoded.jpg')
        if results[1]:
            print("[+] Decoded message:", results[1])


if __name__ == "__main__":
    decoder = Decoder("in.PNG", "out.PNG")
    #secret_text = str(input('Write your secret message: '))
    #secret_img = None
    #decoder.encode(secret_text=secret_text, secret_img=secret_img)
    decoder.decode()
