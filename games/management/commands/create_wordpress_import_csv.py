# games/management/commands/export_game_data.py

import csv
import locale

from django.core.management.base import BaseCommand
from django.db.models import Min, Max, Q, Count
from django.template.loader import render_to_string
from games.models import Game

locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')


def format_price(price):
    return locale.currency(price, symbol=False, grouping=True).replace(' ', '')


class Command(BaseCommand):
    help = 'Export game data to CSV with lowest affiliate prices and stock status.'

    def handle(self, *args, **options):
        # Define the CSV file path
        file_path = 'game_data_export.csv'

        # Open the CSV file for writing
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(['SKU', 'Original Name', 'Regular price', 'In stock?', 'Short description'])

            # Fetch games with lowest affiliate prices and stock status
            games = Game.objects.annotate(
                # Get the lowest price from affiliates where stock > 0
                lowest_price=Min('affiliate_games__price', filter=Q(affiliate_games__stock__gt=0)),
                # Count the number of affiliates with stock > 0
                in_stock=Count('affiliate_games', filter=Q(affiliate_games__stock__gt=0))
            )

            # Loop through each game and write its data to the CSV file
            for game in games:
                # Generate short description from template
                short_description = render_to_string(
                    'description_template.html',  # Create this template
                    {'game': game}
                ).strip().replace('\n', '').replace('\r', '')

                # Define the stock status as 1 if any affiliate has stock, else 0
                stock_status = 1 if game.in_stock > 0 else 0

                if game.lowest_price:
                    game.last_lowest_price = game.lowest_price
                    game.save(update_fields=['last_lowest_price'])

                # Write game data row
                writer.writerow([
                    game.ean,
                    game.name,
                    format_price(game.last_lowest_price),
                    stock_status,
                    short_description,
                ])

        self.stdout.write(self.style.SUCCESS(f'Data successfully exported to {file_path}'))
