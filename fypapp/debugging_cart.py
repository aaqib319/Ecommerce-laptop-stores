# Add this to your Django app to help debug the issue
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CartItem  # Update this import if your model is different

@login_required
@require_POST
def debug_cart_removal(request, product_id, attribute_id):
    """
    Debug function to examine exactly what's happening during cart item removal.
    """
    debug_info = []
    debug_info.append(f"User: {request.user.username}")
    debug_info.append(f"Product ID: {product_id}")
    debug_info.append(f"Attribute ID: {attribute_id}")
    
    try:
        # First, check if any items match our criteria
        matching_items = CartItem.objects.filter(
            user=request.user,
            product_id=product_id,
            attribute_id=attribute_id
        )
        
        debug_info.append(f"Found {matching_items.count()} matching item(s):")
        
        # List all matching items
        for i, item in enumerate(matching_items):
            debug_info.append(f"Item {i+1}: ID={item.id}, Product={item.product}, Attribute={item.attribute}")
        
        # Try to delete them
        matching_items.delete()
        debug_info.append("Items deleted successfully")
        
    except Exception as e:
        import traceback
        debug_info.append(f"ERROR: {str(e)}")
        debug_info.append(traceback.format_exc())
    
    # Return all debug info as plain text
    return HttpResponse("<br>".join(debug_info), content_type="text/plain")