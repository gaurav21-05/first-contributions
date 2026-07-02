import pandas as pd
import numpy as np

def simulate_bitcoin_prices(days=60, initial_price=50000, mu=0.001, sigma=0.03):
    # Using a seeded value of 0, which we tested earlier to show a cross
    np.random.seed(1)
    dt = 1
    prices = [initial_price]
    for _ in range(1, days):
        shock = np.random.normal(loc=mu * dt, scale=sigma * np.sqrt(dt))
        price = prices[-1] * np.exp(shock)
        prices.append(price)

    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    return pd.DataFrame({'Date': dates, 'Price': prices})


def backtest_strategy(df):
    # Calculate 7-day and 30-day moving averages
    df['7_MA'] = df['Price'].rolling(window=7).mean()
    df['30_MA'] = df['Price'].rolling(window=30).mean()

    cash = 100000.0
    btc_held = 0.0

    print("--- Daily Ledger ---")

    # Iterate through each day to check for Golden Cross (buy/sell) signals
    for i in range(len(df)):
        date = df['Date'].iloc[i]
        price = df['Price'].iloc[i]
        ma7 = df['7_MA'].iloc[i]
        ma30 = df['30_MA'].iloc[i]

        if i > 0:
            prev_ma7 = df['7_MA'].iloc[i-1]
            prev_ma30 = df['30_MA'].iloc[i-1]

            if pd.notna(ma7) and pd.notna(ma30) and pd.notna(prev_ma7) and pd.notna(prev_ma30):
                # Buy signal: 7_MA crosses above 30_MA
                if prev_ma7 <= prev_ma30 and ma7 > ma30:
                    if cash > 0:
                        btc_bought = cash / price
                        print(f"{date.strftime('%Y-%m-%d')}: BUY  {btc_bought:.4f} BTC at ${price:.2f}")
                        btc_held += btc_bought
                        cash = 0.0

                # Sell signal: 7_MA crosses below 30_MA
                elif prev_ma7 >= prev_ma30 and ma7 < ma30:
                    if btc_held > 0:
                        cash_gained = btc_held * price
                        print(f"{date.strftime('%Y-%m-%d')}: SELL {btc_held:.4f} BTC at ${price:.2f}")
                        cash += cash_gained
                        btc_held = 0.0

    final_value = cash + btc_held * df['Price'].iloc[-1]
    print("--------------------")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Total Return: {((final_value - 100000) / 100000) * 100:.2f}%")

if __name__ == '__main__':
    df = simulate_bitcoin_prices(days=60)
    backtest_strategy(df)
