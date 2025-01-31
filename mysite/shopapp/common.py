from csv import DictReader
from io import TextIOWrapper

from django.template.context_processors import request

from shopapp.models import Product


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=request.encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products
