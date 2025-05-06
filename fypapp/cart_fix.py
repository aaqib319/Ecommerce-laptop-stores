# cart_fix.py - Place this in your Django app directory
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CartItem  # Update this import if your model is different

@login_required
@require_POST
def remove_all_from_cart(request, product_id, attribute_id):
    """
    Removes ALL cart items matching the given product_id and attribute_id.
    This function is specifically designed to handle the case where multiple items exist.
    """
    try:
        # Get all matching cart items (could be multiple)
        items = CartItem.objects.filter(
            user=request.user,
            product_id=product_id,
            attribute_id=attribute_id
        )
        
        # Check if any items were found
        if items.exists():
            # Get the count before deletion for the message
            count = items.count()
            # Delete all matching items at once
            items.delete()
            
            # Get updated cart count
            cart_count = CartItem.objects.filter(user=request.user).count()
            
            return JsonResponse({
                'success': True,
                'message': f'{count} item(s) removed from cart',
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