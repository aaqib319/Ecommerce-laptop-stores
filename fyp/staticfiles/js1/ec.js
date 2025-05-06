// Initial setup - no DOM manipulation yet
console.log("JavaScript file loaded!");

// Function to initialize everything once the page is fully loaded
function initializeApp() {
    console.log("Page fully loaded, including all stylesheets!");

    // Wishlist and Cart Toggle Functionality
    const wishlist = document.getElementById("wishlist");
    const cart = document.getElementById("cart");

    if (wishlist && cart) {
        wishlist.addEventListener("change", function () {
            if (this.checked) cart.checked = false;
        });

        cart.addEventListener("change", function () {
            if (this.checked) wishlist.checked = false;
        });
    } else {
        console.log("Wishlist or Cart checkbox not found - this might be expected on some pages");
    }

    // Handle Product Cards - RAM and Storage selection
    document.querySelectorAll(".product-card").forEach(function (card) {
        // Get product ID from the card's data attribute
        let productId = card.dataset.productId;
        
        // Find elements within this specific card
        let ramSelect = card.querySelector(".ram-select");
        let storageSelect = card.querySelector(".storage-select");
        let priceElement = card.querySelector(".product-price");
        
        // Skip if any required elements are missing
        if (!ramSelect || !storageSelect || !priceElement) {
            console.log(`Product ID ${productId}: Missing elements (this might be expected for some products)`);
            return;
        }
        
        // Function to fetch and update price based on selected RAM and storage
        function updatePrice() {
            let ramId = ramSelect.value.trim();
            let storageId = storageSelect.value.trim();
            
            // Validate selections
            if (!ramId || !storageId) {
                priceElement.textContent = "Please select RAM & Storage";
                return;
            }
            
            console.log(`Fetching price for Product ID: ${productId}, RAM: ${ramId}, Storage: ${storageId}`);
            
            // Fetch price from server
            fetch(`/get_price/?product_id=${productId}&ram_id=${ramId}&storage_id=${storageId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        console.error(`Error from server: ${data.error}`);
                        priceElement.textContent = "Price not available";
                    } else {
                        priceElement.textContent = `RS. ${data.price}/-`;
                        console.log(`Updated price for Product ID ${productId}: RS. ${data.price}/-`);
                    }
                })
                .catch(error => {
                    console.error(`Fetch error for Product ID ${productId}:`, error);
                    priceElement.textContent = "Price not available for this spec";
                });
        }
        
        // Add event listeners to dropdowns
        ramSelect.addEventListener("change", updatePrice);
        storageSelect.addEventListener("change", updatePrice);
        
        // Update price on initial load
        updatePrice();
    });
    
    // Handle RAM buttons (if they exist)
    const ramButtons = document.querySelectorAll(".ram-btn");
    
    if (ramButtons.length > 0) {
        ramButtons.forEach(button => {
            button.addEventListener("click", function () {
                let price = this.getAttribute("data-price");
                let productId = this.getAttribute("data-product-id");
                let productCard = document.querySelector(`.product-card[data-product-id="${productId}"]`);
                
                console.log(`RAM button clicked for Product ID: ${productId}, New Price: ${price}`);
                
                // Try to find price element using multiple selector strategies
                let priceElement = null;
                
                // Strategy 1: Check for id="price-X"
                priceElement = document.getElementById(`price-${productId}`);
                
                // Strategy 2: Check within the product card for class .product-price
                if (!priceElement && productCard) {
                    priceElement = productCard.querySelector(".product-price");
                }
                
                // Update price if element found
                if (priceElement) {
                    priceElement.textContent = `RS. ${price}/-`;
                    console.log(`Updated price element for Product ID: ${productId}`);
                } else {
                    console.log(`Could not find price element for Product ID: ${productId}. This is expected if product not on current page.`);
                }
            });
        });
    }
}

// Use window.addEventListener('load') instead of DOMContentLoaded
// This ensures all stylesheets are fully loaded before any layout calculations
window.addEventListener('load', initializeApp);

// For some essential UI behaviors that don't require layout calculations,
// we can still use DOMContentLoaded for better responsiveness
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded (but stylesheets might still be loading)");
    // You could put minimal UI setup here that doesn't require final layout
    // For example, setting up event listeners for navigation toggles
});





document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 E-commerce Script Loaded!");

    // Common Utility Functions
    // ========================
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
               document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
    }

    function showNotification(message, isSuccess = true) {
        // You can implement a more sophisticated notification system here
        if (isSuccess) {
            alert(`✅ ${message}`);
        } else {
            alert(`⚠️ ${message}`);
        }
    }

    // Cart Functions
    // =============
    function updateCartCount() {
        fetch("/cart-count/")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("🛒 Cart count received:", data.count);
                document.getElementById("cart-count").innerText = data.count;
            })
            .catch(error => console.error("❌ Error fetching cart count:", error));
    }

    function setupAddToCartButtons() {
        // Handle both forms and direct buttons
        document.querySelectorAll(".add-to-cart-form").forEach(form => {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                let formData = new FormData(this);

                fetch(this.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        updateCartCount();
                        loadCartItems();
                        showNotification("Product added to cart!");
                    } else {
                        showNotification(data.message || "Failed to add product to cart", false);
                    }
                })
                .catch(error => {
                    console.error("❌ Error adding to cart:", error);
                    showNotification("Failed to add product to cart. Please try again.", false);
                });
            });
        });

        document.querySelectorAll(".add-to-cart").forEach(button => {
            button.addEventListener("click", function (e) {
                if (this.closest(".add-to-cart-form")) {
                    // Skip if this is inside a form (already handled above)
                    return;
                }
                e.preventDefault();
                
                let productCard = this.closest(".product-card");
                let productId = this.dataset.productId || (productCard && productCard.getAttribute("data-product-id"));
                let ramId = this.dataset.ramId || (productCard && productCard.querySelector(".ram-select")?.value);
                let storageId = this.dataset.storageId || (productCard && productCard.querySelector(".storage-select")?.value);
                
                this.disabled = true;

                console.log("🛒 Adding to cart:", { productId, ramId, storageId });

                fetch('/add-to-cart/', {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken()
                    },
                    body: JSON.stringify({
                        'product_id': productId,
                        'ram_id': ramId,
                        'storage_id': storageId
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Cart response:", data);
                    updateCartCount();
                    loadCartItems();
                    showNotification("Product added to cart!");
                })
                .catch(error => {
                    console.error("❌ Error adding to cart:", error);
                    showNotification("Failed to add product to cart. Please try again.", false);
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    }

    // REMOVE FROM CART FUNCTION - With duplicate item handling
// REMOVE FROM CART FUNCTION - Simplified to use one endpoint
function setupRemoveFromCartButtons() {
    document.querySelectorAll(".remove-from-cart").forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            let productId = this.dataset.productId;
            let attributeId = this.dataset.attributeId;
            let csrfToken = getCsrfToken();
            
            console.log(`🗑️ Removing product: ${productId}, attribute: ${attributeId}`);
            this.disabled = true;
            
            fetch(`/cart/remove-all/${productId}/${attributeId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) {
                    // Improved error handling
                    if (response.status === 500) {
                        console.error(`Server error (500) when removing item. This might be because of duplicate items.`);
                        // Force reload the cart instead of showing an error
                        loadCartItems();
                        return { success: true, message: "Cart refreshed. Please try again." };
                    }
                    return response.text().then(text => {
                        console.error("Server error response:", text.substring(0, 200));
                        throw new Error(`Server returned ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Remove response:", data);
                if (data.success) {
                    updateCartCount();
                    
                    // Remove just this row from the table without reloading everything
                    const row = this.closest("tr");
                    if (row) {
                        row.remove();
                    } else {
                        loadCartItems(); // Fall back to reloading all items
                    }
                    
                    showNotification("Item removed from cart!");
                } else {
                    showNotification(data.message || "Error removing item from cart", false);
                }
            })
            .catch(error => {
                console.error("❌ Error removing from cart:", error);
                showNotification("An error occurred. Refreshing cart...", false);
                loadCartItems(); // Always reload cart on error
            })
            .finally(() => {
                this.disabled = false;
            });
        });
    });
}





    function loadCartItems() {
        fetch("/cart/", {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            // Check if response is JSON
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json();
            } else {
                throw new Error("Expected JSON response but got HTML or other content type");
            }
        })
        .then(data => {
            console.log("🛒 Cart data received:", data);
            let cartTableBody = document.querySelector(".cart-table tbody");
            if (!cartTableBody) {
                console.log("Cart table not found on this page");
                return;
            }
            
            cartTableBody.innerHTML = ""; // Clear existing cart items

            if (data.cart_items && data.cart_items.length > 0) {
                data.cart_items.forEach(item => {
                    cartTableBody.innerHTML += `
                        <tr>
                            <td>${item.product}</td>
                            <td>${item.ram || 'N/A'}</td>
                            <td>${item.storage || 'N/A'}</td>
                            <td>RS. ${item.price}/-</td>
                            <td>
                                <button class="remove-from-cart" data-product-id="${item.product_id}" data-attribute-id="${item.attribute_id}">
                                    <i class="fa-solid fa-trash"></i>
                                </button>
                            </td>
                        </tr>`;
                });
            } else {
                cartTableBody.innerHTML = `<tr><td colspan="5">Your cart is empty.</td></tr>`;
            }

            setupRemoveFromCartButtons(); // Reattach event listeners to new remove buttons
        })
        .catch(error => {
            console.error("❌ Error loading cart items:", error);
        });
    }

    // Product Price Updates
    // ====================
    function setupPriceUpdates() {
        document.querySelectorAll(".ram-select, .storage-select").forEach(select => {
            select.addEventListener("change", function () {
                let productCard = this.closest(".product-card");
                let productId = productCard.getAttribute("data-product-id");
                let selectedRam = productCard.querySelector(".ram-select").value;
                let selectedStorage = productCard.querySelector(".storage-select").value;

                console.log(`🔄 Selection changed - Product: ${productId}, RAM: ${selectedRam}, Storage: ${selectedStorage}`);

                fetch(`/update-price/?product_id=${productId}&ram_id=${selectedRam}&storage_id=${selectedStorage}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.price) {
                        productCard.querySelector(".product-price").textContent = `RS. ${data.price}/-`;
                        console.log(`✅ Updated price: RS. ${data.price}/-`);
                    }
                })
                .catch(error => {
                    console.error("❌ Error fetching price:", error);
                });
            });
        });
    }

    // Wishlist Functions
    // =================
    function updateWishlistCount() {
        fetch("/wishlist-count/")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("💖 Wishlist count received:", data.count);
                let wishlistCountElement = document.getElementById("wishlist-count");
                if (wishlistCountElement) {
                    wishlistCountElement.innerText = data.count;
                }
            })
            .catch(error => console.error("❌ Error fetching wishlist count:", error));
    }

    function setupAddToWishlistButtons() {
        document.querySelectorAll(".add-to-wishlist").forEach(button => {
            button.addEventListener("click", function () {
                let productId = this.dataset.productId;
                let ramId = this.dataset.ramId;
                let storageId = this.dataset.storageId;
                let wishlistButton = this;
                
                console.log("💖 Adding to wishlist, product_id:", productId);
                
                if (!productId) {
                    console.error("❌ Error: Missing product ID");
                    return;
                }
                
                wishlistButton.disabled = true;
                
                let requestData = { product_id: productId };
                if (ramId) requestData.ram_id = ramId;
                if (storageId) requestData.storage_id = storageId;
                
                fetch("/add-to-wishlist/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify(requestData),
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            console.error("Server error response:", text.substring(0, 200));
                            throw new Error(`Server error: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Wishlist response:", data);
                    
                    if (data.success) {
                        updateWishlistCount();
                        loadWishlistItems();
                        showNotification("Product added to wishlist!");
                    } else {
                        showNotification(data.message || "Failed to add to wishlist", false);
                    }
                })
                .catch(error => {
                    console.error("❌ Error adding to wishlist:", error);
                    showNotification("Failed to add to wishlist. Please try again.", false);
                })
                .finally(() => {
                    wishlistButton.disabled = false;
                });
            });
        });
    }

    function setupRemoveFromWishlistButtons() {
        document.querySelectorAll(".remove-from-wishlist, .remove-wishlist").forEach(button => {
            button.addEventListener("click", function (e) {
                e.preventDefault();
                
                // Support both data-id and data-product-id formats
                const wishlistId = this.dataset.id || this.dataset.productId;
                
                if (!wishlistId) {
                    console.error("❌ Error: Missing wishlist/product ID");
                    return;
                }
                
                this.disabled = true;
                
                const endpoint = this.dataset.id ? 
                    `/wishlist/remove/${wishlistId}/` : 
                    `/wishlist/remove-product/${wishlistId}/`;
                
                fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCsrfToken(),
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({})
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Remove from wishlist response:", data);
                    
                    if (data.success || data.status === "success") {
                        // Remove item from UI directly if on wishlist page
                        let container = this.closest(".wishlist-item");
                        if (container) {
                            container.remove();
                        }
                        
                        updateWishlistCount();
                        loadWishlistItems();
                        showNotification("Item removed from wishlist!");
                    } else {
                        showNotification(data.message || "Failed to remove from wishlist", false);
                    }
                })
                .catch(error => {
                    console.error("❌ Error removing from wishlist:", error);
                    showNotification("Failed to remove from wishlist. Please try again.", false);
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    }

    function loadWishlistItems() {
        // Only try to load wishlist items if we're on a page with a wishlist container
        const wishlistContainer = document.querySelector(".wishlist-items");
        if (!wishlistContainer) {
            return;
        }
        
        fetch("/wishlist/", {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("💖 Wishlist data received:", data);
            wishlistContainer.innerHTML = ""; // Clear existing wishlist items

            if (data.wishlist_items && data.wishlist_items.length > 0) {
                data.wishlist_items.forEach(item => {
                    let ramText = item.ram && item.ram !== "No RAM" ? `RAM: ${item.ram}` : "";
                    let storageText = item.storage && item.storage !== "No Storage" ? `Storage: ${item.storage}` : "";

                    wishlistContainer.innerHTML += `
                        <div class="wishlist-item">
                            <span>${item.product}</span> 
                            <span>${ramText} ${storageText}</span>
                            <div class="wishlist-buttons">
                                <button class="move-to-cart" data-product-id="${item.product_id}" 
                                        data-ram-id="${item.ram_id || ''}" data-storage-id="${item.storage_id || ''}">
                                    🛒 Add to Cart
                                </button>
                                <button class="remove-from-wishlist" data-product-id="${item.product_id}">
                                    ❌ Remove
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                // Setup move to cart buttons
                setupMoveToCartButtons();
            } else {
                wishlistContainer.innerHTML = `<p>Your wishlist is empty.</p>`;
            }

            setupRemoveFromWishlistButtons();
        })
        .catch(error => {
            console.error("❌ Error loading wishlist items:", error);
        });
    }

    function setupMoveToCartButtons() {
        document.querySelectorAll(".move-to-cart").forEach(button => {
            button.addEventListener("click", function() {
                const productId = this.dataset.productId;
                const ramId = this.dataset.ramId || "1"; // Default values if not specified
                const storageId = this.dataset.storageId || "1"; // Default values if not specified
                
                this.disabled = true;
                
                // First add to cart
                fetch('/add-to-cart/', {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken()
                    },
                    body: JSON.stringify({
                        'product_id': productId,
                        'ram_id': ramId,
                        'storage_id': storageId
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Added to cart from wishlist:", data);
                    updateCartCount();
                    
                    // Then remove from wishlist
                    return fetch(`/wishlist/remove-product/${productId}/`, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCsrfToken(),
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({})
                    });
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("✅ Removed from wishlist:", data);
                    updateWishlistCount();
                    loadWishlistItems();
                    showNotification("Item moved from wishlist to cart!");
                })
                .catch(error => {
                    console.error("❌ Error moving item to cart:", error);
                    showNotification("Failed to move item to cart. Please try again.", false);
                })
                .finally(() => {
                    this.disabled = false;
                });
            });
        });
    }

    // Initialize Everything
    // ====================
    function init() {
        console.log("🔍 Initializing e-commerce functionality...");
        
        // Cart functionality
        updateCartCount();
        setupAddToCartButtons();
        loadCartItems();
        
        // Product price updates
        setupPriceUpdates();
        
        // Wishlist functionality
        updateWishlistCount();
        setupAddToWishlistButtons();
        setupRemoveFromWishlistButtons();
        loadWishlistItems();
        
        console.log("✅ Initialization complete!");
    }

    // Start everything
    init();
});


// attaching google sheet
