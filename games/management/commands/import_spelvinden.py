# your_app/management/commands/update_prices.py

import csv
import requests
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from games.models import Affiliate, AffiliateGame, Game  # Update with your actual models


def parse_price(price_str):
    try:
        # Remove thousands separator (.)
        normalized_price = price_str.replace('.', '')
        # Replace decimal comma (,) with a dot (.)
        normalized_price = normalized_price.replace(',', '.')
        # Convert to float
        return float(normalized_price)
    except ValueError:
        raise ValueError(f"Invalid price format: {price_str}")


class Command(BaseCommand):
    help = 'Import spelvinden games from CSV data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use_sample_data',
            action='store_true',
            help='Use sample data instead of fetching from actual URLs',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting spelvinden data load...")


        if kwargs.get('use_sample_data'):
            # Use the mapped sample data path for this affiliate
            csv_path = os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Spelvinden.csv')
            if not csv_path:
                self.stdout.write(f"No sample data found for Spelvinden...")
                return

            # Open and read CSV data from the sample file
            with open(csv_path, newline='', encoding='utf-8-sig') as f:
                csv_data = f.read().splitlines()
                self.stdout.write(f"Using sample data")
        else:
            self.stdout.write(f"No support yet for dynamic spelvinden data loading, use sample data instead")
            return

        total_added = 0
        total_updated = 0

        reader = csv.DictReader(csv_data, delimiter=',')

        Game.objects.all().delete()

        with transaction.atomic():
            for row in reader:
                ean = row.get('SKU')
                name = row.get('Name')
                description = row.get('Description')
                price = parse_price(row.get('Regular price'))

                game, created = Game.objects.update_or_create(
                    ean=ean,
                    defaults={
                        'name': name,
                        'description': description,
                        'new': False,
                        'last_lowest_price': price,
                    }
                )
                if created:
                    total_added += 1
                else:
                    total_updated += 1

        self.stdout.write(f"Completed price update. Total added: {total_added}. Total updated: {total_updated}")
