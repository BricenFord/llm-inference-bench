#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "config" / "ollama.json"
SBATCH_TEMPLATE_PATH = ROOT / "templates" / "ollama" / "job.sbatch.template"
CLIENT_TEMPLATE_PATH = ROOT / "templates" / "ollama" / "client.py.template"
OUT_DIR = ROOT / "generated" / "ollama"

def slugify_model(model: str) -> str:
    s = model.strip()
    s = s.replace(":", "_").replace("/", "_")
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()

def render_template(template_text: str, mapping: dict) -> str:
    out = template_text
    for k, v in mapping.items():
        out = out.replace(f"{{{{{k}}}}}", str(v))
    leftover = re.findall(r"\{\{[A-Z0-9_]+\}\}", out)
    if leftover:
        raise RuntimeError(f"Unrendered template keys found: {sorted(set(leftover))}")
    return out

def main():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    models = cfg.get("models", [])
    if not models:
        raise RuntimeError("config/ollama.json: 'models' is empty")

    slurm = cfg["slurm"]
    engine = cfg["engine"]
    pycfg = cfg["python"]
    clientcfg = cfg["client"]

    sbatch_template = SBATCH_TEMPLATE_PATH.read_text(encoding="utf-8")
    client_template = CLIENT_TEMPLATE_PATH.read_text(encoding="utf-8")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rel_out_dir = Path("generated") / "ollama"

    num_ctx_cfg = clientcfg.get("num_ctx", None)
    num_ctx_literal = "None" if num_ctx_cfg is None else str(int(num_ctx_cfg))

    for model in models:
        slug = slugify_model(model)

        job_name = f"ollama_{slug}"

        stdout_dir = slurm["stdout_dir"]
        stderr_dir = slurm["stderr_dir"]

        stdout_file = f"{stdout_dir}/{job_name}_%J_stdout.txt"
        stderr_file = f"{stderr_dir}/{job_name}_%J_stderr.txt"

        client_script_name = f"client_{slug}.py"
        sbatch_name = f"ollama_{slug}.sbatch"

        mapping_common = {
            "PARTITION": slurm["partition"],
            "NODES": slurm["nodes"],
            "NTASKS": slurm["ntasks"],
            "CPUS_PER_TASK": slurm["cpus_per_task"],
            "MEM": slurm["mem"],
            "TIME": slurm["time"],
            "MAIL_USER": slurm["mail_user"],
            "MAIL_TYPE": slurm["mail_type"],
            "CHDIR": slurm["chdir"],
            "JOB_NAME": job_name,
            "STDOUT_DIR": stdout_dir,
            "STDERR_DIR": stderr_dir,
            "RUNS_DIR": slurm["runs_dir"],
            "STDOUT_FILE": stdout_file,
            "STDERR_FILE": stderr_file,
            "CONTAINER_IMAGE": engine["container_image"],
            "MODEL_PATH": engine["model_path"],
            "PORT": engine["port"],
            "STARTUP_SLEEP": engine.get("startup_sleep", 7),
            "MODULE_CUDA": pycfg["module_cuda"],
            "MODULE_PYTHON": pycfg["module_python"],
            "VENV_DIR": pycfg["venv_dir"],
            "REQUIREMENTS_FILE": pycfg["requirements_file"],
            "CLIENT_SCRIPT": str(rel_out_dir / client_script_name),
        }

        sbatch_text = render_template(sbatch_template, mapping_common)

        client_mapping = {
            "HOST": clientcfg["host"],
            "MODEL_NAME": model,
            "CSV_FILE": clientcfg["csv_file"],
            "TIMEOUT_S": clientcfg.get("timeout_s", 60),
            "NUM_CTX": num_ctx_literal,
        }
        client_text = render_template(client_template, client_mapping)

        (OUT_DIR / sbatch_name).write_text(sbatch_text, encoding="utf-8")
        client_path = OUT_DIR / client_script_name
        client_path.write_text(client_text, encoding="utf-8")

        try:
            client_path.chmod(0o755)
        except Exception:
            pass

        print(f"Wrote: {OUT_DIR / sbatch_name}")
        print(f"Wrote: {client_path}")

if __name__ == "__main__":
    main()