"""SpectralBio scientific demo for Hugging Face Spaces."""

from __future__ import annotations

import base64
import html
import json
import mimetypes
import os
import random
from functools import lru_cache
from pathlib import Path
from typing import Any

import gradio as gr
import numpy as np
import plotly.graph_objects as go
import torch
from scipy.linalg import eigvalsh
from sklearn.preprocessing import MinMaxScaler
from transformers import EsmForMaskedLM, EsmTokenizer

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

MODEL_NAME = "facebook/esm2_t30_150M_UR50D"
WINDOW_RADIUS = 40
ALPHA = 0.55
AA_LIST = list("ACDEFGHIKLMNPQRSTVWY")
AA_SET = set(AA_LIST)
AA_TO_THREE = {
    "A": "Ala", "C": "Cys", "D": "Asp", "E": "Glu", "F": "Phe",
    "G": "Gly", "H": "His", "I": "Ile", "K": "Lys", "L": "Leu",
    "M": "Met", "N": "Asn", "P": "Pro", "Q": "Gln", "R": "Arg",
    "S": "Ser", "T": "Thr", "V": "Val", "W": "Trp", "Y": "Tyr",
}

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
LINKS = {
    "github": "https://github.com/DaviBonetto/SpectralBio",
    "dataset": "https://huggingface.co/datasets/DaviBonetto/SpectralBio-ClinVar",
    "clawrxiv": "http://www.clawrxiv.io",
    "skill": "https://github.com/DaviBonetto/SpectralBio/blob/main/SKILL.md",
    "space": "https://huggingface.co/spaces/DaviBonetto/spectralbio-demo",
    "claw": "https://claw4s.github.io",
    "author": "https://github.com/DaviBonetto",
}

TP53_SEQUENCE = (
    "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP"
    "DEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAK"
    "SVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHER"
    "CSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSS"
    "CMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPP"
    "GSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGS"
    "RAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD"
)
BRCA1_SEQUENCE = (
    "MDLSALRVEEVQNVINAMQKILECPICLELIKEPVSTKCDHIFCKFCMLKLLNQKKGPSQ"
    "CPLCKNDITKRSLQESTRFSQLVEELLKIICAFQLDTGLEYANSYNFAKKENNSPEHLKD"
    "EVSIIQSMGYRNRAKRLLQSEPENPSLQETSLSVQLSNLGTVRTLRTKQRIQPQKTSVYI"
    "ELGSDSSEDTVNKATYCSVGDQELLQITPQGTRDEISLDSAKKAACEFSETDVTNTEHHQ"
    "PSNNDLNTTEKRAAERHPEKYQGSSVSNLHVEPCGTNTHASSLQHENSSLLLTKDRMNVE"
    "KAEFCNKSKQPGLARSQHNRWAGSKETCNDRRTPSTEKKVDLNADPLCERKEWNKQKLPC"
    "SENPRDTEDVPWITLNSSIQKVNEWFSRSDELLGSDDSHDGESESNAKVADVLDVLNEVD"
    "EYSGSSEKIDLLASDPHEALICKSERVHSKSVESNIEDKIFGKTYRKKASLPNLSHVTEN"
    "LIIGAFVTEPQIIQERPLTNKLKRKRRPTSGLHPEDFIKKADLAVQKTPEMINQGTNQTE"
    "QNGQVMNITNSGHENKTKGDSIQNEKNPNPIESLEKESAFKTKAEPISSSISNMELELNI"
    "HNSKAPKKNRLRRKSSTRHIHALELVVSRNLSPPNCTELQIDSCSSSEEIKKKKYNQMPV"
    "RHSRNLQLMEGKEPATGAKKSNKPNEQTSKRHDSDTFPELKLTNAPGSFTKCSNTSELKE"
    "FVNPSLPREEKEEKLETVKVSNNAEDPKDLMLSGERVLQTERSVESSSISLVPGTDYGTQ"
    "ESISLLEVSTLGKAKTEPNKCVSQCAAFENPKGLIHGCSKDNRNDTEGFKYPLGHEVNHS"
    "RETSIEMEESELDAQYLQNTFKVSKRQSFAPFSNPGNAEEECATFSAHSGSLKKQSPKVT"
    "FECEQKEENQGKNESNIKPVQTVNITAGFPVVGQKDKPVDNAKCSIKGGSRFCLSSQFRG"
    "NETGLITPNKHGLLQNPYRIPPLFPIKSFVKTKCKKNLLEENFEEHSMSPEREMGNENIP"
    "STVSTISRNNIRENVFKEASSSNINEVGSSTNEVGSSINEIGSSDENIQAELGRNRGPKL"
    "NAMLRLGVLQPEVYKQSLPGSNCKHPEIKKQEYEEVVQTVNTDFSPYLISDNLEQPMGSS"
    "HASQVCSETPDDLLDDGEIKEDTSFAENDIKESSAVFSKSVQKGELSRSPSPFTHTHLAQ"
    "GYRRGAKKLESSEENLSSEDEELPCFQHLLFGKVNNIPSQSTRHSTVATECLSKNTEENL"
    "LSLKNSLNDCSNQVILAKASQEHHLSEETKCSASLFSSQCSELEDLTANTNTQDPFLIGS"
    "SKQMRHQSESQGVGLSDKELVSDDEERGTGLEENNQEEQSMDSNLGEAASGCESETSVSE"
    "DCSGLSSQSDILTTQQRDTMQHNLIKLQQEMAELEAVLEQHGSQPSNSYPSIISDSSALE"
    "DLRNPEQSTSEKAVLTSQKSSEYPISQNPEGLSADKFEVSADSSTSKNKEPGVERSSPSK"
    "CPSLDDRWYMHSCSGSLQNRNYPSQEELIKVVDVEEQQLEESGPHDLTETSYLPRQDLEG"
    "TPYLESGISLFSDDPESDPSEDRAPESARVGNIPSSTSALKVPQLKVAESAQSPAAAHTT"
    "DTAGYNAMEESVSREKPELTASTERVNKRMSMVVSGLTPEEFMLVYKFARKHHITLTNLI"
    "TEETTHVVMKTDAEFVCERTLKYFLGIAGGKWVVSYFWVTQSIKERKMLNEHDFEVRGDV"
    "VNGRNHQGPKRARESQDRKIFRGLEICCYGPFTNMPTDQLEWMVQLCGASVVKELSSFTL"
    "GTGVHPIVVVQPDAWTEDNGFHAIGQMCEAPVVTREWVLDSVALYQCQELDTYLIPQIPH"
    "SHY"
)
SEQUENCES = {"TP53": TP53_SEQUENCE, "BRCA1": BRCA1_SEQUENCE}

PRESETS = [
    {"label": "TP53 R175H", "gene": "TP53", "position_0_indexed": 174, "mutant_aa": "H", "note": "Classic TP53 hotspot in the DNA-binding domain."},
    {"label": "TP53 R248W", "gene": "TP53", "position_0_indexed": 247, "mutant_aa": "W", "note": "DNA-contact hotspot with a large structural perturbation."},
    {"label": "TP53 R273H", "gene": "TP53", "position_0_indexed": 272, "mutant_aa": "H", "note": "Canonical TP53 hotspot used across pathogenicity benchmarks."},
    {"label": "TP53 P72R", "gene": "TP53", "position_0_indexed": 71, "mutant_aa": "R", "note": "Benchmark benign variant and a useful counterexample for model stress-testing."},
    {"label": "BRCA1 M1775R", "gene": "BRCA1", "position_0_indexed": 1774, "mutant_aa": "R", "note": "Pathogenic BRCA1 BRCT-domain example from the local artifact set."},
]
PRESET_BY_LABEL = {item["label"]: item for item in PRESETS}

SUMMARY_FALLBACK = {
    "auc_best_sps": 0.5988,
    "auc_ll_proper": 0.5956,
    "auc_best_pair": 0.7498,
    "auc_best_triple": 0.7264,
    "n_total": 255,
    "n_pathogenic": 115,
    "n_benign": 140,
    "reproducibility_delta": 0.0,
    "n_brca1": 100,
    "scoring_time_seconds": 1447.3,
    "best_pair_desc": "0.55*frob_dist + 0.45*ll_proper",
    "brca1_aucs": {"ll_proper": 0.9174, "frob_dist": 0.6401},
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
:root{--bg:#0f1117;--card:#1a1d27;--border:#2a2d3a;--text:#f1f5f9;--muted:#94a3b8;--faded:#475569;--violet:#7c3aed;--violet-light:#a78bfa;--teal:#2dd4bf;--path:#f87171;--benign:#4ade80;--uncertain:#fbbf24;--white:#ffffff}
html,body,.gradio-container,.gradio-container>.contain,.gradio-container .wrap{background:var(--bg)!important;color:var(--text)!important;font-family:'Inter',ui-sans-serif,system-ui,sans-serif!important}
.gradio-container{--body-background-fill:var(--bg);--background-fill-primary:var(--bg);--background-fill-secondary:var(--card);--block-background-fill:transparent;--block-border-color:transparent;--border-color-primary:var(--border);--input-background-fill:var(--card);--input-border-color:var(--border);--color-accent:var(--violet);--color-accent-soft:rgba(124,58,237,.18);--body-text-color:var(--text)}
.gradio-container .block,.gradio-container .gr-block,.gradio-container .gr-panel,.gradio-container .gr-box,.gradio-container .gr-group,.gradio-container .gr-form,.gradio-container .form,.gradio-container .panel{background:transparent!important;border:0!important;box-shadow:none!important}
.gradio-container [role='tablist']{display:flex!important;justify-content:center!important;align-items:center!important;gap:12px!important;max-width:760px;margin:8px auto 28px auto!important;padding:8px!important;background:var(--card)!important;border:1px solid var(--border)!important;border-radius:26px!important;position:sticky;top:12px;z-index:30}.gradio-container [role='tab']{flex:1 1 0!important;min-height:48px!important;border:1px solid var(--border)!important;border-radius:18px!important;background:transparent!important;color:var(--muted)!important;font-size:14px!important;font-weight:600!important;letter-spacing:-0.02em!important;padding:12px 18px!important;transition:background .2s ease,border-color .2s ease,color .2s ease}.gradio-container [role='tab'][aria-selected='true']{background:var(--violet)!important;border-color:var(--violet)!important;color:var(--white)!important}
.surface-card{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:20px!important}.compact-card{padding:16px!important}
label,input,textarea,select,h1,h2,h3,h4,p,span,td,th,code,pre,div{font-family:'Inter',ui-sans-serif,system-ui,sans-serif!important}
input,textarea,select{background:var(--card)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:12px!important}input::placeholder,textarea::placeholder{color:var(--faded)!important}
.primary-action button{min-height:44px!important;background:var(--violet)!important;border:1px solid var(--violet)!important;color:var(--white)!important;border-radius:12px!important;font-size:14px!important;font-weight:600!important}.preset-btn button{min-height:38px!important;background:var(--bg)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:10px!important;font-size:12px!important;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace!important}.preset-btn button:hover,.secondary-link:hover{border-color:var(--violet)!important;color:var(--violet-light)!important}
.figure-media,.plot-shell{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;overflow:hidden!important}.figure-media img{border-radius:12px!important}#hero-image{border-radius:16px!important}
.copy-card p,.copy-card li{line-height:1.7;font-size:14px}.copy-card pre,.copy-card code,.markdown pre,.markdown code{background:var(--bg)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:12px!important;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace!important}.copy-card pre,.markdown pre{padding:14px!important;overflow-x:auto}
.helper-text{margin-top:10px;color:var(--muted);font-size:12px;line-height:1.6}.helper-text code{color:var(--white)}.link-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.secondary-link{display:inline-flex;justify-content:center;align-items:center;min-height:44px;background:var(--card);border:1px solid var(--border);border-radius:12px;color:var(--muted);text-decoration:none;font-size:13px;font-weight:500}
.hero-card{max-width:1080px;margin:18px auto 0 auto;text-align:center}.hero-logo-stack{display:grid;justify-items:center;gap:16px;margin-top:22px;padding-top:20px;border-top:1px solid var(--border)}.hero-logo-row{display:flex;justify-content:center;align-items:stretch;gap:20px;flex-wrap:wrap}.hero-logo-panel{display:flex;justify-content:center;align-items:center;padding:14px 18px;border:1px solid var(--border);border-radius:14px;background:linear-gradient(180deg,rgba(26,29,39,.95),rgba(22,26,36,.95));min-height:110px}.hero-logo-panel-princeton{background:linear-gradient(180deg,rgba(148,163,184,.24),rgba(100,116,139,.2));border-color:rgba(148,163,184,.38)}.hero-logo{width:auto;object-fit:contain;display:block}.hero-logo-stanford{width:370px;max-width:42vw;filter:brightness(1.07)}.hero-logo-princeton{width:390px;max-width:44vw;filter:drop-shadow(0 0 1px rgba(241,245,249,.95)) drop-shadow(0 0 10px rgba(148,163,184,.45))}.hero-clawrxiv-logo{width:440px;max-width:58vw;object-fit:contain;display:block;filter:brightness(1.1) contrast(1.08)}.hero-badge{display:inline-flex;align-items:center;background:var(--violet);color:var(--white);border-radius:20px;padding:8px 14px;font-size:12px;font-weight:600}.hero-chip-row{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:20px}.hero-chip{display:inline-flex;align-items:center;gap:12px;padding:12px 16px;border:1px solid var(--border);border-radius:24px;background:var(--card);color:var(--text);text-decoration:none}.hero-chip:hover{border-color:var(--violet)!important}.hero-chip-meta{display:flex;flex-direction:column;gap:2px;text-align:left}.hero-chip-title{font-size:14px;font-weight:600;color:var(--text)}.hero-chip-subtitle{font-size:12px;color:var(--muted)}.hero-chip-mark{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:999px;background:var(--violet);color:var(--white);font-size:12px;font-weight:600}
.abstract-card{max-width:980px;margin:20px auto 0 auto;text-align:center}.abstract-label{color:var(--faded);font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase}.abstract-actions{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:18px}.cta-link{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 18px;border-radius:12px;border:1px solid var(--border);background:var(--card);color:var(--text);text-decoration:none;font-size:13px;font-weight:600}.cta-link:hover{border-color:var(--violet)!important;color:var(--violet-light)!important}.cta-link-primary{background:#22d3ee;border-color:#22d3ee;color:#082f49}.cta-link-primary:hover{background:#67e8f9;border-color:#67e8f9;color:#082f49!important}
.stats-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;max-width:1080px;margin:20px auto 0 auto}
.feature-glossary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}.feature-tile{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px}.feature-tile h4{margin:0;font-size:13px;font-weight:600;letter-spacing:-0.02em}.feature-tile p{margin:8px 0 0 0;color:var(--muted);font-size:13px;line-height:1.7}.feature-tone-violet{color:var(--violet)}.feature-tone-light{color:var(--violet-light)}.feature-tone-teal{color:var(--teal)}.feature-tone-white{color:var(--white)}.discussion-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}
.analysis-loading-shell{display:grid;gap:14px}.loading-spinner{display:inline-block;width:20px;height:20px;border-radius:999px;border:2px solid rgba(167,139,250,.22);border-top-color:var(--violet-light);animation:spin 1s linear infinite}.loading-track{position:relative;height:8px;border-radius:999px;background:#12141c;border:1px solid var(--border);overflow:hidden}.loading-track span{position:absolute;inset:0 auto 0 -40%;width:40%;background:linear-gradient(90deg,transparent,rgba(167,139,250,.9),transparent);animation:loading-slide 1.4s ease-in-out infinite}
.nav-primary-btn button,.nav-secondary-btn button{min-height:46px!important;border-radius:12px!important;font-size:14px!important;font-weight:600!important}.nav-primary-btn button{background:var(--violet)!important;border:1px solid var(--violet)!important;color:var(--white)!important}.nav-secondary-btn button{background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text)!important}.nav-secondary-btn button:hover{border-color:var(--violet)!important;color:var(--violet-light)!important}
@keyframes spin{to{transform:rotate(360deg)}}@keyframes loading-slide{0%{transform:translateX(0)}100%{transform:translateX(350%)}}
@media (max-width:900px){.gradio-container [role='tablist']{max-width:none;gap:8px;padding:6px}.gradio-container [role='tab']{min-width:0;padding:10px 12px!important;font-size:12px!important}.hero-logo-row{gap:12px}.hero-logo-panel{padding:12px 14px;min-height:92px}.hero-logo-stanford{width:300px;max-width:78vw}.hero-logo-princeton{width:320px;max-width:82vw}.hero-clawrxiv-logo{width:330px;max-width:84vw}.stats-grid{grid-template-columns:1fr}.link-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.feature-glossary-grid,.discussion-grid{grid-template-columns:1fr}}
@media (max-width:680px){.gradio-container [role='tablist']{top:8px}.link-grid{grid-template-columns:1fr}.hero-chip-row,.abstract-actions{flex-direction:column}.hero-chip,.cta-link{width:100%}}
"""


def resolve_existing(candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_json_file(candidates: list[Path], fallback: Any) -> Any:
    path = resolve_existing(candidates)
    if path is None:
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def file_uri(path: Path | None) -> str:
    if path is None:
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


SUMMARY = load_json_file([DATA_DIR / "summary.json", ROOT.parent / "colab" / "results" / "summary.json"], SUMMARY_FALLBACK)
SCORES = load_json_file([DATA_DIR / "scores.json", ROOT.parent / "colab" / "results" / "scores.json"], [])
TP53_VARIANTS = load_json_file([DATA_DIR / "tp53_variants.json", ROOT.parent / "colab" / "results" / "tp53_variants.json"], [])
BRCA1_VARIANTS = load_json_file([DATA_DIR / "brca1_variants.json", ROOT.parent / "hf_publish" / "brca1_variants.json"], [])
RESULTS_FIGURE_PATH = resolve_existing([ASSET_DIR / "figures.png", ROOT.parent / "colab" / "results" / "figures.png"])
HERO_BG_PATH = resolve_existing([ASSET_DIR / "hero_bg.png.png"])
METHOD_DIAGRAM_PATH = resolve_existing([ASSET_DIR / "method_diagram.png.png"])
ESM2_LAYERS_PATH = resolve_existing([ASSET_DIR / "esm2_layers.png.jpeg"])
STANFORD_LOGO_URI = file_uri(resolve_existing([ASSET_DIR / "Stanford_logo.png"]))
PRINCETON_LOGO_URI = file_uri(resolve_existing([ASSET_DIR / "Princenton_logo.png"]))
CLAWRXIV_LOGO_URI = file_uri(resolve_existing([ASSET_DIR / "clawRxiv_logo.png"]))

REFERENCE_COMBINED = np.array([ALPHA * row["frob_dist"] + (1.0 - ALPHA) * row["ll_proper"] for row in SCORES], dtype=float)
if REFERENCE_COMBINED.size == 0:
    REFERENCE_COMBINED = np.array([0.0, 1.0], dtype=float)
REFERENCE_COMBINED_SORTED = np.sort(REFERENCE_COMBINED)
REFERENCE_SCALER = MinMaxScaler().fit(REFERENCE_COMBINED.reshape(-1, 1))

VARIANT_INDEX: dict[tuple[str, int, str], dict[str, Any]] = {}
for row in TP53_VARIANTS + BRCA1_VARIANTS:
    VARIANT_INDEX[(str(row.get("gene", "")).upper(), int(row["position"]), str(row["mut_aa"]).upper())] = row

@lru_cache(maxsize=1)
def model_bundle() -> tuple[EsmTokenizer, EsmForMaskedLM, str, dict[str, int]]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = EsmTokenizer.from_pretrained(MODEL_NAME)
    model = EsmForMaskedLM.from_pretrained(MODEL_NAME).to(device).eval()
    aa_token_ids = {aa: tokenizer.convert_tokens_to_ids(aa) for aa in AA_LIST}
    return tokenizer, model, device, aa_token_ids


WT_CACHE: dict[tuple[str, int, int], dict[str, Any]] = {}


def residue_name(aa: str) -> str:
    return AA_TO_THREE.get(aa.upper(), aa.upper())


def protein_variant(position_0: int, wt_aa: str, mut_aa: str) -> str:
    return f"p.{residue_name(wt_aa)}{position_0 + 1}{residue_name(mut_aa)}"


def combined_raw_score(frob_dist: float, ll_proper: float) -> float:
    return ALPHA * float(frob_dist) + (1.0 - ALPHA) * float(ll_proper)


def combined_percentile(raw_score: float) -> float:
    rank = int(np.searchsorted(REFERENCE_COMBINED_SORTED, raw_score, side="right"))
    return round(100.0 * rank / len(REFERENCE_COMBINED_SORTED), 1)


def classification_from_percent(percent_value: float) -> tuple[str, str]:
    if percent_value > 55.0:
        return "Likely Pathogenic", "path"
    if percent_value < 35.0:
        return "Likely Benign", "benign"
    return "Uncertain", "uncertain"


def get_hidden_states(sequence: str, center_pos: int, window_radius: int = WINDOW_RADIUS) -> tuple[np.ndarray, torch.Tensor, int]:
    tokenizer, model, device, _ = model_bundle()
    start = max(0, center_pos - window_radius)
    end = min(len(sequence), center_pos + window_radius + 1)
    local_sequence = sequence[start:end]
    local_pos = center_pos - start
    inputs = tokenizer(local_sequence, return_tensors="pt", add_special_tokens=True, padding=False)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    hidden = torch.stack(outputs.hidden_states[1:], dim=0)[:, 0, 1:-1, :].cpu().numpy()
    logits = outputs.logits[0].cpu()
    return hidden, logits, local_pos


def compute_layer_stats(hidden_layers: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    stats: list[tuple[np.ndarray, np.ndarray]] = []
    for layer_hidden in hidden_layers:
        covariance = np.cov(layer_hidden.T)
        eigenvalues = np.sort(eigvalsh(covariance))
        stats.append((covariance, eigenvalues))
    return stats


def get_wildtype_bundle(gene: str, position_0: int, window_radius: int = WINDOW_RADIUS) -> dict[str, Any]:
    cache_key = (gene, position_0, window_radius)
    if cache_key not in WT_CACHE:
        hidden, logits, local_pos = get_hidden_states(SEQUENCES[gene], position_0, window_radius)
        WT_CACHE[cache_key] = {
            "hidden": hidden,
            "logits": logits,
            "local_pos": local_pos,
            "layer_stats": compute_layer_stats(hidden),
        }
    return WT_CACHE[cache_key]


def compute_ll_proper(logits_wt: torch.Tensor, local_pos: int, wt_aa: str, mut_aa: str) -> float:
    _, _, _, aa_token_ids = model_bundle()
    token_pos = local_pos + 1
    log_probs = torch.log_softmax(logits_wt[token_pos], dim=-1)
    return float(log_probs[aa_token_ids[wt_aa]].item() - log_probs[aa_token_ids[mut_aa]].item())


def compute_features(wt_bundle: dict[str, Any], hidden_mut: np.ndarray, wt_aa: str, mut_aa: str) -> dict[str, Any]:
    eps = 1e-10
    layer_stats_mut = compute_layer_stats(hidden_mut)
    shifts_log: list[float] = []
    trace_ratios: list[float] = []
    frob_dists: list[float] = []
    for (cov_wt, ev_wt), (cov_mut, ev_mut) in zip(wt_bundle["layer_stats"], layer_stats_mut):
        min_len = min(len(ev_wt), len(ev_mut))
        ev_wt_t = ev_wt[:min_len]
        ev_mut_t = ev_mut[:min_len]
        shifts_log.append(float(np.sum((np.log(np.abs(ev_mut_t) + eps) - np.log(np.abs(ev_wt_t) + eps)) ** 2)))
        tr_wt = float(np.trace(cov_wt))
        tr_mut = float(np.trace(cov_mut))
        trace_ratios.append(abs(tr_mut / tr_wt - 1.0) if abs(tr_wt) > eps else 0.0)
        frob_dists.append(float(np.linalg.norm(cov_mut - cov_wt, "fro")))
    return {
        "frob_dist": float(np.mean(frob_dists)),
        "trace_ratio": float(np.mean(trace_ratios)),
        "sps_log": float(np.mean(shifts_log)),
        "ll_proper": compute_ll_proper(wt_bundle["logits"], wt_bundle["local_pos"], wt_aa, mut_aa),
        "frob_per_layer": frob_dists,
    }


def build_placeholder_plot(message: str) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27",
        margin=dict(l=40, r=20, t=56, b=50),
        height=360,
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=13),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[dict(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(color="#94a3b8", size=14))],
    )
    return figure


def build_layer_plot(layer_values: list[float]) -> go.Figure:
    mean_value = float(np.mean(layer_values)) if layer_values else 0.0
    colors = ["#ffffff" if value > mean_value else "#7c3aed" for value in layer_values]
    figure = go.Figure(data=[go.Bar(x=list(range(1, len(layer_values) + 1)), y=layer_values, marker_color=colors, marker_line_color="#2a2d3a", marker_line_width=1, hovertemplate="Layer %{x}<br>FrobDist %{y:.4f}<extra></extra>")])
    figure.update_layout(
        title=dict(text="FrobDist per ESM2 Layer (1-30)", x=0.02, xanchor="left", font=dict(size=16, color="#f1f5f9")),
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#1a1d27",
        margin=dict(l=52, r=24, t=60, b=58),
        height=360,
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=13),
        xaxis=dict(title="ESM2 Layer", tickmode="linear", dtick=1, showgrid=False, linecolor="#2a2d3a", tickcolor="#2a2d3a", zeroline=False),
        yaxis=dict(title="Frobenius Distance", gridcolor="#2a2d3a", linecolor="#2a2d3a", tickcolor="#2a2d3a", zeroline=False),
        bargap=0.16,
        showlegend=False,
    )
    return figure


def format_feature(value: float) -> str:
    return f"{value:.4f}"


def render_empty_output() -> str:
    return '<div class="surface-card compact-card copy-card"><div style="color:#94a3b8;font-size:14px;line-height:1.7;">Select a variant and click Analyze</div></div>'


def render_error_output(message: str) -> str:
    safe = html.escape(message)
    return f'<div class="surface-card compact-card copy-card" style="border-color:#f87171 !important;"><div style="color:#f87171;font-size:12px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;">Input Error</div><div style="margin-top:10px;color:#f1f5f9;font-size:14px;line-height:1.7;">{safe}</div></div>'


def render_loading_output(gene: str, position_0_indexed: int, mutant_aa: str) -> str:
    gene_value = html.escape(str(gene).strip().upper() or "Variant")
    mutant_value = html.escape(str(mutant_aa).strip().upper() or "?")
    try:
        context = f"{gene_value} \u00b7 position {int(position_0_indexed)} \u00b7 mutant {mutant_value}"
    except Exception:
        context = f"{gene_value} \u00b7 mutant {mutant_value}"
    return (
        "<div class='surface-card compact-card copy-card analysis-loading-shell'>"
        f"<div style='color:#94a3b8;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;'>{context}</div>"
        "<div style='display:flex;align-items:center;gap:12px;'><span class='loading-spinner'></span>"
        "<span style='color:#f1f5f9;font-size:18px;font-weight:600;letter-spacing:-0.03em;'>Analyzing variant...</span></div>"
        "<div class='loading-track'><span></span></div>"
        "<div style='color:#94a3b8;font-size:14px;line-height:1.7;'>Running ESM2-150M on the selected local window, extracting covariance matrices, and computing spectral features across all 30 layers.</div>"
        "</div>"
    )


def render_result_output(result: dict[str, Any]) -> str:
    score_color = {"path": "#f87171", "uncertain": "#fbbf24", "benign": "#4ade80"}[result["tone"]]
    feature_specs = [("FrobDist", result["scores"]["frob_dist"], "#7c3aed"), ("TraceRatio", result["scores"]["trace_ratio"], "#a78bfa"), ("SPS-log", result["scores"]["sps_log"], "#94a3b8"), ("LL Proper", result["scores"]["ll_proper"], "#ffffff")]
    feature_cells = ''.join([f'<div style="background:#0f1117;border:1px solid #2a2d3a;border-radius:8px;padding:12px;"><div style="color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">{html.escape(name)}</div><div style="margin-top:6px;color:{color};font-size:15px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;">{format_feature(value)}</div></div>' for name, value, color in feature_specs])
    benchmark = ''
    if result.get("benchmark_name"):
        benchmark = f'<div style="margin-top:12px;color:#94a3b8;font-size:12px;">Local benchmark entry: {html.escape(result["benchmark_name"])} &middot; label {html.escape(result["benchmark_label_text"] or "Unknown")}</div>'
    return f'<div class="surface-card compact-card copy-card"><div style="color:#94a3b8;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;">{html.escape(result["display_context"])}</div><div style="margin-top:10px;color:{score_color};font-size:48px;font-weight:600;letter-spacing:-0.07em;line-height:1;">{result["combined_percentile"]:.1f}%</div><div style="margin-top:8px;color:{score_color};font-size:16px;font-weight:600;">{html.escape(result["label"])}</div><div style="margin-top:6px;color:#94a3b8;font-size:13px;line-height:1.7;">Combined score (FrobDist + LL Proper, &alpha;=0.55) calibrated as a TP53 reference percentile.</div><div style="margin-top:8px;color:#475569;font-size:12px;line-height:1.6;">Raw combined score {result["combined_raw"]:.4f} &middot; 0-index {result["position_0_indexed"]} &middot; 1-index {result["position_1_indexed"]} &middot; window &plusmn;40 residues</div><div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:18px;">{feature_cells}</div>{benchmark}</div>'


def score_variant(gene: str, position_0_indexed: int, mutant_aa: str) -> dict[str, Any]:
    gene_value = str(gene).strip().upper()
    if gene_value not in SEQUENCES:
        raise ValueError(f"Unsupported gene '{gene}'.")
    try:
        pos = int(position_0_indexed)
    except Exception as exc:
        raise ValueError("Position must be an integer in 0-indexed coordinates.") from exc
    mut = str(mutant_aa).strip().upper()
    if mut not in AA_SET:
        raise ValueError("Mutant amino acid must be one of the 20 canonical one-letter codes.")
    seq = SEQUENCES[gene_value]
    if pos < 0 or pos >= len(seq):
        raise ValueError(f"Position {pos} is out of range for {gene_value}. Valid range is 0 to {len(seq) - 1}.")
    wt = seq[pos]
    if wt == mut:
        raise ValueError(f"Mutant amino acid matches the wild-type residue at {gene_value} position {pos} ({wt}).")
    wt_bundle = get_wildtype_bundle(gene_value, pos, WINDOW_RADIUS)
    hidden_mut, _, _ = get_hidden_states(seq[:pos] + mut + seq[pos + 1 :], pos, WINDOW_RADIUS)
    features = compute_features(wt_bundle, hidden_mut, wt, mut)
    raw = combined_raw_score(features["frob_dist"], features["ll_proper"])
    percentile = combined_percentile(raw)
    label, tone = classification_from_percent(percentile)
    scaled = float(REFERENCE_SCALER.transform(np.array([[raw]], dtype=float))[0, 0])
    benchmark_row = VARIANT_INDEX.get((gene_value, pos, mut))
    benchmark_label_text = None if benchmark_row is None else ("Pathogenic" if int(benchmark_row.get("label", 0)) == 1 else "Benign")
    return {
        "status": "ok",
        "gene": gene_value,
        "position_0_indexed": pos,
        "position_1_indexed": pos + 1,
        "wt_aa": wt,
        "mutant_aa": mut,
        "protein_change": protein_variant(pos, wt, mut),
        "display_context": f"{gene_value} \u00b7 {protein_variant(pos, wt, mut)}",
        "combined_raw": raw,
        "combined_percentile": percentile,
        "combined_minmax": round(max(0.0, min(1.0, scaled)), 6),
        "label": label,
        "tone": tone,
        "scores": {"frob_dist": float(features["frob_dist"]), "trace_ratio": float(features["trace_ratio"]), "sps_log": float(features["sps_log"]), "ll_proper": float(features["ll_proper"])},
        "plot_values": [float(value) for value in features["frob_per_layer"]],
        "model": {"name": MODEL_NAME, "window_radius": WINDOW_RADIUS, "seed": SEED},
        "formula": {"alpha": ALPHA, "description": "0.55*frob_dist + 0.45*ll_proper"},
        "reference": {"distribution": "TP53 combined-score reference set", "n": int(len(REFERENCE_COMBINED_SORTED))},
        "benchmark_name": None if benchmark_row is None else benchmark_row.get("name"),
        "benchmark_label": None if benchmark_row is None else int(benchmark_row.get("label", 0)),
        "benchmark_label_text": benchmark_label_text,
        "links": LINKS,
    }


def run_analysis(gene: str, position_0_indexed: int, mutant_aa: str) -> tuple[str, go.Figure]:
    try:
        result = score_variant(gene, position_0_indexed, mutant_aa)
        return render_result_output(result), build_layer_plot(result["plot_values"])
    except Exception as exc:
        return render_error_output(str(exc)), build_placeholder_plot("No plot available for the current input.")


def show_loading_state(gene: str, position_0_indexed: int, mutant_aa: str) -> tuple[str, go.Figure]:
    return render_loading_output(gene, position_0_indexed, mutant_aa), build_placeholder_plot("Analyzing the selected local window across 30 ESM2 layers...")


def api_analysis(gene: str, position_0_indexed: int, mutant_aa: str) -> dict[str, Any]:
    return score_variant(gene, position_0_indexed, mutant_aa)


def apply_preset(label: str) -> tuple[str, int, str, str]:
    preset = PRESET_BY_LABEL[label]
    return preset["gene"], preset["position_0_indexed"], preset["mutant_aa"], preset["note"]

def build_overview_header_html() -> str:
    return (
        f"<div class='surface-card hero-card copy-card'>"
        "<div style='margin-top:18px;'><span class='hero-badge'>Claw4S 2026</span></div>"
        "<h1 style='margin:18px 0 0 0;color:#f1f5f9;font-size:36px;font-weight:600;letter-spacing:-0.07em;'>SpectralBio</h1>"
        "<p style='margin:12px auto 0 auto;max-width:860px;color:#94a3b8;font-size:16px;line-height:1.8;'>Spectral Covariance Analysis of PLM Hidden States for Zero-Shot Variant Pathogenicity Prediction</p>"
        "<div class='hero-chip-row'>"
        f"<a href='{LINKS['claw']}' target='_blank' class='hero-chip'><span style='font-size:18px;line-height:1;'>&#129438;</span>"
        "<span class='hero-chip-meta'><span class='hero-chip-title'>Claw</span><span class='hero-chip-subtitle'>AI Co-author</span></span></a>"
        f"<a href='{LINKS['author']}' target='_blank' class='hero-chip'><span class='hero-chip-mark'>DB</span>"
        "<span class='hero-chip-meta'><span class='hero-chip-title'>Davi Bonetto</span><span class='hero-chip-subtitle'>Independent Researcher</span></span></a>"
        f"</div><div class='hero-logo-stack'>"
        f"<img src='{CLAWRXIV_LOGO_URI}' alt='ClawRxiv' class='hero-clawrxiv-logo' />"
        f"<div class='hero-logo-row'>"
        f"<div class='hero-logo-panel'><img src='{STANFORD_LOGO_URI}' alt='Stanford University' class='hero-logo hero-logo-stanford' /></div>"
        f"<div class='hero-logo-panel hero-logo-panel-princeton'><img src='{PRINCETON_LOGO_URI}' alt='Princeton University' class='hero-logo hero-logo-princeton' /></div>"
        f"</div></div>"
        "</div></div>"
    )


def build_overview_abstract_html() -> str:
    return (
        f"<div class='surface-card abstract-card copy-card'>"
        "<div class='abstract-label'>Paper abstract</div>"
        "<h2 style='margin:12px 0 0 0;color:#f1f5f9;font-size:22px;font-weight:600;letter-spacing:-0.05em;'>A zero-shot spectral readout for protein variant pathogenicity</h2>"
        "<p style='margin:14px auto 0 auto;max-width:820px;color:#94a3b8;font-size:14px;line-height:1.8;'>SpectralBio tests whether covariance geometry in ESM2 hidden states carries mutation-level pathogenicity signal without retraining. The method compares wild-type and mutant local windows within a &plusmn;40 residue neighborhood, summarizes layerwise spectral perturbation with matrix-aware descriptors, and combines the strongest signal with LL Proper. In the v2 artifact set, the best TP53 combination reaches AUC 0.7498 on 255 variants, while LL Proper transfers to BRCA1 with AUC 0.9174 across 100 variants under zero retraining.</p>"
        "<div class='abstract-actions'>"
        f"<a class='cta-link cta-link-primary' href='{LINKS['clawrxiv']}' target='_blank'>Read full paper</a>"
        f"<a class='cta-link' href='{LINKS['dataset']}' target='_blank'>Open dataset</a>"
        "</div></div>"
    )


def build_stats_html() -> str:
    return "<div class='copy-card' style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;max-width:1080px;margin:20px auto 0 auto;'><div class='surface-card compact-card'><div style='color:#7c3aed;font-size:30px;font-weight:600;letter-spacing:-0.07em;'>0.7498</div><div style='margin-top:6px;color:#f1f5f9;font-size:14px;font-weight:500;'>AUC &mdash; TP53</div><div style='margin-top:4px;color:#94a3b8;font-size:12px;'>FrobDist + LL Proper &middot; N=255</div></div><div class='surface-card compact-card'><div style='color:#2dd4bf;font-size:30px;font-weight:600;letter-spacing:-0.07em;'>0.9174</div><div style='margin-top:6px;color:#f1f5f9;font-size:14px;font-weight:500;'>AUC &mdash; BRCA1</div><div style='margin-top:4px;color:#94a3b8;font-size:12px;'>Cross-protein transfer &middot; N=100</div></div><div class='surface-card compact-card'><div style='color:#4ade80;font-size:30px;font-weight:600;letter-spacing:-0.07em;'>0.0</div><div style='margin-top:6px;color:#f1f5f9;font-size:14px;font-weight:500;'>&Delta;rep &mdash; Reproducibility</div><div style='margin-top:4px;color:#94a3b8;font-size:12px;'>Exact &middot; seed=42</div></div></div>"


def build_method_html() -> str:
    return "<div class='copy-card' style='max-width:1080px;margin:24px auto 0 auto;'><h2 style='margin:0;color:#f1f5f9;font-size:20px;font-weight:600;letter-spacing:-0.03em;'>How it works</h2><p style='margin:14px 0 0 0;color:#94a3b8;font-size:14px;line-height:1.8;'>SpectralBio extracts covariance matrices from ESM2 hidden states in a local window of &plusmn;40 residues around the mutation, computes spectral features such as FrobDist, TraceRatio, and SPS-log, and combines them with LL Proper for zero-shot prediction.</p></div>"


def build_layer_explainer_html() -> str:
    return "<div class='surface-card compact-card copy-card'><h3 style='margin:0;color:#f1f5f9;font-size:16px;font-weight:600;letter-spacing:-0.03em;'>Layerwise spectral anatomy</h3><div style='margin-top:14px;display:grid;gap:12px;'><div style='display:grid;grid-template-columns:48px 1fr;gap:12px;align-items:start;'><div style='color:#7c3aed;font-size:12px;font-weight:600;letter-spacing:0.08em;'>01</div><div style='color:#94a3b8;font-size:14px;line-height:1.7;'>Wild-type and mutant local windows are encoded by ESM2-150M, producing 30 hidden-state layers per sequence.</div></div><div style='display:grid;grid-template-columns:48px 1fr;gap:12px;align-items:start;'><div style='color:#7c3aed;font-size:12px;font-weight:600;letter-spacing:0.08em;'>02</div><div style='color:#94a3b8;font-size:14px;line-height:1.7;'>Each layer is converted into a covariance matrix over hidden dimensions, preserving local representational geometry.</div></div><div style='display:grid;grid-template-columns:48px 1fr;gap:12px;align-items:start;'><div style='color:#7c3aed;font-size:12px;font-weight:600;letter-spacing:0.08em;'>03</div><div style='color:#94a3b8;font-size:14px;line-height:1.7;'>Spectral perturbation is summarized with FrobDist, TraceRatio, and SPS-log, while LL Proper reads the wild-type token likelihood margin.</div></div><div style='display:grid;grid-template-columns:48px 1fr;gap:12px;align-items:start;'><div style='color:#7c3aed;font-size:12px;font-weight:600;letter-spacing:0.08em;'>04</div><div style='color:#94a3b8;font-size:14px;line-height:1.7;'>The demo uses the best v2 combination exactly as reported in the paper: 0.55 &times; FrobDist + 0.45 &times; LL Proper.</div></div></div></div>"


def build_feature_glossary_html() -> str:
    return (
        "<div class='surface-card compact-card copy-card' style='margin-top:16px;'>"
        "<h3 style='margin:0;color:#f1f5f9;font-size:16px;font-weight:600;letter-spacing:-0.03em;'>What each score is reading</h3>"
        "<div class='feature-glossary-grid'>"
        "<div class='feature-tile'><h4 class='feature-tone-violet'>FrobDist</h4><p>Measures the full covariance-matrix shift between wild-type and mutant local windows.</p></div>"
        "<div class='feature-tile'><h4 class='feature-tone-light'>TraceRatio</h4><p>Tracks whether total variance expands or contracts after the mutation.</p></div>"
        "<div class='feature-tile'><h4 class='feature-tone-teal'>SPS-log</h4><p>Reads the log-scale movement of eigenvalues, emphasizing spectral redistribution.</p></div>"
        "<div class='feature-tile'><h4 class='feature-tone-white'>LL Proper</h4><p>Uses the wild-type forward pass to compare the native token against the mutant alternative.</p></div>"
        "</div><div style='margin-top:14px;padding:14px;border:1px solid #2a2d3a;border-radius:10px;background:#0f1117;color:#94a3b8;font-size:13px;line-height:1.8;'>In the live demo, the right-hand score panel keeps the raw feature values visible so you can tell whether a prediction is being driven mostly by covariance geometry, token likelihood, or both.</div></div>"
    )


def build_paper_discussion_html() -> str:
    return (
        "<div class='surface-card compact-card copy-card' style='margin-top:16px;'>"
        "<h3 style='margin:0;color:#f1f5f9;font-size:16px;font-weight:600;letter-spacing:-0.03em;'>Paper discussion highlights</h3>"
        "<div class='discussion-grid'>"
        "<div class='feature-tile'><h4 class='feature-tone-violet'>Combination signal</h4><p>The v2 best pair (0.55 &times; FrobDist + 0.45 &times; LL Proper) balances geometry shift and token-likelihood evidence without retraining.</p></div>"
        "<div class='feature-tile'><h4 class='feature-tone-teal'>Transfer behavior</h4><p>LL Proper reaches AUC 0.9174 in BRCA1 transfer, showing that wild-type token margin can carry strong cross-protein generalization signal.</p></div>"
        "<div class='feature-tile'><h4 class='feature-tone-white'>Interpretability</h4><p>The interface keeps raw feature values and layerwise bars visible so users can inspect whether a prediction is spectrum-driven, likelihood-driven, or mixed.</p></div>"
        "</div>"
        "<div style='margin-top:14px;padding:14px;border:1px solid #2a2d3a;border-radius:10px;background:#0f1117;color:#94a3b8;font-size:13px;line-height:1.8;'>These scores are calibrated percentiles against the TP53 reference distribution in <code>scores.json</code>, not direct clinical probabilities.</div>"
        "</div>"
    )


def build_results_table_html() -> str:
    return "<div class='surface-card compact-card copy-card'><h2 style='margin:0;color:#f1f5f9;font-size:20px;font-weight:600;letter-spacing:-0.03em;'>Results &mdash; TP53 Classification (N=255)</h2><table style='width:100%;border-collapse:collapse;margin-top:16px;'><thead><tr><th style='text-align:left;padding:10px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;font-weight:500;'>Method</th><th style='text-align:left;padding:10px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;font-weight:500;'>Type</th><th style='text-align:right;padding:10px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;font-weight:500;'>AUC-ROC</th></tr></thead><tbody><tr style='background:#1e1040;'><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>FrobDist + LL Proper</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#a78bfa;font-size:13px;'>combination</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#a78bfa;font-size:13px;text-align:right;font-weight:600;'>0.7498 &uarr;</td></tr><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>LL Crude (baseline)</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>likelihood</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;text-align:right;'>0.7026</td></tr><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>LL Crude + Trace + Frob</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>triple</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;text-align:right;'>0.7264</td></tr><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>TraceRatio</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>spectral-matrix</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#a78bfa;font-size:13px;text-align:right;'>0.6242</td></tr><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>FrobDist</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>spectral-matrix</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#a78bfa;font-size:13px;text-align:right;'>0.6209</td></tr><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>SPS-log</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>eigenvalue-only</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;text-align:right;'>0.5988</td></tr><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>LL Proper</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>likelihood</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;text-align:right;'>0.5956</td></tr></tbody></table><div style='height:1px;background:#2a2d3a;margin:18px 0;'></div><div style='color:#2dd4bf;font-size:14px;font-weight:600;'>BRCA1 Generalization (N=100, zero retraining)</div><table style='width:100%;border-collapse:collapse;margin-top:10px;'><tbody><tr><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:13px;'>LL Proper</td><td style='padding:12px 10px;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:13px;'>likelihood</td><td style='padding:12px 0;border-bottom:1px solid #2a2d3a;color:#2dd4bf;font-size:13px;text-align:right;font-weight:600;'>0.9174 &#10022;</td></tr><tr><td style='padding:12px 10px;color:#f1f5f9;font-size:13px;'>FrobDist</td><td style='padding:12px 10px;color:#94a3b8;font-size:13px;'>spectral-matrix</td><td style='padding:12px 0;color:#2dd4bf;font-size:13px;text-align:right;'>0.6401</td></tr></tbody></table><p style='margin:12px 0 0 0;color:#475569;font-size:12px;line-height:1.7;'>&#10022; LL Proper scores 0.5956 on TP53 but 0.9174 on BRCA1 &mdash; exceptional cross-protein transfer.</p></div>"


def build_links_html() -> str:
    return f"<div class='link-grid'><a class='secondary-link' href='{LINKS['github']}' target='_blank'>GitHub</a><a class='secondary-link' href='{LINKS['dataset']}' target='_blank'>Dataset</a><a class='secondary-link' href='{LINKS['clawrxiv']}' target='_blank'>clawRxiv</a><a class='secondary-link' href='{LINKS['skill']}' target='_blank'>SKILL.md</a></div>"


def build_citation_html() -> str:
    bibtex = "@misc{bonetto2026spectralbio,\n  title={SpectralBio: Spectral Covariance Analysis of PLM Hidden States for Zero-Shot Variant Pathogenicity Prediction},\n  author={Davi Bonetto and Claw},\n  year={2026},\n  howpublished={Claw4S 2026 submission},\n  note={Stanford + Princeton executable science track},\n  url={http://www.clawrxiv.io}\n}"
    return f"<div class='surface-card compact-card copy-card'><div style='color:#475569;font-size:11px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;'>Citation</div><pre style='margin-top:12px;'>{html.escape(bibtex)}</pre></div>"


def build_try_intro_html() -> str:
    return "<div class='surface-card compact-card copy-card' style='margin-bottom:14px;'><div class='abstract-label'>Interactive demo</div><h2 style='margin:10px 0 0 0;color:#f1f5f9;font-size:20px;font-weight:600;letter-spacing:-0.03em;'>Analyze a variant</h2><p style='margin:12px 0 0 0;color:#94a3b8;font-size:14px;line-height:1.8;'>Choose a gene, enter a 0-indexed substitution, and run the exact SpectralBio v2 scoring pipeline exposed by this Space.</p><p style='margin:10px 0 0 0;color:#94a3b8;font-size:13px;line-height:1.7;'>Positions stay 0-indexed for agent-friendly reproducibility, while all rendered protein changes are mirrored back in standard 1-indexed notation for humans.</p></div>"


def build_agent_repro_html() -> str:
    return "<div class='surface-card compact-card copy-card' style='border-color:#4ade80 !important;'><div style='color:#4ade80;font-size:16px;font-weight:600;'>SKILL.md available &mdash; fully reproducible pipeline</div><p style='margin:10px 0 0 0;color:#94a3b8;font-size:14px;line-height:1.7;'>Any agent can reproduce the paper workflow in roughly 24 minutes on a Colab T4 using the repo-local SKILL.md. Seeds are fixed, datasets are public, and the pipeline requires zero manual configuration.</p><pre style='margin-top:14px;'>Seeds: 42 (PyTorch, NumPy, random)\nModel: facebook/esm2_t30_150M_UR50D\nDataset: ClinVar FTP (public)\nRuntime: ~1447s on NVIDIA T4\nDelta_rep: 0.0 (exact)</pre></div>"


def build_agent_api_html() -> str:
    return "<div class='surface-card compact-card copy-card'><h3 style='margin:0;color:#f1f5f9;font-size:16px;font-weight:600;letter-spacing:-0.03em;'>API scores from this Space</h3><p style='margin:10px 0 0 0;color:#94a3b8;font-size:14px;line-height:1.7;'>This demo exposes a programmatic JSON endpoint via Gradio. Agents can call the Space directly and receive the same calibrated score, raw feature values, metadata, and benchmark annotations that power the UI.</p><pre style='margin-top:14px;'>from gradio_client import Client\n\nclient = Client(\"DaviBonetto/spectralbio-demo\")\nresult = client.predict(\n    \"TP53\",\n    174,\n    \"H\",\n    api_name=\"/score_variant\",\n)\nprint(result[\"combined_percentile\"], result[\"label\"])</pre></div>"


with gr.Blocks(title="SpectralBio") as demo:
    with gr.Tabs(elem_id="main-tabs"):
        with gr.Tab("01 Overview", id="overview", elem_id="overview-tab"):
            if HERO_BG_PATH is not None:
                gr.Image(value=str(HERO_BG_PATH), show_label=False, interactive=False, container=False, elem_id="hero-image", elem_classes="figure-media")
            gr.HTML(build_overview_header_html())
            gr.HTML(build_overview_abstract_html())
            gr.HTML(build_stats_html())
            gr.HTML(build_method_html())
            if METHOD_DIAGRAM_PATH is not None:
                gr.Image(value=str(METHOD_DIAGRAM_PATH), show_label=False, interactive=False, container=False, elem_classes="figure-media")
            with gr.Row(equal_height=True):
                with gr.Column(scale=4):
                    if ESM2_LAYERS_PATH is not None:
                        gr.Image(value=str(ESM2_LAYERS_PATH), show_label=False, interactive=False, container=False, elem_classes="figure-media")
                with gr.Column(scale=5):
                    gr.HTML(build_layer_explainer_html())
                    gr.HTML(build_feature_glossary_html())
                    gr.HTML(build_paper_discussion_html())
            with gr.Row(equal_height=True):
                with gr.Column(scale=5):
                    gr.HTML(build_results_table_html())
                with gr.Column(scale=4):
                    if RESULTS_FIGURE_PATH is not None:
                        gr.Image(value=str(RESULTS_FIGURE_PATH), show_label=False, interactive=False, container=False, elem_classes="figure-media")
            gr.HTML(build_links_html())
            gr.HTML(build_citation_html())
            with gr.Row():
                overview_next = gr.Button("Next: Try it", elem_classes="nav-primary-btn")
                overview_agents = gr.Button("Jump to AI Agents", elem_classes="nav-secondary-btn")
        with gr.Tab("02 Try It", id="try-it", elem_id="try-tab"):
            gr.HTML(build_try_intro_html())
            with gr.Row(equal_height=False):
                with gr.Column(scale=4, elem_classes=["surface-card", "input-panel"]):
                    gene_input = gr.Dropdown(choices=["TP53", "BRCA1"], value="TP53", label="Gene", container=False)
                    position_input = gr.Number(value=174, precision=0, label="Position (0-indexed)", info="Example: p.Arg175His = position 174.", container=False)
                    mutant_input = gr.Dropdown(choices=AA_LIST, value="H", label="Mutant amino acid", container=False)
                    gr.HTML("<div style='margin-top:18px;color:#94a3b8;font-size:12px;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;'>Curated presets</div>")
                    preset_note = gr.Markdown(PRESETS[0]["note"], elem_classes="helper-text")
                    with gr.Row():
                        preset_1 = gr.Button("TP53 R175H", elem_classes="preset-btn")
                        preset_2 = gr.Button("TP53 R248W", elem_classes="preset-btn")
                    with gr.Row():
                        preset_3 = gr.Button("TP53 R273H", elem_classes="preset-btn")
                        preset_4 = gr.Button("TP53 P72R", elem_classes="preset-btn")
                    with gr.Row():
                        preset_5 = gr.Button("BRCA1 M1775R", elem_classes="preset-btn")
                    analyze_button = gr.Button("Analyze variant", elem_classes="primary-action")
                    gr.HTML("<div class='helper-text'>ESM2-150M is loaded lazily on the first run. Subsequent analyses reuse the cached model and wild-type forward passes.</div>")
                with gr.Column(scale=5, elem_classes=["surface-card", "copy-card"]):
                    result_output = gr.HTML(render_empty_output())
            layer_plot = gr.Plot(value=build_placeholder_plot("Run an analysis to see the layerwise perturbation profile."), container=False, elem_classes="plot-shell")
            with gr.Row():
                try_overview = gr.Button("Back: Overview", elem_classes="nav-secondary-btn")
                try_agents = gr.Button("Next: For AI Agents", elem_classes="nav-primary-btn")
            preset_1.click(lambda: apply_preset("TP53 R175H"), outputs=[gene_input, position_input, mutant_input, preset_note])
            preset_2.click(lambda: apply_preset("TP53 R248W"), outputs=[gene_input, position_input, mutant_input, preset_note])
            preset_3.click(lambda: apply_preset("TP53 R273H"), outputs=[gene_input, position_input, mutant_input, preset_note])
            preset_4.click(lambda: apply_preset("TP53 P72R"), outputs=[gene_input, position_input, mutant_input, preset_note])
            preset_5.click(lambda: apply_preset("BRCA1 M1775R"), outputs=[gene_input, position_input, mutant_input, preset_note])
            analyze_event = analyze_button.click(show_loading_state, inputs=[gene_input, position_input, mutant_input], outputs=[result_output, layer_plot], queue=False, show_progress="hidden")
            analyze_event.then(run_analysis, inputs=[gene_input, position_input, mutant_input], outputs=[result_output, layer_plot], api_name="analyze_variant_ui", show_progress="full")
            hidden_api_button = gr.Button(visible=False)
            hidden_api_json = gr.JSON(visible=False)
            hidden_api_button.click(api_analysis, inputs=[gene_input, position_input, mutant_input], outputs=hidden_api_json, api_name="score_variant", show_progress="hidden")
        with gr.Tab("03 AI Agents", id="agents", elem_id="agents-tab"):
            gr.HTML(build_agent_repro_html())
            gr.Markdown("### Quick start for AI agents\n\n```bash\ngit clone https://github.com/DaviBonetto/SpectralBio\ncd SpectralBio\nopenclaw run SKILL.md\n```\n\nAny agent that can read `SKILL.md` can reproduce the workflow end-to-end, inspect the benchmark artifacts, and align the Space outputs with the executable-science pipeline.", elem_classes=["surface-card", "compact-card", "copy-card"])
            gr.HTML(build_agent_api_html())
            with gr.Row():
                agents_try = gr.Button("Back: Try it", elem_classes="nav-secondary-btn")
                agents_overview = gr.Button("Back to Overview", elem_classes="nav-primary-btn")

    overview_next.click(fn=None, js="() => { document.getElementById('try-tab-button')?.click(); window.scrollTo({ top: 0, behavior: 'smooth' }); }")
    overview_agents.click(fn=None, js="() => { document.getElementById('agents-tab-button')?.click(); window.scrollTo({ top: 0, behavior: 'smooth' }); }")
    try_overview.click(fn=None, js="() => { document.getElementById('overview-tab-button')?.click(); window.scrollTo({ top: 0, behavior: 'smooth' }); }")
    try_agents.click(fn=None, js="() => { document.getElementById('agents-tab-button')?.click(); window.scrollTo({ top: 0, behavior: 'smooth' }); }")
    agents_try.click(fn=None, js="() => { document.getElementById('try-tab-button')?.click(); window.scrollTo({ top: 0, behavior: 'smooth' }); }")
    agents_overview.click(fn=None, js="() => { document.getElementById('overview-tab-button')?.click(); window.scrollTo({ top: 0, behavior: 'smooth' }); }")

demo.queue(default_concurrency_limit=2)

if __name__ == "__main__":
    demo.launch(css=CSS, theme=gr.themes.Base())
