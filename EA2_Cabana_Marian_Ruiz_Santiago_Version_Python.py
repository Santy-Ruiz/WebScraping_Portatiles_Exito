from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

print("Levantando el navegador local... esto puede tomar unos segundos.")

# Configuración de Selenium para ejecución local
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--log-level=3")

driver = webdriver.Chrome(options=chrome_options)

# Lista global para consolidar los productos de todas las páginas
todos_los_portatiles = []

# Definimos cuántas páginas queremos descargar
paginas_a_descargar = 4

print(f"\nIniciando la extracción de las primeras {paginas_a_descargar} páginas...")

for pagina in range(1, paginas_a_descargar + 1):
    url_dinamica = f"https://www.exito.com/tecnologia/computadores/portatiles?category-1=tecnologia&category-2=computadores&category-3=portatiles&facets=category-1%2Ccategory-2%2Ccategory-3&sort=score_desc&page={pagina}"
    
    print(f"Procesando página {pagina} de {paginas_a_descargar}... ", end="")
    
    try:
        driver.get(url_dinamica)
        # Tiempo de espera
        time.sleep(5)

        # Pasamos el HTML ya renderizado a BeautifulSoup
        soup_pag = BeautifulSoup(driver.page_source, 'html.parser')
        # Buscamos el contenedor usando lambda para ignorar los códigos alfanuméricos variables
        contenedores = soup_pag.find_all("div", class_=lambda x: x and "productCard_productInfo" in x)
        
        conteo_pagina = 0
        for caja in contenedores:
            # Nombre y Marca
            nombre_tag = caja.find("a", {"data-testid": "product-link"})
            nombre = nombre_tag.text.strip() if nombre_tag else "No disponible"
            
            marca_tag = caja.find("h3", class_=lambda x: x and "styles_brand" in x)
            marca = marca_tag.text.strip() if marca_tag else "Genérica"

            # Precio 1: Otros medios de pago
            precio_otros_tag = caja.find("p", {"data-fs-container-price-otros": "true"})
            precio_otros = precio_otros_tag.text.strip() if precio_otros_tag else "Consultar"

            # Precio 2: Tarjeta Aliada (Éxito)
            precio_aliado_tag = caja.find("p", class_=lambda x: x and "allieds-display_bestDiscount__Kb8eD" in x)
            precio_aliado = precio_aliado_tag.text.replace("price", "").strip() if precio_aliado_tag else "No aplica"

            # Descuento general
            descuento_tag = caja.find("div", class_=lambda x: x and "priceSection_container-promotion_discount" in x)
            descuento = descuento_tag.text.strip() if descuento_tag else "0%"
            
            todos_los_portatiles.append({
                "Marca": marca,
                "Computador": nombre,
                "Precio (Otros medios)": precio_otros,
                "Precio (Tarjeta Aliada)": precio_aliado,
                "Descuento": descuento,
                "Ubicación": f"Pág {pagina}"
            })
            conteo_pagina += 1
            
        print(f"¡Completada! Se encontraron {conteo_pagina} productos.")
        
    except Exception as e:
        print(f"Error al procesar la página {pagina}: {str(e)}")

driver.quit()

# Creamos el DataFrame consolidador
df_exito = pd.DataFrame(todos_los_portatiles)

if not df_exito.empty:
    # Eliminamos posibles registros duplicados
    df_exito = df_exito.drop_duplicates(subset=['Computador'])
    print(f"\nExtracción finalizada. Total de productos únicos recolectados: {len(df_exito)}")

     # Exportamos y descargamos automáticamente el archivo
    nombre_archivo = "portatiles_exito_doble_precio.csv"
    df_exito.to_csv(nombre_archivo, index=False, encoding='utf-8-sig', sep=';')
    print(f"\nEl archivo '{nombre_archivo}' fue guardado exitosamente en el directorio actual.")
else:
    print("\nNo se extrajeron datos.")