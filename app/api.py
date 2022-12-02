
import os
from fastapi import FastAPI ,File, status, UploadFile,HTTPException
from app import config
from app.extraction import AwsTableExtract
from app.img_to_hocr import DataExtract
from fastapi.responses import FileResponse

content_extract = FastAPI()

@content_extract.get("/")
def read_root():
   return {"Status": "UP"}

@content_extract.post("/get_text_file/")
async def get_barcode_data(uploaded_file: UploadFile = File(...)):
    input_path = config.input_file_path

    files_to_delete=os.listdir(input_path)
    for i in files_to_delete:
        os.remove(input_path+'/'+i)

    file_location = f"{input_path}/{uploaded_file.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(uploaded_file.file.read())  
    try:     
        text_obj = DataExtract()
        final_result = text_obj.final_hocr_result(file_location)
        
        return FileResponse(final_result, media_type='text/html')
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)


@content_extract.post("/get_excel_file/")
async def get_barcode_data(uploaded_file: UploadFile = File(...)):
    input_path = config.input_file_path

    files_to_delete=os.listdir(input_path)
    for i in files_to_delete:
        os.remove(input_path+'/'+i)

    file_location = f"{input_path}/{uploaded_file.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(uploaded_file.file.read())  
    try:     
        excle_obj = AwsTableExtract()
        excel_output = excle_obj.image_to_data(file_location)
        headers = {'Content-Disposition': 'attachment; filename="Book.xlsx"'}
        return FileResponse(excel_output, headers=headers)
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)

    
