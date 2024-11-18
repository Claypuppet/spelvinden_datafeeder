# your_app/management/commands/update_prices.py

from games.management.commands.affiliate_command_base import AffiliateCommandBase
from games.models import Affiliate, AffiliateGame, Game, AffiliateCategory  # Update with your actual models



class Command(AffiliateCommandBase):
    help = 'Create Affiliate categories for affiliates from CSV data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use_sample_data',
            action='store_true',
            help='Use sample data instead of fetching from actual URLs',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting category update for affiliates...")

        affiliates = Affiliate.objects.filter(enabled=True)  # Get only enabled affiliates
        total_added = 0

        for affiliate in affiliates:
            self.stdout.write(f"---")
            self.stdout.write(f"Processing {affiliate.name} ({affiliate.program})...")
            game_data = self.process_affiliate(affiliate, kwargs.get('use_sample_data'))

            category_set = set([game.category for game in game_data if game.category])

            created_count = 0
            for category in category_set:
                ac, created = AffiliateCategory.objects.get_or_create(
                    affiliate=affiliate,
                    name=category,
                    defaults=dict(include=False),
                )
                if created:
                    created_count += 1

            self.stdout.write(f'Added {created_count} categories for {affiliate.name}\n')

            total_added += created_count

        self.stdout.write(f'---')
        self.stdout.write(f'Completed category update for all affiliates, total of {total_added} categories added.')
