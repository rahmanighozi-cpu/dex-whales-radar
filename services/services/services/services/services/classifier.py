def classify_wallet(arkham, etherscan):
    if arkham.get("entity"):
        return "Labeled Entity"

    if "binance" in str(etherscan).lower():
        return "Exchange / CEX"

    return "Smart Money"
