from django.core.management.base import BaseCommand
from products.models import Product
from imagekit.cachefiles import ImageCacheFile

class Command(BaseCommand):
    help = 'Regenerates thumbnails for all products'

    def handle(self, *args, **options):
        products = Product.objects.all()
        for product in products:
            if product.image:
                try:
                    # Force regeneration of the thumbnail
                    if hasattr(product, 'image_thumbnail'):
                        thumbnail = ImageCacheFile(product.image_thumbnail)
                        thumbnail.generate()
                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully regenerated thumbnail for {product.name}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error regenerating thumbnail for {product.name}: {str(e)}')
                    ) 