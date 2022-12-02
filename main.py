import os
import uvicorn
from app import constant

if __name__ == "__main__":
    hostip = "127.0.0.1"
    # hostip = constants.SERVER_IP
    uvicorn.run("app.api:content_extract", 
                # host=hostip, port=constants.SERVER_PORT, reload=True)
                host=hostip, port=8000, reload=True)
