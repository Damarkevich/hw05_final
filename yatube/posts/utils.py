from django.conf import settings
from django.core.paginator import Paginator


def create_page_obj(request, post_list):
    paginator = Paginator(post_list, settings.AMOUNT_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
