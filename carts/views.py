# Create your views here.
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect


from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressCheckoutForm
from addresses.models import Address

from billing.models import BillingProfile
from orders.models import Order
from products.models import Product
from .models import Cart, CartProductsQte


import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_cu1lQmcg1OLffhLvYrSCp5XE")
STRIPE_PUB_KEY =  getattr(settings, "STRIPE_PUB_KEY", 'pk_test_PrV61avxnHaWIYZEeiYTTVMZ')
stripe.api_key = STRIPE_SECRET_KEY



def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
            "id": x.id,
            "url": x.get_absolute_url(),
            "name": x.name, 
            "price": x.price
            } 
            for x in cart_obj.products.all()]
    cart_data  = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    print("request user")
    print(request.user)
    cartproductsqtes = []
    cart_obj, new_obj = Cart.objects.new_or_get(request) 
    
    if Order.objects.filter(cart=cart_obj).count()>0:
        print('In orderrrrrrrrr')
        return render(request, "carts/home.html", {"cart_products": cartproductsqtes, "cart": 0})
    
    print('cart_obj')
    print(cart_obj)
    for un_product in cart_obj.products.all():
        #print('avant')
        #print(CartProductsQte.objects.get(cart=cart_obj, product=un_product).first())
        #print(un_product.cartproductsqte_set.get(cart=cart_obj))
        cartproductsqtes.append(CartProductsQte(product=un_product, cart=cart_obj,qte=un_product.cartproductsqte_set.get(cart=cart_obj)).qte)
        #print('apres')
    #print((cart_obj.products.all().first().cartproductsqte_set.get(cart=cart_obj)).qte)
    #(cart_obj.products.all().first().cartproductsqte_set.get(cart=cart_obj)).qte 
    return render(request, "carts/home.html", {"cart_products": cartproductsqtes, "cart": cart_obj})


def cart_update(request):
    if request.user.is_authenticated:
        print("Authentifieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        product_id = request.POST.get('product_id')
        qte = request.POST.get('qte')
        #print('quantité = ')
        #print(qte)
        if product_id is not None:
            try:
                product_obj = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                print("Show message to user, product is gone?")
                return redirect("cart:home")
            cart_obj, new_obj = Cart.objects.new_or_get(request)
            print(product_obj)
            print(cart_obj.products)
            print(new_obj)
            if product_obj in cart_obj.products.all() and qte=='0':
                print('dans delete producttttttttttttt')
                p = Product.objects.get_by_id(id=product_obj.id)
                cartProductsQte = CartProductsQte.objects.get(cart=cart_obj, product=product_obj)
                print("qte a supprimer = ")
                print(cartProductsQte.qte)
                p.qte = p.qte+cartProductsQte.qte
                p.save()
                cart_obj.products.remove(product_obj)
                added = False
                print('Ok delete')    

            elif product_obj in cart_obj.products.all() and int(qte)>0:
                print('dans update qte producttttttttttttt')
                print(request.POST.get('product_id'))
                print(request.POST.get('qte'))
                #return 0
                p = Product.objects.get_by_id(id=product_obj.id)
                cartProductsQte = CartProductsQte.objects.get(cart=cart_obj, product=product_obj)
                #oldqte_cartProductsQte = cartProductsQte.qte
                #oldqte_total = cartProductsQte.qte + p.qte
                p.qte = p.qte + cartProductsQte.qte - int(qte) #  p.qte+cartProductsQte.qte
                cartProductsQte.qte = qte

                cartProductsQte.save()
                p.save()      
                
                products = cart_obj.products.all()
                total = 0
                for x in products:
                    cartProductsQte = CartProductsQte.objects.get(cart=cart_obj, product=x)
                    print('affichage de cartProductsQte.qte')
                    print(cartProductsQte.qte)
                    total += x.price * cartProductsQte.qte
                    print('In m2m_changed_cart_receiver')
                    print(cartProductsQte.qte)
                    print(total)
                if cart_obj.subtotal != total:
                    cart_obj.subtotal = total
                    cart_obj.save()
                          
                #cart_obj.products.remove(product_obj)
                added = False
                print('Ok update')                 #cart_obj.products.remove(product_obj)
                added = False
                print("update ok")
                
            else:
                cart_obj.products.add(product_obj, through_defaults={'qte': qte}) # cart_obj.products.add(product_id)
                p = Product.objects.get_by_id(id=product_obj.id)
                print('qte1 = ')
                print(p.qte)
                print('qte2 = ')
                print(qte)
                p.qte = p.qte-int(qte)
                p.save()
                added = True
            request.session['cart_items'] = cart_obj.products.count()
            # return redirect(product_obj.get_absolute_url())
            if request.is_ajax(): # Asynchronous JavaScript And XML / JSON
                print("Ajax request")
                json_data = {
                    "added": added,
                    "removed": not added,
                    "cartItemCount": cart_obj.products.count()
                }
                return JsonResponse(json_data, status=200) # HttpResponse
                # return JsonResponse({"message": "Error 400"}, status=400) # Django Rest Framework
        else:
            print("Produit nooooooooooooooooooooooooooooooooooooone")
        return redirect("cart:home")

    else:
        print("Nonnnnnnnnnnnn Authentifieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        redirect("/login")


def checkout_home(request):
    print("checkout_homeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")    
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")  
    
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    billing_address_id = request.session.get("billing_address_id", None)

    shipping_address_required = not cart_obj.is_digital


    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    print(billing_profile)
    print(billing_profile_created)
    if billing_profile is not None:
        print("billing_profile is not nonnneeeeeeeeeeeeee")    
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
            print('ok1')
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            print('ok2')
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id) 
            print('ok3')
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()
            print('ok4')
        has_card = billing_profile.has_card

    if request.method == "POST":
        "check that order is done"
        print('postttttttttttttt')
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid() # sort a signal for us
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    '''
                    is this the best spot?
                    '''
                    billing_profile.set_cards_inactive()
                    print('successssssssssssssssss')
                return redirect("cart:success")
            else:
                print("error did charge")
                print(crg_msg)
                return redirect("cart:checkout")
    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
        "shipping_address_required": shipping_address_required,
    }
    return render(request, "carts/checkout.html", context)







def checkout_done_view(request):
    return render(request, "carts/checkout-done.html", {})





