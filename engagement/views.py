from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Review


@login_required
def submit_review(request, booking_id):
    """
    Handles review submission for a completed booking.
    NOTE: booking lookup is stubbed until bookings.Booking is live.
    """
    booking = None  # TEMPORARY STUB

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if not rating:
            messages.error(request, 'Please provide a rating.')
            return render(request, 'engagement/review_form.html', {'booking_id': booking_id})

        Review.objects.create(
            reviewer=request.user,
            rating=rating,
            comment=comment,
        )

        messages.success(request, 'Review submitted successfully.')
        return redirect('submit_review', booking_id=booking_id)

    return render(request, 'engagement/review_form.html', {'booking_id': booking_id})


@staff_member_required
def admin_overview(request):
    """
    Admin KPI dashboard. Using placeholder values until bookings/accounts models are live.
    Alerts are sample data standing in for a real Dispute/Flag/Compliance model.
    """
    context = {
        'total_gmv': '2.4M',
        'active_vendors': 142,
        'total_bookings': 850,
        'pending_verifications': 28,
        'alerts': [
            {
                'id': 8492,
                'type': 'dispute',
                'title': 'Active Dispute #8492',
                'description': 'Client reported venue condition did not match listing photography.',
                'tag': 'High Priority',
                'action_label': 'Review',
                'action_url_name': 'dispute_detail',
                'action_url_arg': 8492,
            },
            {
                'id': None,
                'type': 'flag',
                'title': 'Flagged Listing',
                'description': 'Automated system detected potential duplicate content for "The Grand Hall".',
                'tag': 'System Flag',
                'action_label': 'Inspect',
                'action_url_name': 'coming_soon',
                'action_url_arg': 'Listing Inspection',
            },
            {
                'id': None,
                'type': 'compliance',
                'title': 'Missing Compliance Data',
                'description': '12 high-volume vendors require updated tax documentation for Q4.',
                'tag': None,
                'action_label': 'Send Bulk Reminder',
                'action_url_name': 'send_bulk_reminder',
                'action_url_arg': None,
            },
        ],
    }
    return render(request, 'engagement/admin_overview.html', context)


@staff_member_required
def send_bulk_reminder(request):
    """Sends a compliance reminder to vendors with missing documentation. POST-only, stubbed."""
    if request.method == 'POST':
        messages.success(request, 'Reminder sent to 12 vendors. (stubbed — no real email sent yet)')
    return redirect('admin_overview')


@staff_member_required
def export_report(request):
    """Exports the platform growth report. POST-only, stubbed."""
    if request.method == 'POST':
        messages.success(request, 'Report export started. (stubbed — no real file generated yet)')
    return redirect('admin_overview')


@staff_member_required
def verification_queue(request):
    """
    Lists vendors pending verification approval.
    NOTE: no VendorProfile model connection yet — using sample data
    until Team 1 delivers accounts.VendorProfile with verification_status.
    """
    sample_vendors = [
        {
            'id': 1,
            'name': 'Bloom & Bower',
            'category': 'Florist & Decor',
            'category_tag': 'Floral Design',
            'submitted_date': 'Oct 24, 2024',
            'photo': 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=200&q=80',
            'documents': [
                {'name': 'License.pdf', 'preview': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=300&q=80'},
                {'name': 'Tax_Form.pdf', 'preview': 'https://images.unsplash.com/photo-1554224154-22dec7ec8818?auto=format&fit=crop&w=300&q=80'},
            ],
        },
        {
            'id': 2,
            'name': 'Gourmet Gatherings',
            'category': 'Catering Services',
            'category_tag': 'Food & Beverage',
            'submitted_date': 'Oct 23, 2024',
            'photo': 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=200&q=80',
            'documents': [
                {'name': 'Health_Permit.pdf', 'preview': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=300&q=80'},
            ],
        },
        {
            'id': 3,
            'name': 'Grand Hall Events',
            'category': 'Event Venue',
            'category_tag': 'Venue',
            'submitted_date': 'Oct 22, 2024',
            'photo': 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=200&q=80',
            'documents': [
                {'name': 'Registration.pdf', 'preview': 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=300&q=80'},
            ],
        },
    ]  # TEMPORARY sample data — replace with accounts.VendorProfile.objects.filter(verification_status='pending')

    search_query = request.GET.get('q', '').strip().lower()
    if search_query:
        sample_vendors = [
            v for v in sample_vendors
            if search_query in v['name'].lower() or search_query in v['category'].lower()
        ]

    context = {
        'pending_vendors': sample_vendors,
    }
    return render(request, 'engagement/verification_queue.html', context)


@staff_member_required
def approve_vendor(request, vendor_id):
    """
    Approves a vendor's verification. POST-only action.
    """
    if request.method == 'POST':
        messages.success(request, 'Vendor approved. (stubbed — no real save yet)')
    return redirect('verification_queue')


@staff_member_required
def reject_vendor(request, vendor_id):
    """
    Rejects a vendor's verification. POST-only action.
    """
    if request.method == 'POST':
        messages.success(request, 'Vendor rejected. (stubbed — no real save yet)')
    return redirect('verification_queue')


@staff_member_required
def booking_oversight(request):
    """
    Admin view of all bookings and payments, with search and status filtering.
    Depends on bookings.Booking — stubbed with fake sample data for visual
    testing until Team 3 delivers the real model. Replace with real queryset then.
    """
    all_bookings = [
        {'id': 892, 'client': 'Eleanor Sterling', 'listing': 'Lumina Catering Co.', 'event_date': 'Oct 12, 2024', 'total_price': 4250, 'status': 'Paid', 'is_flagged': False},
        {'id': 891, 'client': 'Julian Davenport', 'listing': 'The Velvet String Quartet', 'event_date': 'Nov 05, 2024', 'total_price': 1100, 'status': 'Pending', 'is_flagged': False},
        {'id': 889, 'client': 'Alice Walker', 'listing': 'Metro Sound and Lighting', 'event_date': 'Oct 28, 2024', 'total_price': 8500, 'status': 'Paid', 'is_flagged': True},
        {'id': 888, 'client': 'Marcus Bell', 'listing': 'Oakwood Estate Venue', 'event_date': 'Dec 15, 2024', 'total_price': 12000, 'status': 'Pending', 'is_flagged': False},
    ]  # TEMPORARY fake data — remove once bookings.Booking exists

    search_query = request.GET.get('q', '').strip().lower()
    status_filter = request.GET.get('status', 'all')

    if search_query:
        all_bookings = [
            b for b in all_bookings
            if search_query in str(b['id']).lower() or search_query in b['client'].lower()
        ]

    if status_filter == 'pending':
        all_bookings = [b for b in all_bookings if b['status'] == 'Pending']
    elif status_filter == 'flagged':
        all_bookings = [b for b in all_bookings if b['is_flagged']]
    elif status_filter == 'paid':
        all_bookings = [b for b in all_bookings if b['status'] == 'Paid']

    context = {
        'all_bookings': all_bookings,
        'total_count': len(all_bookings),
    }
    return render(request, 'engagement/booking_oversight.html', context)


@staff_member_required
def dispute_detail(request, booking_id):
    """
    Shows details of a flagged/disputed booking for admin review.
    NOTE: no Dispute model exists in the schema yet — using sample data
    stored in the session so actions (resolve, refund, notes) persist
    across requests during testing. Replace with real Dispute/Booking
    models once Team 3 delivers bookings and the team confirms whether
    disputes need their own model.
    """
    session_key = f'dispute_{booking_id}'

    if session_key not in request.session:
        request.session[session_key] = {
            'status': 'Action Required',
            'client_name': 'Sarah Jenkins',
            'client_email': 'sarah.j@example.com',
            'vendor_name': 'Luxe Catering Co.',
            'vendor_email': 'contact@luxecatering.com',
            'package_name': 'Premium Wedding Package',
            'event_date': 'Oct 24, 2024',
            'location': 'The Grand Hall, NY',
            'total_value': 4500.00,
            'dispute_reason': 'Service not delivered as described (Missing vegetarian options).',
            'escrow_status': 'Held (In Dispute)',
            'messages_log': [
                {'sender': 'Sarah Jenkins', 'time': 'Oct 12, 10:45 AM', 'text': 'I am opening this dispute because half of the promised vegetarian options were missing at the event.', 'side': 'left'},
                {'sender': 'Luxe Catering Co.', 'time': 'Oct 12, 11:30 AM', 'text': 'We apologize for the inconvenience. Our supplier failed to deliver ingredients for the secondary dish.', 'side': 'right'},
            ],
            'internal_notes': [
                'Vendor contract stipulates full menu delivery or 15% refund per missing item.',
            ],
        }

    dispute = request.session[session_key]

    context = {
        'booking_id': booking_id,
        'dispute': dispute,
    }
    return render(request, 'engagement/dispute_detail.html', context)


@staff_member_required
def resolve_dispute(request, booking_id):
    """Marks a dispute as resolved. POST-only."""
    if request.method == 'POST':
        session_key = f'dispute_{booking_id}'
        if session_key in request.session:
            request.session[session_key]['status'] = 'Resolved'
            request.session.modified = True
        messages.success(request, 'Dispute marked as resolved.')
    return redirect('dispute_detail', booking_id=booking_id)


@staff_member_required
def issue_refund(request, booking_id):
    """Issues a full or partial refund. POST-only."""
    if request.method == 'POST':
        refund_type = request.POST.get('refund_type', 'full')
        session_key = f'dispute_{booking_id}'
        if session_key in request.session:
            request.session[session_key]['escrow_status'] = f'{refund_type.title()} refund issued'
            request.session.modified = True
        messages.success(request, f'{refund_type.title()} refund issued. (stubbed — no real payment processed)')
    return redirect('dispute_detail', booking_id=booking_id)


@staff_member_required
def add_internal_note(request, booking_id):
    """Adds an internal admin note to a dispute. POST-only."""
    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        session_key = f'dispute_{booking_id}'
        if note and session_key in request.session:
            request.session[session_key]['internal_notes'].append(note)
            request.session.modified = True
        else:
            messages.error(request, 'Note cannot be empty.')
    return redirect('dispute_detail', booking_id=booking_id)


def platform_overview(request):
    return render(request, "engagement/platform_overview.html")


def client_reviews(request):
    """
    Public-facing vendor review page: aggregate rating + review list with search.
    Depends on engagement.Review (booking FK still stubbed) — using sample data
    for now until real Review records exist with bookings wired in.
    """
    sample_reviews = [
        {'reviewer': 'Eleanor Vance', 'role': 'Wedding Client', 'date': 'Oct 15, 2024', 'rating': 5,
         'comment': 'Working with Lumina Floral Design was an absolute dream. They perfectly captured the editorial, moody aesthetic we wanted for our autumn wedding.'},
        {'reviewer': 'James & David', 'role': 'Corporate Gala', 'date': 'Sep 02, 2024', 'rating': 5,
         'comment': 'We hired Lumina for a high-end corporate gala, and they delivered beyond expectations. Highly recommend for any upscale function.'},
        {'reviewer': 'Sarah Jenkins', 'role': 'Anniversary Party', 'date': 'Aug 18, 2024', 'rating': 4,
         'comment': 'Beautiful flowers and good service. The quality of the blooms was top-tier, and they lasted beautifully throughout the evening.'},
    ]  # TEMPORARY sample data — replace with real Review queryset once bookings.Booking exists

    search_query = request.GET.get('q', '').strip().lower()
    if search_query:
        sample_reviews = [
            r for r in sample_reviews
            if search_query in r['reviewer'].lower() or search_query in r['comment'].lower()
        ]

    # TEMPORARY hardcoded breakdown — replace with a real aggregation
    # (e.g. Review.objects.values('rating').annotate(count=Count('rating')))
    # once real Review data with bookings exists.
    rating_breakdown = [
        (5, 85),
        (4, 10),
        (3, 3),
        (2, 1),
        (1, 1),
    ]

    context = {
        'reviews': sample_reviews,
        'total_reviews': len(sample_reviews),
        'rating_breakdown': rating_breakdown,
    }
    return render(request, 'engagement/client_review.html', context)


@staff_member_required
def flag_booking(request, booking_id):
    """
    Toggles the flagged/suspicious status of a booking. POST-only.
    NOTE: 'is_flagged' isn't a real field yet — needs bookings.Booking to exist
    with a flag field, or a related model. Raise with Team 3 before building this for real.
    """
    if request.method == 'POST':
        messages.success(request, 'Booking flag toggled. (stubbed — no real save yet)')
    return redirect('booking_oversight')


def coming_soon(request, feature_name):
    """
    Generic placeholder page for links to features not yet built by other teams
    (e.g. Bookings, Messages, Profile). Not a real destination — just avoids dead links.
    """
    context = {'feature_name': feature_name}
    return render(request, 'engagement/coming_soon.html', context)