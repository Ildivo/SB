"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам, и т.д.
"""
from csv import DictWriter
from dataclasses import field
from timeit import default_timer
import logging
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from docutils.parsers.rst.directives import encoding
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .common import save_csv_products
from .forms import ProductForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer

log = logging.getLogger(__name__)

@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный набор CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    )
    search_fields = ('name','description')
    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived',
    ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]
    @action(methods=['GET'], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type='text/csv')
        filename ="products-export.csv"
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        #print('hello products list')
        return super().list(*args, **kwargs)

    @action(
        detail=False,
        methods=['POST'],
        parser_classes=(MultiPartParser,)
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['products'].file,
            encoding = request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, return 404 if not found",
        responses={
        200: ProductSerializer,
        400: OpenApiResponse(description='Empty response, product by id not found'),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)



# Create your views here.
class ShopIndexView(View):

    #@method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
                ('Laptop', 1999),
                ('Desktop', 2999),
                ('Smartphone', 999),
            ]
        context = {
                "time_running": default_timer(),
                "products": products,
                "items": 1,
            }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")

        print('shop index context', context)
        return render(request, 'shopapp/shop-index.html', context=context)


# def shop_index(request: HttpRequest):
#     products = [
#         ('Laptop', 1999),
#         ('Desktop', 2999),
#         ('Smartphone', 999),
#     ]
#     context = {
#         "time_running": default_timer(),
#         "products": products,
#     }
#     return render(request, 'shopapp/shop-index.html', context=context)

class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all,
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)

# class ProductDetailView(View):
#     def get(self, request: HttpRequest, pk: int) -> HttpResponse:
#         product = get_object_or_404(Product, pk=pk)
#         context = {
#             'product': product,
#         }
#         return render(request, 'shopapp/products-details.html', context=context)

class ProductDetailView(DetailView):
    template_name = 'shopapp/products-details.html'
    #model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'

#def groups_list(request: HttpRequest):
#     context = {
#         "groups": Group.objects.prefetch_related('permissions').all,
#     }
#     return render(request, 'shopapp/groups-list.html', context=context)

# class ProductListView(TemplateView):
#     template_name = 'shopapp/products-list.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['products'] = Product.objects.all()
#         return context

class ProductListView(ListView):
    template_name = 'shopapp/products-list.html'
    #model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):#UserPassesTestMixin,# CreateView):
    def test_func(self):
        return self.request.user.is_superuser

    model = Product
    fields = 'name', 'price', 'description', 'discount', 'preview'
    success_url = reverse_lazy('shopapp:products_list')


class ProductUpdateView(UpdateView):
    model = Product
    fields = 'name', 'price', 'description', 'discount', 'preview'
    success_url = reverse_lazy('shopapp:products_list')
    template_name_suffix = '_update_form'
    # form_class = ProductForm

    def get_success_url(self):
        return reverse(
            'shopapp:product_detail',
                       kwargs={'pk': self.object.pk}
        )

    # def form_valid(self, form):
    #     response = super().form_valid(form)
    #     for image in form.files.getlist('images'):
    #         ProductImage.objects.create(
    #             product=self.object,
    #             image=image,
    #         )
    #     return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)

def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data['name']
            # price = form.cleaned_data['price']
            #Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products_list")
            return redirect(url)
    else:
        form = ProductForm()
    form = ProductForm()
    context ={
        "form": form,
    }
    return render(request, 'shopapp/create-product.html', context=context)

# def orders_list(request: HttpRequest):
#     context = {
#         "orders": Order.objects.select_related("user").prefetch_related('products').all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)

class OrderListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related('products')
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related('products')
    )

class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'product_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived,
                }
                for product in products
            ]
        cache.set(cache_key, products_data, 300)
        elem = products_data[0]
        name = elem["name"]
        print('name:', name)
        return JsonResponse({'products': products_data})