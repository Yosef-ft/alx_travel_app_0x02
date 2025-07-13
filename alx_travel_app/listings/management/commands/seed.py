import random
from datetime import timedelta
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker


from listings.models import Listing, Booking, Review

User = get_user_model()

class Command(BaseCommand):

    help = 'Seeds the database with listings, bookings, and reviews.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write("Creating new data...")
        fake = Faker()

        self.stdout.write("Creating users...")
        users = []
        for _ in range(15):
            profile = fake.profile(fields=['username', 'name', 'mail'])
            user, created = User.objects.get_or_create(
                username=profile['username'],
                defaults={
                    'first_name': profile['name'].split()[0],
                    'last_name': profile['name'].split()[1],
                    'email': profile['mail'],
                }
            )
            user.set_password('password123')
            user.save()
            users.append(user)
            if created:
                self.stdout.write(f'  Created user: {user.username}')

        self.stdout.write("Creating listings...")
        listings = []
        listing_titles = [
            "Kolfe", "Abuare", "Mehandis",
            "Zeneb werk", "Ayer tena", "Kara",
            "Family Home", "Studio"
        ]
        for _ in range(25):
            host = random.choice(users)
            listing = Listing.objects.create(
                host=host,
                title=random.choice(listing_titles) + f" in {fake.city()}",
                description=fake.paragraph(nb_sentences=5),
                location=fake.address(),
                price_per_night=round(random.uniform(50.00, 450.00), 2)
            )
            listings.append(listing)
        self.stdout.write(f'  Created {len(listings)} listings.')

        self.stdout.write("Creating bookings...")
        bookings = []
        for listing in listings:
            for _ in range(random.randint(1, 5)):                
                possible_guests = [user for user in users if user != listing.host]
                if not possible_guests:
                    continue
                guest = random.choice(possible_guests)

                start_date = fake.date_between(start_date='-30d', end_date='+60d')
                duration = random.randint(2, 10)
                end_date = start_date + timedelta(days=duration)

                total_price = listing.price_per_night * duration

                booking = Booking.objects.create(
                    listing=listing,
                    guest=guest,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_price,
                )
                bookings.append(booking)
        self.stdout.write(f'  Created {len(bookings)} bookings.')

        self.stdout.write("Creating reviews...")
        past_bookings = [b for b in bookings if b.end_date < fake.date_object()]
        
        for booking in random.sample(past_bookings, k=int(len(past_bookings) * 0.7)):
            if not hasattr(booking, 'review'):
                Review.objects.create(
                    booking=booking,
                    reviewer=booking.guest,
                    rating=random.randint(1, 5), 
                    comment=fake.paragraph(nb_sentences=2) if random.random() > 0.2 else "",
                )
        self.stdout.write(f'  Created reviews for past bookings.')

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database."))