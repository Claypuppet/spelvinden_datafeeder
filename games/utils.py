import csv
from .models import Game
from django.core.exceptions import ValidationError

def create_wordpress_import_csv():
    try:
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        for row in reader:
            game, created = Game.objects.update_or_create(
                ean=row['ean'],
                defaults={
                    'name': row['name'],
                    'description': row['description'],
                    'new': row['new'].lower() == 'true',
                    'stock': int(row['stock']),
                }
            )
    except Exception as e:
        raise ValidationError(f"Error processing CSV: {str(e)}")
