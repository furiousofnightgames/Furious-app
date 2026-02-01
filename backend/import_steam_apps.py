import json
import os
import sys

# Adicionar o diretório raiz ao sys.path para importar módulos do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import get_session, init_db
from backend.models.models import SteamApp
from backend.steam_service import steam_client
from sqlmodel import select, func

def import_steam_apps():
    # Garantir que o DB está inicializado (tabelas criadas)
    init_db()
    
    # IMPORTANTE: Agora lemos do diretório de dados (Roaming), para onde o main.py copiou o arquivo.
    from backend.db import get_db_path
    db_dir = get_db_path().parent
    list_path = os.path.join(db_dir, 'steam_applist.json')
    
    if not os.path.exists(list_path):
        print(f"[Import] Erro: Arquivo seed não encontrado em {list_path}")
        return

    # 1. Verificar se já existem apps
    session = get_session()
    try:
        existing_count = session.exec(select(func.count(SteamApp.appid))).one()
        if existing_count > 0:
            print(f"O banco já contém {existing_count} apps. Pulando importação.")
            return
    except Exception as e:
        print(f"Erro ao verificar contagem: {e}")
    finally:
        session.close()

    # 2. Ler JSON
    print("Lendo steam_applist.json...")
    try:
        with open(list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            apps = data.get('applist', {}).get('apps', [])
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return

    # 3. Importar em lotes
    total = len(apps)
    print(f"Importando {total} apps...")
    batch_size = 2000
    
    for i in range(0, total, batch_size):
        batch_session = get_session()
        try:
            batch = apps[i:i + batch_size]
            db_batch = []
            for app in batch:
                name = app.get('name', '')
                if not name:
                    continue
                
                norm = steam_client.normalize_game_name(name)
                db_batch.append(SteamApp(
                    appid=app['appid'],
                    name=name,
                    normalized_name=norm
                ))
            
            batch_session.add_all(db_batch)
            batch_session.commit()
            if (i + batch_size) % 10000 == 0 or (i + batch_size) >= total:
                print(f"Progresso: {min(i + batch_size, total)} / {total}")
        except Exception as e:
            print(f"Erro no lote {i}: {e}")
            batch_session.rollback()
        finally:
            batch_session.close()
            
    print("Importação concluída com sucesso!")

if __name__ == "__main__":
    import_steam_apps()
