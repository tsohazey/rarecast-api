# ADD THIS FUNCTION (replace the old Buyee block in run_hunt)

def scrape_buyee_unicorns():
    buyee_alerts = []
    url = "https://buyee.jp/item/search/query/メガバス%20(ビジョン110%20OR%20110jr%20OR%20110+1%20OR%20i-switch%20OR%20ポップマックス%20OR%20ポップX)?category=23321&status=on_sale"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # Buyee changed layout in 2024–2025 → this selector still works as of Nov 2025
        for item in soup.select('.p-item-card'):
            title_tag = item.select_one('.p-item-card__title a')
            price_tag = item.select_one('.p-item-card__price .price')
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://buyee.jp" + title_tag['href']

            if matches(title):
                price = price_tag.get_text(strip=True) if price_tag else "Price hidden"
                buyee_alerts.append(f"*BUYEE UNICORN*\n{title}\n{price}\n{link}")

    except Exception as e:
        print("Buyee scrape error:", e)

    return buyee_alerts
