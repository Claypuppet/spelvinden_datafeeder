import csv
import gzip
import io
import os
from collections import namedtuple
from typing import List, Set

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from games.models import Affiliate


def get_csv_reader(file_path_or_lines, delimiter=None):
    """
    Reads and returns CSV data as a DictReader.

    :param file_path_or_lines: Path to a file or a list of lines from a response.
    :param delimiter: Optional delimiter to force usage.
    :return: A CSV DictReader instance.
    """
    if isinstance(file_path_or_lines, str):  # Assume it's a file path
        with open(file_path_or_lines, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    else:  # Assume it's already lines (e.g., from response content)
        lines = file_path_or_lines

    if not delimiter:
        sample = "\n".join(lines[:10])  # Use first 10 lines as sample
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter

    return csv.DictReader(lines, delimiter=delimiter)



ParsedGameData = namedtuple('ParsedGameData', ['ean', 'price', 'stock', 'description', 'category', 'image', 'link'])


class BaseAffiliateParser:
    """
    Base class for affiliate-specific data parsing.
    """
    def parse_row(self, row):
        """
        Parse a single CSV row and return structured data.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement parse_row")


class AdtractionParser(BaseAffiliateParser):
    def parse_row(self, row):
        ean = int(row.get('Ean', 0) or 0)
        if not ean:
            return None

        return ParsedGameData(
            ean=ean,
            price=float(row.get('Price', 0) or '0'),
            stock=1 if row.get('Instock') == 'yes' else 0,
            description=row.get('Description'),
            category=row.get('Category', ''),
            image=row.get('ImageUrl', ''),
            link=row.get('TrackingUrl')
        )


class TradeTrackerParser(BaseAffiliateParser):
    """
    Parser for TradeTracker affiliate CSV data.
    """
    def parse_row(self, row):
        ean = int(row.get('EAN') or row.get('GTIN') or 0)
        if not ean:
            return None

        return ParsedGameData(
            ean=ean,
            price=float(row.get('price', 0) or '0'),
            stock=1 if row.get('availability', '').lower() == 'op voorraad' else 0,
            description=row.get('description'),
            category=row.get('categories', ''),
            image=row.get('imageURL', ''),
            link=row.get('productURL', '')
        )


class AwinParser(BaseAffiliateParser):
    """
    Parser for Awin affiliate CSV data.
    """
    def parse_row(self, row):
        ean = int(row.get('ean') or 0)
        if not ean:
            return None

        return ParsedGameData(
            ean=ean,
            price=float((row.get('store_price') or '0').replace(',', '.')),  # Handle prices with commas
            stock=int(row.get('stock_quantity') or '0'),
            description=row.get('description'),
            category=row.get('merchant_category', ''),
            image=row.get('merchant_image_url', ''),
            link=row.get('aw_deep_link', '')
        )


class DaisyconParser(BaseAffiliateParser):
    """
    Parser for Daisycon affiliate CSV data.
    """
    def parse_row(self, row):
        ean = int(row.get('ean') or 0)
        if not ean:
            return None

        return ParsedGameData(
            ean=ean,
            price=float(row.get('price', 0) or '0'),
            stock=int(row.get('in_stock_amount', 0) or '0') > 0,
            description=row.get('description'),
            category=row.get('category', ''),
            image=row.get('image_default', ''),
            link=row.get('link', '')
        )



# Mapping affiliate programs to their parsers
AFFILIATE_PARSERS = {
    Affiliate.Program.ADTRACTION: AdtractionParser,
    Affiliate.Program.TRADETRACKER: TradeTrackerParser,
    Affiliate.Program.AWIN: AwinParser,
    Affiliate.Program.DAISYCON: DaisyconParser,
}


# Mapping of affiliate names to their sample data file paths, using BASE_DIR
SAMPLE_DATA_PATHS = {
    "999 Games": os.path.join(settings.BASE_DIR, 'games', 'sample_data', '999 Games.csv'),
    "Coolshop": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Coolshop.csv'),
    "Valhallaboardgames": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Valhallaboardgames.csv'),
    "Spelhuis": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Spelhuis.csv'),
    "Spelspul": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Spelspul.csv'),
    "Spellenrijk": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Spellenrijk.csv'),
    "Top1Toys": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Top1Toys.csv'),
    "Alternate": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Alternate.csv'),
    "Cardpile": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Cardpile.csv'),
    "Degrotespeelgoedwinkel": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Degrotespeelgoedwinkel.csv'),
    "Internet-Toys": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Internet-Toys.csv'),
    "Blokker": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Blokker.csv'),
    "Bruna": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'Bruna.csv'),
    "De Spelletjes Vrienden": os.path.join(settings.BASE_DIR, 'games', 'sample_data', 'De Spelletjes Vrienden.csv'),
}

class AffiliateCommandBase(BaseCommand):
    """
    Base class for affiliate-related commands.
    """
    def fetch_csv_data(self, affiliate: AFFILIATE_PARSERS, use_sample: bool):
        if use_sample:
            csv_path = SAMPLE_DATA_PATHS.get(affiliate.name)
            if not csv_path:
                self.stdout.write(f"No sample data found for {affiliate.name}. Skipping...")
                return None
            return get_csv_reader(csv_path)
        else:
            self.stdout.write(f"Retrieving remote data for {affiliate.name}...")
            response = requests.get(affiliate.data_source_url)
            response.raise_for_status()

            # Check if the response is a gzipped file
            if response.headers.get('Content-Type') == 'application/gzip':
                # Unzip the content
                with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gzipped_file:
                    # Read the CSV data from the unzipped content
                    csv_content = gzipped_file.read().decode('utf-8')
            else:
                csv_content = response.content.decode('utf-8')

            return get_csv_reader(csv_content.splitlines())

    def process_affiliate(self, affiliate: Affiliate, use_sample: bool, game_eans: Set[str] = None) -> List[ParsedGameData]:
        try:
            csv_reader = self.fetch_csv_data(affiliate, use_sample)
            if not csv_reader:
                return []

            parser_class = AFFILIATE_PARSERS.get(affiliate.program, None)
            if not parser_class:
                self.stdout.write(f"Unknown affiliate program: {affiliate.program}. Skipping...")
                return []

            parser = parser_class()
            parsed_data = []

            for row in csv_reader:
                data = parser.parse_row(row)
                if data and (not game_eans or data.ean in game_eans):
                    parsed_data.append(data)

            return parsed_data
        except Exception as e:
            self.stderr.write(f"Error processing {affiliate.name}: {e}")
            return []
