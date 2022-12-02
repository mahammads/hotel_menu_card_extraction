---------------------------Hotel Menu Card Extraction------------------------------

In config file save the aws credentials and required path for the folders as below:

temp: to save the enhanced images.
hocr_pdf: to save the editable to pdfs for text Extraction.
excel_folder : to save to excel output file in local folder.
input: to save the incoming image/pdf file from user.
translated_output ; to save the extracted text file.

img_ocr.py: this file will enhance each image in pdf/jpg.tiff files.
and then convert it into text file by reserving the same format as pdf/image.

extraction.py: in this file we are using aws textract service to identify and extract table.
after extraction we are cleansing the output and combining the one excel file.

api.py:this file used for creating an apis to interface the soln with browser.