# from bs4 import BeautifulSoup
# import os
# from django.core.files import File
# from django.conf import settings
# from fypapp.models import Laptop

# # Load the HTML file
# html_file_path = os.path.join(settings.BASE_DIR, "path_to_extracted_html_file.html")
# with open(html_file_path, "r", encoding="utf-8") as file:
#     soup = BeautifulSoup(file, "html.parser")

# # Find all cards
# cards = soup.find_all("div", class_="card")

# for card in cards:
#     name = card.find("div", class_="name").text.strip()
#     specs = card.find("p").text.strip().split("\n")
    
#     # Extract specs
#     processor = specs[0].split(":")[-1].strip()
#     ram = specs[1].split(":")[-1].strip()
#     storage = specs[2].split(":")[-1].strip()

#     price_text = card.find("div", class_="price").text.strip()
#     price = float(price_text.split("$")[-1])

#     img_tag = card.find("img")
#     image_path = img_tag["src"] if img_tag else ""

#     # Save to database
#     laptop = Laptop(
#         name=name,
#         processor=processor,
#         ram=ram,
#         storage=storage,
#         price=price,
#     )

#     # Save image if applicable
#     if image_path:
#         image_name = os.path.basename(image_path)
#         laptop.image.save(image_name, File(open(image_path, "rb")))

#     laptop.save()
#     print(f"Saved {name} to database.")
