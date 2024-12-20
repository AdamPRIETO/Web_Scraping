# créer l'Environment: scrapy startproject projet_groupe

import scrapy
import re

class ProduitSpider(scrapy.Spider):
    name = "produit"
    allowed_domains = ["www.auchan.fr"]
    start_urls = ["https://www.auchan.fr"]

    nombre_lien = 0

    def caracteristiques(self, response, element):
        caracteristique = response.css("div.product-description__feature-values")
        resultat = None
        for car in caracteristique:
            label = car.css("span::text").get()
            if label and label.strip() == element:
                resultat = car.css("span.product-description__feature-value::text").get()
                break
        return resultat

    def parse(self, response):

        if self.nombre_lien >= 1000:
            self.crawler.engine.close_spider(self)
            return
        else:
            url = response.url

            if re.match(r"https://www\.auchan\.fr/.+/pr-.+", url):
                self.nombre_lien += 1
                product_title = response.css('div.offer-selector__name--large h1::text').get()
                vendeur = response.css('div.offer-selector__seller span.offer-selector__marketplace-label span.bolder::text').get()
                retrait = response.css("div.delivery-promise__offer-cell--name span::text").get()
                product_price = response.css('div.product-price.product-price--large.bolder.text-dark-color::text').get()

                licence = self.caracteristiques(response, "Licence")
                Descriptif_produit = self.caracteristiques(response, "Descriptif produit (FPF)")
                marque = self.caracteristiques(response, "Marque")
                GTIN = self.caracteristiques(response, "GTIN")

                produit_detail=response.css("div.product-description__content-wrapper")
                ref_EAN=produit_detail.css("div.product-description__feature-values::text").get().split()

                etoile = response.css("span.rating-value--extra-big::text").get()

                etoile_qualite_prix = None
                etoile_caracteristique = response.css("ul.reviews__list-rating--secondary li")
                for et in etoile_caracteristique:
                    label = et.css("span::text").get()
                    if label and label.strip() == "Rapport qualité / prix":
                        etoile_qualite_prix = et.css("meter::attr(value)").get()
                        break

                yield {
                    "url": url,
                    "product_title": product_title.strip() if product_title else None,
                    "vendeur": vendeur.strip() if vendeur else None,
                    "retrait": retrait,
                    "product_price": product_price.strip() if product_price else None,
                    "licence": licence,
                    "Descriptif_produit": Descriptif_produit,
                    "marque": marque,
                    "GTIN": GTIN,
                    "ref_EAN": ref_EAN,
                    "etoile": etoile,
                    "etoile_qualite_prix": etoile_qualite_prix
                    
                }
        
        links = [link for link in response.css("a::attr(href)").getall() if link.startswith("/")]
        yield from response.follow_all(links, callback=self.parse)


# scrapy crawl produit -O produit.csv



        
