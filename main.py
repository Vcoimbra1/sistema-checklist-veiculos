from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os
import shutil

app = FastAPI(title="API - Checklist Royal Motors")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
UPLOAD_DIR = "uploads/fotos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que qualquer site acesse sua API
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],
)



# Função para criar o arquivo do banco e as tabelas automaticamente
def iniciar_banco():
    conn = sqlite3.connect("checklist.db")
    cursor = conn.cursor()
    
    # 1. Tabela de Veículos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT UNIQUE NOT NULL,
        marca TEXT,
        modelo TEXT,
        ano INTEGER,
        cor TEXT
    )
    """)
    
    # 2. Tabela de Checklists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        veiculo_id INTEGER NOT NULL,
        data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
        responsavel TEXT,
        estado_limpeza_externa TEXT,
        estado_limpeza_interna TEXT,
        estado_pneus TEXT,
        estado_estepe TEXT,
        observacoes TEXT,
        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
    )
    """)

    # 3. A TABELA QUE FALTAVA: Fotos do Veículo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fotos_veiculo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER NOT NULL,
        tipo_foto TEXT,
        descricao TEXT,
        caminho_arquivo TEXT NOT NULL,
        FOREIGN KEY (checklist_id) REFERENCES checklists (id)
    )
    """)
    
    conn.commit()
    conn.close()

# Executa a função logo que o código rodar
iniciar_banco()

# --- MODELOS DE DADOS (O que a API espera receber) ---
class Veiculo(BaseModel):
    placa: str
    marca: str
    modelo: str
    ano: int
    cor: str

class ChecklistForm(BaseModel):
    veiculo_id: int
    responsavel: str
    estado_limpeza_externa: str
    estado_limpeza_interna: str
    estado_pneus: str
    estado_estepe: str
    observacoes: str | None = None # Opcional, pois pode não ter observação
# --- ROTAS DA API ---

@app.get("/")
def home():
    return FileResponse("index.html")
@app.get("/admin")
def painel_admin():
    return FileResponse("admin.html")

@app.post("/veiculos/")
def cadastrar_veiculo(veiculo: Veiculo):
    conn = sqlite3.connect("checklist.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO veiculos (placa, marca, modelo, ano, cor) VALUES (?, ?, ?, ?, ?)",
            (veiculo.placa.upper(), veiculo.marca, veiculo.modelo, veiculo.ano, veiculo.cor)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return {"mensagem": "Veículo cadastrado com sucesso!", "id_veiculo": novo_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Veículo com esta placa já está cadastrado.")
    finally:
        conn.close()

@app.post("/checklists/")
def criar_checklist(checklist: ChecklistForm):
    conn = sqlite3.connect("checklist.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO checklists (
                veiculo_id, responsavel, estado_limpeza_externa, 
                estado_limpeza_interna, estado_pneus, estado_estepe, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                checklist.veiculo_id, checklist.responsavel, 
                checklist.estado_limpeza_externa, checklist.estado_limpeza_interna, 
                checklist.estado_pneus, checklist.estado_estepe, checklist.observacoes
            )
        )
        conn.commit()
        novo_id = cursor.lastrowid
        return {"mensagem": "Checklist salvo com sucesso!", "id_checklist": novo_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar checklist: {str(e)}")
    finally:
        conn.close()

@app.post("/checklists/{checklist_id}/fotos/")
def subir_foto(
    checklist_id: int, 
    tipo_foto: str = Form(...), 
    descricao: str = Form(""), 
    arquivo: UploadFile = File(...)
):
    # 1. Monta o nome do arquivo para não ter foto repetida (ex: checklist_1_Frontal.jpg)
    extensao = arquivo.filename.split(".")[-1]
    nome_arquivo = f"checklist_{checklist_id}_{tipo_foto}.{extensao}"
    caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo)
    
    # 2. Salva o arquivo físico na pasta do seu computador
    with open(caminho_completo, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)
        
    # 3. Salva o caminho dessa foto no banco de dados SQLite
    conn = sqlite3.connect("checklist.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO fotos_veiculo (checklist_id, tipo_foto, descricao, caminho_arquivo) VALUES (?, ?, ?, ?)",
            (checklist_id, tipo_foto, descricao, caminho_completo)
        )
        conn.commit()
        return {"mensagem": "Foto salva com sucesso!", "caminho": caminho_completo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco: {str(e)}")
    finally:
        conn.close()

@app.get("/api/checklists-completos/")
def listar_checklists():
    conn = sqlite3.connect("checklist.db")
    conn.row_factory = sqlite3.Row # Permite acessar as colunas pelo nome
    cursor = conn.cursor()
    try:
        # Um JOIN clássico para juntar os dados do checklist com o carro!
        cursor.execute("""
            SELECT 
                c.id as checklist_id, 
                v.placa, 
                v.marca, 
                v.modelo, 
                c.data_entrada, 
                c.responsavel
            FROM checklists c
            JOIN veiculos v ON c.veiculo_id = v.id
            ORDER BY c.data_entrada DESC
        """)
        # Transforma o resultado do banco em uma lista de dicionários para o JSON
        checklists = [dict(row) for row in cursor.fetchall()]
        return checklists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")
    finally:
        conn.close()

@app.get("/api/checklist/{checklist_id}/detalhes/")
def buscar_detalhes_checklist(checklist_id: int):
    conn = sqlite3.connect("checklist.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Busca os dados do Checklist e do Veículo (JOIN)
        cursor.execute("""
            SELECT 
                c.id as checklist_id, 
                v.placa, v.marca, v.modelo, v.ano, v.cor,
                c.data_entrada, c.responsavel, 
                c.estado_limpeza_externa, c.estado_limpeza_interna, 
                c.estado_pneus, c.estado_estepe, c.observacoes
            FROM checklists c
            JOIN veiculos v ON c.veiculo_id = v.id
            WHERE c.id = ?
        """, (checklist_id,))
        
        dados_base = cursor.fetchone()
        if not dados_base:
            raise HTTPException(status_code=404, detail="Checklist não encontrado")
        
        resultado = dict(dados_base)
        
        # 2. Busca todas as fotos vinculadas a este checklist
        cursor.execute("SELECT tipo_foto, descricao, caminho_arquivo FROM fotos_veiculo WHERE checklist_id = ?", (checklist_id,))
        fotos = [dict(row) for row in cursor.fetchall()]
        
        resultado["fotos"] = fotos
        
        return resultado
        
    finally:
        conn.close()