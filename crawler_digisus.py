"""
crawler_digisus.py – 20 jul 2025
"""

import re, time, requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException)
from webdriver_manager.chrome import ChromeDriverManager

URL       = "https://digisusgmp.saude.gov.br/v1.5/transparencia/downloads"
DEST_DIR  = Path("Documentos_Saude_Brasil")
TIMEOUT   = 30
HEADLESS  = True

FasesMunicipais = {"2018 a 2021", "2022 a 2025"}
FasesEstaduais  = {"2016 a 2019", "2020 a 2023", "2024 a 2027"}

YEARS_MUN = {
    "Plano de Saúde":               {"2019", "2022"},
    "Programação Anual de Saúde":   {str(y) for y in range(2020, 2026)},
    "Relatório Anual de Gestão":    {str(y) for y in range(2020, 2026)},
    "RAG":                          {str(y) for y in range(2020, 2026)},
}
YEARS_EST = {
    "Plano de Saúde":               {"2020", "2024"},
    "Programação Anual de Saúde":   {str(y) for y in range(2020, 2026)},
    "Relatório Anual de Gestão":    {str(y) for y in range(2020, 2026)},
    "RAG":                          {str(y) for y in range(2020, 2026)},
}

LABEL_DOC = {
    "Plano de Saúde":             "Plano de Saúde",
    "Programação Anual de Saúde": "Programação Anual de Saúde",
    "Relatório Anual de Gestão":  "RAG",
    "RAG":                        "RAG",
}
LABEL_VIG = {
    "Plano de Saúde":             "Plano de Saúde",
    "Programação Anual de Saúde": "Programação Anual de Saúde",
    "Relatório Anual de Gestão":  "Relatório Anual de Gestão",
    "RAG":                        "Relatório Anual de Gestão",
}

# ───────── helpers ──────────────────────────────────────────────
def mk_driver():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox"); opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def download(url: str, tgt: Path):
    tgt.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=90) as r:
        r.raise_for_status()
        with open(tgt, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

def safe_click(drv, element):
    drv.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    drv.execute_script("arguments[0].click();", element)

def close_modal(drv):
    for sel in ("button.btn-close","button.close","[data-dismiss='modal']"):
        btn = drv.find_elements(By.CSS_SELECTOR, sel)
        if btn:
            safe_click(drv, btn[0]); return
    # fallback ESC
    from selenium.webdriver.common.keys import Keys
    webdriver.ActionChains(drv).send_keys(Keys.ESCAPE).perform()
    time.sleep(.1)

def link_modal(modal, label):
    try:
        row = modal.find_element(
            By.XPATH,
            ".//h5[contains(text(),'Documentos Vigentes')]/following::tbody[1]"
            f"/tr[td[1][normalize-space()='{label}']][1]")
        return row.find_element(By.CSS_SELECTOR, "a[href*='/downloads/file/']"), "match"
    except NoSuchElementException:
        pass
    try:
        tbody = modal.find_element(
            By.XPATH,
            ".//h5[contains(text(),'Documentos Vigentes')]/following::tbody[1]")
        links = tbody.find_elements(By.CSS_SELECTOR, "a[href*='/downloads/file/']")
        if links:
            return links[-1], "fallback"
    except NoSuchElementException:
        pass
    return None, None

def wait_table(wait, secs=15):
    try:
        sel = (By.CSS_SELECTOR, "table.table-hover tbody")
        wait.until(EC.presence_of_element_located(sel), secs)
        return True
    except TimeoutException:
        return False

def safe_get_municipios(drv, retries=3):
    for _ in range(retries):
        try:
            sel = Select(drv.find_element(By.NAME, "municipio"))
            vals = [o.get_attribute("value") for o in sel.options if o.get_attribute("value")]
            return sel, vals
        except StaleElementReferenceException:
            time.sleep(0.5)
    raise StaleElementReferenceException("combo município instável")

# ───────── crawler ──────────────────────────────────────────────
def crawler():
    drv = mk_driver()
    wait = WebDriverWait(drv, TIMEOUT)
    total = 0
    try:
        drv.get(URL)
        uf_sel   = Select(wait.until(EC.presence_of_element_located((By.NAME, "uf"))))
        fase_sel = Select(wait.until(EC.presence_of_element_located((By.NAME, "fase"))))
        fases    = [o.get_attribute("value") for o in fase_sel.options if o.get_attribute("value")]

        for uf_val in [o.get_attribute("value") for o in uf_sel.options if o.get_attribute("value")]:
            uf_sel.select_by_value(uf_val)
            est_txt = uf_sel.first_selected_option.text
            est_dir = re.sub(r'\s+', '_', est_txt)

            for fase_val in fases:
                fase_sel.select_by_value(fase_val)
                fase_txt = fase_sel.first_selected_option.text.strip()

                # ═════ ESTADUAL ═════
                if fase_txt in FasesEstaduais and wait_table(wait):
                    for doc, anos in YEARS_EST.items():
                        try:
                            header = drv.find_element(By.XPATH, f"//h5[contains(text(), '{doc}')]")
                        except NoSuchElementException:
                            continue
                        for tr in header.find_elements(By.XPATH, "ancestor::tbody//tbody/tr"):
                            ano = tr.find_element(By.CSS_SELECTOR, "td:first-child").text
                            if ano not in anos:
                                continue
                            btns = tr.find_elements(By.CSS_SELECTOR,
                                "button[title='Exibir lista de documentos']")
                            if not btns:
                                continue
                            safe_click(drv, btns[0])

                            modal = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-content")))
                            link, modo = link_modal(modal, LABEL_VIG[doc])
                            if link:
                                nota = "" if modo == "match" else " (últ.vigente)"
                                tgt  = DEST_DIR/est_dir/"Estadual"/LABEL_DOC[doc]/f"{ano}.pdf"
                                if not tgt.exists():
                                    print(f"{est_txt:<25} | ESTADUAL | {doc:<28} | {ano} … baixando{nota}")
                                    download(link.get_attribute("href"), tgt); total += 1
                            close_modal(drv); wait_table(wait)

                # ═════ MUNICIPAL ═════
                if fase_txt in FasesMunicipais:
                    # espera até que o combo tenha pelo menos 2 opções (header + 1 município)
                    try:
                        sel_mun = WebDriverWait(drv, 15).until(
                            lambda d: len(Select(d.find_element(By.NAME, "municipio")).options) > 1
                        )
                    except TimeoutException:
                        print(f"{est_txt:<25} | fase '{fase_txt}' sem municípios — pulando fase")
                        continue

                    # agora captura o combo com tratamento de 'stale'
                    try:
                        mun_sel, mun_vals = safe_get_municipios(drv)
                    except StaleElementReferenceException:
                        print(f"{est_txt:<25} | fase '{fase_txt}' combo instável — pulando fase")
                        continue

                    for mun_val in mun_vals:
                        mun_sel = Select(drv.find_element(By.NAME, "municipio"))
                        mun_sel.select_by_value(mun_val)
                        mun_txt = mun_sel.first_selected_option.text.upper()

                        # espera grade (duas tentativas)
                        if not wait_table(wait) and not wait_table(wait):
                            print(f"{est_txt:<25} | {mun_txt:<20} | fase '{fase_txt}' sem tabela")
                            continue

                        for doc, anos in YEARS_MUN.items():
                            try:
                                header = drv.find_element(By.XPATH, f"//h5[contains(text(), '{doc}')]")
                            except NoSuchElementException:
                                continue
                            for tr in header.find_elements(By.XPATH, "ancestor::tbody//tbody/tr"):
                                ano = tr.find_element(By.CSS_SELECTOR, "td:first-child").text
                                if ano not in anos:
                                    continue
                                btns = tr.find_elements(By.CSS_SELECTOR,
                                    "button[title='Exibir lista de documentos']")
                                if not btns:
                                    continue
                                safe_click(drv, btns[0])

                                modal = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-content")))
                                link, modo = link_modal(modal, LABEL_VIG[doc])
                                if link:
                                    nota = "" if modo == "match" else " (últ.vigente)"
                                    tgt = (
                                        DEST_DIR / est_dir / "Municipal" /
                                        re.sub(r'\s+', '_', mun_txt) /
                                        LABEL_DOC[doc] / f"{ano}.pdf"
                                    )
                                    if not tgt.exists():
                                        print(f"{est_txt:<25} | {mun_txt:<20} | {doc:<28} | {ano} … baixando{nota}")
                                        download(link.get_attribute("href"), tgt); total += 1
                                close_modal(drv); wait_table(wait)
    finally:
        drv.quit()
        print(f"\n✅ Concluído – {total} PDF(s) baixados")

if __name__ == "__main__":
    crawler()
