import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
 
df = pd.read_csv('dataset/cardekho_dataset.csv')
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nData types:")
print(df.dtypes)
print("\nMissing values:")
print(df.isnull().sum())
print("\nSample data:")
print(df.head(3))
print("\nPrice stats:")
print(df['selling_price'].describe())
 
# Price distribution chart
plt.figure(figsize=(10,5))
plt.hist(df['selling_price'], bins=50, color='#2E75B6', edgecolor='white')
plt.title('Distribution of Selling Price')
plt.xlabel('Price (Rs.)')
plt.ylabel('Count')
plt.savefig('static/images/price_distribution.png', bbox_inches='tight')
plt.close()
 
# Correlation heatmap
numeric = df.select_dtypes(include=['number'])
plt.figure(figsize=(10,8))
sns.heatmap(numeric.corr(), annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Feature Correlation Heatmap')
plt.savefig('static/images/correlation_heatmap.png', bbox_inches='tight')
plt.close()
print("\nCharts saved to static/images/")
