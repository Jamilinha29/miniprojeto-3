import logging

logging.basicConfig(
    filename="simulacao.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def registrar(msg):
    logging.info(msg)