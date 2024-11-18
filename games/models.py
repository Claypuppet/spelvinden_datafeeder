import html
from bs4 import BeautifulSoup
from django.db import models


class Game(models.Model):
    ean = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    new = models.BooleanField(default=True)
    last_lowest_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.name} (EAN: {self.ean})"

    @property
    def affiliate_count(self):
        return self.affiliate_games.count()

    @property
    def stock(self):
        return self.affiliate_games.aggregate(models.Sum('stock'))['stock__sum'] or 0

    @property
    def available_game_affiliates(self):
        return self.affiliate_games.filter(stock__gt=0).order_by('price')

    @property
    def clean_description(self):
        # Use BeautifulSoup to remove HTML tags and just keep the plain text
        return BeautifulSoup(html.unescape(self.description), 'html.parser').get_text().replace("\\n", " ")


class Affiliate(models.Model):

    class Program(models.TextChoices):
        ADTRACTION = 'Adtraction', 'Adtraction'
        TRADETRACKER = 'TradeTracker', 'TradeTracker'
        AWIN = 'Awin', 'Awin'
        DAISYCON = 'Daisycon', 'Daisycon'


    name = models.CharField(max_length=100)
    program = models.CharField(max_length=100, choices=Program.choices)
    enabled = models.BooleanField(default=True)
    data_source_url = models.URLField(max_length=1000)

    tariff = models.CharField(max_length=100, blank=True, default='')
    shipping_nl = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shipping_be = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    free_shipping_nl = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    free_shipping_be = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shipping_note = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.program})"

    @property
    def game_count(self):
        return self.games.count()


class AffiliateCategory(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    include = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def game_count(self):
        return self.games.count()


class AffiliateGame(models.Model):
    class Meta:
        unique_together = ('affiliate', 'game')

    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='affiliate_games')
    category = models.ForeignKey(AffiliateCategory, on_delete=models.CASCADE, related_name='games', null=True)

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock_r = models.TextField(blank=True, default='')
    stock = models.IntegerField(default=0)
    tags = models.CharField(max_length=1000, blank=True, default='')
    image = models.URLField(max_length=800, blank=True, default='')
    link = models.URLField(max_length=800, blank=True, default='')

    def __str__(self):
        return f"{self.name} - {self.affiliate.name} (Price: {self.price})"
