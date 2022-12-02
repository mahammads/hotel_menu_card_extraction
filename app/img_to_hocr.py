from PIL import Image, ImageEnhance
import os
import pytesseract as pt
from pdf2image import convert_from_path
import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter
import io
import app.config as config
import subprocess as sp
import app.config as config
import logging
import datetime as dt
import traceback

tesseract = config.tesseract
pt.pytesseract.tesseract_cmd = tesseract
poppler_path = config.poppler_path

Image.MAX_IMAGE_PIXELS = 933120000

time_now = dt.datetime.now()
time_now = dt.datetime.strftime(time_now, "%d-%m-%Y")
current_path = config.root_path
log_directory = current_path + '/LOGS/' + str(time_now)

if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
logging.basicConfig(filename=log_directory + "/solution_run.log", filemode= "a",format = "%(asctime)s %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

class DataExtract:
   
    def hocr_pdf(self,input_file):
        ##---------------------------------------------------------------------------------------##
        ## This function enhance the image and convert it inot editable pdfs                     ##
        ##---------------------------------------------------------------------------------------##
        logger.setLevel(logging.INFO)
        try:
            file_extenssion =  input_file.split('.')[-1]
            image_ext_list = ['jpg','jpeg','tif','tiff','png', 'webp']

            if file_extenssion.lower() in image_ext_list:
                image_list = []
                img = Image.open(input_file)
                filter = ImageEnhance.Brightness(img)
                new_image = filter.enhance(1.7)
                image_list.append(new_image)

            if file_extenssion.lower() == 'pdf':
                image_list = convert_from_path(input_file, poppler_path=poppler_path)
                # image_list = [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) for img in image_list ]
        
            name = os.path.split(input_file)[-1]
            print(name)
            logger.info(f"file name is {name}")
            temp_folder_path = config.hocr_pdfs
            if not os.path.exists(temp_folder_path):
                os.makedirs(temp_folder_path)
            pdf_writer = PyPDF2.PdfFileWriter()

            for image in image_list:
                page = pt.pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
                pdf = PyPDF2.PdfFileReader(io.BytesIO(page))
                pdf_writer.addPage(pdf.getPage(0))

            # export the searchable PDF to searchable.pdf
            for file_path in os.listdir(temp_folder_path):
                os.remove(temp_folder_path + "/" + file_path)

            new_folder_path = temp_folder_path
            new_pdf_name = os.path.join(new_folder_path,"Temp_" + name + '.pdf')
            with open(new_pdf_name, "wb") as f:
                pdf_writer.write(f)
            logger.info(f"{new_pdf_name} pdf created successfully.")
            return new_pdf_name
        except Exception as err:
            err = traceback.format_exc()
            logger.error(err)
            print(err)


    def pdf2text_poplr(self,pdf_name):
      
        ##---------------------------------------------------------------------------------------##
        ## This function extracts text from the pdf by preserving the format                     ##
        ##---------------------------------------------------------------------------------------##
        try:
            logger.setLevel(logging.INFO)
            file_name = os.path.split(pdf_name)[-1]
            for file in os.listdir(config.translated_output_folder):
                os.remove(config.translated_output_folder +'/'+ file)
            text_file_name = config.translated_output_folder + '/'+ file_name + ".txt"
            if not os.path.exists(config.translated_output_folder):
                os.makedirs(config.translated_output_folder)

            args = [config.poppler_path_exe, "-layout", pdf_name, "-"]
            cp = sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, check=True, text=True, encoding="utf8")
            text = cp.stdout
            with open(text_file_name, 'w', encoding="utf8") as f:
                f.write(cp.stdout)
            logger.info(f"{text_file_name} text file created successfully.")
            return text,text_file_name
            # return cp.stdout
        except Exception as err:
            err = traceback.format_exc()
            logger.error(err)
            print(err)

    def final_hocr_result(self,file_name):
        ##----------------------------------------------------------##
        ## This function combined the all functions                 ##
        ##----------------------------------------------------------##
        try:
            pdf_path = self.hocr_pdf(file_name)
            text,text_file_name = self.pdf2text_poplr(pdf_path)
            return text_file_name
        except Exception as err:
            err = traceback.format_exc()
            logger.error(err)
            print(err)

if __name__ == "__main__":
    pass