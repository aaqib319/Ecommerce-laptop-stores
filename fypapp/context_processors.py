from .models import Brands

def brand_list(request):
    brands = Brands.objects.all()
    return {'brands': brands}