# Games Affiliate Integration Django App
This Django app is designed to manage affiliate data for board games, including updating prices, importing game data from various sources, and generating a CSV export for integration with WordPress.

## **Setup Instructions**

### 1. Install Dependencies
Ensure you have Django and other required dependencies installed. You can install the necessary packages via:

```
pip install -r requirements.txt
```

## **Database Setup**

### 1. Apply Migrations
After making any changes to models or setting up the project for the first time, run the following commands:

```
python manage.py makemigrations
python manage.py migrate
```

This ensures all model changes are reflected in the database.

## **Admin View**

The Django admin interface provides an easy way to manage affiliate game data. The key models available in the admin include `Game`, `Affiliate`, `AffiliateCategory`, and `AffiliateGame`. You can view and manage information such as game details, affiliate data, categories, and pricing.

### **Accessing the Admin Interface**
To access the admin interface:
1. Start the Django server:
   '''
   python manage.py runserver
   '''
2. Go to `http://127.0.0.1:8000/admin` in your browser.
3. Log in using your superuser credentials.

### **Admin Tips**
- Use the search bar to quickly find specific games, affiliates, or categories by name or identifier.
- Use the list filters to narrow down results by specific fields like affiliate status or game availability.
- For managing affiliate game data, the `AffiliateGame` section lets you update pricing and stock information per affiliate.

## **Commands Overview**

This app provides custom management commands to handle various tasks related to game data management. Below is a description of the key commands and how to use them.

### **1. Import Spelvinden Data**
The `import_spelvinden` command imports game data specifically from Spelvinden's CSV file. It reads from the sample data located at `games/sample_data/Spelvinden.csv`.

#### **Usage**
```
python manage.py import_spelvinden
```

#### **Functionality**
- Imports all games listed in the Spelvinden CSV file into the database.
- Ensures no duplicate records are created.

### **2. Update Prices**
The `update_prices` command fetches affiliate CSV data and updates game prices accordingly. This command can handle multiple affiliate programs, such as Daisycon, Awin, and TradeTracker. It also supports processing local sample data for testing.

#### **Usage**
```
python manage.py update_prices [--use_sample_data]
```

#### **Options**
- `--use_sample_data`: If specified, the command reads from local sample files instead of fetching data from online sources.

#### **Example**
```
python manage.py update_prices --use_sample_data
```

This will process affiliate CSVs from the `games/sample_data` directory.

### **3. Create WordPress Import CSV**
The `create_wordpress_import_csv` command generates a CSV file that can be imported into WordPress to update game data and prices.

#### **Usage**
```
python manage.py create_wordpress_import_csv
```

#### **Output**
- The command creates a CSV file in the project’s `exports` directory, named something like `wordpress_import_<timestamp>.csv`.
- The CSV includes the following fields:
  - `name`: Game name
  - `lowest price`: Lowest price across all affiliates
  - `short description`: A brief description of the game (generated using a Django template)
  - `stock`: Whether the game is in stock (1 for in stock, 0 for out of stock)

#### **Example**
```
python manage.py create_wordpress_import_csv
```
