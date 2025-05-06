
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.timezone import now
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import *
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.timezone import now
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Products, Brands, Category, ProductAttribute, CartItem, WishlistItem


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})
# ---------------- Base View ----------------
def base_view(request):
    brands = Brands.objects.all()
    return render(request, 'base.html', {'brands': brands, "timestamp": now().timestamp()})

# ---------------- Ecommerce View ----------------

def ecommerce_view(request):
    # products = Products.objects.all().prefetch_related('productattribute_set')
    products = Products.objects.filter(is_featured=True, status=True).prefetch_related('productattribute_set')


    # Add unique RAM and Storage values for each product
    for product in products:
        product.unique_rams = (
            product.productattribute_set.values_list("ram__id", "ram__ram").distinct()
        )
        product.unique_storages = (
            product.productattribute_set.values_list("storage__id", "storage__storage").distinct()
        )

    # Fetch cart items for the logged-in user (if authenticated)
    cart_items = CartItem.objects.filter(user=request.user).select_related("product", "attribute") if request.user.is_authenticated else []

    # Calculate total price of cart
    total_price = sum(item.attribute.price for item in cart_items if item.attribute)

    context = {
        "data": products,
        "cart_items": cart_items,  # Pass cart items to ecommerce.html
        "total_price": total_price,  # Pass total price for display
        "wishlist_items": WishlistItem.objects.filter(user=request.user) if request.user.is_authenticated else [],
        "brands": Brands.objects.all(),
    }

    return render(request, "ecommerce.html", context)

# trending view
from .models import Products

def trending_products_view(request):
    featured_products = Products.objects.filter(is_featured=True, status=True)
    print("Featured products count:", featured_products.count())  # DEBUG
    for p in featured_products:
        print("Featured product:", p.title)
    return render(request, 'ecommerce.html', {'data': featured_products})


# ---------------- Brand-specific Views ----------------
def brand_view(request, brand_name):
    products = Products.objects.filter(brand__title__icontains=brand_name).order_by('-id')
    return render(request, f'{brand_name.lower()}.html', {'products': products})

# ---------------- Category List View ----------------
def category_list_view(request):
    data = Category.objects.all().order_by('id')
    return render(request, 'category_list.html', {'data': data})

# ---------------- Search View ----------------
def search(request):
    query = request.GET.get("q", "")
    
    # Get products matching the search query
    products = Products.objects.filter(title__icontains=query)
    
    related_products = []
    if products.exists():
        first_product = products.first()
        product_ids = list(products.values_list('id', flat=True))
        
        # Get the brand name as a string instead of the Brand object
        brand_name = first_product.brand.name if hasattr(first_product.brand, 'name') else str(first_product.brand)
        
        # Check if search query is only a brand name (no model specified)
        is_brand_only_search = any(term.lower() in brand_name.lower() 
                                for term in query.lower().split() if len(term) > 2)
        other_terms_in_query = any(term.lower() not in brand_name.lower() 
                                  for term in query.lower().split() if len(term) > 2)
        
        if is_brand_only_search and not other_terms_in_query:
            # For brand-only searches, show products from OTHER brands
            related_products = Products.objects.exclude(
                brand=first_product.brand
            ).exclude(id__in=product_ids).order_by('?')[:3]
        else:
            # For specific product searches, show related products from SAME brand
            related_products = Products.objects.filter(
                brand=first_product.brand
            ).exclude(id__in=product_ids)[:3]
    
    # Add RAM and storage attributes to both product lists
    for product in list(products) + list(related_products):
        product.unique_rams = (
            ProductAttribute.objects.filter(product=product)
            .values_list("ram__id", "ram__ram").distinct()
        )
        product.unique_storages = (
            ProductAttribute.objects.filter(product=product)
            .values_list("storage__id", "storage__storage").distinct()
        )
    
    return render(
        request, 
        "search.html", 
        {"products": products, "related": related_products}
    )

# brands view
def brand_list(request):
    brands = Brands.objects.all()  
    return render( {'brands': brands})
# get price view

def get_price(request):
    # Get parameters from request
    product_id = request.GET.get("product_id")
    ram_id = request.GET.get("ram_id")
    storage_id = request.GET.get("storage_id")
    
    print(f"Product ID: {product_id}, RAM ID: {ram_id}, Storage ID: {storage_id}")
    
    if not product_id or not ram_id or not storage_id:
        return JsonResponse({"error": "Missing product_id, ram_id, or storage_id"}, status=400)
    
    try:
        product_id = int(product_id)
        ram_id = int(ram_id)
        storage_id = int(storage_id)
    except ValueError:
        return JsonResponse({"error": "Invalid product_id, ram_id, or storage_id. Must be integers."}, status=400)

    try:
        price_entry = ProductAttribute.objects.filter(
            product_id=product_id, ram_id=ram_id, storage_id=storage_id
        ).first()
        
        if price_entry:
            return JsonResponse({"price": price_entry.price})
        
        return JsonResponse({"error": "Price not available for these attributes"}, status=404)
    
    except ProductAttribute.DoesNotExist:
        return JsonResponse({"error": "No matching product attribute found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)





# Brands view

def brand_view(request, brand_name):
    products = Products.objects.filter(
        brand__title__icontains=brand_name,
        status=True  # ✅ Only include active products
    ).order_by('-id')

    for product in products:
        product.unique_rams = (
            ProductAttribute.objects.filter(product=product)
            .values_list("ram__id", "ram__ram").distinct()
        )
        product.unique_storages = (
            ProductAttribute.objects.filter(product=product)
            .values_list("storage__id", "storage__storage").distinct()
        )

    return render(request, f'{brand_name.lower()}.html', {'products': products})


# Individual Brand Views
def dell_view(request):
    return brand_view(request, "dell")

def hp_view(request):
    return brand_view(request, "hp")

def lenovo_view(request):
    return brand_view(request, "lenovo")

def microsoft_view(request):
    return brand_view(request, "microsoft")

def apple_view(request):
    return brand_view(request, "apple")

# ---------------- Product Detail View ----------------
def product_detail_view(request, id):
    product = get_object_or_404(Products, id=id)
    attributes = ProductAttribute.objects.filter(product=product)
    return render(request, 'product_detail.html', {'product': product, 'attributes': attributes})

# ---------------- Signup View ----------------
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ecommerce')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})















#----------------- Login Status View ----------------

def check_login_status(request):
    is_logged_in = request.user.is_authenticated
    return JsonResponse({'is_logged_in': is_logged_in})

# ---------------- Login View ----------------
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('ecommerce')
        messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# ---------------- Logout View ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('ecommerce')

# ---------------- Cart Views ----------------


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('attribute')
    return render(request, 'cart.html', {'cart_items': cart_items})


from fypapp.models import Cart 
from django.http import JsonResponse
from django.views.decorators.http import require_POST # Replace with your actual model import
@login_required



@require_POST
@login_required
def remove_from_cart(request, product_id, attribute_id):
    """
    Removes all cart items matching the given product_id and attribute_id.
    Handles cases where multiple items exist with the same identifiers.
    """
    if request.method == "POST":
        try:
            # Use filter() to get all matching items
            items = CartItem.objects.filter(
                user=request.user,
                product_id=product_id,
                attribute_id=attribute_id
            )
            
            # Check if any items were found
            if items.exists():
                # Get the count before deletion
                count = items.count()
                # Delete all matching items
                items.delete()
                
                # Get updated cart count
                cart_count = CartItem.objects.filter(user=request.user).count()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Item removed from cart.',
                    'cart_count': cart_count
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Item not found in cart'
                })
        except Exception as e:
            # Log the error for debugging
            import traceback
            print(f"Error removing from cart: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)






@login_required
def remove_all_from_cart(request, product_id, attribute_id):
    """
    Dedicated function to remove all instances of an item from the cart.
    """
    if request.method == "POST":
        try:
            # Use filter() instead of get_object_or_404()
            items = CartItem.objects.filter(
                user=request.user,
                product_id=product_id,
                attribute_id=attribute_id
            )
            
            if items.exists():
                count = items.count()
                items.delete()
                
                cart_count = CartItem.objects.filter(user=request.user).count()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Items removed from cart',
                    'cart_count': cart_count
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No matching items found in cart'
                })
        except Exception as e:
            import traceback
            print(f"Error in remove_all_from_cart: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)
    
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)

def add_to_cart(request):
    if request.method == "POST":
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                product_id = data.get('product_id')
                ram_id = data.get('ram_id')
                storage_id = data.get('storage_id')
            else:
                product_id = request.POST.get('product_id')
                ram_id = request.POST.get('ram_id')
                storage_id = request.POST.get('storage_id')

            if not product_id or not ram_id or not storage_id:
                return JsonResponse({"success": False, "message": "Product, RAM, and Storage are required."}, status=400)

            product = get_object_or_404(Products, id=product_id)
            attribute = get_object_or_404(ProductAttribute, product=product, ram_id=ram_id, storage_id=storage_id)

            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                attribute=attribute
            )

            cart_count = CartItem.objects.filter(user=request.user).count()

            return JsonResponse({
                "success": True,
                "message": "Added to cart!",
                "cart_count": cart_count
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

@login_required
def remove_from_cart(request, product_id, attribute_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id, attribute_id=attribute_id)
        cart_item.delete()

        updated_cart_count = CartItem.objects.filter(user=request.user).count()

        return JsonResponse({"success": True, "message": "Item removed from cart.", "cart_count": updated_cart_count})

    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    cart_data = [
        {
            "product_id": item.product.id,
            "product": item.product.title,
            "ram": item.attribute.ram.ram,
            "storage": item.attribute.storage.storage,
            "price": item.attribute.price,
            "attribute_id": item.attribute.id
        }
        for item in cart_items
    ]

    return JsonResponse({"cart_items": cart_data})


# ---------------- Cart Count View ----------------
from django.http import JsonResponse
from .models import CartItem

def cart_count(request):
    print("🔍 Cart Count View Called")
    print(f"User Authenticated: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
        print(f"🛒 Cart Count: {count}")
        print(f"🔢 Returning JSON: {{'count': {count}}}")
        return JsonResponse({'count': count})
    else:
        print("👤 User not authenticated, returning 0")
        return JsonResponse({'count': 0})

# ---------------- wishlist view ----------------
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import WishlistItem, Products, ProductAttribute



def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        items_data = []
        for item in wishlist_items:
            items_data.append({
                'product': item.product.name,
                'product_id': item.product.id,
                'ram': str(item.ram) if item.ram else "No RAM",
                'storage': str(item.storage) if item.storage else "No Storage",
                'ram_id': item.ram.id if item.ram else "",
                'storage_id': item.storage.id if item.storage else "",
            })
        return JsonResponse({'wishlist_items': items_data})
    
    
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('attribute')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


@login_required
@csrf_exempt
def add_to_wishlist(request):
    if request.method == "POST":
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                product_id = data.get('product_id')
                ram_id = data.get('ram_id')
                storage_id = data.get('storage_id')
            else:
                product_id = request.POST.get('product_id')
                ram_id = request.POST.get('ram_id')
                storage_id = request.POST.get('storage_id')

            if not product_id:
                return JsonResponse({"success": False, "message": "Product ID is required."}, status=400)

            product = get_object_or_404(Products, id=product_id)

            # Get product attribute if both ram and storage are provided
            attribute = None
            if ram_id and storage_id:
                try:
                    attribute = ProductAttribute.objects.get(
                        product=product,
                        ram_id=ram_id,
                        storage_id=storage_id
                    )
                except ProductAttribute.DoesNotExist:
                    return JsonResponse({"success": False, "message": "Invalid product variant."}, status=400)

            # Create or get wishlist item
            wishlist_item, created = WishlistItem.objects.get_or_create(
                user=request.user,
                product=product,
                attribute=attribute
            )

            wishlist_count = WishlistItem.objects.filter(user=request.user).count()

            return JsonResponse({
                "success": True,
                "message": "Added to wishlist!" if created else "Already in wishlist.",
                "wishlist_count": wishlist_count
            }, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({"success": False, "message": f"Invalid JSON format: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)




@login_required
def wishlist_count(request):
    count = WishlistItem.objects.filter(user=request.user).count()
    return JsonResponse({"count": count})


@login_required
def view_wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)

    wishlist_data = [
        {
            "product_id": item.product.id,
            "product": item.product.title,
            "ram": item.attribute.ram.ram if item.attribute and hasattr(item.attribute, 'ram') else "No RAM",
            "storage": item.attribute.storage.storage if item.attribute and hasattr(item.attribute, 'storage') else "No Storage",
            "attribute_id": item.attribute.id if item.attribute else None
        }
        for item in wishlist_items
    ]

    return JsonResponse({"wishlist_items": wishlist_data})


@login_required
def remove_from_wishlist(request, wishlist_id):
    if request.method == "POST":
        wishlist_item = get_object_or_404(WishlistItem, id=wishlist_id, user=request.user)
        wishlist_item.delete()
        return JsonResponse({"message": "Removed from wishlist", "status": "success"})

    return JsonResponse({"message": "Invalid request"}, status=400)


@login_required
def get_wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user).select_related("product", "ram", "storage", "attribute")

        data = []
        for item in wishlist_items:
            print(f"DEBUG: Product: {item.product.name}, RAM: {item.ram}, Storage: {item.storage}")

            data.append({
                "product_id": item.product.id,
                "product": item.product.name,
                "ram": item.ram.name if item.ram else None,
                "storage": item.storage.name if item.storage else None,
                "attribute_id": item.attribute.id if item.attribute else None
            })

        return JsonResponse({"wishlist_items": data})

    return JsonResponse({"error": "User not authenticated"}, status=401)

    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user).select_related("product", "ram", "storage")


        data = []
        for item in wishlist_items:
            print(f"DEBUG: Product: {item.product.name}, RAM: {item.ram}, Storage: {item.storage}")  # Debugging

            data.append({
                "product_id": item.product.id,
                "product": item.product.name,
                "ram": item.ram.name if item.ram else None,  # Fix: Don't return "No RAM"
                "storage": item.storage.name if item.storage else None,  # Fix: Don't return "No Storage"
                "attribute_id": item.attribute.id if item.attribute else None
            })
        
        return JsonResponse({"wishlist_items": data})

    return JsonResponse({"error": "User not authenticated"}, status=401)


# ---------------- Checkout View ----------------
import stripe
import requests
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import CartItem  # Update this import based on your actual model location

stripe.api_key = settings.STRIPE_SECRET_KEY

# Google Sheets Webhook URL
GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxgI-iUnMO9XqbuNTPB0OoE1IzYi1o0Aw20akbvvz0tLGmtS75q7EYBwO9L7ElGFzwE/exec"


def send_to_google_sheet(data):
    """
    Sends the user data to Google Sheets through a webhook.
    """
    try:
        response = requests.post(
            GOOGLE_SHEET_WEBHOOK_URL,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )
        # Return whether the request was successful
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send data to Google Sheet: {e}")
        return False

@login_required
def checkout_view(request):
    """
    Handle the checkout view where users are redirected to Stripe for payment and 
    their order details are sent to Google Sheets.
    """
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Please add items to proceed.")
        return redirect("view_cart")

    total_price = sum(item.attribute.price for item in cart_items if item.attribute)
    shipping_cost = 2000
    final_total = int((total_price + shipping_cost) * 100)  # Convert to paisa

    if request.method == 'POST':
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        pno = request.POST.get("pno")
        address = request.POST.get("address")

        # Send data to Google Sheets
        if send_to_google_sheet({
            "fname": fname,
            "lname": lname,
            "email": email,
            "pno": pno,
            "address": address
        }):
            print("Data sent successfully to Google Sheets.")
        else:
            messages.error(request, "Failed to send your details to Google Sheets.")
        
        # Proceed to Stripe
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {
                        'name': 'Cart Payment',
                    },
                    'unit_amount': final_total,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/payment-success/',
            cancel_url=YOUR_DOMAIN + '/checkout/',
            metadata={
                'user_id': request.user.id,
            }
        )
        return redirect(checkout_session.url, code=303)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "shipping_cost": shipping_cost,
        "final_total": final_total / 100,
    })

@csrf_exempt
def create_checkout_session(request):
    """
    Creates a Stripe checkout session for payments and redirects the user.
    """
    YOUR_DOMAIN = 'http://127.0.0.1:8000'
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'pkr',
                'product_data': {
                    'name': 'Cart Payment',
                },
                'unit_amount': 50000,  # Example price (in paisa)
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/payment-success/',
        cancel_url=YOUR_DOMAIN + '/checkout/',
    )
    return redirect(checkout_session.url, code=303)

# move to cart view
from django.shortcuts import get_object_or_404, redirect
from fypapp.models import WishlistItem, CartItem

def move_to_cart(request, wishlist_id):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_id)

    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, 
        product=wishlist_item.product,
        attribute=wishlist_item.attribute  # Ensure attribute is included
    )

    # If item was newly created, save it
    if created:
        cart_item.save()

    # Remove from wishlist after moving to cart
    wishlist_item.delete()

    return redirect('wishlist')  # Redirect back to the wishlist page

# ------------- payment succesful view --------

def payment_success(request):
    return render(request, "payment_success.html")




# ------------- move to cart -------------
from django.shortcuts import redirect
from .models import WishlistItem, CartItem

def move_all_to_cart(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)

    for item in wishlist_items:
        CartItem.objects.create(user=request.user, product=item.product, attribute=item.attribute)

    wishlist_items.delete()  # Clear wishlist after moving items to cart
    return redirect('cart')  # Redirect to cart page

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import WishlistItem, CartItem

def move_to_cart(request, wishlist_id):
    wishlist_item = WishlistItem.objects.filter(id=wishlist_id, user=request.user).first()

    if not wishlist_item:
        messages.error(request, "Wishlist item not found or does not belong to you.")
        return redirect('ecommerce')  # Redirect back to wishlist page

    # Move the item to the cart
    CartItem.objects.create(user=request.user, product=wishlist_item.product, attribute=wishlist_item.attribute)

    # Delete the wishlist item
    wishlist_item.delete()

    messages.success(request, "Item successfully moved to cart!")
    return redirect('wishlist')





