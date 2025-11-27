import logging
from datetime import datetime
from recognition2 import analyze_read
from cdb_extract import save_to_cosmos

def main(myblob: bytes, name: str):
    upload_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    logging.info(f"Se subió un archivo: {name} a las {upload_time}")

    if name.lower().endswith(".pdf"):
        logging.info(f"Procesando PDF: {name}")
        result = analyze_read(myblob, name)
        save_to_cosmos(result)
        logging.info(f"PDF {name} procesado y guardado en Cosmos DB")