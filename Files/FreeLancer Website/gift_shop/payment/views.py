import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Only set Stripe API key if it's configured
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, paid=False)
    
    # Check if Stripe is enabled
    if not getattr(settings, 'STRIPE_ENABLED', False) or not settings.STRIPE_SECRET_KEY:
        messages.warning(request, 'Payment processing is currently in demo mode. No real payments will be processed.')
        return render(request, 'payment/demo_mode.html', {
            'order': order,
            'demo_mode': True
        })
    
    if request.method == 'POST':
        try:
            success_url = request.build_absolute_uri(f'/payment/success/{order.id}/')
            cancel_url = request.build_absolute_uri(f'/payment/cancel/{order.id}/')

            session_data = {
                'mode': 'payment',
                'client_reference_id': order.id,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'line_items': []
            }

            # Add order items to the Stripe checkout session
            for item in order.items.all():
                session_data['line_items'].append({
                    'price_data': {
                        'unit_amount': int(item.price * 100),  # amount in cents
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        },
                    },
                    'quantity': item.quantity,
                })

            # Create Stripe checkout session
            session = stripe.checkout.Session.create(**session_data)

            # Update order with payment intent
            order.payment_intent_id = session.payment_intent
            order.save()

            return JsonResponse({'sessionId': session.id})
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'payment/process.html', {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY or 'demo_key'
    })

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # In demo mode, mark order as paid
    if not getattr(settings, 'STRIPE_ENABLED', False):
        order.paid = True
        order.save()
        messages.success(request, 'Demo payment successful! Order has been marked as paid.')
    
    return render(request, 'payment/success.html', {'order': order})

@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payment/cancel.html', {'order': order})

@csrf_exempt
def stripe_webhook(request):
    # Skip webhook processing if Stripe is disabled
    if not getattr(settings, 'STRIPE_ENABLED', False) or not settings.STRIPE_SECRET_KEY:
        return HttpResponse(status=200)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        order_id = session.client_reference_id
        order = Order.objects.get(id=order_id)
        order.paid = True
        order.stripe_id = session.payment_intent
        order.save()

    return HttpResponse(status=200)
