import time
import base64
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

class PortalTransparenciaBot:
    def __init__(self, headless=False):
        self.options = Options()
        self.options.add_argument("--window-size=1920,1080")
        if headless:
            self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 15)
        self.short_wait = WebDriverWait(self.driver, 5)
    
    def iniciar(self):
        """Fluxo principal de execução"""
        try:
            # Preparação do ambiente
            os.makedirs("data/screenshots", exist_ok=True)
            
            # Carrega os dados de entrada
            with open("src/entrada_busca.json", "r", encoding="utf-8") as file:
                pessoas = json.load(file)["pessoas"][:10]
            
            # Inicia o processo
            self._iniciar_sessao()
            resultados = []
            
            for idx, pessoa in enumerate(pessoas, 1):
                print(f"\n Processando {idx}/10: {pessoa['nome']}")
                resultado = self._processar_pessoa(pessoa['nome'], idx)
                if resultado:
                    resultados.append(resultado)
            
            # Salva os resultados finais
            self._salvar_resultados(resultados)
            print("\n Processo concluído com sucesso!")
            
        except Exception as e:
            print(f"\n Erro fatal: {str(e)}")
        finally:
            self.driver.quit()
    
    def _iniciar_sessao(self):
        """Prepara a sessão inicial com todos os filtros"""
        print(" Iniciando navegador...")
        self.driver.get("https://portaldatransparencia.gov.br/pessoa/visao-geral")
        self.driver.maximize_window()
        
        # Acessa busca avançada
        self._clicar_com_espera(".d-flex.align-center", "Acessar busca")
        self._rejeitar_cookies()
        
        # Configura filtros
        self._aplicar_filtro_beneficiario()
        print(" Filtros aplicados com sucesso")
    
    def _processar_pessoa(self, nome, idx):
        """Processa uma pessoa individual"""
        try:
            # Limpa e preenche o campo de busca
            campo_busca = self.wait.until(
                EC.presence_of_element_located((By.ID, "termo")))
            campo_busca.clear()
            campo_busca.send_keys(nome)
            
            # Executa a consulta
            self._clicar_com_espera("#btnConsultarPF", "Consultar")
            
            # Verifica se há resultados
            try:
                # Aguarda o resultado aparecer
                resultado = self.short_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "link-busca-nome")))
                resultado.click()
                
                # Captura o screenshot
                screenshot_path = f"data/screenshots/pessoa_{idx}.png"
                self.driver.save_screenshot(screenshot_path)
                
                # Converte para base64
                with open(screenshot_path, "rb") as img:
                    imagem_base64 = base64.b64encode(img.read()).decode("utf-8")
                
                # Prepara os dados para retorno
                dados = {
                    "nome": nome,
                    "indice": idx,
                    "imagem_base64": imagem_base64,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "sucesso"
                }
                
                # Volta para a página de busca
                print(f" Voltando para página de busca...")
                self.driver.back()
                
                # Garante que voltou para a página correta
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "termo")))
                
                # Reaplica os filtros (importante!)
                self._aplicar_filtro_beneficiario()
                
                return dados
                
            except TimeoutException:
                print(f" Nenhum resultado para: {nome}")
                self.driver.back()
                return {
                    "nome": nome,
                    "indice": idx,
                    "status": "sem_resultados",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
        except Exception as e:
            print(f" Erro ao processar {nome}: {str(e)}")
            return {
                "nome": nome,
                "indice": idx,
                "status": "erro",
                "erro": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _aplicar_filtro_beneficiario(self):
        """Aplica o filtro de beneficiário social"""
        try:
            # Expande a seção de refinamento
            self._clicar_com_espera(
                "//button[@class='header' and span[contains(text(), 'Refine a Busca')]]",
                "Refine a Busca",
                by=By.XPATH
            )
            
            # Marca a opção de beneficiário
            self._clicar_com_espera(
                "//label[@for='beneficiarioProgramaSocial']",
                "Beneficiário Social",
                by=By.XPATH
            )
            
        except Exception as e:
            print(f" Erro ao aplicar filtro: {str(e)}")
            raise
    
    def _clicar_com_espera(self, seletor, descricao, by=By.CSS_SELECTOR):
        """Wrapper para clicar em elementos com tratamento de erro"""
        try:
            elemento = self.wait.until(
                EC.element_to_be_clickable((by, seletor)))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)
            time.sleep(0.5)
            elemento.click()
            print(f" {descricao} - OK")
            return True
        except Exception as e:
            print(f" Falha ao clicar em {descricao}: {str(e)}")
            raise
    
    def _rejeitar_cookies(self):
        """Tenta rejeitar os cookies se aparecerem"""
        try:
            botao = self.short_wait.until(
                EC.element_to_be_clickable((By.ID, "accept-minimal-btn")))
            botao.click()
            print(" Cookies rejeitados")
        except TimeoutException:
            pass
    
    def _salvar_resultados(self, resultados):
        """Salva os resultados em arquivo JSON"""
        dados_saida = {
            "metadata": {
                "data_processamento": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_pessoas": len(resultados),
                "sucessos": sum(1 for r in resultados if r.get("status") == "sucesso"),
                "erros": sum(1 for r in resultados if r.get("status") == "erro"),
                "sem_resultados": sum(1 for r in resultados if r.get("status") == "sem_resultados")
            },
            "resultados": resultados
        }
        
        with open("data/resultado_final.json", "w", encoding="utf-8") as f:
            json.dump(dados_saida, f, ensure_ascii=False, indent=4)
        
        print(f" Resultados salvos em data/resultado_final.json")

if __name__ == "__main__":
    print("="*50)
    print("INICIANDO ROBÔ PORTAL TRANSPARÊNCIA")
    print("="*50)
    
    bot = PortalTransparenciaBot(headless=False)  # Altere para True em produção
    bot.iniciar()