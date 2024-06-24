class Scrapper:

    def __init__(self) -> None:
        """
        Function that set up the base of the scrapping
        """
        self.start_url = "https://www.immoweb.be/en/search/"

        # Work around for the restriction where immoweb don't allow request that aren't coming from a browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": self.start_url,
        }

    def get_url_sale(self, type):
        self.type = type
        self.to_buy = "/for-sale"
        self.url = (
            "https://www.immoweb.be/en/classified/house/for-sale/nassogne/6950/11485698"
        )
        # r = requests.get(f"{self.start_url}{self.type}{self.buy}")
        self.r = requests.get(f"{self.url}", headers=self.headers)
        self.r.raise_for_status()
        self.soup = BeautifulSoup(self.r.content, "html.parser").get_text()
        self.soup = re.sub("\n\n", "", self.soup)
        print(self.soup)

    def save(self):
        with open("test.json", "w") as file:
            file = json.dump(self.soup, file)


if __name__ == "__main__":
    s = Scrapper()
    s.set_up()
    s.save()
