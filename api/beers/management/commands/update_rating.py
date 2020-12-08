                beer.name = match['beer']['beer_name']
                beer.abv = match['beer']['beer_abv']
                beer.ibu = match['beer']['beer_ibu']
                beer.untappd_id = match['beer']['bid']
                beer.style = match['beer']['beer_style']
                beer.description = match['beer']['beer_description']
                beer.label_url = match['beer']['beer_label']
                beer.undappd_url = "https://untappd.com/b/"+match['beer']['beer_slug']+"/"+str(match['beer']['bid'])