# Create your models here.
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed

from products.models import Product
#from orders.models import Order


User = settings.AUTH_USER_MODEL

class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        #elif Order.objects.filter(cart=self.get_queryset().filter(user=request.user)).count()>0:
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

class Cart(models.Model):
    #user        = models.ForeignKey(User, null=True, blank=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE,)    
    #products    = models.ManyToManyField(Product, blank=True)
    products    = models.ManyToManyField(Product, through='CartProductsQte')
    subtotal    = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    total       = models.DecimalField(default=0.00, max_digits=65, decimal_places=2)
    updated     = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def is_digital(self):
        qs = self.products.all() #every product
        new_qs = qs.filter(is_digital=False) # every product that is not digial
        if new_qs.exists():
            return False
        return True



class CartProductsQteQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)


class CartProductsQteManager(models.Manager):
    def get_queryset(self):
        return CartProductsQteQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

#    def featured(self): #Product.objects.featured() 
#        return self.get_queryset().featured()
    def new(self, product, cart, qte):
        print('in new')
        return self.model.objects.create(product=product, cart=cart, qte='1')



class CartProductsQte(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,)
    cart    = models.ForeignKey(Cart, on_delete=models.CASCADE,)
    qte     = models.IntegerField(default='0')

    objects = CartProductsQteManager()

    def get_queryset(self):
        return CartProductsQteQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

#    def featured(self): #Product.objects.featured() 
#        return self.get_queryset().featured()


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        #print('affichage de instance')
        #print(instance)
        products = instance.products.all()
        total = 0
        for x in products:
            cartProductsQte = CartProductsQte.objects.get(cart=instance, product=x)
            print('affichage de cartProductsQte.qte')
            print(cartProductsQte.qte)
            total += x.price * cartProductsQte.qte
            print('In m2m_changed_cart_receiver')
            print(cartProductsQte.qte)
            print(total)
        if instance.subtotal != total:
            instance.subtotal = total
            instance.save()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.products.through)




def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = Decimal(instance.subtotal) * Decimal(1.08) # 8% tax
    else:
        instance.total = 0.00

pre_save.connect(pre_save_cart_receiver, sender=Cart)












