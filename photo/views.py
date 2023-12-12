from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from validators import email

import stripe

from .models import Images, Sale

# Create your views here.
def index(request):
    return render(request, "photo/index.html", {
        "images": Images.objects.all()
    })

def photo_buy(request, buy):
    img = Images.objects.get(heading=buy)
    return render(request, "photo/buy.html", {
        "image": img
    })

def purchase(request):
    if request.method != "POST":
        return HttpResponse("request must be post")
    
    form = request.POST

    if not email(form['email']):
        return HttpResponse('bad email', status=469)

    img = Images.objects.get(heading=form["image"])

    sale = Sale(
        email = form["email"]
    )
    sale.save()

    stripe.api_key = settings.STRIPE_SECRET_KEY

    YOUR_DOMAIN = 'http://127.0.0.1:8000/'

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items = [
                {
                    "price_data": {
                        "currency": "aud",
                        "product_data": {
                            "name": f"{img.heading}",
                        },
                        "unit_amount": 100,
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "booking_id": sale.id,
                "image": img.image.url,
                "sale_type": "image"
            },
            mode="payment",
            success_url=YOUR_DOMAIN,
            cancel_url=YOUR_DOMAIN,
        )

        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return HttpResponse(str(e))
    
@csrf_exempt
def my_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, "whsec_6d25ba83cc1adf323c3e7fc16d559b5009748b5ea2448988418f4e3d3c244a14"
        )
    except ValueError as e:
        print(str(e))
        return HttpResponse(status=468)
    except stripe.error.SignatureVerificationError as e:
        print(str(e))
        return HttpResponse(status=469)
    
    session = None
    
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
            )
        
        if session["payment_status"] != "paid":
            return HttpResponse(status=464)
        
        sale = Sale.objects.get(id=session['metadata']['booking_id'])
        
        custemer_email_content = f"your photo {session['metadata']['image']}"
        
        send_mail(
                    "Payment Received",
                    custemer_email_content,
                    "django@admin.com",
                    [sale.email]
                )
    
    return HttpResponse(status=200)