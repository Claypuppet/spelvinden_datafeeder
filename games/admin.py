from django.contrib import admin

from .models import Game, Affiliate, AffiliateCategory, AffiliateGame


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('ean', 'name', 'new', 'stock', 'affiliate_count')
    search_fields = ('ean', 'name')
    list_filter = ('new',)


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'enabled', 'game_count')
    search_fields = ('name', 'program')
    list_filter = ('enabled',)




def enable_categories(modeladmin, request, queryset):
    """
    Custom admin action to enable (set 'include' to True) selected AffiliateCategory instances.
    """
    queryset.update(include=True)  # Set 'include' to True for all selected categories
    modeladmin.message_user(request, f"Enabled {queryset.count()} categories.")

enable_categories.short_description = 'Enable selected categories'

def disable_categories(modeladmin, request, queryset):
    """
    Custom admin action to disable (set 'include' to False) selected AffiliateCategory instances.
    """
    queryset.update(include=False)  # Set 'include' to False for all selected categories
    modeladmin.message_user(request, f"Disabled {queryset.count()} categories.")

disable_categories.short_description = 'Disable selected categories'


@admin.register(AffiliateCategory)
class AffiliateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'affiliate', 'include', 'game_count')
    search_fields = ('name',)
    list_filter = ('include', 'affiliate')
    actions = [enable_categories, disable_categories]


@admin.register(AffiliateGame)
class AffiliateGameAdmin(admin.ModelAdmin):
    list_display = ('game', 'affiliate', 'price', 'stock', 'category')
    search_fields = ('game__name', 'game__ean', 'category__name')
    list_filter = ('affiliate',)
