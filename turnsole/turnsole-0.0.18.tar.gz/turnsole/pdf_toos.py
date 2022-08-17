import cv2
import fitz
import numpy as np

def pdf_to_images(pdf_path: str):
    """PDF 转 OpenCV Image
    
    Args:
        pdf_path (str): Description
    
    Returns:
        TYPE: Description
    """
    images = []
    doc = fitz.open(pdf_path)
    # producer = doc.metadata.get('producer')

    for pno in range(doc.page_count):
        page = doc.load_page(pno)

        all_texts = page.get_text().replace('\n', '').strip()
        # 根据经验过滤掉特殊情况
        all_texts = all_texts.strip('Click to buy NOW!PDF-XChangewww.docu-track.comClick to buy NOW!PDF-XChangewww.docu-track.com')
        blocks = page.get_text("dict")["blocks"]
        imgblocks = [b for b in blocks if b["type"] == 1]

        page_images = []
        # 如果一个字都没有，
        if len(all_texts) == 0 and len(imgblocks) != 0:
            # # 这些 producer 包含碎图，如果真的是碎图我们把碎图拼接一下
            # if producer in ['Microsoft: Print To PDF',
            #                 'GPL Ghostscript 8.71',
            #                 'doPDF Ver 7.3 Build 398 (Windows 7 Business Edition (SP 1) - Version: 6.1.7601 (x64))',
            #                 '福昕阅读器PDF打印机 版本 11.0.114.4386']:
            patches = []
            for imgblock in imgblocks:
                contents = imgblock["image"]
                img_array = np.frombuffer(contents, dtype=np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                patches.append(image)
            try:
                try:
                    image = np.concatenate(patches, axis=0)
                    page_images.append(image)
                except:
                    image = np.concatenate(patches, axis=1)
                    page_images.append(image)
            except:
                # 当两张拼不到一块的时候我们可以认为他是两张图，如果超过两张那就不一定了
                if len(patches) == 2:
                    page_images = patches
                else:
                    pix = page.get_pixmap(dpi=300)
                    contents = pix.tobytes(output="png")
                    img_array = np.frombuffer(contents, dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    page_images.append(image)
            # else:
            #     for imgblock in imgblocks:
            #         contents = imgblock["image"]
            #         img_array = np.frombuffer(contents, dtype=np.uint8)
            #         image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            #         page_images.append(image)
        else:
            pix = page.get_pixmap(dpi=300)
            contents = pix.tobytes(output="png")
            img_array = np.frombuffer(contents, dtype=np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            page_images.append(image)
        images.append(page_images)
    return images

