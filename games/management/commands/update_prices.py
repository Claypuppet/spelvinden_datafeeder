# your_app/management/commands/update_prices.py

from games.management.commands.affiliate_command_base import AffiliateCommandBase
from games.models import Affiliate, AffiliateGame, Game, AffiliateCategory  # Update with your actual models



class Command(AffiliateCommandBase):
    help = 'Update prices for affiliate games from CSV data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use_sample_data',
            action='store_true',
            help='Use sample data instead of fetching from actual URLs',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting price update for affiliates...")

        affiliates = Affiliate.objects.filter(enabled=True)  # Get only enabled affiliates
        game_eans = set(Game.objects.values_list('ean', flat=True))  # Fetch all EANs
        total_updated = 0

        for affiliate in affiliates:
            self.stdout.write(f"---")
            self.stdout.write(f"Processing {affiliate.name} ({affiliate.program})...")
            game_data = self.process_affiliate(affiliate, kwargs.get('use_sample_data'), game_eans)
            affiliate_categories_dict = {category.name: category for category in AffiliateCategory.objects.filter(affiliate=affiliate)}

            created_count = 0
            updated_count = 0
            for game in game_data:
                ag, created = AffiliateGame.objects.update_or_create(
                    affiliate=affiliate,
                    game_id=game.ean,
                    defaults={
                        'price': game.price,
                        'stock': game.stock if game.price else 0,
                        'description': game.description,
                        'category': affiliate_categories_dict.get(game.category, None),
                        'image': game.image,
                        'link': game.link
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(f'Updated prices from {affiliate.name} for {updated_count} games, added price for {created_count} games\n')

            total_updated += updated_count

        self.stdout.write(f'---')
        self.stdout.write(f'Completed price update for all affiliates, total of {total_updated} prices updated.')
