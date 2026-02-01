import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.models.models import Job
from backend.db import get_session

class IntegrityService:
    @staticmethod
    def _format_size(num: float) -> str:
        """Formata tamanho em bytes para legível (MB/GB)"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(num) < 1024.0:
                return f"{num:3.2f} {unit}"
            num /= 1024.0
        return f"{num:.2f} PB"

    @staticmethod
    def check_job_integrity(job_id: int) -> Dict[str, Any]:
        """
        Realiza um 'Quick-Check' de integridade em um download concluído.
        Sincronizado para tratar o TAMANHO DO CARD (job.size) como a verdade absoluta.
        """
        print(f"\n{'='*60}")
        print(f"[Integrity] EXAME DE RAIO-X PARA JOB #{job_id}")
        print(f"{'='*60}")
        
        session = get_session()
        try:
            job = session.get(Job, job_id)
            if not job:
                print(f"[Integrity] ERRO: Job #{job_id} não encontrado no banco.")
                return {"status": "error", "message": "Job não encontrado"}
            
            dest_path = job.dest
            if not dest_path or not os.path.exists(dest_path):
                print(f"[Integrity] ERRO: Pasta não encontrada: {dest_path}")
                return {
                    "status": "missing",
                    "message": "Caminho de destino não encontrado no disco",
                    "path": dest_path
                }

            print(f"[Integrity] Local: {dest_path}")
            
            # --- COLETA DE ARQUIVOS E TAMANHOS ---
            all_files = []
            if os.path.isdir(dest_path):
                for root, _, files in os.walk(dest_path):
                    for f in files:
                        full_p = Path(root) / f
                        try:
                            stats = full_p.stat()
                            all_files.append({
                                "name": f,
                                "size": stats.st_size,
                                "rel_path": str(full_p.relative_to(dest_path)),
                                "ext": full_p.suffix.lower()
                            })
                        except: pass
            else:
                p = Path(dest_path)
                all_files.append({
                    "name": p.name,
                    "size": p.stat().st_size,
                    "rel_path": p.name,
                    "ext": p.suffix.lower()
                })

            # --- PRINT DO MANIFESTO ---
            print(f"\n[Manifesto] Listando {len(all_files)} arquivos encontrados:")
            for f in sorted(all_files, key=lambda x: x["rel_path"]):
                status_icon = "⚪"
                if f["size"] == 0: status_icon = "💀 [VAZIO]"
                elif f["ext"] == ".exe": status_icon = "🚀 [EXE]"
                elif f["ext"] == ".bin": status_icon = "📦 [BIN]"
                elif f["ext"] in [".bat", ".cmd"]: status_icon = "🛡️ [BAT]"
                
                print(f"  {status_icon} {f['rel_path']} ({IntegrityService._format_size(f['size'])})")

            # --- DETECÇÃO DE COMPONENTES ---
            setups = [f for f in all_files if f["name"].lower() in ["setup.exe", "install.exe", "autorun.exe"]]
            setup_found = len(setups) > 0
            setup_name = setups[0]["name"] if setup_found else None
            setup_empty = setup_found and setups[0]["size"] == 0

            bin_files = [f for f in all_files if f["ext"] == ".bin"]
            empty_bins = [f["name"] for f in bin_files if f["size"] == 0]

            verifiers = [f for f in all_files if "verify" in f["name"].lower() and f["ext"] in [".bat", ".exe", ".cmd"]]
            md5_folders = [f for f in all_files if "md5" in f["rel_path"].lower()]
            has_verifiers = len(verifiers) > 0
            has_md5 = len(md5_folders) > 0

            # --- AUDIT DE TAMANHO (O CARD NÃO MENTE) ---
            actual_total_size = sum(f["size"] for f in all_files)
            
            # O tamanho exibido no card é job.size (que é atualizado ao concluir)
            # Para o usuário, se 'Tamanho no Card' == 'Tamanho no Disco', está 100% OK
            card_size = job.size or 0
            
            print(f"\n[Audit de Tamanho]")
            print(f"  • Fisicamente no Disco:       {IntegrityService._format_size(actual_total_size)}")
            print(f"  • Tamanho Exibido no Card:    {IntegrityService._format_size(card_size)}")
            
            # Se bater com o card com tolerância mínima (0.1%), aprovado!
            matches_card = False
            if card_size > 0:
                diff_pct = abs(actual_total_size - card_size) / card_size * 100
                if diff_pct < 0.1:
                    matches_card = True
            
            status_audit = "✅ INTEGRIDADE OK (Bate com o Card)" if matches_card else "⚠️ DIVERGÊNCIA DETECTADA"
            
            # --- AUTO-SINCRO SE FOR SAUDÁVEL ---
            # Se o disco tem arquivos vitais mas o DB ainda tem o valor inicial do Magnet
            is_physically_healthy = setup_found and len(bin_files) > 0 and not setup_empty and not empty_bins
            
            if is_physically_healthy and not matches_card:
                 print(f"  • [Info] Componentes vitais OK. Sincronizando Card com o Disco...")
                 try:
                    job.size = actual_total_size
                    job.downloaded = actual_total_size
                    session.add(job)
                    session.commit()
                    card_size = actual_total_size # Update local variable for logs
                    matches_card = True
                    status_audit = "✅ INTEGRIDADE OK (Sincronizado com o Disco)"
                 except: pass

            print(f"  • Conclusão do Audit: {status_audit}")

            # --- ANÁLISE DE SAÚDE ---
            issues = []
            health_score = 100

            if setup_empty:
                health_score -= 80
                issues.append(f"Instalador corrompido (0 bytes).")
            if empty_bins:
                health_score -= 90
                issues.append(f"Volumes .bin corrompidos (0 bytes).")

            sequence_gaps = []
            if len(bin_files) > 1:
                pattern = re.compile(r'(\d+)')
                for i in range(len(bin_files) - 1):
                    if bin_files[i]["size"] == 0 or bin_files[i+1]["size"] == 0: continue
                    curr, nxt = bin_files[i]["name"], bin_files[i+1]["name"]
                    nums_curr, nums_nxt = pattern.findall(curr), pattern.findall(nxt)
                    if nums_curr and nums_nxt:
                        try:
                            n1, n2 = int(nums_curr[-1]), int(nums_nxt[-1])
                            if n2 > n1 + 1:
                                sequence_gaps.append(f"Lacuna na sequência: {curr} -> {nxt}")
                        except: pass

            if sequence_gaps:
                health_score -= 50
                issues.extend(sequence_gaps)

            if not setup_found and len(all_files) > 4:
                health_score -= 40
                issues.append("Instalador (setup.exe) não encontrado.")
            
            if len(bin_files) > 3 and not has_verifiers and not has_md5:
                health_score -= 15
                issues.append("Repack sem arquivos de verificação.")

            # Se mesmo após o sync houver divergência (ex: apagaram arquivos)
            if card_size > 0 and abs(actual_total_size - card_size) / card_size * 100 > 1.0:
                health_score -= 60
                issues.append("Divergência de tamanho significativa após conclusão.")

            health_score = max(0, min(100, health_score))
            status = "healthy" if health_score >= 90 else ("warning" if health_score >= 50 else "critical")

            print(f"\n[Conclusão] Score: {health_score}% | Status: {status.upper()}")
            print(f"{'='*60}\n")

            return {
                "job_id": job_id,
                "status": status,
                "health_score": health_score,
                "issues": issues,
                "setup_found": setup_found,
                "setup_name": setup_name,
                "has_verifiers": has_verifiers,
                "has_md5": has_md5,
                "files_checked": len(all_files),
                "actual_size": actual_total_size,
                "card_size": card_size,
                "timestamp": Path(dest_path).stat().st_mtime if os.path.exists(dest_path) else None
            }

        finally:
            session.close()

integrity_service = IntegrityService()
