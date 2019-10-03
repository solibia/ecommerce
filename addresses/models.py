# Create your models here.
from django.db import models
from django.urls import reverse
from billing.models import BillingProfile
#from django.conf import settings

ADDRESS_TYPES = (
    ('billing', 'Billing address'),
    ('shipping', 'Shipping address'),
)

class Address(models.Model):
    #billing_profile = models.ForeignKey(BillingProfile)
    #billing_profile = models.ForeignKey(to='BillingProfile.User'.related_name='outras_coisas', null=True)
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    #billing_profile = models.OneToOneField(BillingProfile, null=True, blank=True,  on_delete=models.CASCADE)
    #billing_profile = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=('BillingProfile'), on_delete=models.CASCADE,)
    name            = models.CharField(max_length=120, null=True, blank=True, help_text='Shipping to? Who is it for?')
    nickname        = models.CharField(max_length=120, null=True, blank=True, help_text='Internal Reference Nickname')
    address_type    = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    address_line_1  = models.CharField(max_length=120)
    address_line_2  = models.CharField(max_length=120, null=True, blank=True)
    city            = models.CharField(max_length=120)
    country         = models.CharField(max_length=120, default='VIETNAM')
    state           = models.CharField(max_length=120)
    postal_code     = models.CharField(max_length=120)

    #class Meta:
    #    abstract = True
    
    def __str__(self):
        if self.nickname:
            return str(self.nickname)
        return str(self.address_line_1)

    def get_absolute_url(self):
        return reverse("address-update", kwargs={"pk": self.pk})

    def get_short_address(self):
        for_name = self.name 
        if self.nickname:
            for_name = "{} | {},".format( self.nickname, for_name)
        return "{for_name} {line1}, {city}".format(
                for_name = for_name or "",
                line1 = self.address_line_1,
                city = self.city
            ) 

    def get_address(self):
        return "{for_name}\n{line1}\n{line2}\n{city}\n{state}, {postal}\n{country}".format(
                for_name = self.name or "",
                line1 = self.address_line_1,
                line2 = self.address_line_2 or "",
                city = self.city,
                state = self.state,
                postal= self.postal_code,
                country = self.country
            )