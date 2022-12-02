import boto3
import boto3.session
from trp import Document
import pandas as pd
from PIL import Image, ImageEnhance, ImageSequence
import os
from pdf2image import convert_from_path
from app import config
import pytesseract as pt
import pandas as pd
from app.img_to_hocr import logger
import traceback
import logging

AWSAccessKeyId = config.aws_access_key
AWSSecretKey = config.aws_secret_key
region_name = config.aws_region
tesseract = config.tesseract
pt.pytesseract.tesseract_cmd = tesseract
poppler_path = config.poppler_path

class AwsTableExtract():
    ##----------------------------------------------------------##
    ## This function enhance the image or pdf clearity          ##
    ##----------------------------------------------------------##
    def conv_img_enhance(self, img_name):
        try:
            logger.setLevel(logging.INFO)
            if not os.path.exists(config.temp_path):
                os.makedirs(config.temp_path)
            for file in os.listdir(config.temp_path):
                os.remove(config.temp_path + '/'+file)
            file_ext = img_name.split('.')[-1]
            img_ext_list = ['jpg', 'jpeg', 'webp', 'tif', 'png']
            image_list = []
            if file_ext.lower() in img_ext_list:
                image = Image.open(img_name)
                for i, page in enumerate(ImageSequence.Iterator(image)):
                    image = page.convert('RGB')
                    image_list.append(image)
            
            if file_ext.lower() == 'pdf':
                image_list = convert_from_path(img_name, poppler_path=poppler_path)

            for ind, image in enumerate(image_list):
                enhancer = ImageEnhance.Brightness(image)
                im_output = enhancer.enhance(1.8)
                new_img_path = os.path.join(config.temp_path, 'new_image'+str(ind)+'.jpg')
                im_output.save(new_img_path)
            logger.info(f"{img_name} image enhances succesfully.")
            return True
        except Exception as err:
            err = traceback.format_exc()
            logger.error(err)
            print(err)

    ##----------------------------------------------------------##
    ## This function will extract raw tables from images        ##
    ##----------------------------------------------------------##
    def extract_raw_table(self,file_name):
        try:
            logger.setLevel(logging.INFO)
            client = boto3.client('textract', aws_access_key_id=AWSAccessKeyId,
                                    aws_secret_access_key=AWSSecretKey, region_name=region_name)
            logger.info("connected to aws successfully.")
            df_list = []
            status = self.conv_img_enhance(file_name)
            if status:
                for img in os.listdir(config.temp_path):
                    img_path = os.path.join(config.temp_path, img)
                    with open(img_path, 'rb') as document:
                        imageBytes = bytearray(document.read())
                    response = client.analyze_document(
                        Document={'Bytes': imageBytes}, FeatureTypes=["TABLES", "FORMS"])
                    doc = Document(response)
                    # print(doc)
                    for page in doc.pages:
                        for table in page.tables:
                            row_list = []
                            for r, row in enumerate(table.rows):
                                cell_list = []
                                for c, cell in enumerate(row.cells):
                                    cell_list.append(cell.text)
                                row_list.append(cell_list)
                            df = pd.DataFrame(row_list)
                            df_list.append(df)
            logger.info("extracted raw tables from received file.")
            return df_list
        except Exception as err:
            err = traceback.format_exc()
            logger.error(err)
            print(err)

    ##----------------------------------------------------------------------------------##
    ## This function will combine all the tables and export into clean dataframe        ##
    ##----------------------------------------------------------------------------------##
    def image_to_data(self, file_name):
        try:
            logger.setLevel(logging.INFO)
            logger.info(f"processing started for filename {file_name}")
            for excel_file in os.listdir(config.output_excel_folder):
                os.remove(config.output_excel_folder+'/'+ excel_file)
            dictionary =config.dictionary
            only_file_name = os.path.split(file_name)[-1]
            df_list = self.extract_raw_table(file_name)
            result = ''
            if len(df_list) != 0:
                # obj = DataExtract()
                # text_file_path = obj.final_hocr_result(file_name)
                # result = 'No Tables Detected.'
                for df in df_list:
                    df.replace(dictionary, inplace=True)
                    col_list = df.columns.tolist()
                    print(col_list)
                    if len(col_list) == 2:
                        df.columns = ['Menu', 'Price']
                output_file_path = os.path.join(config.output_excel_folder,only_file_name + '.xlsx')
                with pd.ExcelWriter(output_file_path) as writer:
                    for ind, df in enumerate(df_list):
                        # print(df)
                        df.to_excel(writer, sheet_name='table_'+str(ind))
            logger.info(f"excel output file saved in local folder {output_file_path}")
            return output_file_path
        except Exception as err:
            err = traceback.format_exc()
            logger.error(err)
            print(err)
    
if __name__ == "__main__":
    pass